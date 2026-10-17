# 軒軒自修室：技術規範

公開的靜態 PWA，由 GitHub Pages 發佈：`https://brandnewxuanxuan.github.io/xuanxuan-learning/`。
本檔只放技術規範；色票、字體、元件與可視化教學規範在 [DESIGN.md](DESIGN.md)，做任何頁面前都要先讀。學習流程與各領域進度在使用者的 Obsidian 專案筆記，不寫在這裡。

網站會有多個領域（Claude、之後的佛學、術數…），每個領域通常由不同的研究夥伴 session 負責。所以：**只動自己負責的領域的檔案**；共用檔（`assets/`、`DESIGN.md`、本檔、`data/domains.json`、`data/feeds.json`）要改時，改動範圍越小越好。

## 隱私（硬規則）

- repo 與網站完全公開，git 歷史刪不掉。只放通用教材：不得出現金鑰、token、帳號、Email、本機路徑、Vault 筆記內容、人名、命盤或任何個人生活細節。
- 外部文章用自己的話重新解釋並附原文連結，不整篇翻譯、不大段引用。
- 每次 commit 前執行 `./check-privacy.sh`（也檢查 commit 作者是 GitHub 匿名信箱），有命中就停下處理，不得略過。
- 發佈（commit + push）只在使用者明確說「發佈」後進行。

## 動手前、commit 前

1. 動手前先 `git pull --rebase`：別的領域的 session 可能剛推過。
2. commit 前跑 `./check-privacy.sh` 與 `python3 tools/sources.py check`（全站一致性；push 時 GitHub 也會再跑一次）。
3. push 被拒時先 `git pull --rebase` 再推；衝突只會出在共用檔，保留雙方的改動。

## 結構

```
index.html                  殼頁：首頁、領域、主題、學習軌跡（hash 路由 #/ #/d/<領域> #/t/<領域>/<主題> #/log）
assets/style.css            全站樣式與色彩 token（只有淺色，見 DESIGN.md）
assets/app.js               讀 data/domains.json 與各領域檔，產生殼頁所有畫面
assets/lesson.js            單元頁共用：註冊 service worker
assets/iso.js               單元頁共用：等角立體方塊等繪圖工具（window.Iso）
assets/icons.svg            全站 icon（SVG symbol）；新增時只在 </defs> 前追加，id 加領域前綴避免撞名（例：buddhism-sutra）
data/domains.json           領域清單與順序：{"domains": ["claude", ...]}
data/domains/<領域>.json     該領域的主題與單元（含狀態），一個領域一個檔
data/sources/<領域>.json     該領域的來源清單（見下方「來源清單」）
data/feeds.json             有自動追蹤的領域與它們的 sitemap；沒有 feed 的領域不用列
lessons/<領域>/<單元>.html   單元頁，獨立完整 HTML，互動腳本寫在頁內
tools/sources.py            來源清單工具與全站一致性檢查
.github/workflows/          weekly-sources（每週找新文章）、check（push 時檢查資料）
sw.js                       service worker，network-first，離線時用快取
manifest.webmanifest        PWA 設定；icons/ 放圖示（make_icons.py 產生）
```

## 領域檔 data/domains/<領域>.json

- 領域：`id`（與檔名相同）、`title`、`short`（膠囊上的短名）、`icon`、`summary`、`topics[]`。
- 主題：`id`、`title`、`summary`、`icon`、`color`（DESIGN.md 的主題色 token）、`lessons[]`。
- 單元：`id`、`short`（中文短名，例「帳單」）、`title`、`summary`、`file`、`status`、`added`（YYYY-MM-DD）、`learnedAt`、`note`、`sources[{title,url}]`。
- `status` 只用三個值：`planned`（規劃中，可無 file）、`ready`（可學）、`learned`（已學完）。
- 改成 `learned` 的條件：使用者已完成回顧，且 Obsidian 知識筆記已寫好；同時填 `learnedAt` 與 `note`（筆記名稱，只寫名稱）。
- 主題狀態由單元推導，不另存。
- id 只需在領域內唯一；**單元的中文短名必須全站唯一**（使用者用「帳單 3」指位置，不會說是哪個領域）。

## 新增

- 新領域：建 `data/domains/<id>.json`、`data/sources/<id>.json`（可先空）、`lessons/<id>/`，把 id 加進 `data/domains.json`，在 `sw.js` 的 SHELL 加上領域檔並把 `VERSION` 加一。有官方 sitemap 可追的才加進 `data/feeds.json`。Vault 那邊另建學習專案筆記（見研究夥伴角色檔）。
- 新單元：複製既有單元頁的骨架（header、數字段落標籤、頁尾），寫好後在領域檔對應主題加一筆。同一主題的新單元一律放進原主題，不因時間另開。
- 新主題：主題清單不是固定的。新內容不屬於任何既有主題時，新建主題（畫一個新 icon、接著分配主題色），不硬塞進不合的主題，也不因為沒有位置而捨棄。所有領域都適用。
- 段落用 `<section id="s1">`，標題前顯示純數字標籤（不用 `§` 等難打的符號）。

## 來源清單 data/sources/<領域>.json

- 該領域所有候選來源的唯一清單，每篇一筆：網址、標題、日期、分類、摘要、`status`、`topic`、`priority`、`lesson`、`reason`。狀態說明寫在檔內 `statuses`：`new` 待分類、`todo` 要學、`done` 已做成課、`skip` 不學、`outdated` 過時。
- 一篇來源只歸一個領域：放在「會拿它來教」的那個領域；別的領域也用到時，在自己的單元 `sources` 裡引用網址即可，不重複建清單。
- 有 feed 的領域：`tools/sources.py scan` 只抓還不在清單裡的網址，不呼叫 AI；每週一由 GitHub Actions 自動跑，有新文章就 commit 並開 issue。
- 沒有 feed 的領域（使用者想到什麼就學什麼）：用 `tools/sources.py add <領域> <網址>` 手動加入。
- 分類時只讀 `tools/sources.py new <領域>` 的輸出，不要整份讀清單。做成課之後改 `status: done` 並填 `lesson`。

## 單元頁

- 設計與可視化規範全部在 DESIGN.md，這裡不重複。
- 不引入框架、不需建置；外部資源只用 Google Fonts，必要的腳本只用固定版本的 CDN。

## 快取與更新

- `sw.js` 採 network-first，連線時永遠拿最新版；改了殼頁檔案清單（含新增領域檔）時把 `VERSION` 加一。
- 所有路徑用相對路徑（網站在子路徑 `/xuanxuan-learning/` 下）。

## 本機預覽

```bash
python3 -m http.server 8765 --directory ~/Desktop/Coding/xuanxuan-learning
```
