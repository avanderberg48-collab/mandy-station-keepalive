import base64, io, json, os, sys, tarfile, urllib.request

RADIO = "/home/user/radio"
MUSIC = RADIO + "/music"
REPO = "avanderberg48-collab/mandy-radio-library"
TOK = os.environ.get("MANDY_PAT", "").strip()
if not TOK:
    print("no token"); raise SystemExit(1)
os.makedirs(MUSIC, exist_ok=True)
os.makedirs(RADIO + "/playlists", exist_ok=True)
open(RADIO + "/.ghtoken.b64", "w").write(base64.b64encode(TOK.encode()).decode())

H = {"Authorization": "Bearer " + TOK, "User-Agent": "mandy-keepalive"}

def gj(u):
    return json.load(urllib.request.urlopen(
        urllib.request.Request(u, headers=dict(H, Accept="application/vnd.github+json")), timeout=60))

def ga(u):
    return urllib.request.urlopen(
        urllib.request.Request(u, headers=dict(H, Accept="application/octet-stream")), timeout=180).read()

# 1) meta: schedule, programs, story, playlists
try:
    for r in gj("https://api.github.com/repos/%s/releases?per_page=20" % REPO):
        if r.get("tag_name") != "radio-meta":
            continue
        for a in r.get("assets", []):
            n = a["name"]
            if n == "meta_playlists.tar.gz":
                d = ga(a["url"])
                with tarfile.open(fileobj=io.BytesIO(d), mode="r:gz") as tf:
                    tf.extractall(RADIO)
            elif n.startswith("meta_") and n.endswith(".json"):
                open(os.path.join(RADIO, n[5:]), "wb").write(ga(a["url"]))
    print("meta ok", flush=True)
except Exception as e:
    print("meta fail", e, flush=True)

# 2) music, story and programs first
try:
    rel = gj("https://api.github.com/repos/%s/releases/tags/library" % REPO)
    assets = []
    page = 1
    while page <= 12:
        b = gj("https://api.github.com/repos/%s/releases/%s/assets?per_page=100&page=%d" % (REPO, rel["id"], page))
        if not b:
            break
        assets += b
        page += 1
    pri = ("stryd_", "prog_", "gsp_")
    assets.sort(key=lambda a: (0 if a["name"].startswith(pri) else 1, a["name"]))
    got = skip = fail = 0
    for a in assets:
        nm = a["name"]
        if not nm.lower().endswith(".mp3"):
            continue
        dest = os.path.join(MUSIC, nm)
        if os.path.exists(dest) and os.path.getsize(dest) == a["size"]:
            skip += 1
            continue
        try:
            d = urllib.request.urlopen(urllib.request.Request(a["url"], headers={
                "Authorization": "Bearer " + TOK, "User-Agent": "mandy-keepalive",
                "Accept": "application/octet-stream"}), timeout=120).read()
            if len(d) == a["size"]:
                open(dest, "wb").write(d)
                got += 1
            else:
                fail += 1
        except Exception:
            fail += 1
    print("music done got", got, "skip", skip, "fail", fail, "total", len(os.listdir(MUSIC)), flush=True)
except Exception as e:
    print("music fail", e, flush=True)
