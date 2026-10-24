"""把 lessons-src/<領域>/<單元>.lesson 組成 lessons/<領域>/<單元>.html。

用法：python3 tools/build_lessons.py            # 全部重組
      python3 tools/build_lessons.py <領域>     # 只組某個領域

.lesson 格式：第一行 JSON（id, short, title, desc, topic, topicTitle, sources:[[title,url]]；可選 domain，預設為資料夾名；
可選 license:{work,url,name,licenseUrl}，原文有授權條款（例如 CC BY-NC-SA）時在頁面最下方標出處與授權）
接著用 ===CSS=== / ===BODY=== / ===JS=== 分段。BODY 裡用 {{hint N}} 產生提問提示、{{icon x}} 產生 icon。"""
import json, re, sys, html
VER = '20261025a'  # 改了 assets 就換版本號，強制瀏覽器抓新檔
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
ONLY = sys.argv[1] if len(sys.argv) > 1 else None
def build(f):
    raw = f.read_text(encoding='utf-8')
    head, rest = raw.split('\n', 1)
    m = json.loads(head)
    dom = m.get('domain') or f.parent.name
    out = ROOT / 'lessons' / dom
    out.mkdir(parents=True, exist_ok=True)
    parts = dict(re.findall(r'===(CSS|BODY|JS)===\n(.*?)(?=\n===(?:CSS|BODY|JS)===\n|\Z)', rest, re.S))
    body = parts.get('BODY', '')
    body = re.sub(r'\{\{hint (\d+)\}\}', lambda x: f'<div class="ask-hint">看不懂就回來說 <code>{m["short"]} {x.group(1)}</code></div>', body)
    body = re.sub(r'\{\{icon ([\w-]+)\}\}', lambda x: f'<svg><use href="../../assets/icons.svg?v={VER}#{x.group(1)}"/></svg>', body)
    lic = m.get('license')
    lic = (f'''\n  <p class="lic" style="margin:18px 2px 0;font-size:12.5px;line-height:1.7;color:var(--ink-3)">原文出處：<a href="{lic["url"]}" target="_blank" rel="noopener">{html.escape(lic["work"])}</a>（上方原文清單），以 <a href="{lic["licenseUrl"]}" target="_blank" rel="noopener">{html.escape(lic["name"])}</a> 授權。本頁是用自己的話改寫、並換成自己的例子，改寫內容同樣以 {html.escape(lic["name"])} 授權。</p>''' if lic else '')
    srcs = '\n'.join(f'    <li><a href="{u}" target="_blank" rel="noopener">{html.escape(t)}</a></li>' for t, u in m['sources'])
    page = f'''<!doctype html>
<html lang="zh-Hant-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(m["title"])}</title>
<meta name="description" content="{html.escape(m["desc"])}">
<meta name="theme-color" content="#f1f0eb">
<link rel="manifest" href="../../manifest.webmanifest">
<link rel="icon" href="../../icons/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="../../icons/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Huninn&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/style.css?v={VER}">
<style>
{parts.get("CSS","").strip()}
</style>
</head>
<body class="lesson">
<header class="bar"><div class="bar-in">
  <a class="back" href="../../index.html#/t/{dom}/{m["topic"]}" aria-label="回到主題"><svg class="i"><use href="../../assets/icons.svg?v={VER}#back"/></svg></a>
  <span class="bar-title">{html.escape(m["topicTitle"])}</span>
</div></header>

<main class="wrap">
{body.strip()}

  <h2>原文</h2>
  <ul class="srcs">
{srcs}
  </ul>

  <div class="foot"><svg><use href="../../assets/icons.svg?v={VER}#chat"/></svg><span>學完了，回研究夥伴說「學完{m["short"]}」。一起回顧、寫成筆記之後，這張卡才會蓋上「學完」章。</span></div>{lic}
</main>

<script src="../../assets/iso.js?v={VER}"></script>
<script src="../../assets/kit.js?v={VER}"></script>
<script>
(() => {{
{parts.get("JS","").strip()}
}})();
</script>
<script src="../../assets/lesson.js" data-root="../../"></script>
</body>
</html>
'''
    (out / f'{m["id"]}.html').write_text(page, encoding='utf-8')
    return m
files = sorted((ROOT / 'lessons-src').glob(f'{ONLY or "*"}/*.lesson'))
for f in files:
    m = build(f)
    print(f'{f.parent.name}/{m["id"]}')