import json, urllib.request

URL = "https://superagent-269bfe30.base44.app/functions/kaleidoscopeRadio"

try:
    req = urllib.request.Request(URL, data=json.dumps({"action": "info"}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    info = json.load(urllib.request.urlopen(req, timeout=30))
except Exception as e:
    print("station call failed:", e)
    print("songs=0")
    raise SystemExit(0)

songs = info.get("songs") or []
print("now playing:", info.get("np"), "| songs:", len(songs))
print("stream:", info.get("stream"))
print("songs=%d" % len(songs))
