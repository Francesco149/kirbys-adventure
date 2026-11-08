"""jev.py — TypeSafe Jev on OpenRouter's Decisions API: typed questions in, probabilities out.

POST https://openrouter.ai/api/alpha/decisions  {model, state, questions, files?}
  choice {"instructions", "criteria": {key: description}} -> {"choice", "probabilities", "confidence"}
Key: OPENROUTER_API_KEY from ~/.omp/agent/.env (never printed or logged).
"""
import base64
import json
import os
import time
import urllib.error
import urllib.request

URL = "https://openrouter.ai/api/alpha/decisions"
MODEL = os.environ.get("JEV_MODEL", "~typesafe/jev-latest")
_key = None


def key():
    global _key
    if _key is None:
        _key = os.environ.get("OPENROUTER_API_KEY")
        if not _key:
            for line in open(os.path.expanduser("~/.omp/agent/.env")):
                if line.startswith("OPENROUTER_API_KEY="):
                    _key = line.split("=", 1)[1].strip().strip('"')
        if not _key or not _key.startswith("sk-or-"):
            raise RuntimeError("no OpenRouter key (OPENROUTER_API_KEY or ~/.omp/agent/.env)")
    return _key


class Usage:
    calls = 0
    cost = 0.0
    seconds = 0.0
    input_tokens = 0


USAGE = Usage()


def decide(state, questions, png=None, retries=3, timeout=60):
    body = {"model": MODEL, "state": state, "questions": questions}
    if png is not None:
        body["files"] = ["data:image/png;base64," + base64.b64encode(png).decode()]
    data = json.dumps(body).encode()
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(URL, data=data, headers={
            "Authorization": f"Bearer {key()}", "Content-Type": "application/json",
            "X-Title": "kirby-tas"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                resp = json.loads(r.read())
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read()[:400]!r}"
            if e.code in (400, 401, 402, 403):
                raise RuntimeError(last)
            time.sleep(2 * (attempt + 1))
            continue
        except (urllib.error.URLError, TimeoutError) as e:
            last = str(e)
            time.sleep(2 * (attempt + 1))
            continue
        USAGE.calls += 1
        USAGE.seconds += time.time() - t0
        u = resp.get("usage") or {}
        USAGE.cost += float(u.get("cost") or 0)
        USAGE.input_tokens += int(u.get("input_tokens") or 0)
        if "answers" not in resp:
            last = json.dumps(resp)[:300]
            continue
        return resp["answers"], resp
    raise RuntimeError(f"Jev failed after {retries} tries: {last}")
