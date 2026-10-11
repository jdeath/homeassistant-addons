#!/usr/bin/env python3
"""
Shared Citi session + login primitives (reverse-engineered from the login
frontend bundle + HAR).

Citi's login has NO captcha. It uses a client-side end-to-end (e2e) crypto
exchange to protect the password in transit. The exact protocol:

  randomValues():
      blob = 256 random hex chars (128 bytes);  n,i,r,s = blob[0:64][64:128][128:192][192:256]
      iv   = HMAC-SHA256(r, key=n)[:32 hex]
      eKey = HMAC-SHA256(i, key=n)      (32 bytes)
      hKey = HMAC-SHA256(s, key=n)      (32 bytes)
      CR   = 32 random hex chars         (client random, 16 bytes)
  (HMAC key = the slice as hex bytes; message = the slice as hex bytes.)

  1. GET  /security/e2e/key                -> {"modulus"(2048),"exponent":65537}
  2. POST /security/e2e/key                -> registers key material; returns `eventid`
         response header (the encrypted session-recovery token, "eventID")
         { "encryptedPayload":  b64(RSA(eKey + iv + hKey)),  # 48B -> 256B, base64
           "encKeyCheckDigit":  hex(AES-NoPad(eKey, iv, " "*16))[:6],
           "hmacKeyCheckDigit": hex(AES-NoPad(hKey, iv, " "*16))[:6],
           "algorithm": "AES" }
  3. eventID = b64(AES-CBC(body)) + "." + b64(AES-CBC(tail))
         decSR = AES-CBC-decrypt(b64decode(eventID part0))     # the 32-byte session secret
  4. POST /cbol/security/auth/passwordLogin
         password field = b64(AES-NOPAD(eKey, iv, CR + decSR + "b" + password))
                          + "." + b64(HMAC-SHA256(hex(ciphertext), key=hKey))
         (AES-NOPAD: the message is padded with zero bytes up to a 16-byte boundary.)
         The response sets citi_authorization / isLoggedIn cookies and returns
         customerProfileData (accountId, ccsId, …).

  After login, navigating to online.citi.com ROTATES the `tmx_sessionid`
  cookie. The offers API then sends that cookie value back as the
  `TMXSessionId` header.

Uses curl_cffi to impersonate a real browser TLS fingerprint (firefox135,
matching the captured HAR).
"""

import base64
import hashlib
import hmac
import os

from curl_cffi.requests import Session
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from Crypto.Cipher import AES

DEFAULT_BROWSER = "firefox135"

CLIENT_ID = "4a51fb19-a1a7-4247-bc7e-18aa56dd1c40"

WWW = "https://www.citi.com"
OLN = "https://online.citi.com"
API = "/gcgapi/prod/public/v1"

E2E_KEY = WWW + API + "/security/e2e/key"
SIGNOFF = WWW + API + "/digital/security/auth/demotedCustomerSignoff"
PASSWORD_LOGIN = WWW + API + "/cbol/security/auth/passwordLogin"
OFFERS_PAGE = OLN + "/US/nga/products-offers/merchantoffers"

LOG_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": WWW,
    "Referer": OFFERS_PAGE,
    "client_id": CLIENT_ID,
    "businessCode": "GCB",
    "countryCode": "US",
    "channelId": "CBOL",
    "appVersion": "173875-CBOL-ANGS-2025-08-00",
    "tenantId": "DEFAULT",
    "appId": "BROWSER",
    "environmentId": "loginAuth",
    "countOfUserName": "1",
}


# --------------------------------------------------------------------------- #
#  Crypto helpers (match the JS CryptoJS usage exactly)
# --------------------------------------------------------------------------- #
def _b64(b: bytes) -> str:
    return base64.b64encode(b).decode()


def _b64pad(b: bytes) -> str:
    return base64.b64encode(b).decode().rstrip("=")


def _aes_cbc(key: bytes, iv: bytes, pt: bytes) -> bytes:
    return AES.new(key, AES.MODE_CBC, iv).encrypt(pt)


def _zero_pad16(b: bytes) -> bytes:
    n = len(b) % 16
    return b + b"\x00" * (16 - n if n else 0)


def _hmac_sha256_hex(msg_hex: str, key_hex: str) -> str:
    """JS: Mac(alg=HmacSHA256, pass:{hex:key}).updateHex(msg).doFinal()."""
    return hmac.new(bytes.fromhex(key_hex),
                    bytes.fromhex(msg_hex), hashlib.sha256).hexdigest()


def random_values() -> dict:
    """Replicate the frontend's randomValues() key derivation."""
    blob = os.urandom(128).hex()
    n, i, r, s = blob[0:64], blob[64:128], blob[128:192], blob[192:256]
    return {
        "iv": _hmac_sha256_hex(r, n)[:32],
        "eKey": _hmac_sha256_hex(i, n),
        "hKey": _hmac_sha256_hex(s, n),
        "CR": os.urandom(16).hex(),
    }


def rsa_encrypt_pkcs1v15(n: int, e: int, msg: bytes) -> str:
    pub = rsa.RSAPublicNumbers(e, n).public_key()
    return pub.encrypt(msg, padding.PKCS1v15()).hex()


# --------------------------------------------------------------------------- #
#  Session factory
# --------------------------------------------------------------------------- #
def new_session(browser: str = DEFAULT_BROWSER) -> Session:
    s = Session(impersonate=browser)
    s.headers.update({"Accept-Language": "en-US,en;q=0.9", "DNT": "1", "Sec-GPC": "1"})
    return s


def _parse_eventid(eventid: str, eKey: bytes, iv: bytes) -> bytes | None:
    """Decrypt the eventID token's first ciphertext part -> the 32-byte decSR.
    eventID = b64(AES-CBC(body)) + '.' + b64(AES-CBC(tail))."""
    if not eventid:
        return None
    parts = [p for p in eventid.split(".") if p != ""]
    try:
        c1 = base64.b64decode(parts[0])
        return AES.new(eKey, AES.MODE_CBC, iv).decrypt(c1)
    except Exception:
        return None


# --------------------------------------------------------------------------- #
#  Login
# --------------------------------------------------------------------------- #
def login(s: Session, username: str, password: str) -> dict:
    """Full Citi password login. Returns the parsed passwordLogin response on
    success, raises on failure. Populates s.cookies in place."""
    h = dict(LOG_HEADERS)

    try:
        s.delete(SIGNOFF, headers=h, json={})
    except Exception:
        pass

    # 1. RSA public key
    r = s.get(E2E_KEY, headers=h)
    r.raise_for_status()
    mod = r.json()
    n, e = int(mod["modulus"], 16), int(mod["exponent"], 16)

    # NOTE: In a real browser the e2e POST is only reached AFTER a ThreatMetrix
    # sensor handshake (content22.online.citi.com sensor pings + the bm_sz beacon
    # chain), which is what makes the server accept the key exchange and return
    # the base64 `eventid` token. A plain curl_cffi client skips that, so the
    # e2e POST typically returns 400 and no usable eventid. See citi_login.py
    # --diag. The reliable path is a real-browser login (cookies) + this script
    # for the offers API, which does NOT need the e2e handshake.

    # 2. derive key material + register it (returns the eventid header)
    kv = random_values()
    iv = bytes.fromhex(kv["iv"])
    eKey = bytes.fromhex(kv["eKey"])
    hKey = bytes.fromhex(kv["hKey"])
    cr = bytes.fromhex(kv["CR"])
    payload = rsa_encrypt_pkcs1v15(n, e, eKey + iv + hKey)  # hex (256B -> 512 chars)
    r = s.post(E2E_KEY, headers=h, json={
        "encryptedPayload": payload,
        "encKeyCheckDigit": _aes_cbc(eKey, iv, b" " * 16).hex()[:6],
        "hmacKeyCheckDigit": _aes_cbc(hKey, iv, b" " * 16).hex()[:6],
        "algorithm": "AES",
    })
    if r.status_code >= 400:
        raise RuntimeError(
            f"e2e key POST rejected (HTTP {r.status_code}): {r.text[:200]} — the "
            "server is rejecting the key exchange. See citi_login.py --diag."
        )
    eventid = r.headers.get("eventid") or r.headers.get("Eventid") or ""

    # 3. recover the server session secret (decSR) from the eventID token
    dec_sr = _parse_eventid(eventid, eKey, iv)
    if dec_sr is None:
        raise RuntimeError(
            "Could not recover the session secret (decSR) from the e2e eventid. "
            "The key material may not match what the server expects."
        )

    # 4. build the encrypted password: AES-NOPAD(CR + decSR + "b" + pwd) . HMAC
    raw = cr + dec_sr + b"b" + password.encode()
    ct = _aes_cbc(eKey, iv, _zero_pad16(raw))
    tag = bytes.fromhex(_hmac_sha256_hex(ct.hex(), kv["hKey"]))
    encrypted_password = _b64(ct) + "." + _b64(tag)

    headers = dict(h)
    headers["TMXDigitalApplicationType"] = "PC_BROWSER"
    headers["BioCatchSessionId"] = s.cookies.get("bcsid", "")
    headers["customersessionid"] = s.cookies.get("bcsid", "")

    # 5. login
    r = s.post(PASSWORD_LOGIN, headers=headers, json={
        "userId": username,
        "password": encrypted_password,
        "privateMode": False,
        "rememberUserIdFlag": False,
    })
    text = r.text
    if r.status_code >= 400:
        raise RuntimeError(f"passwordLogin HTTP {r.status_code}: {text[:300]}")
    try:
        data = r.json()
    except ValueError:
        raise RuntimeError(f"passwordLogin non-JSON response: {text[:300]}")

    mfa = data.get("mfaResponse", {})
    if mfa.get("mfaResponse") != "ALLOW":
        raise RuntimeError(f"MFA required: {mfa.get('mfaChallengeType')}")
    return data


def establish_offers_session(s: Session) -> None:
    """Hit the offers page so online.citi.com issues/rotates the
    `tmx_sessionid` cookie (and `citi_authorization`) the API expects."""
    s.get(OFFERS_PAGE, headers={"Referer": WWW + "/login"}, allow_redirects=True)


def export_cookies(s: Session, path: str) -> None:
    """Write the session's citi.com cookies as a 'k=v; k=v' header string."""
    jar = s.cookies.jar
    cookies = jar if isinstance(jar, list) else list(jar)
    parts = [f'{c["name"]}={c["value"]}' for c in cookies
             if "citi.com" in (c.get("domain") or "")]
    with open(path, "w") as f:
        f.write("; ".join(parts))
