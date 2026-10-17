#!/usr/bin/env python3
"""各領域的來源清單管理（data/sources/<領域>.json）。只用 Python 標準庫，不呼叫任何 AI，不耗 Claude 額度。

用法：
  python3 tools/sources.py scan [領域]           # 依 data/feeds.json 的 sitemap 找新文章（不給領域＝全部有設定 feed 的領域）
  python3 tools/sources.py add <領域> <網址>      # 手動加一個來源（沒有 feed 的領域，例如佛學、術數）
  python3 tools/sources.py new [領域]            # 列出 status=new（待分類）的來源
  python3 tools/sources.py stats [領域]          # 各狀態數量
  python3 tools/sources.py check                 # 檢查全站資料：id、短名衝突、來源指到不存在的單元

已在清單裡的網址不會再抓，每週重跑的成本只有 sitemap 加上新文章本身。
"""
import concurrent.futures as cf
import datetime as dt
import html
import json
import re
import sys
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
UA = {"User-Agent": "Mozilla/5.0 (xuanxuan-learning source tracker)"}
CATEGORIES = ["Product announcements", "Best practices", "Perspectives", "Insights"]
STATUSES = {
    "new": "剛加入、尚未分類",
    "todo": "要學（topic 主題、priority 1 核心／2 延伸）",
    "done": "已做成課（lesson 為單元 id）",
    "skip": "不學：與需求關聯低（reason 為類別）",
    "outdated": "不學：已過時（reason 為原因）",
}


def domains():
    return json.loads((DATA / "domains.json").read_text(encoding="utf-8"))["domains"]


def feeds():
    p = DATA / "feeds.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def src_path(domain):
    return DATA / "sources" / f"{domain}.json"


def load(domain):
    p = src_path(domain)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"domain": domain, "updated": None, "statuses": STATUSES, "items": []}


def save(domain, db):
    db["items"].sort(key=lambda x: (x.get("date") or "", x["url"]), reverse=True)
    db["statuses"] = STATUSES
    src_path(domain).parent.mkdir(parents=True, exist_ok=True)
    src_path(domain).write_text(json.dumps(db, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def get(url, timeout=25):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def meta(url):
    """抓單篇的標題、日期、分類、摘要（只取公開 metadata）。"""
    try:
        h = get(url)
    except Exception as e:  # noqa: BLE001
        return {"title": "", "summary": "", "date": "", "category": "", "error": str(e)[:80]}
    pick = lambda pat: (m.group(1) if (m := re.search(pat, h, re.S)) else "")
    title = pick(r'<meta property="og:title" content="([^"]*)"') or pick(r"<title>([^<]*)")
    title = re.sub(r"\s*[|/\\-]\s*(Claude by Anthropic|Anthropic|Claude|claude\.dev Blog)\s*$", "", html.unescape(title)).strip()
    desc = html.unescape(pick(r'<meta name="description" content="([^"]*)"') or pick(r'<meta property="og:description" content="([^"]*)"'))
    date = pick(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})')
    if not date:
        m = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (20\d\d)", h)
        if m:
            date = dt.datetime.strptime(" ".join(m.groups()), "%B %d %Y").strftime("%Y-%m-%d")
    cat = next((c for c in CATEGORIES if c in h), "")
    return {"title": title, "summary": desc[:300], "date": date, "category": cat}


def item(url, feed, m):
    return {"url": url, "feed": feed, "seen": dt.date.today().isoformat(), **m,
            "status": "new", "topic": None, "priority": None, "lesson": None, "reason": ""}


def scan(domain=None):
    targets = [domain] if domain else list(feeds())
    for d in targets:
        db = load(d)
        known = {i["url"].rstrip("/") for i in db["items"]}
        found = []
        for f in feeds().get(d, []):
            try:
                xml = get(f["sitemap"])
            except Exception as e:  # noqa: BLE001
                print(f"⚠️ [{d}] 讀不到 {f['sitemap']}：{e}")
                continue
            for loc in re.findall(r"<loc>([^<]+)</loc>", xml):
                if re.match(f["match"], loc) and loc.rstrip("/") not in known:
                    found.append((f["name"], loc))
                    known.add(loc.rstrip("/"))
        with cf.ThreadPoolExecutor(max_workers=8) as ex:
            metas = list(ex.map(lambda x: meta(x[1]), found))
        db["items"] += [item(u, fn, m) for (fn, u), m in zip(found, metas)]
        db["updated"] = dt.date.today().isoformat()
        save(d, db)
        print(f"## {d}：新文章 {len(found)} 篇")
        for (fn, u), m in zip(found, metas):
            print(f"- [{d}] {m.get('date', '')} {m.get('title') or u}  {u}")


def add(domain, url):
    if domain not in domains():
        sys.exit(f"沒有這個領域：{domain}（先在 data/domains.json 加上）")
    db = load(domain)
    if any(i["url"].rstrip("/") == url.rstrip("/") for i in db["items"]):
        sys.exit("已經在清單裡了")
    db["items"].append(item(url, "manual", meta(url)))
    save(domain, db)
    print("已加入：", db["items"][-1].get("title") or url)


def show_new(domain=None):
    for d in ([domain] if domain else domains()):
        for i in load(d)["items"]:
            if i["status"] == "new":
                print(f"{d}\t{i.get('date', '')}\t{i['feed']}\t{i.get('category', '')}\t{i.get('title', '')}\t{i['url']}")


def stats(domain=None):
    for d in ([domain] if domain else domains()):
        c = Counter(i["status"] for i in load(d)["items"])
        print(d, dict(c), "共", sum(c.values()))


def check():
    """全站一致性檢查：有問題就以非 0 結束。"""
    errs, shorts = [], {}
    for d in domains():
        dom = json.loads((DATA / "domains" / f"{d}.json").read_text(encoding="utf-8"))
        if dom["id"] != d:
            errs.append(f"{d}.json 的 id 是 {dom['id']}")
        tids = [t["id"] for t in dom["topics"]]
        errs += [f"[{d}] 主題 id 重複：{x}" for x, n in Counter(tids).items() if n > 1]
        lids = []
        for t in dom["topics"]:
            for l in t.get("lessons", []):
                lids.append(l["id"])
                s = l.get("short")
                if not s:
                    errs.append(f"[{d}] 單元 {l['id']} 沒有中文短名")
                elif s in shorts:
                    errs.append(f"短名「{s}」重複：{shorts[s]} 與 {d}/{l['id']}（短名全站唯一）")
                else:
                    shorts[s] = f"{d}/{l['id']}"
                if l.get("status") == "learned" and not (l.get("learnedAt") and l.get("note")):
                    errs.append(f"[{d}] {l['id']} 標成已學完，但缺 learnedAt 或 note")
        errs += [f"[{d}] 單元 id 重複：{x}" for x, n in Counter(lids).items() if n > 1]
        for i in load(d)["items"]:
            if i.get("lesson") and i["lesson"] not in lids:
                errs.append(f"[{d}] 來源指到不存在的單元：{i['lesson']}")
            if i.get("topic") and i["topic"] not in tids:
                errs.append(f"[{d}] 來源指到不存在的主題：{i['topic']}（{i.get('title', '')[:30]}）")
    print("\n".join(errs) if errs else "✓ 資料一致")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0] if a else "stats"
    if cmd == "add" and len(a) == 3:
        add(a[1], a[2])
    elif cmd in ("scan", "new", "stats"):
        {"scan": scan, "new": show_new, "stats": stats}[cmd](a[1] if len(a) > 1 else None)
    elif cmd == "check":
        check()
    else:
        print(__doc__)
