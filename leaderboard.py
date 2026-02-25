# dreamlo leaderboard wrapper
#
# the private key is lightly obfuscated (XOR + base64) so it doesn't show
# up in a casual grep. anyone reading this file can obviously decode it,
# but that's fine -- it just keeps bots from scraping plaintext secrets.
#
# to encode a new key if you need to rotate it:
#
#   import base64
#   key = "your-new-private-key"
#   salt = "asteroids-salt-2024"
#   xored = bytes(a ^ b for a, b in zip(key.encode(), (salt * (len(key) // len(salt) + 1)).encode()))
#   print(base64.b64encode(xored).decode())

import base64
import json
import threading
import urllib.request

_SALT = "asteroids-salt-2024"
_PRIVATE_KEY_ENC = "Dj8NITQlOg4EeF43AQxscwZxAxVDJTc7LQEnHnkeFjkRaEZadHgsEDY1Cz4="
PUBLIC_KEY = "699ea7bc8f40bb1a147f96ef"  # read-only, safe to expose


def _decode_key(encoded):
    raw = base64.b64decode(encoded)
    salt_bytes = (_SALT * (len(raw) // len(_SALT) + 1)).encode()
    return bytes(a ^ b for a, b in zip(raw, salt_bytes)).decode()


def _private_key():
    return _decode_key(_PRIVATE_KEY_ENC)


def submit_score(name, score):
    # dreamlo uses GET for writes, yeah, it's weird.
    # also uses * and / as delimiters so those can't appear in names
    name = name.replace("*", "").replace("/", "")
    if not name:
        return
    key = _private_key()
    url = f"http://dreamlo.com/lb/{key}/add/{name}/{score}"
    with urllib.request.urlopen(urllib.request.Request(url), timeout=5) as resp:
        resp.read()


def fetch_leaderboard():
    url = f"http://dreamlo.com/lb/{PUBLIC_KEY}/json"
    with urllib.request.urlopen(urllib.request.Request(url), timeout=5) as resp:
        data = json.loads(resp.read().decode())

    entries = data.get("dreamlo", {}).get("leaderboard", {}).get("entry", [])
    # when there's only one score dreamlo returns a bare dict instead of a list
    if isinstance(entries, dict):
        entries = [entries]

    return [
        {"name": e.get("name", "???"), "score": int(e.get("score", 0))}
        for e in entries[:10]
    ]


def fetch_leaderboard_async(callback):
    # runs the fetch on a background thread so the game over screen
    # doesn't hang while we wait on the network
    def _run():
        try:
            entries = fetch_leaderboard()
            callback(entries, None)
        except Exception as e:
            callback(None, str(e))

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t
