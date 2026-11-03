import base64, json, os, urllib.request

URL = "https://superagent-269bfe30.base44.app/functions/kaleidoscopeRadio"
PAT = os.environ.get("MANDY_PAT", "").strip()
if not PAT:
    print("no token in secrets")
    raise SystemExit(1)

b64 = base64.b64encode(open("heal.py", "rb").read()).decode()
cmd = ("echo %s | base64 -d > /home/user/radio/heal.py; "
       "mkdir -p /home/user/radio/music; cd /home/user/radio && "
       "(MANDY_PAT=%s nohup python3 heal.py > heal.log 2>&1 &) ; echo healing" % (b64, PAT))
body = json.dumps({"action": "run", "command": cmd}).encode()
req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"}, method="POST")
print(urllib.request.urlopen(req, timeout=60).read()[:300].decode())
