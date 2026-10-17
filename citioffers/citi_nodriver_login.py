#!/usr/bin/env python3
"""
Citi login via nodriver (ultrafunkamsterdam/nodriver) — a real, non-"webdriver"
Chrome instance. This is the reliable path around Citi's ThreatMetrix bot gate
that blocks the pure curl_cffi e2e handshake (see citi_session.py / citi_login.py).

nodriver talks straight to Chrome over CDP (no webdriver automation flags), so it
passes the same TLS/JS fingerprint checks the real site expects. The login page
is an Angular SPA, so we auto-fill the credential fields, click sign-in, and
detect success by watching for the `tmx_sessionid` cookie. If Citi presents
MFA/2FA (or the layout changed), it prints a hint and waits for you to finish
manually in the window (or re-run with --manual to skip auto-fill entirely).

Outputs a cookies file compatible with citi_activate_all_offers.py.

Usage:
    pip install nodriver --break-system-packages
    python3 citi_nodriver_login.py --user YOUR_USERNAME        # prompts for password
    python3 citi_nodriver_login.py --user U -p P -o session.txt
    python3 citi_nodriver_login.py --user U --manual           # you do the typing/MFA
    python3 citi_nodriver_login.py --user U --keep-open        # stay open (reuse / debug)

NOTE: a real browser window opens. nodriver needs a system Chrome/Chromium.
"""

import argparse
import asyncio
import getpass
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import nodriver as uc
except ImportError:
    sys.exit("nodriver is not installed. Run:  pip install nodriver --break-system-packages")

# Verbose logging is OFF by default so the run output stays clean. Turn it on
# with --verbose (or the VERBOSE=1 env) only when debugging.
VERBOSE = os.environ.get("VERBOSE", "").lower() in ("1", "true", "yes", "on")

def log(msg: str):
    """Diagnostic line — printed only in verbose mode."""
    if VERBOSE:
        print(msg, file=sys.stderr, flush=True)

def info(msg: str):
    """Essential progress/result line — always printed."""
    print(msg, file=sys.stderr, flush=True)

# Start on the OFFERS page itself. If not authenticated, Citi redirects to the
# sign-on page; after login it redirects back to the offers page — which
# establishes the online.citi.com SSO session (a fresh profile logging in on
# www.citi.com does NOT always carry over to online.citi.com, which is why a
# fresh Docker profile bounced to the homepage). This mirrors what a human does.
LOGIN_URL = "https://online.citi.com/US/nga/products-offers/merchantoffers"
SUCCESS_COOKIE = "tmx_sessionid"
# The offers API. Pulled IN the authenticated browser so it passes Citi's
# Akamai/TMX bot gate (a curl_cffi client gets 403 here even with valid cookies).
OFFERS_API = ("https://online.citi.com/gcgapi/prod/public/v1/"
              "digital/customers/creditCards/merchantOffers/retrieve")
# The actual offers UI page (same origin as the API) — the real browser navigates
# here and calls retrieve() itself, which we capture. This avoids a cross-origin
# fetch from the www.citi.com login page (which Citi rejects with 403).
OFFERS_PAGE = "https://online.citi.com/US/nga/products-offers/merchantoffers"
ENROLL_API = ("https://online.citi.com/gcgapi/prod/public/v1/"
              "digital/customers/creditCards/accounts/rewards/specialOffers/enrollMerchantOffer")
OFFERS_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "client_id": "4a51fb19-a1a7-4247-bc7e-18aa56dd1c40",
    "businessCode": "GCB", "countryCode": "US", "channelId": "CBOL",
    "appVersion": "CBOL-ANG-2026-09-00", "environmentID": "SuperMarioPROD",
    "Origin": "https://online.citi.com",
    "Referer": "https://online.citi.com/US/nga/products-offers/merchantoffers",
}
# Chrome binaries nodriver may use (first existing wins), incl. the local copy
# extracted under ~/.chrome (downloaded by setup for this environment).
CHROME_CANDIDATES = [
    "/opt/google/chrome/chrome",                      # Docker / .deb install
    "/opt/google/chrome/google-chrome",
    "/home/gans/.chrome/extracted/opt/google/chrome/chrome",
    "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium", "/usr/bin/chromium-browser",
]
# The Angular signon form uses DYNAMIC ids: #CdsSignon3_<N>_username / _password
# (N changes per render). Submit button text is "Sign On". We match by id-pattern,
# type, and label so it survives re-renders. (Confirmed live: #CdsSignon3_0_username,
# #CdsSignon3_0_password, button "Sign On".)
# NOTE: keep these TIGHT. A loose selector like input[name*='user' i] matched a
# NON-username field and the password got typed into the user field. Only match
# fields that are unambiguously the user-id / password inputs.
USER_SELECTORS = [
    "input[id*='username' i]", "input[id*='userid' i]", "input[id*='coboUserName' i]",
    "input[autocomplete='username']",
]
PASS_SELECTORS = [
    "input[id*='password' i]", "input[type='password']",
    "input[autocomplete='current-password']",
]
# Cookie-consent banner buttons to dismiss before the form (order matters: try
# "Continue" / "Accept" first; they vary).
CONSENT_BUTTON_TEXTS = ["Continue", "Accept", "Accept All", "Agree", "OK"]

# In-page JS helpers. The Citi sign-on is an Angular app; nodriver's
# find_element_by_text is unreliable here (raises TypeError), so we locate and
# act on elements with in-page JavaScript, which is proven to work.
JS_SET_VALUE = (
    "(function(){var el=document.querySelector(__SEL__);"
    "if(!el)return false;"
    "var d=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value');"
    "d.set.call(el, __VAL__);"
    "el.dispatchEvent(new Event('input',{bubbles:true}));"
    "el.dispatchEvent(new Event('change',{bubbles:true}));"
    "return true;})()"
)
JS_CLICK_TEXT = (
    "(function(){var bs=[].slice.call(document.querySelectorAll('button,a,[role=button]'));"
    "var b=bs.filter(function(x){return x.textContent.trim()===__T1__;})[0]"
    " ||bs.filter(function(x){return __RX__.test(x.textContent.trim());})[0];"
    "if(b){b.scrollIntoView({block:'center'});b.click();return b.textContent.trim();}return null;})()"
)

def _val(r):
    """nodriver's evaluate() returns a RemoteObject; unwrap to its .value.
    Handles both a RemoteObject wrapper and an already-plain value."""
    if r is None:
        return None
    if hasattr(r, "value"):
        return r.value
    return r


def _val_json(r):
    """Like _val but for JS that returns a JSON string (primitives serialize
    reliably; objects can come back as references with value=None)."""
    v = _val(r)
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:
            return v
    return v


async def dismiss_consent(page) -> None:
    """Click the cookie-consent banner if present (best effort, non-fatal)."""
    rx = "Continue|Accept All|Accept|Agree|OK"
    js = JS_CLICK_TEXT.replace("__T1__", """'Accept'""").replace("__RX__", f"/{rx}/i")
    try:
        res = _val(await page.evaluate(js, return_by_value=True))
        if res:
            log(f"    dismissed consent banner ('{res}')")
            await page.wait(1)
    except Exception:
        pass


def _js_type(selector: str, text: str) -> str:
    """In-page JS that types `text` into `selector` via per-keystroke events
    (keydown/keypress/input/keyup) — accepted by Angular ngModel, and immune to
    CDP node-id errors that can hit send_keys on dynamic forms."""
    return (
        "(function(){var el=document.querySelector(__SEL__);if(!el)return -1;"
        "el.focus();if(el.select)el.select();"
        "var setV=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value');"
        "for(var i=0;i<__TXT__.length;i++){"
        " var ch=__TXT__[i];"
        " el.dispatchEvent(new KeyboardEvent('keydown',{key:ch,bubbles:true}));"
        " el.dispatchEvent(new KeyboardEvent('keypress',{key:ch,bubbles:true}));"
        " setV.set.call(el,(el.value||'')+ch);"
        " el.dispatchEvent(new Event('input',{bubbles:true}));"
        " el.dispatchEvent(new KeyboardEvent('keyup',{key:ch,bubbles:true}));"
        "}"+"return (el.value||'').length;})()"
    ).replace("__SEL__", json.dumps(selector)).replace("__TXT__", json.dumps(text))


def _js_type_char(selector: str, ch: str) -> str:
    """In-page JS that appends ONE char to `selector` with full keystroke events
    (keydown/keypress/input/keyup) + native value setter — what Angular ngModel
    accepts. Returns the new value length, or -1 if the element is missing."""
    return (
        "(function(){var el=document.querySelector(__SEL__);if(!el)return -1;"
        "if(document.activeElement!==el)el.focus();"
        "var setV=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value');"
        "var ch=__CH__;"
        "el.dispatchEvent(new KeyboardEvent('keydown',{key:ch,bubbles:true}));"
        "el.dispatchEvent(new KeyboardEvent('keypress',{key:ch,bubbles:true}));"
        "setV.set.call(el,(el.value||'')+ch);"
        "el.dispatchEvent(new Event('input',{bubbles:true}));"
        "el.dispatchEvent(new KeyboardEvent('keyup',{key:ch,bubbles:true}));"
        "return (el.value||'').length;})()"
    ).replace("__SEL__", json.dumps(selector)).replace("__CH__", json.dumps(ch))


async def _fresh_el(page, selector: str, timeout: int = 8):
    """Re-resolve an element FRESH (the Angular SPA re-renders, so a previously
    obtained reference can go stale/null). Returns the element or None."""
    try:
        return await page.wait_for(selector, timeout=timeout)
    except Exception:
        return None


async def _read_value(page, selector: str):
    """Read a field's current value, tolerating a missing element (null)."""
    try:
        return _val(await page.evaluate(
            "(function(){var el=document.querySelector(" + json.dumps(selector) + ");"
            "return el ? (el.value||'') : null;})()", return_by_value=True))
    except Exception:
        return None


# Windows virtual key codes for printable characters (A-Z=65-90, 0-9=48-57, and
# punctuation per the US-QWERTY layout). Used by _cdp_type_text so keyDown events
# carry the correct code for a Carbon masked input to accept.
_VK = {}
for _i in range(26):
    _VK[chr(ord("a") + _i)] = 65 + _i      # a-z -> A-Z VK codes (65-90)
    _VK[chr(ord("A") + _i)] = 65 + _i
for _i in range(10):
    _VK[str(_i)] = 48 + _i                 # 0-9 -> 48-57
# Punctuation / symbols (US layout)
_VK.update({
    "-": 189, "=": 187, "[": 219, "]": 221, "\\": 220, ";": 186, "'": 192,
    ",": 188, ".": 190, "/": 191, "`": 192, " ": 32,
})


def _vk_code(ch: str) -> int:
    """Best-effort Windows virtual key code for a single character."""
    if ch in _VK:
        return _VK[ch]
    if ch.isalpha():
        return ord(ch.upper())
    if ch.isdigit():
        return ord(ch)
    # Fallback: uppercase code point (works for most letters/digits).
    return ord(ch.upper()) if ch.isalpha() else ord(ch)


async def _cdp_type_text(page, selector: str, text: str) -> bool:
    """Type `text` into `selector` using CDP Input.dispatchKeyEvent (isTrusted=true
    events). The username field has a 'nnn' honeypot that Citi's JS resets when it
    detects a non-trusted (JS-dispatched) value change; trusted CDP keystrokes
    bypass that check. Returns True if the value landed."""
    from nodriver import cdp
    import random
    LEFT = getattr(cdp.input_.MouseButton, "LEFT", None)
    try:
        # Get the field's center so we can click it with a trusted mouse event.
        r = _val(await page.evaluate(
            "(function(){var el=document.querySelector(" + json.dumps(selector) + ");"
            "if(!el)return null;var b=el.getBoundingClientRect();"
            "return JSON.stringify({x:b.left+b.width/2,y:b.top+b.height/2});})()",
            return_by_value=True))
        if not r:
            return False
        x, y = float(r["x"]), float(r["y"])
        # Trusted click to focus.
        await page.send(cdp.input_.dispatch_mouse_event(type_="mouseMoved", x=x, y=y))
        await asyncio.sleep(random.uniform(0.05, 0.15))
        await page.send(cdp.input_.dispatch_mouse_event(
            type_="mousePressed", x=x, y=y, button=LEFT, click_count=1))
        await page.send(cdp.input_.dispatch_mouse_event(
            type_="mouseReleased", x=x, y=y, button=LEFT, click_count=1))
        await asyncio.sleep(random.uniform(0.1, 0.25))
        # Clear via trusted key events (select-all + delete), then type.
        await page.send(cdp.input_.dispatch_key_event("keyDown", key="a",
            text="", unmodified_text="", windows_virtual_key_code=65, modifiers=2))
        await page.send(cdp.input_.dispatch_key_event("keyUp", key="a",
            windows_virtual_key_code=65, modifiers=2))
        await page.send(cdp.input_.dispatch_key_event("keyDown", key="Backspace",
            windows_virtual_key_code=8))
        await page.send(cdp.input_.dispatch_key_event("keyUp", key="Backspace",
            windows_virtual_key_code=8))
        await asyncio.sleep(0.2)
        for ch in text:
            # The field is a Carbon Design System MASKED Angular input
            # (cdsinputmask, formcontrolname). The mask processes KEYDOWN events
            # to manage the value; a bare 'char' event bypasses the mask and gets
            # cleared. So send keyDown + keyUp with the correct virtual key code
            # and the character in `text`, so the mask's handler accepts it.
            vkc = _vk_code(ch)
            await page.send(cdp.input_.dispatch_key_event("keyDown", key=ch,
                text=ch, unmodified_text=ch, windows_virtual_key_code=vkc))
            await page.send(cdp.input_.dispatch_key_event("char", text=ch))
            await page.send(cdp.input_.dispatch_key_event("keyUp", key=ch,
                windows_virtual_key_code=vkc))
            await asyncio.sleep(random.uniform(0.05, 0.15))
        await page.wait(0.4)
        return True
    except Exception as e:
        log(f"    (CDP trusted type failed: {type(e).__name__}: {e})")
        return False


async def _type_into(field_selector: str, text: str, page, expect: str | None = None) -> bool:
    """Focus a field and type `text` with human-timed keystrokes.

    Citi's sign-on form is an Angular SPA that re-renders, so element references
    go stale. We re-resolve the element fresh, focus + clear it via JS, then type
    char-by-char with real CDP keystrokes (nodriver send_keys) at ~40-140ms/char.
    Finally we VERIFY the field holds the expected value (not a decoy)."""
    import random
    sel = field_selector
    # NOTE: we do NOT rely on page.wait_for() here — it timed out on the user-id
    # field even though document.querySelector found it. All typing below goes
    # through in-page JS that resolves the element itself via querySelector.
    # Focus + clear the LIVE element via JS so we start from an empty field.
    # (insertText then writes the full value; we don't strip the Carbon mask
    # attributes — insertText works with them in place.)
    try:
        await page.evaluate(
            "(function(){var el=document.querySelector(" + json.dumps(sel) + ");"
            "if(!el)return false;"
            "el.focus();"
            "var s=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;"
            "s.call(el,''); el.dispatchEvent(new Event('input',{bubbles:true}));"
            "el.dispatchEvent(new Event('change',{bubbles:true})); return true;})()",
            return_by_value=True)
        await page.wait(0.2)
    except Exception as e:
        log(f"    (focus/clear failed: {e})")
    # PRIMARY: CDP Input.insertText — a full trusted string insert (like a paste).
    # PROVEN to work on Citi's Carbon-masked username field (cdsinputmask), which
    # rejects per-keystroke events (CDP keyDown, JS events). insertText bypasses
    # the mask's keydown handler and the value lands cleanly.
    from nodriver import cdp
    ok = False
    try:
        c = await _field_center(page, sel)
        if c:
            await _trusted_click(page, c[0], c[1])
        await page.wait(0.3)
        await page.send(cdp.input_.insert_text(text=text))
        await page.wait(0.4)
        v = await _read_value(page, sel)
        ok = (v == expect) if expect is not None else bool(v)
        if ok:
            info(f"    {sel!r}: insertText landed")
    except Exception as e:
        info(f"    {sel!r}: insertText failed ({type(e).__name__}: {e})")
    # FALLBACK: in-page JS per-keystroke (works for the password field, which has
    # no mask; the username needs insertText).
    if not ok:
        try:
            for ch in text:
                r = _val(await page.evaluate(_js_type_char(sel, ch), return_by_value=True))
                if r in (None, -1):
                    break
                await asyncio.sleep(random.uniform(0.04, 0.14))
            await page.wait(0.4)
            v = await _read_value(page, sel)
            ok = (v == expect) if expect is not None else bool(v)
        except Exception as e:
            info(f"    {sel!r}: JS typing failed ({type(e).__name__}: {e})")
    v = await _read_value(page, sel)
    landed = (v == expect) if expect is not None else bool(v)
    # Never print the actual secret (especially the password) to the logs —
    # show only length + a match flag.
    info(f"    {sel!r}: value={'(len %d)' % len(v) if v else 'empty'} "
         f"expected={'(len %d)' % len(expect) if expect else 'any'} "
         f"landed={landed}")
    return landed


async def _fill_first_match(page, selectors, text, label) -> bool:
    """Try each selector until one lands text. Returns True on success."""
    for sel in selectors:
        present = False
        try:
            present = await page.evaluate(
                "!!document.querySelector(" + json.dumps(sel) + ")", return_by_value=True)
        except Exception:
            pass
        if not present:
            continue
        ok = await _type_into(sel, text, page, expect=text)
        info(f"    {label}: selector {sel!r} present, landed={ok}")
        if ok:
            return True
    log(f"    {label}: no selector landed text (tried {len(selectors)})")
    return False


async def _wait_form_settled(page, timeout_s: int = 25) -> bool:
    """Wait until the login form is stable: both the username and password fields
    are present in the DOM, and the page is NOT mid-navigation. Citi's SSO does
    several client-side re-navigations right after landing on /login; any CDP
    command issued during one of those throws 'Inspected target navigated or
    closed' (ProtocolException). We treat that as 'not settled yet' and retry.
    Returns True once the form is stably present."""
    import time
    deadline = time.time() + timeout_s
    stable_count = 0
    while time.time() < deadline:
        try:
            r = _val(await page.evaluate(
                "(function(){"
                " var u=document.querySelector(" + json.dumps("input[id*='username' i]") + ")"
                "  || document.querySelector('input[autocomplete=username]')"
                "  || document.querySelector('input[type=text]');"
                " var p=document.querySelector('input[type=password]');"
                " return JSON.stringify({u:!!u, p:!!p, ready:document.readyState});" +
                " })()", return_by_value=True)) or {}
            if r.get("u") and r.get("p") and r.get("ready") == "complete":
                stable_count += 1
                # Require it to be stable for 2 consecutive checks (~2s) to avoid
                # catching a fleeting render between navigations.
                if stable_count >= 2:
                    return True
            else:
                stable_count = 0
        except Exception:
            # ProtocolException / navigation in progress -> not settled.
            stable_count = 0
        await page.wait(1)
    return False


async def _field_center(page, selector: str):
    """Return (x, y) center of the element matching `selector`, or None."""
    raw = await page.evaluate(
        "(function(){var el=document.querySelector(" + json.dumps(selector) + ");"
        "if(!el)return null;var b=el.getBoundingClientRect();"
        "return JSON.stringify({x:b.left+b.width/2,y:b.top+b.height/2});})()",
        return_by_value=True)
    # raw is the JSON string (or None if the element wasn't found).
    if raw in (None, "", "null"):
        return None
    try:
        r = json.loads(raw) if isinstance(raw, str) else raw
        return (float(r["x"]), float(r["y"]))
    except Exception:
        return None


async def _trusted_click(page, x, y):
    """A trusted CDP mouse click at (x, y)."""
    from nodriver import cdp
    LEFT = getattr(cdp.input_.MouseButton, "LEFT", None)
    await page.send(cdp.input_.dispatch_mouse_event(type_="mouseMoved", x=x, y=y))
    await page.wait(0.15)
    await page.send(cdp.input_.dispatch_mouse_event(
        type_="mousePressed", x=x, y=y, button=LEFT, click_count=1))
    await page.send(cdp.input_.dispatch_mouse_event(
        type_="mouseReleased", x=x, y=y, button=LEFT, click_count=1))


async def _autofill_login(page, timeout_s: int = 20) -> bool:
    """Trigger Chrome's native password-manager autofill and submit. Chrome fills
    BOTH fields with trusted input Citi's anti-bot accepts (unlike programmatic
    typing into the Carbon masked username field). Requires the Citi password to
    already be saved in this Chrome profile (origin https://www.citi.com/login).

    Strategy: click the USERNAME field, then click the PASSWORD field. Chrome's
    0-click autofill is keyed off the password field focus + a matching saved
    credential; focusing it populates both. Then wait for both to fill and
    submit. Returns True if autofilled + submitted."""
    import time
    USER = "input[id*='username' i]"
    PASS = "input[type=password]"
    # Help Chrome's autofill match: Citi's fields have empty autocomplete attrs,
    # which makes 0-click autofill unreliable. Set the standard values so Chrome
    # unambiguously pairs the saved (username, password) with these fields.
    try:
        await page.evaluate(
            "(function(){var u=document.querySelector(" + json.dumps(USER) + ");"
            " var p=document.querySelector(" + json.dumps(PASS) + ");"
            " if(u)u.setAttribute('autocomplete','username');"
            " if(p)p.setAttribute('autocomplete','current-password');"
            " var f=document.querySelector('form');"
            " if(f){f.setAttribute('autocomplete','on');}" +
            " return true; })()", return_by_value=True)

    except Exception as e:
        log(f"    [autofill] could not set autocomplete hints: {e}")
    await page.wait(0.4)
    # 1) Focus the username field (trusted click).
    cu = await _field_center(page, USER)
    if not cu:
        info("    [autofill] no username field found")
        return False
    info(f"    [autofill] focusing username field…")
    try:
        await _trusted_click(page, cu[0], cu[1])
    except Exception as e:
        log(f"    [autofill] username focus failed: {e}")
    await page.wait(0.6)
    # 2) Focus the password field (this is what triggers Chrome's autofill).
    cp = await _field_center(page, PASS)
    if cp:
        info(f"    [autofill] focusing password field to trigger autofill…")
        try:
            await _trusted_click(page, cp[0], cp[1])
        except Exception as e:
            log(f"    [autofill] password focus failed: {e}")
    # 2b) Also try a JS focus + a real CDP keypress in the password field. Some
    #     Chrome builds only trigger the PM when a genuine key event lands in the
    #     password field, not just on focus/click.
    try:
        await page.evaluate(
            "(function(){var p=document.querySelector(" + json.dumps(PASS) + ");"
            "if(p){p.focus();return true;}return false;})()", return_by_value=True)
        from nodriver import cdp
        await page.wait(0.3)
        await page.send(cdp.input_.dispatch_key_event("keyDown", key="a",
            text="a", unmodified_text="a", windows_virtual_key_code=65))
        await page.send(cdp.input_.dispatch_key_event("keyUp", key="a",
            windows_virtual_key_code=65))
        # Remove the stray 'a' we just typed so the field is clean if autofill
        # doesn't take over immediately.
        await page.evaluate(
            "(function(){var p=document.querySelector(" + json.dumps(PASS) + ");"
            "if(p){var s=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;"
            " s.call(p,'');p.dispatchEvent(new Event('input',{bubbles:true}));}return true;})()",
            return_by_value=True)
    except Exception as e:
        log(f"    [autofill] keypress trigger failed: {e}")
    # 3) Wait for both fields to populate.
    deadline = time.time() + timeout_s
    filled = False
    while time.time() < deadline:
        st = _val_json(await page.evaluate(
            "(function(){var u=document.querySelector(" + json.dumps(USER) + ");"
            " var p=document.querySelector(" + json.dumps(PASS) + ");"
            " return JSON.stringify({u:u?(u.value||''):'', p:p?(p.value||''):'(none)'});})()",
            return_by_value=True)) or {}
        u, p = st.get("u", ""), st.get("p", "")
        if u and p and p != "(none)":
            info(f"    [autofill] fields populated (user={u[:3]}…, pass={'yes' if p else 'no'})")
            filled = True
            break
        await page.wait(1)
    if not filled:
        # 4) Fallback: click username, Tab to password (a real keyboard nav that
        #    also triggers Chrome's autofill on the password field).
        info("    [autofill] still empty — trying Tab navigation from username…")
        cu2 = await _field_center(page, USER)
        if cu2:
            try:
                await _trusted_click(page, cu2[0], cu2[1])
                from nodriver import cdp
                await page.send(cdp.input_.dispatch_key_event("keyDown", key="Tab",
                    windows_virtual_key_code=9))
                await page.send(cdp.input_.dispatch_key_event("keyUp", key="Tab",
                    windows_virtual_key_code=9))
            except Exception as e:
                log(f"    [autofill] Tab fallback failed: {e}")
        await page.wait(3)
        st = _val_json(await page.evaluate(
            "(function(){var u=document.querySelector(" + json.dumps(USER) + ");"
            " var p=document.querySelector(" + json.dumps(PASS) + ");"
            " return JSON.stringify({u:u?(u.value||''):'', p:p?(p.value||''):'(none)'});})()",
            return_by_value=True)) or {}
        if st.get("u") and st.get("p") and st.get("p") != "(none)":
            info(f"    [autofill] fields populated via Tab (user={st.get('u','')[:3]}…)")
            filled = True
    if not filled:
        info("    [autofill] Chrome did NOT autofill.")
        info("    → confirm the password is saved for https://www.citi.com/login in")
        info("      this profile, and that Chrome's 'Autofill & save passwords'")
        info("      setting is ON. Then re-run with --autofill.")
        return False
    # Submit.
    submitted = await _click_submit(page)
    if submitted:
        info("    [autofill] submitted (clicked Sign On)")
    return True


async def _probe_username_typing(page) -> dict:
    """Try several typing methods on the username field and report which lands.
    Used to determine how to fill the Carbon-masked username field. Returns a dict
    of method -> final value."""
    from nodriver import cdp
    import random
    USER = "input[id*='username' i]"
    results = {}
    test = "TEST123"

    async def _read():
        return _val(await page.evaluate(
            "(function(){var el=document.querySelector(" + json.dumps(USER) + ");"
            "return el?(el.value||''):'(gone)';})()", return_by_value=True))

    async def _reset():
        await page.evaluate(
            "(function(){var el=document.querySelector(" + json.dumps(USER) + ");"
            "if(!el)return false;el.focus();"
            "var s=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;"
            "s.call(el,'');el.dispatchEvent(new Event('input',{bubbles:true}));return true;})()",
            return_by_value=True)
        await page.wait(0.3)

    async def _url():
        try:
            return (_val(await page.evaluate("location.href", return_by_value=True)) or "").strip()
        except Exception:
            return "(nav?)"

    url0 = await _url()
    results["url_before"] = url0

    # Method 1: Input.insertText (full trusted string, like a paste).
    try:
        await _reset()
        c = await _field_center(page, USER)
        if c:
            await _trusted_click(page, c[0], c[1])
        await page.wait(0.3)
        await page.send(cdp.input_.insert_text(text=test))
        await page.wait(0.5)
        v = await _read()
        results["insertText"] = v
        results["insertText_url_after"] = await _url()
    except Exception as e:
        results["insertText"] = f"ERR {e}"

    # Method 2: CDP keyDown with text + VKC (proper keystrokes).
    try:
        await _reset()
        c = await _field_center(page, USER)
        if c:
            await _trusted_click(page, c[0], c[1])
        await page.wait(0.3)
        for ch in test:
            vkc = _vk_code(ch)
            await page.send(cdp.input_.dispatch_key_event("keyDown", key=ch,
                text=ch, unmodified_text=ch, windows_virtual_key_code=vkc))
            await page.send(cdp.input_.dispatch_key_event("char", text=ch))
            await page.send(cdp.input_.dispatch_key_event("keyUp", key=ch,
                windows_virtual_key_code=vkc))
            await asyncio.sleep(random.uniform(0.05, 0.12))
        await page.wait(0.5)
        v = await _read()
        results["cdp_keydown"] = v
        results["cdp_keydown_url_after"] = await _url()
    except Exception as e:
        results["cdp_keydown"] = f"ERR {e}"

    # Method 3: JS per-keystroke (works for the password field) — test if it works
    # for the username when the page is stable.
    try:
        await _reset()
        c = await _field_center(page, USER)
        if c:
            await _trusted_click(page, c[0], c[1])
        await page.wait(0.3)
        for ch in test:
            r = _val(await page.evaluate(_js_type_char(USER, ch), return_by_value=True))
            if r in (None, -1):
                break
            await asyncio.sleep(0.06)
        await page.wait(0.5)
        v = await _read()
        results["js_typing"] = v
        results["js_typing_url_after"] = await _url()
    except Exception as e:
        results["js_typing"] = f"ERR {e}"

    results["url_final"] = await _url()
    results["reloaded"] = (await _url()) != url0
    return results


async def _click_submit(page) -> bool:
    """Click the 'Sign On' button (full trusted MouseEvent sequence) and verify we
    left the login page. A bare JS .click() does NOT trigger Citi's Angular
    submit, so we dispatch pointerdown/mousedown/mouseup/click with proper
    bubbles/composed. Falls back to form.requestSubmit(), then Enter."""
    submit_js = (
        "(function(){ var bs=[].slice.call(document.querySelectorAll('button,a,[type=submit],[role=button],input[type=submit]'));"
        " var b=bs.find(function(x){return /sign on|sign in|log in/i.test((x.textContent||x.value||'').trim());});"
        " if(!b){ var f=document.querySelector('form'); if(f&&f.requestSubmit){f.requestSubmit(); return {clicked:'form.requestSubmit'};}; return {clicked:null}; }"
        " var opts={bubbles:true, cancelable:true, composed:true, view:window, button:0};"
        " b.dispatchEvent(new PointerEvent('pointerdown',opts));"
        " b.dispatchEvent(new MouseEvent('mousedown',opts));"
        " b.dispatchEvent(new PointerEvent('pointerup',opts));"
        " b.dispatchEvent(new MouseEvent('mouseup',opts));"
        " b.dispatchEvent(new MouseEvent('click',opts));"
        " return {clicked:b.textContent.trim()}; })()"
    )
    try:
        res = _val(await page.evaluate(submit_js, return_by_value=True)) or {}
        clicked = res.get("clicked") if isinstance(res, dict) else None
        if not clicked:
            info("    'Sign On' button not found — click it manually.")
            return False
        info(f"    submitted (clicked {clicked!r}), waiting for navigation…")
        for _ in range(6):
            await page.wait(1)
            if "/login" not in (page.url or "").lower():
                log("    (navigated off login page)")
                break
        else:
            info("    (still on login page after click — pressing Enter to submit)")
            try:
                pw = await page.wait_for(PASS_SELECTORS[0], timeout=3)
                await pw.send_keys("\n")
                await page.wait(2)
            except Exception as e:
                log(f"    (Enter fallback failed: {e})")
        try:
            await page.wait(1.5)
            u = (_val(await page.evaluate("location.href", return_by_value=True)) or "").strip()
            info(f"    after submit, URL = {u}")
        except Exception:
            pass
        return True
    except Exception as e:
        info(f"    submit click failed ({type(e).__name__}: {e})")
        return False


async def fill_and_submit(page, user: str, password: str) -> bool:
    """Fill the dynamic sign-on fields (real keyboard) and click Sign On (JS)."""
    try:
        # One-time diagnostic: dump every input field (id, type, current value,
        # whether it's in an iframe) so we can see exactly what we're filling.
        try:
            # Dump EVERY input field (id, type, autocomplete, visibility, value)
            # so we can see the real form structure. Always printed.
            dump = _val_json(await page.evaluate(
                "(function(){"
                " var out={url:location.href, iframes:document.querySelectorAll('iframe').length, inputs:[]};"
                " [].slice.call(document.querySelectorAll('input')).slice(0,40).forEach(function(i,idx){"
                "  var vis=(i.offsetParent!==null && i.type!=='hidden');"
                "  out.inputs.push(idx+': id=['+i.id+'] type=['+i.type+'] auto=['+(i.autocomplete||'')+']'"
                "   +(vis?'':' [HIDDEN]')+' val=['+(i.value||'').slice(0,20)+']');"
                " });"
                " return JSON.stringify(out); })()", return_by_value=True)) or {}
            info(f"    [inputs] url={dump.get('url')} iframes={dump.get('iframes')}")
            for line in (dump.get("inputs") or []):
                # Mask the value of any password field so secrets never hit the log.
                if "type=[password]" in line and "val=[" in line:
                    head, _, _valpart = line.partition("val=[")
                    line = head + "val=[••••••••]"
                info(f"      {line}")
            # Probe: retry a few times reporting which selectors match + visibility,
            # then type ONE char into the first match and read it back.
            probe_sels = ["input[id*='username' i]", "input[id*='userid' i]",
                          "input[autocomplete='username']", "input[type='text']"]
            probe_arr = json.dumps(probe_sels)
            for attempt in range(4):
                info(f"    [probe try{attempt+1}]")
                match = _val_json(await page.evaluate(
                    "(function(){var out={};"
                    " " + probe_arr + ".forEach(function(s){"
                    "  var el;try{el=document.querySelector(s);}catch(e){return;}"
                    "  if(el)out[s]={id:el.id,type:el.type,visible:el.offsetParent!==null,val:(el.value||'')};});"
                    " return JSON.stringify(out); })()", return_by_value=True)) or {}
                info(f"      matches: {match}")
                if match:
                    sel = list(match.keys())[0]
                    # Probe BOTH typing methods and read value + placeholder +
                    # outerHTML immediately after, to see what the field does.
                    # (1) JS type one char
                    r1 = _val(await page.evaluate(_js_type_char(sel, "a"), return_by_value=True))
                    info(f"      JS-typed 'a' -> jsret={r1}")
                    # (2) CDP trusted char for 'b'
                    try:
                        await _cdp_type_text(page, sel, "b")
                        info(f"      CDP-typed 'b' -> done")
                    except Exception as e:
                        info(f"      CDP-typed 'b' -> failed: {e}")
                    st = _val(await page.evaluate(
                        "(function(){var el=document.querySelector(" + json.dumps(sel) + ");"
                        "if(!el)return JSON.stringify({gone:true});"
                        "return JSON.stringify({value:el.value,placeholder:el.placeholder,"
                        "  readonly:el.readOnly,disabled:el.disabled,"
                        "  html:el.outerHTML.slice(0,160)});})()", return_by_value=True))
                    info(f"      state: {st}")
                    break
                await page.wait(1)
        except Exception as e:
            info(f"    [inputs] DUMP FAILED: {type(e).__name__}: {e}")
        # Wait for ANY username-like field to render.
        found_sel = None
        for _ in range(40):
            for sel in USER_SELECTORS:
                try:
                    if await page.evaluate(
                            "!!document.querySelector(" + json.dumps(sel) + ")",
                            return_by_value=True):
                        found_sel = sel
                        break
                except Exception:
                    pass
            if found_sel:
                break
            await page.wait(0.5)
        if not found_sel:
            log("    (no username field found after 20s — is the form rendered?)")
            # Dump what inputs exist so we can fix the selectors.
            try:
                inputs = _val(await page.evaluate(
                    "[].slice.call(document.querySelectorAll('input')).map(function(i){"
                    "return i.id+'|'+i.name+'|'+i.type+'|'+(i.autocomplete||'');}).join('\\n')",
                    return_by_value=True)) or "(none)"
                log(f"    (inputs on page:\n{inputs})")
            except Exception:
                pass
            return False
        log(f"    (username field matched: {found_sel!r})")
        ok_u = await _fill_first_match(page, USER_SELECTORS, user, "user")
        await page.wait(0.3)
        ok_p = await _fill_first_match(page, PASS_SELECTORS, password, "pass")
        if not (ok_u and ok_p):
            log(f"    field fill incomplete (user={ok_u}, pass={ok_p}) — finish manually.")
            return False
        await page.wait(0.4)
        # Submit via the shared helper (trusted MouseEvent sequence + Enter fallback).
        return await _click_submit(page)
    except Exception as e:
        info(f"    auto-fill failed ({type(e).__name__}: {e}).")
        return False


async def _handle_mfa(page, code: str | None, mfa_wait: int):
    """Best-effort completion of Citi's second-factor step.

    1. Click "Remember/trust this device" if offered (makes future runs skip MFA).
    2. If a one-time code was supplied (or a code field is present), enter it.
    3. Click Continue / Verify.
    If it's a push/app approval we can't do it here, so we just report it.
    """
    # 1) Remember-this-device (idempotent; harmless if absent).
    remember = (
        "(function(){ var b=[].slice.call(document.querySelectorAll('button,[role=button],a,label,span'))"
        ".find(function(x){return /remember this device|trust this device|keep me signed in|"
        "remember me|don.t ask again/i.test(x.textContent.trim()) && x.offsetParent!==null;});"
        " if(b){ b.click(); return b.textContent.trim(); } return null; })()"
    )
    try:
        r = _val(await page.evaluate(remember, return_by_value=True))
        if r:
            log(f"[mfa] clicked remember-device: {r!r}")
            await page.wait(1)
    except Exception as e:
        log(f"[mfa] remember-device check failed: {e}")

    # 2) Enter a one-time code if we have one and there's a code field.
    if code:
        code_js = (
            "(function(){ var el=document.querySelector("
            "'input[inputmode=numeric],input[type=tel],input[maxlength=6],input[maxlength=8],"
            "input[id*=code i],input[placeholder*=code i]');"
            " if(!el) return -1; el.focus();"
            " var setV=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;"
            " setV.call(el, " + json.dumps(code) + "); "
            " el.dispatchEvent(new Event('input',{bubbles:true}));"
            " el.dispatchEvent(new Event('change',{bubbles:true})); return el.value.length; })()"
        )
        try:
            n = _val(await page.evaluate(code_js, return_by_value=True))
            log(f"[mfa] entered code ({n} chars)")
            await page.wait(0.5)
        except Exception as e:
            log(f"[mfa] code entry failed: {e}")

    # 3) Click Continue / Verify.
    cont = JS_CLICK_TEXT.replace("__T1__", "'Continue'").replace("__RX__", "/continue|verify|submit|confirm|next/i")
    try:
        c = _val(await page.evaluate(cont, return_by_value=True))
        if c:
            log(f"[mfa] clicked: {c!r}")
            await page.wait(2)
    except Exception as e:
        log(f"[mfa] continue click failed: {e}")

    if mfa_wait > 0:
        log(f"[mfa] waiting up to {mfa_wait}s for you to finish MFA in the browser "
              "(push/app/SMS)…")


async def _check_login_error(page):
    """After a submit, detect a failure reason: invalid credentials, CAPTCHA, or a
    rate-limit. Prints it so we know why the SSO didn't complete."""
    js = (
        "(function(){ try {"
        " var t=(document.body?document.body.innerText:'');"
        " var cap=/captcha|recaptcha|verify you are human|i am not a robot|"
        "complete the puzzle/i.test(t);"
        " var bad=/invalid (user id|password|credentials)|incorrect (user|password)|"
        "incorrect username|username or password is incorrect|unsuccessful sign|"
        "account is locked|too many attempts|please try again later/i.test(t);"
        " var errEl=document.querySelector('[role=alert],.error,.alert,.cbol-error," +
        " [class*=error i],[class*=invalid i]');"
        " var err=errEl?errEl.textContent.trim().slice(0,160):'';"
        " return JSON.stringify({url:location.href, captcha:cap, bad:bad, err:err});"
        " } catch(e){ return JSON.stringify({err:String(e)}); } })()"
    )
    try:
        d = _val_json(await page.evaluate(js, return_by_value=True)) or {}
        if d.get("captcha"):
            info("[login] CAPTCHA detected — a human must solve it (use --manual).")
        if d.get("bad") or d.get("err"):
            info(f"[login] possible login failure: err={d.get('err')!r} url={d.get('url')}")
            info("[login]   ^ if 'invalid/incorrect', the credentials were rejected.")
    except Exception as e:
        log(f"[login] error-check failed: {e}")


async def _detect_mfa(page, tries: int = 6) -> dict | None:
    """Detect a Citi second-factor / "Verify your identity" screen and report
    what verification methods are offered. Retries a few times because the
    screen appears a few seconds after submit, *after* a redirect (evaluating
    mid-redirect throws). Returns the parsed dict of the last successful read.
    """
    # The whole body is wrapped in try/catch INSIDE the page so a mid-redirect
    # DOM never throws back to us (which surfaced as ExceptionDetails).
    js = (
        "(function(){ try {"
        "var t=(document.body?document.body.innerText:'');"
        "var m=/verify your identity|one[- ]time|verification code|enter the code|"
        "push notification|approve the request|text me|call me|security code|"
        "remember this device|keep me signed in|trust this device/i.test(t);"
        "var btns=[]; try{"
        " btns=[].slice.call(document.querySelectorAll('button,[role=button],a'))"
        ".map(function(b){return b.textContent.trim().slice(0,40);})"
        ".filter(function(x){return x.length>1;}).slice(0,20); }catch(e){}"
        "var h=[]; try{"
        " h=[].slice.call(document.querySelectorAll('h1,h2,h3'))"
        ".map(function(e){return e.textContent.trim().slice(0,80)}); }catch(e){}"
        "return JSON.stringify({mfa:m, url:location.href, headings:h, buttons:btns, "
        "snippet:(t||'').slice(0,400)});"
        " } catch(e){ return JSON.stringify({err:String(e), url:location.href}); } })()"
    )
    last = None
    for i in range(tries):
        try:
            d = _val_json(await page.evaluate(js, return_by_value=True))
            if isinstance(d, dict) and d:
                last = d
                url = (d.get("url") or "").lower()
                log(f"[mfa] try{i+1} url={d.get('url')} mfa_marker={'YES' if d.get('mfa') else 'no'} "
                      f"headings={d.get('headings')}")
                log(f"[mfa] buttons={d.get('buttons')}")
                if d.get("snippet"):
                    log(f"[mfa] snippet: {(d.get('snippet') or '').strip()[:250]!r}")
                # Stop once we're clearly past login (on the offers page) or on a
                # stable MFA screen.
                if "merchantoffers" in url and "/login" not in url:
                    return d
                if d.get("mfa"):
                    return d
        except Exception as e:
            log(f"[mfa] try{i+1} eval error: {e}")
        await page.wait(2)
    if last is not None and last.get("mfa"):
        log("    >> SECOND-FACTOR REQUIRED — see the handlers below.")
    return last


async def wait_for_login(browser, page, timeout_s: int) -> bool:
    """Wait until a FULL login is detected or timeout.

    Reliable signal: we have reached the OFFERS page (the login's nextRoute).
    Merely having a session cookie is NOT enough — Citi sets citi_authorization
    on the *login* page too, which caused false positives (we'd "log in" while
    still sitting on an empty sign-on form). So we require the URL to actually
    reach the merchantoffers page (or at least leave /login with an offer in it).
    """
    deadline = asyncio.get_event_loop().time() + timeout_s
    warned = False
    last_url = ""
    while asyncio.get_event_loop().time() < deadline:
        # Get a FRESH url from the page (page.url can be stale in some nodriver
        # versions, which made this loop miss the redirect and run to timeout).
        url = ""
        try:
            url = (_val(await page.evaluate("location.href", return_by_value=True)) or "").lower()
        except Exception:
            pass
        if not url:
            try:
                url = (page.url or "").lower()
            except Exception:
                pass
        # Success (1): we're on the offers page (login's nextRoute target).
        if "merchantoffers" in url and "/login" not in url:
            return True
        # Success (2): we've LEFT the login page AND hold a real session cookie.
        # A successful login lands on the dashboard homepage ("Good Evening,
        # <name>"), NOT directly on merchantoffers. The main flow then navigates
        # to the offers page. So 'left /login + citi_authorization present' is a
        # valid success signal.
        on_login_page = "/login" in url or "signon" in url or "loginscreenid" in url
        if not on_login_page and url and "citi.com" in url:
            try:
                names = {getattr(c, "name", "") for c in await browser.cookies.get_all()}
            except Exception:
                names = set()
            if "citi_authorization" in names:
                log(f"    (logged in — on {url[:70]}, has citi_authorization)")
                return True
        if on_login_page and url != last_url and not warned:
            warned = True
            log(f"    (still on sign-on: {url[:80]})")
        last_url = url
        await browser.sleep(1.5)
    return False


async def export_cookies(browser) -> list:
    """Return all cookies as (name, value, domain) tuples."""
    raw = await browser.cookies.get_all()
    return [(getattr(c, "name", ""), getattr(c, "value", ""),
             getattr(c, "domain", "")) for c in raw]


async def _browser_post(page, url: str, body: dict, match: str, wait_s: float = 4.0):
    """POST to a Citi API URL *inside* the authenticated browser and return
    (http_status, parsed_json_or_None).


    A cross-origin fetch() to online.citi.com is blocked by CORS, so we fire the
    request from the page's JS context (real browser state => passes Citi's
    Akamai/TMX bot gate) and capture the response via the CDP Network domain.
    `match` is a URL substring used to identify the right response."""
    from nodriver import cdp
    try:
        from nodriver.core.network import ResponseReceived
    except Exception:
        from nodriver.cdp.network import ResponseReceived

    captured: dict = {}

    def on_response(e):
        resp = e.response
        rurl = resp.get("url", "") if isinstance(resp, dict) else getattr(resp, "url", "")
        if match in rurl:
            captured["request_id"] = e.request_id
            captured["status"] = resp.get("status") if isinstance(resp, dict) else getattr(resp, "status", None)

    status = None
    try:
        await page.send(cdp.network.enable())
        page.add_handler(ResponseReceived, on_response)
        body_js = json.dumps(json.dumps(body or {}))  # JSON string of the JSON body
        js = ("(async()=>{ try { const r=await fetch(" + json.dumps(url) + ","
              "{method:'POST', headers:" + json.dumps(OFFERS_HEADERS) + ", body:" + body_js +
              ", credentials:'include'}); return r.status; } catch(e){ return 0; } })()")
        await page.evaluate(js, await_promise=True, return_by_value=True)
        await page.wait(wait_s)  # let the network event fire
    except Exception as e:
        log(f"    request error: {type(e).__name__} {e}")
        return None, None

    status = captured.get("status")
    rid = captured.get("request_id")
    if not rid:
        log(f"    (no response captured; status={status})")
        return status, None
    try:
        body_str, is_base64 = await page.send(cdp.network.get_response_body(rid))
        if is_base64:
            import base64
            body_str = base64.b64decode(body_str).decode("utf-8", "replace")
        return status, json.loads(body_str)
    except Exception as e:
        log(f"    (status={status}; could not read body: {e})")
        return status, None


async def fetch_offers_in_browser(browser, page) -> dict | None:
    """Pull the merchant-offers JSON from inside the authenticated browser."""
    status, data = await _browser_post(page, OFFERS_API, {}, "merchantOffers/retrieve", wait_s=5.0)
    log(f"    offers API -> HTTP {status}")
    return data


async def enroll_offers_in_browser(page, offers_data: dict, account_id: str,
                                   dry_run: bool, delay: float = 1.0) -> int:
    """Enroll (activate) all AVAILABLE offers, in the browser. Returns 0 on full
    success, 1 if any enrollment failed. Skips everything and just prints the
    list when dry_run is True."""
    # flatten offers + de-dupe by offerId (same logic as the standalone script)
    seen, unique = set(), []
    for cat in offers_data.get("merchantOffers") or []:
        for o in cat.get("offers") or []:
            oid = o.get("offerId")
            if oid and oid not in seen:
                seen.add(oid)
                unique.append({**o, "category": cat.get("displayOffersCategory")})
    available = [o for o in unique if o.get("offerStatus") == "AVAILABLE"]
    enrolled = [o for o in unique if o.get("offerStatus") == "ENROLLED"]

    info(f"\n{len(unique)} total  ({len(available)} available, {len(enrolled)} enrolled)")
    for o in unique:
        icon = "\U0001F7E2" if o.get("offerStatus") == "AVAILABLE" else "\U0001F535"
        log(f"  {icon} [{o.get('offerStatus','?'):>9}] "
              f"{o.get('merchantName','?')} — {o.get('offerTitle','?')}")

    if dry_run:
        info(f"\n[DRY RUN] would enroll {len(available)} offer(s). "
             "Re-run without --dry-run to activate.")
        return 0

    if not account_id:
        info("No accountId resolved — cannot enroll.")
        return 1

    ok = fail = 0
    for o in available:
        oid, name = o.get("offerId"), o.get("merchantName") or o.get("offerTitle")
        body = {"offerId": oid, "accountId": account_id, "oneClickEnroll": "true"}
        status, resp = await _browser_post(page, ENROLL_API, body, "enrollMerchantOffer", wait_s=6.0)
        success = status in (200, 201, 204) and (resp is None or (isinstance(resp, dict) and "error" not in resp))
        if success:
            info(f"  \u2705 {name}"); ok += 1
        else:
            info(f"  \u274c {name}: HTTP {status} {resp}"); fail += 1
        await asyncio.sleep(delay)
    info(f"\nDone  enrolled: {ok}  failed: {fail}  total: {len(available)}")
    return 0 if fail == 0 else 1


# --- UI-button activation (bypasses the TMX-gated API entirely) ----------------
# The offers page renders fine in the container, so we can click each offer's own
# Activate/Enroll button — the page's own click passes the bot gate. Used as a
# fallback when the retrieve/enroll API returns 403.
JS_UI_ACTIVATE = (
    "(function(){"
    "var btns=[].slice.call(document.querySelectorAll('button,a,[role=button]'));"
    "var act=btns.filter(function(b){var t=b.textContent.trim().toLowerCase();"
    "  return /activate|enroll|redeem|add to card|get offer/i.test(t) && !b.disabled;});"
    "if(!act.length)return {found:0};"
    "var b=act[0]; b.scrollIntoView({block:'center'}); b.click();"
    "return {found:act.length, clicked:b.textContent.trim()};})()"
)


async def _dump_page_diag(page, tag="diag"):
    """Dump the page's buttons/links + text + screenshot + HTML to /config/out so
    the offer-card markup can be matched. Returns the button count."""
    outdir = Path("/config/out")
    try:
        outdir.mkdir(parents=True, exist_ok=True)
    except Exception:
        outdir = Path("/tmp")
    js_diag = (
        "(function(){"
        "var els=[].slice.call(document.querySelectorAll('button,a,[role=button],input[type=submit]'));"
        "var info=els.slice(0,200).map(function(e){return (e.tagName+':'+e.textContent.trim().slice(0,60));});"
        "var h2=[].slice.call(document.querySelectorAll('h1,h2,h3,h4')).map(function(e){return e.textContent.trim().slice(0,80);});"
        "return JSON.stringify({url:location.href, title:document.title, "
        "bodyLen:document.body?document.body.innerText.length:0, buttons:info, headings:h2});})()"
    )
    try:
        d = _val_json(await page.evaluate(js_diag, return_by_value=True)) or {}
        (outdir / f"{tag}_info.json").write_text(json.dumps(d, indent=2))
        log(f"  diag url={d.get('url')} title={d.get('title')!r} bodyLen={d.get('bodyLen')}")
        log(f"  diag headings={d.get('headings')}")
        log(f"  diag buttons (first 40)={d.get('buttons', [])[:40]}")
    except Exception as e:
        log(f"  (diag eval failed: {e})")
    try:
        # Screenshot (use the high-level API that we know works in this nodriver).
        shot_path = str(outdir / f"{tag}.png")
        await page.save_screenshot(shot_path)
        log(f"  diag screenshot → {shot_path}")
    except Exception as e:
        log(f"  (screenshot failed: {e})")
    try:
        html = _val(await page.evaluate("document.documentElement.outerHTML", return_by_value=True))
        (outdir / f"{tag}.html").write_text(html or "")
        log(f"  diag HTML → {outdir / (tag + '.html')}")
    except Exception as e:
        log(f"  (HTML dump failed: {e})")


async def ui_activate_offers(page, target_count: int, dry_run: bool, delay: float = 2.0) -> int:
    """Activate offers by clicking the page's own buttons (no API). Returns 0 on
    success. Keeps clicking until no more activate buttons remain or we reach
    target_count. Safe to call repeatedly (enrolled offers drop off the list)."""
    if dry_run:
        # Give the SPA a moment to finish rendering its offer cards.
        await page.wait(3)
        found = _val(await page.evaluate(JS_UI_ACTIVATE.replace(".click()", ""), return_by_value=True)) or {}
        n = found.get("found", 0) if isinstance(found, dict) else 0
        log(f"\n[DRY RUN] {n} activate button(s) visible on the page.")
        if n == 0:
            log("  (0 found — dumping page diagnostics so the markup can be matched)")
            await _dump_page_diag(page, tag="offers_page")
        log("Re-run in 'activate' mode to click them.")
        return 0

    done = 0
    guard = 0
    while done < target_count and guard < 200:  # hard cap on iterations
        guard += 1
        # Scroll to load lazy cards, then look for an activate button.
        await page.evaluate("window.scrollBy(0, 900)", return_by_value=True)
        await page.wait(0.8)
        res = _val(await page.evaluate(JS_UI_ACTIVATE, return_by_value=True))
        if not (isinstance(res, dict) and res.get("found", 0)):
            # No more buttons — scroll back to top and confirm it's truly empty.
            await page.evaluate("window.scrollTo(0,0)", return_by_value=True)
            await page.wait(1.5)
            res2 = _val(await page.evaluate(JS_UI_ACTIVATE, return_by_value=True))
            if not (isinstance(res2, dict) and res2.get("found", 0)):
                break
            res = res2
        info(f"  \u2b05 clicked '{res.get('clicked')}' ({done+1}/{target_count})")
        done += 1
        # Wait for the modal/confirmation to process; dismiss any confirm dialog.
        await page.wait(delay)
        await page.evaluate(
            "(function(){var b=[].slice.call(document.querySelectorAll('button'))."
            "find(x=>/confirm|yes|ok|activate|enroll/i.test(x.textContent.trim()));"
            "if(b)b.click();return !!b;})()", return_by_value=True)
        await page.wait(1.5)
    info(f"\nDone  activated via UI: {done}/{target_count}")
    return 0 if done >= target_count else 1


def find_chrome() -> str | None:
    import shutil
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
    for name in ("google-chrome", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    return None


def _resolve_account_id(offers_data: dict, cookies: list) -> str | None:
    """accountId from the retrieve response (cardArtDetails[0].accountId), else
    the accountId cookie."""
    try:
        cards = offers_data.get("cardArtDetails") or []
        if cards and cards[0].get("accountId"):
            return cards[0]["accountId"]
    except Exception:
        pass
    for n, v, _ in cookies:
        if n == "accountId" and v:
            return v
    return None


async def run(args) -> int:
    # First line: when this run started (local time), for log correlation.
    info(f"===== citi-offers started {datetime.now():%Y-%m-%d %H:%M:%S} =====")
    # Clean mode banner (always shown, not gated by --verbose).
    if args.activate and not args.dry_run:
        info("===== MODE: ACTIVATE — this will ENROLL available offers =====")
    elif args.dry_run:
        info("===== MODE: DRY RUN — list only, nothing is enrolled =====")
    else:
        info("===== MODE: LIST — list offers, nothing is changed =====")
    chrome = args.chrome or find_chrome()
    if not (chrome and Path(chrome).exists()):
        log(f"[nodriver] no Chrome found at {CHROME_CANDIDATES} — install Chrome "
              "or pass --chrome /path/to/chrome")
        return 2
    # Extra Chrome flags for container/Xvfb/root stability.
    extra_flags = [
        "--disable-dev-shm-usage",        # avoid /dev/shm crashes in Docker
        "--no-first-run",
        "--no-default-browser-check",
        "--no-remote-extensions",
        "--disable-infobars",
        "--disable-session-crashed-bubble",
        "--disable-features=Translate,MediaRouter,OptimizationHints",
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-sync",
        "--disable-translate",
        "--metrics-recording-only",
        "--no-pings",
        "--mute-audio",
        "--lang=en-US",
        "--window-size=1280,900",
        # Enable the password manager + autofill so --autofill works, and keep the
        # 'Save password' UI from stealing focus / blocking unattended runs.
        "--enable-features=PasswordManagerOnboarding,AutofillServerCommunication",
        "--disable-features=PasswordLeakDetection",  # don't hang on leak checks
        # Keep a REAL (headed) window — TMX blocks headless — but tuck it out of
        # the way so it's not obtrusive: start minimized and offset off-screen.
        "--start-minimized",
        "--window-position=-2000,-2000",
    ]
    # Running as root (e.g. Home Assistant add-on) makes Chrome refuse to start
    # without these; add them when uid==0.
    if os.geteuid() == 0:
        extra_flags += [
            "--no-sandbox",
            "--no-zygote",
            "--single-process" if os.environ.get("CITI_SINGLE_PROC") else "--disable-gpu",
        ]
    import subprocess
    log(f"[nodriver] uid={os.geteuid()} chrome={chrome}")
    log(f"[nodriver] flags: {' '.join(extra_flags)}")
    # Smoke-test that Chrome can actually start in this environment, and capture
    # its error output (which tells us the real reason for a connect failure).
    try:
        st = subprocess.run(
            [chrome, "--version"], capture_output=True, text=True, timeout=15)
        log(f"[nodriver] chrome --version: {st.stdout.strip() or st.stderr.strip()}")
    except Exception as ex:
        log(f"[nodriver] chrome --version failed: {ex}")

    async def _start(flags):
        try:
            return await uc.start(
                headless=False,
                user_data_dir=str(Path(args.profile).resolve()),
                sandbox=False,
                browser_executable_path=chrome,
                browser_args=flags,
            )
        except TypeError:
            return await uc.start(
                headless=False,
                user_data_dir=str(Path(args.profile).resolve()),
                sandbox=False,
                browser_executable_path=chrome,
            )

    try:
        browser = await _start(extra_flags)
        await browser.wait(2)
    except Exception as ex:
        log(f"[nodriver] first launch failed ({ex}) — retrying with --single-process --no-zygote")
        browser = await _start(extra_flags + ["--single-process", "--no-zygote", "--disable-gpu"])
        await browser.wait(2)
    info(f"launching browser → {LOGIN_URL}")
    page = await browser.get(LOGIN_URL)
    # The offers page either renders (already logged in) or redirects to sign-on.
    # Wait a moment for any redirect to settle before we inspect the form.
    for _ in range(10):
        await browser.sleep(1)
        if "/login" in (page.url or "").lower() or "signon" in (page.url or "").lower():
            break
    log(f"[nodriver] landed on: {page.url}")
    await browser.sleep(2)  # let Angular render the signon form (if redirected)
    await dismiss_consent(page)      # cookie banner may overlay the form

    # We're on a login screen if the URL looks like one OR the page has a
    # password field. The inactivity page (https://www.citi.com/?loginScreenId=
    # inactivityHomePage) has NO /login in the path, so the URL check alone
    # misses it — the password-field check catches it.
    url_now = (page.url or "").lower()
    on_login_url = ("/login" in url_now or "signon" in url_now or "loginscreenid" in url_now)
    has_pw_field = False
    try:
        has_pw_field = bool(_val(await page.evaluate(
            "!!document.querySelector('input[type=password]')", return_by_value=True)))
    except Exception:
        pass
    on_login = on_login_url or has_pw_field
    if getattr(args, "probe_typing", False):
        import sys as _sys
        def _p(msg):
            print(msg, file=_sys.stderr, flush=True)
            print(msg, file=_sys.stdout, flush=True)
        _p("[probe] STEP 0: probe branch entered")
        try:
            _p("[probe] STEP 1: waiting for form to settle…")
            await _wait_form_settled(page, timeout_s=25)
            _p("[probe] STEP 2: settled, probing typing methods…")
            res = await _probe_username_typing(page)
            _p(f"[probe] url_before = {res.get('url_before')}")
            _p(f"[probe] url_final  = {res.get('url_final')}  reloaded={res.get('reloaded')}")
            for method in ("insertText", "cdp_keydown", "js_typing"):
                val = res.get(method)
                mark = "  LANDED" if val == "TEST123" else ("  partial" if val else "  empty")
                _p(f"[probe]    {method:14} -> value={val!r}{mark}")
            _p("[probe] STEP 4: done")
        except Exception as e:
            import traceback
            _p(f"[probe] ERROR: {type(e).__name__}: {e}")
            _p(traceback.format_exc())
        try:
            await browser.aclose()
        except Exception:
            pass
        _p("[probe] STEP 5: returning 0")
        return 0
    if not on_login:
        log("Already authenticated (offers page loaded directly) — skipping login.")
    elif args.manual:
        log("Manual mode: type your credentials (and any MFA) in the window.")
    elif args.autofill:
        # Chrome's native password-manager autofill (trusted input that Citi's
        # anti-bot accepts). The password must already be saved in this profile.
        info("waiting for the login form to settle…")
        await _wait_form_settled(page, timeout_s=25)
        ok = await _autofill_login(page, timeout_s=25)
        if not ok:
            log("    [autofill] failed — Chrome did not autofill.")
            log("    → save the password first (run once with --manual and accept")
            log("      the 'Save password' prompt), then re-run with --autofill.")
            log("    Manual mode: type your credentials in the window to finish.")
    else:
        # Wait for the login form to be STABLE (both fields present, no pending
        # navigation). Citi's SSO re-navigates a few times after landing on
        # /login; interacting mid-navigation throws 'Inspected target navigated
        # or closed'. Poll until the form settles, up to ~20s.
        info("waiting for the login form to settle…")
        settled = await _wait_form_settled(page, timeout_s=25)
        if not settled:
            log("    (form did not fully settle — attempting fill anyway)")
        info(f"auto-filling credentials for '{args.user}' …")
        ok = await fill_and_submit(page, args.user, args.password)
        if not ok:
            log("    → falling back to manual entry. Finish in the window.")

    # After submitting credentials, Citi may present a second-factor screen
    # ("Verify your identity") before completing the SSO. Detect it and report
    # exactly what's on screen so the right verification can be completed.
    await browser.sleep(3)
    await _check_login_error(page)
    mfa = await _detect_mfa(page)
    # If we're still on a sign-on/verify screen (not the offers page), try to
    # complete the second factor (remember-device + code + continue).
    mfa_url = (mfa.get("url", "") if mfa else "").lower()
    if mfa and ("/login" in mfa_url or "signon" in mfa_url or mfa.get("mfa")):
        await _handle_mfa(page, code=args.mfa_code, mfa_wait=args.mfa_wait)

    info(f"waiting for login to complete (up to {args.timeout}s)…")
    success = await wait_for_login(browser, page, args.timeout)

    # Diagnostic: always snapshot the post-login state so we can see what happened.
    try:
        await page.save_screenshot(args.profile + "_login_result.png")
        url = page.url
        body_text = _val(await page.evaluate("document.body ? document.body.innerText.slice(0,600) : ''")) or ""
        names = {getattr(c, "name", "") for c in await browser.cookies.get_all()}
        log(f"\n[diag] URL: {url}")
        log(f"[diag] citi_authorization={'Y' if 'citi_authorization' in names else 'N'} "
              f"tmx_sessionid={'Y' if SUCCESS_COOKIE in names else 'N'}")
        log(f"[diag] page text: {body_text.strip()[:300]}")
    except Exception as e:
        log(f"[diag] screenshot/text failed: {e}")

    citi = []
    if success:
        citi = [ (n, v, d) for (n, v, d) in await export_cookies(browser) if n ]
        info(f"login OK — captured {len(citi)} cookies")
    else:
        info("LOGIN FAILED (timed out). Check the screenshot " + args.profile + "_login_result.png")

    rc = 0 if success else 1

    if success and (args.offers or args.activate):
        info("logged in — navigating to the merchant-offers page…")
        # Turn on the Network domain BEFORE navigating so we catch the offers
        # page's own retrieve() call (same origin => correct cookies + TMX state).
        from nodriver import cdp
        from nodriver.cdp.network import ResponseReceived
        captured: dict = {}

                # Capture the response body EAGERLY: read it the instant the response is
        # received, before Chrome evicts it from memory (CDP drops old responses,
        # so a later getResponseBody call fails with "No data found").
        from nodriver.cdp.network import LoadingFinished
        async def on_response(e):
            resp = e.response
            rurl = resp.get("url", "") if isinstance(resp, dict) else getattr(resp, "url", "")
            if "merchantOffers/retrieve" in rurl:
                rid = e.request_id
                status = resp.get("status") if isinstance(resp, dict) else getattr(resp, "status", None)
                captured["status"] = status
                try:
                    # Small grace for the body to be fully buffered.
                    for _ in range(20):
                        try:
                            body, is_b64 = await page.send(cdp.network.get_response_body(rid))
                            break
                        except Exception:
                            await asyncio.sleep(0.15)
                    else:
                        body, is_b64 = "", False
                    if is_b64:
                        import base64
                        body = base64.b64decode(body).decode("utf-8", "replace")
                    captured["body"] = body
                    captured["done"] = True
                except Exception as ex:
                    captured["error"] = str(ex)

        try:
            await page.send(cdp.network.enable())
            page.add_handler(ResponseReceived, on_response)
        except Exception as e:
            log(f"    (could not enable network capture: {e})")

        # Navigate to the offers page. After a www.citi.com login the SSO to
        # online.citi.com may not be ready on the first hop, which bounces us to
        # the homepage. Retry a couple of times until we actually land on the
        # merchantoffers page (the SPA then calls retrieve() itself).
        landed = False
        for attempt in range(3):
            await page.get(OFFERS_PAGE)
            # Give the SPA + any SSO redirect time to settle.
            for _ in range(12):
                await page.wait(1)
                cur = (page.url or "").lower()
                if "merchantoffers" in cur and "/login" not in cur:
                    break
            cur = (page.url or "").lower()
            log(f"    offers page attempt {attempt+1} -> url={cur[:90]}")
            if "merchantoffers" in cur and "/login" not in cur:
                landed = True
                break
            log("    (not on the offers page — SSO may still be settling; retrying…)")
        info("waiting for the offers to load…")
        offers = None
        for _ in range(60):  # up to ~60s for the SPA to call retrieve
            await page.wait(1)
            if captured.get("done") or captured.get("error"):
                status = captured.get("status")
                info(f"offers API -> HTTP {status}")
                body = captured.get("body")
                if body:
                    try:
                        offers = json.loads(body)
                    except Exception as ex:
                        log(f"    bad JSON: {ex}")
                elif captured.get("error"):
                    log(f"    body read failed: {captured['error']}")
                break
        # Fallback: issue retrieve() from the (authenticated, same-origin) page directly.
        if not offers:
            log("    (falling back to issuing retrieve() from the offers page…)")
            status, offers = await _browser_post(page, OFFERS_API, {}, "merchantOffers/retrieve", wait_s=8.0)
            info(f"offers API -> HTTP {status}")
        # A 403 (TMX bot gate) returns a JSON *error* object, which is truthy. Treat
        # any non-200 status as "no offers" so the UI fallback kicks in.
        if offers is not None and status is not None and status != 200:
            log(f"    (treating HTTP {status} as no data)")
            offers = None
        use_ui = args.ui
        if not offers:
            log("Offers API did not return data (403/timeout).")
            # The TMX bot gate blocks the API in the container, but the offers page
            # still RENDERS. So fall back to reading/activating via the UI:
            #  - activate mode  -> click the page's own Activate buttons
            #  - list / dry-run -> dry-run the UI to count what's on the page
            if args.activate and not args.dry_run:
                log("    (TMX bot gate active — falling back to clicking the page's "
                      "own Activate buttons…)")
                use_ui = True
            else:
                log("    (TMX bot gate active — falling back to a UI dry-run to list "
                      "the offers shown on the page…)")
                use_ui = True
                args.dry_run = True   # never actually activate when we only asked to list

        if use_ui and (args.activate or args.dry_run):
            # Count of offers to activate: use API count if we have it, else a
            # generous cap (the loop stops when no activate buttons remain).
            target = 0
            if offers:
                seen = set()
                for cat in offers.get("merchantOffers") or []:
                    for o in cat.get("offers") or []:
                        if o.get("offerStatus") == "AVAILABLE" and o.get("offerId") not in seen:
                            seen.add(o.get("offerId")); target += 1
            if target == 0:
                target = 200  # let the UI loop run until no buttons remain
            rc = await ui_activate_offers(page, target, dry_run=args.dry_run, delay=args.delay)
        else:
            if args.offers:
                # Default output to a writable location (/config/out) if the cwd
                # isn't writable; fall back gracefully if the write still fails.
                out = args.offers_out or "offers.json"
                p = Path(out)
                if not p.parent.exists() or not os.access(str(p.parent) or ".", os.W_OK):
                    alt = Path("/config/out") / "offers.json"
                    alt.parent.mkdir(parents=True, exist_ok=True)
                    if os.access(str(alt.parent), os.W_OK):
                        out = str(alt)
                try:
                    Path(out).write_text(json.dumps(offers or {}, indent=2))
                    info(f"Saved offers → {out}")
                except Exception as ex:
                    info(f"(could not save offers to {out}: {ex})")
            if args.activate and not args.dry_run:
                acct = _resolve_account_id(offers, citi)
                log(f"accountId = {acct}")
                rc = await enroll_offers_in_browser(
                    page, offers, acct, dry_run=args.dry_run, delay=args.delay)

    # Export the raw Cookie header (all citi.com cookies, incl. Akamai/TMX tokens)
    if success and args.out:
        raw = "; ".join(f"{n}={v}" for n, v, _ in citi)
        Path(args.out).write_text(raw)
        log(f"Saved raw Cookie header ({len(citi)} cookies) → {args.out}")
        # also save nodriver's native session (pickle) for fast re-login later
        try:
            session_file = str(Path(args.profile).resolve()) + ".session.dat"
            await browser.cookies.save(session_file)
        except Exception as e:
            log(f"(note: could not save native nodriver session: {e})")

    if args.keep_open:
        log("--keep-open: leaving the browser running. Ctrl+C to exit.")
        try:
            await asyncio.sleep(3600)
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass

    browser.stop()
    return rc


def _load_credentials(args) -> tuple:
    """Resolve (user, password). Sources, in priority order:
      1. -u / -p CLI flags
      2. CITI_USER / CITI_PASSWORD environment variables (ideal for Docker/HA
         — no file needed, and the HA add-on passes these as env vars)
      3. --config YAML file (defaults to ./credentials.yaml if it exists)
      4. interactive prompt (last resort)
    YAML format:
        user:  your_username
        password: your_password
    (top-level keys, or a nested 'citi:' block)"""
    user = password = None
    # 3. YAML config — default to ./credentials.yaml if present and --config
    #    wasn't given explicitly.
    cfg = args.config or ("credentials.yaml" if Path("credentials.yaml").exists() else None)
    if cfg:
        try:
            import yaml
            with open(cfg) as f:
                data = yaml.safe_load(f) or {}
            node = data.get("citi", data) if isinstance(data, dict) else {}
            user = node.get("user") or node.get("username")
            password = node.get("password")
            log(f"Loaded credentials from {cfg}")
        except Exception as e:
            sys.exit(f"Could not read --config {cfg}: {e}")
    # 1 + 2. CLI flags and env vars override the file.
    user = args.user or os.environ.get("CITI_USER") or user
    password = args.password or os.environ.get("CITI_PASSWORD") or password
    if not user:
        sys.exit("No username. Pass --config credentials.yaml, -u USER, "
                 "or set the CITI_USER environment variable.")
    if not password:
        if os.isatty(0):   # interactive terminal only
            password = getpass.getpass(f"Password for {user} (hidden): ")
        else:
            sys.exit(f"No password for {user!r}. Pass -p, set CITI_PASSWORD, "
                     "or add it to credentials.yaml.")
    return user, password


def main() -> int:
    p = argparse.ArgumentParser(
        description="Citi login + merchant-offer activation via nodriver (real Chrome, CDP).")
    p.add_argument("-c", "--config", help="YAML file with user/password (see --help-config)")
    p.add_argument("-u", "--user", help="Citi username (overrides --config)")
    p.add_argument("-p", "--password", help="Citi password (overrides --config)")
    p.add_argument("-o", "--out", default="session.txt",
                   help="write the session cookies here (default session.txt)")
    p.add_argument("--profile", default=".citi_nodriver_profile",
                   help="Chrome user-data dir (default .citi_nodriver_profile)")
    p.add_argument("--chrome", help="path to Chrome/Chromium binary (auto-detected if omitted)")
    p.add_argument("--manual", action="store_true",
                   help="skip auto-fill; you type credentials + any MFA yourself")
    p.add_argument("--probe-typing", action="store_true",
                   help="DIAGNOSTIC: launch, go to login, and try several typing "
                        "methods on the username field, reporting which lands.")
    p.add_argument("--autofill", action="store_true",
                   help="use Chrome's native password-manager autofill (password "
                        "must be saved in this profile first via one manual login); "
                        "best for unattended runs — Chrome fills both fields, the "
                        "script just clicks Sign On")
    p.add_argument("--timeout", type=int, default=90,
                   help="seconds to wait for login success if it hasn't completed "
                        "(default 90; on success this returns immediately, so this "
                        "only bounds a FAILED login)")
    p.add_argument("--keep-open", action="store_true", help="keep browser open after login")
    p.add_argument("--offers", action="store_true",
                   help="after login, fetch the merchant offers JSON in the browser and save it")
    p.add_argument("--offers-out", help="output file for --offers (default offers.json)")
    p.add_argument("--activate", action="store_true",
                   help="after login, fetch offers and ENROLL all AVAILABLE ones (in the browser)")
    p.add_argument("--ui", action="store_true",
                   help="activate by clicking the page's own buttons (bypasses the TMX-gated API); auto-used when the API 403s")
    p.add_argument("--mfa-code", default=None,
                   help="one-time verification code to enter if Citi asks for a second factor")
    p.add_argument("--mfa-wait", type=int, default=0,
                   help="if set, after submitting, wait up to N seconds for you to "
                        "complete MFA manually in the browser (push/SMS/app)")
    p.add_argument("--dry-run", action="store_true",
                   help="with --activate: list what would be enrolled, enroll nothing")
    p.add_argument("--delay", type=float, default=1.0,
                   help="seconds between enroll requests (default 1.0)")
    p.add_argument("--verbose", action="store_true",
                   help="print full diagnostic output (off by default)")
    args = p.parse_args()

    global VERBOSE
    VERBOSE = args.verbose or VERBOSE

    args.user, args.password = _load_credentials(args)

    return uc.loop().run_until_complete(run(args))


if __name__ == "__main__":
    sys.exit(main())
