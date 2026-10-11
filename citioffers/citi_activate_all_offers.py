#!/usr/bin/env python3
"""
Citi Activate All Merchant Offers — standalone script.

Mirrors citi_activate_all_offers.user.js but runs outside the browser.
Uses curl_cffi to impersonate a real browser (Chrome) TLS/JA3/JA4 fingerprint
so the requests are not flagged as non-browser clients.

Auth: paste your session cookies (from a logged-in online.citi.com tab)
into CITI_COOKIES below, or pass them via the --cookies-file flag
(export the browser cookies as a single "k1=v1; k2=v2" header string,
or a Netscape-format file if you prefer the --cookies-netscape flag).

The most important cookie is `tmx_sessionid` (sent as the tmxsessionid
header). `accountId` is normally auto-detected from the retrieve response
(cardArtDetails[0].accountId), with the cookie as a fallback.

Usage:
    python3 citi_activate_all_offers.py                     # list + activate all
    python3 citi_activate_all_offers.py --list-only
    python3 citi_activate_all_offers.py --dry-run
    python3 citi_activate_all_offers.py --cookies "tmx_sessionid=...; JSESSIONID=..."
    python3 citi_activate_all_offers.py --delay 1.0
"""

import argparse
import getpass
import json
import os
import sys
import time
from http.cookiejar import CookieJar

from curl_cffi.requests import Session

try:
    import citi_session
except ImportError:
    citi_session = None

BASE_URL = "https://online.citi.com"
API = "/gcgapi/prod/public/v1"
RETRIEVE_URL = API + "/digital/customers/creditCards/merchantOffers/retrieve"
ENROLL_URL = API + "/digital/customers/creditCards/accounts/rewards/specialOffers/enrollMerchantOffer"

# Headers exactly as sent by the browser (see HAR). Note: businesscode/
# countrycode/channelid/appversion/environmentid are lowercase on the offers
# API but camelCase on the login API — they differ between the two hosts.
REQ_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": BASE_URL,
    "Referer": BASE_URL + "/US/nga/products-offers/merchantoffers",
    "client_id": "4a51fb19-a1a7-4247-bc7e-18aa56dd1c40",
    "businessCode": "GCB",
    "countryCode": "US",
    "channelId": "CBOL",
    "appVersion": "CBOL-ANG-2026-09-00",
    "environmentID": "SuperMarioPROD",
}

GREEN = "\033[92m"
RED = "\033[91m"
DIM = "\033[2m"
RESET = "\033[0m"


def log(msg: str) -> None:
    print(msg, flush=True)


def build_session(cookie_source: str | None, cookie_is_netscape: bool,
                  browser: str = "chrome") -> Session:
    """Create a curl_cffi session that impersonates a real browser."""
    s = citi_session.new_session(browser) if citi_session else Session(impersonate=browser)

    if cookie_source:
        if cookie_is_netscape:
            jar = CookieJar()
            with open(cookie_source) as f:
                jar.load(f)
            s.cookies = {c.name: c.value for c in jar}
        else:
            for part in cookie_source.split(";"):
                part = part.strip()
                if not part or "=" not in part:
                    continue
                k, v = part.split("=", 1)
                s.cookies[k.strip()] = v.strip()

    return s


def api_post(s: Session, path: str, body: dict) -> dict:
    headers = dict(REQ_HEADERS)
    # The offers API authenticates via the tmx_sessionid cookie, mirrored into
    # the TMXSessionId header (and the legacy tmxsessionid header the
    # userscript used). Both are set from the same cookie.
    tmx = s.cookies.get("tmx_sessionid")
    if tmx:
        headers["TMXSessionId"] = tmx
        headers["tmxsessionid"] = tmx

    resp = s.post(BASE_URL + path, headers=headers, json=body or {})
    text = resp.text
    if resp.status_code >= 400:
        raise RuntimeError(f"HTTP {resp.status_code}: {text[:200]}")
    return json.loads(text)


def fetch_offers(s: Session) -> dict:
    return api_post(s, RETRIEVE_URL, {})


def enroll_offer(s: Session, offer_id: str, account_id: str) -> dict:
    return api_post(s, ENROLL_URL, {
        "offerId": offer_id,
        "accountId": account_id,
        "oneClickEnroll": "true",
    })


def unique_offers(data: dict):
    seen = set()
    unique = []
    for cat in data.get("merchantOffers") or []:
        for o in cat.get("offers") or []:
            if o.get("offerId") not in seen:
                seen.add(o["offerId"])
                unique.append({**o, "category": cat.get("displayOffersCategory")})
    return unique


def resolve_account_id(data: dict, s: Session) -> str | None:
    cards = data.get("cardArtDetails") or []
    if cards and cards[0].get("accountId"):
        return cards[0]["accountId"]
    return s.cookies.get("accountId")


def cmd_list(s: Session, prefetched: dict | None = None) -> int:
    log(f"{DIM}Fetching offers…{RESET}")
    data = prefetched if prefetched is not None else fetch_offers(s)
    offers = unique_offers(data)
    avail = sum(1 for o in offers if o.get("offerStatus") == "AVAILABLE")
    enrolled = sum(1 for o in offers if o.get("offerStatus") == "ENROLLED")
    log(f"{len(offers)} total  ({avail} available, {enrolled} enrolled)\n")
    for o in offers:
        icon = "\U0001F7E2" if o.get("offerStatus") == "AVAILABLE" else "\U0001F535"
        log(f"{icon} [{o.get('offerStatus','?'):>9}] "
            f"{o.get('merchantName','?')} — {o.get('offerTitle','?')}")
    return 0


def cmd_activate(s: Session, delay: float, dry_run: bool) -> int:
    log(f"{DIM}Loading offers and account info…{RESET}")
    try:
        data = fetch_offers(s)
    except Exception as e:
        log(f"{RED}Failed to fetch offers: {e}{RESET}")
        return 1

    account_id = resolve_account_id(data, s)
    if not account_id:
        log(f"{RED}Could not find accountId. Are you logged in? "
            f"(pass a cookies string containing tmx_sessionid){RESET}")
        return 1
    log(f"Account: {account_id}\n")

    available = [o for o in unique_offers(data)
                 if o.get("offerStatus") == "AVAILABLE"]

    if not available:
        log("No available offers to activate.")
        return 0

    log(f"Enrolling {len(available)} offers…{' (dry run)' if dry_run else ''}\n")
    ok = fail = 0

    for i, o in enumerate(available, 1):
        label = (f"[{i}/{len(available)}] "
                 f"{o.get('merchantName','?'):<30} {o.get('offerTitle','?')}  ")
        if dry_run:
            log(f"{DIM}{label} … skipped{RESET}")
            continue
        try:
            enroll_offer(s, o["offerId"], account_id)
            ok += 1
            log(f"{GREEN}{label} … OK{RESET}")
        except Exception as e:
            fail += 1
            log(f"{RED}{label} … FAIL – {str(e)[:80]}{RESET}")
        time.sleep(delay)

    if not dry_run:
        log(f"\nDone  enrolled: {ok}  failed: {fail}  total: {len(available)}")
    return 0 if fail == 0 else 1


def main() -> int:
    p = argparse.ArgumentParser(description="Activate all Citi merchant offers.")
    p.add_argument("--cookies", help='"k1=v1; k2=v2" cookie string from online.citi.com')
    p.add_argument("--cookies-file", help="file containing a 'k1=v1; k2=v2' cookie string")
    p.add_argument("--cookies-netscape", action="store_true",
                   help="treat --cookies-file as a Netscape-format cookies.txt")
    p.add_argument("--offers", help="use a pre-fetched offers JSON file (from "
                   "citi_nodriver_login.py --offers) instead of calling the API.")
    p.add_argument("--list-only", action="store_true", help="only list offers")
    p.add_argument("--dry-run", action="store_true", help="list what would be enrolled")
    p.add_argument("--delay", type=float, default=0.5,
                   help="seconds between enroll requests (default 0.5)")
    p.add_argument("--browser", default="firefox135",
                   help="curl_cffi impersonate target: chrome, safari, firefox, "
                        "edge, firefox135 (default firefox135, matches the HAR)")
    p.add_argument("-u", "--user", help="Citi username (enables auto-login)")
    p.add_argument("-p", "--password",
                   help="Citi password (or read from CITI_PASSWORD env / prompt)")
    p.add_argument("--cookies-out", help="save the fresh session cookies to this file")
    args = p.parse_args()

    cookie_source = None
    if args.cookies_file:
        with open(args.cookies_file) as f:
            cookie_source = f.read().strip()
    elif args.cookies:
        cookie_source = args.cookies

    # --offers: pre-fetched offers file (bypasses the API/bot-gate for listing)
    prefetched = None
    if args.offers:
        with open(args.offers) as f:
            prefetched = json.load(f)

    if not cookie_source and not args.user and not prefetched:
        p.error("provide --cookies/--cookies-file, --user, or --offers")

    s = build_session(cookie_source, args.cookies_netscape, args.browser)

    # Auto-login with credentials (optional; works alongside or instead of cookies)
    if args.user:
        if not citi_session:
            p.error("--user requires citi_session.py (same directory)")
        password = args.password or os.environ.get("CITI_PASSWORD") \
            or getpass.getpass(f"Password for {args.user}: ")
        print(f"Logging in as {args.user} …", file=sys.stderr)
        try:
            citi_session.login(s, args.user, password)
            citi_session.establish_offers_session(s)
            print("Login OK.", file=sys.stderr)
        except Exception as e:
            print(f"Login failed: {e}", file=sys.stderr)
            return 1
        if args.cookies_out:
            citi_session.export_cookies(s, args.cookies_out)
            print(f"Saved session cookies to {args.cookies_out}", file=sys.stderr)

    if args.list_only:
        return cmd_list(s, prefetched)
    if args.dry_run:
        cmd_list(s, prefetched)
        log("")
        if prefetched:
            log("(list only — activate via --offers requires a live API session)")
            return 0
        return cmd_activate(s, args.delay, dry_run=True)
    if prefetched:
        log("(using pre-fetched offers for listing; live enrollment needs --cookies/--user)")
        return cmd_list(s, prefetched)
    return cmd_activate(s, args.delay, dry_run=False)


if __name__ == "__main__":
    sys.exit(main())
