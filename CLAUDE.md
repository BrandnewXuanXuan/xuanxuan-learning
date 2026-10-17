# 軒軒的學習網頁：技術規範

公開的靜態 PWA，由 GitHub Pages 發佈：`https://brandnewxuanxuan.github.io/xuanxuan-learning/`。
本檔只放技術規範；色票、字體、元件與可視化教學規範在 [DESIGN.md](DESIGN.md)，做任何頁面前都要先讀。學習流程與各領域進度在使用者的 Obsidian 專案筆記，不寫在這裡。

## 隱私（硬規則）

- repo 與網站完全公開，git 歷史刪不掉。只放通用教材：不得出現金鑰、token、帳號、Email、本機路徑、Vault 筆記內容、人名、命盤或任何個人生活細節。
- 外部文章用自己的話重新解釋並附原文連結，不整篇翻譯、不大段引用。
- 每次 commit 前執行 `./check-privacy.sh`，有命中就停下處理，不得略過。
- 發佈（commit + push）只在使用者明確說「發佈」後進行。

## 結構

```
index.html              殼頁：首頁、領域、主題、學習軌跡（hash 路由 #/ #/d/<領域> #/t/<領域>/<主題> #/log）
assets/style.css        全站樣式與色彩 token（只有淺色，見 DESIGN.md）
assets/app.js           讀 data/catalog.json 產生殼頁所有畫面
assets/lesson.js        單元頁共用：註冊 service worker
assets/iso.js           單元頁共用：等角立體方塊等繪圖工具（window.Iso）
assets/icons.svg        全站 icon（SVG symbol，新主題要在這裡畫新 icon）
data/catalog.json       唯一資料來源：領域 → 主題 → 單元，含狀態
lessons/<領域>/<單元>.html  單元頁，獨立完整 HTML，互動腳本寫在頁內
sw.js                   service worker，network-first，離線時用快取
manifest.webmanifest    PWA 設定；icons/ 放圖示（make_icons.py 產生）
```

## catalog.json

- 領域：`id`、`title`、`summary`、`topics[]`。
- 主題：`id`、`title`、`summary`、`icon`、`color`（DESIGN.md 的主題色 token）、`lessons[]`。
- 單元：`id`、`short`（中文短名，例「帳單」）、`title`、`summary`、`file`、`status`、`added`（YYYY-MM-DD）、`learnedAt`、`note`、`sources[{title,url}]`。
- `status` 只用三個值：`planned`（規劃中，可無 file）、`ready`（可學）、`learned`（已學完）。
- 改成 `learned` 的條件：使用者已完成回顧，且 Obsidian 知識筆記已寫好；同時填 `learnedAt` 與 `note`（筆記名稱，只寫名稱）。
- 主題狀態由單元推導，不另存。

## 新增

- 新領域：在 `domains` 加一筆（含領域 icon）；首頁自動出現。
- 新單元：複製既有單元頁的骨架（header、數字段落標籤、頁尾），寫好後在 catalog 對應主題加一筆。同一主題的新單元一律放進原主題，不因時間另開。
- 新主題：主題清單不是固定的。新內容不屬於任何既有主題時，新建主題（畫一個新 icon、接著分配主題色），不硬塞進不合的主題，也不因為沒有位置而捨棄。所有領域都適用。
- 段落用 `<section id="s1">`，標題前顯示純數字標籤（不用 `§` 等難打的符號）。每個單元有一個好記的中文短名（例：「帳單」），使用者會說「帳單 3」來指定位置。

## 單元頁

- 設計與可視化規範全部在 DESIGN.md，這裡不重複。
- 不引入框架、不需建置；外部資源只用 Google Fonts，必要的腳本只用固定版本的 CDN。

## 快取與更新

- `sw.js` 採 network-first，連線時永遠拿最新版；改了殼頁檔案清單時把 `VERSION` 加一。
- 所有路徑用相對路徑（網站在子路徑 `/xuanxuan-learning/` 下）。

## 本機預覽

```bash
python3 -m http.server 8765 --directory ~/Desktop/Coding/xuanxuan-learning
```
