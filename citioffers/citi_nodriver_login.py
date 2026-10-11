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
USER_SELECTORS = [
    "input[id*='username' i]", "input[id*='userid' i]", "input[id*='coboUserName' i]",
    "input[autocomplete='username']", "input[name*='user' i]",
]
PASS_SELECTORS = [
    "input[id*='password' i]", "input[type='password']",
    "input[autocomplete='current-password']", "input[name*='password' i]",
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


async def _type_into(field_selector: str, text: str, page) -> bool:
    """Focus a field and type `text`.
    Primary: real keyboard events (send_keys) after focusing. If a CDP node error
    breaks that path, fall back to an in-page JS keystroke simulation. Verify the
    value actually landed before reporting success."""
    landed = False
    try:
        el = await page.wait_for(field_selector, timeout=8)
        await page.evaluate(
            "(function(){var el=document.querySelector(" + json.dumps(field_selector) +
            ");if(el){el.focus();if(el.select)el.select();}return 1;})()",
            return_by_value=True)
        await page.wait(0.3)
        try:
            await el.click()
        except Exception:
            pass
        for ch in text:
            await el.send_keys(ch)
            await asyncio.sleep(0.02)
        await page.wait(0.3)
        v = _val(await page.evaluate(
            "(document.querySelector(" + json.dumps(field_selector) + ").value)||''",
            return_by_value=True))
        landed = len(v or "") > 0
    except Exception as e:
        log(f"    (send_keys path failed: {type(e).__name__}; trying JS typing…)")
    if not landed:
        try:
            n = _val(await page.evaluate(_js_type(field_selector, text), return_by_value=True))
            landed = isinstance(n, int) and n > 0
            if landed:
                await page.wait(0.3)
        except Exception as e:
            log(f"    (JS typing failed: {e})")
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
        ok = await _type_into(sel, text, page)
        log(f"    {label}: selector {sel!r} present, landed={ok}")
        if ok:
            return True
    log(f"    {label}: no selector landed text (tried {len(selectors)})")
    return False


async def fill_and_submit(page, user: str, password: str) -> bool:
    """Fill the dynamic sign-on fields (real keyboard) and click Sign On (JS)."""
    try:
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
        # Submit. A bare JS .click() does NOT trigger Citi's Angular submit, so we
        # dispatch a full MouseEvent sequence (pointerdown/mousedown/mouseup/click)
        # with proper bubbles/composed, then verify we left the login page. If we
        # still haven't navigated, press Enter in the password field (submits form).
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
        res = _val(await page.evaluate(submit_js, return_by_value=True)) or {}
        clicked = res.get("clicked") if isinstance(res, dict) else None
        if not clicked:
            log("    'Sign On' button not found — click it manually.")
            return False
        log(f"    clicked Sign On ({clicked!r}), waiting for navigation…")
        # Give the SSO a moment; if we're still on the login page, press Enter.
        for _ in range(6):
            await page.wait(1)
            if "/login" not in (page.url or "").lower():
                log("    (navigated off login page)")
                break
        else:
            log("    (still on login page — pressing Enter to submit the form)")
            try:
                pw = await page.wait_for(PASS_SELECTORS[0], timeout=3)
                await pw.send_keys("\n")
                await page.wait(2)
            except Exception as e:
                log(f"    (Enter fallback failed: {e})")
        return True
    except Exception as e:
        log(f"    auto-fill failed ({type(e).__name__}: {e}). Complete the login "
              f"manually in the window.")
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
            log("[login] CAPTCHA detected — a human must solve it (use --manual).")
        if d.get("bad") or d.get("err"):
            log(f"[login] possible login failure: bad={d.get('bad')} err={d.get('err')!r} "
                  f"url={d.get('url')}")
            log("[login]  ^ If 'invalid/incorrect', the credentials were rejected.")
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
        # Success: we're on the offers page (login's nextRoute target).
        if "merchantoffers" in url and "/login" not in url:
            return True
        on_login_page = "/login" in url or "signon" in url
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
        "--disable-infobars",
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-sync",
        "--disable-translate",
        "--metrics-recording-only",
        "--no-pings",
        "--mute-audio",
        "--lang=en-US",
        "--window-size=1280,900",
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

    on_login = "/login" in (page.url or "").lower() or "signon" in (page.url or "").lower()
    if not on_login:
        log("Already authenticated (offers page loaded directly) — skipping login.")
    elif args.manual:
        log("Manual mode: type your credentials (and any MFA) in the window.")
    else:
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
    """Resolve (user, password) from --config YAML, then -u/-p, then env, then prompt.
    YAML format:
        user:  your_username
        password: your_password
    (top-level keys, or a nested 'citi:' block)"""
    user = password = None
    if args.config:
        try:
            import yaml
            with open(args.config) as f:
                data = yaml.safe_load(f) or {}
            node = data.get("citi", data) if isinstance(data, dict) else {}
            user = node.get("user") or node.get("username")
            password = node.get("password")
            log(f"Loaded credentials from {args.config}")
        except Exception as e:
            sys.exit(f"Could not read --config {args.config}: {e}")
    user = args.user or user
    password = args.password or os.environ.get("CITI_PASSWORD") or password
    if not user:
        sys.exit("No username. Pass --config credentials.yaml or -u USER")
    if not password:
        password = getpass.getpass(f"Password for {user} (hidden): ")
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
