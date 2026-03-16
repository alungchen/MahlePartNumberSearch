# 上傳 GitHub 與部署說明

## 一、上傳 GitHub

### 1. 安裝 Git（若尚未安裝）

- 下載：https://git-scm.com/download/win
- 安裝後重開終端機

### 2. 初始化並推送到 GitHub

在專案目錄 `MahlePartNumberSearch` 執行：

```bash
# 初始化
git init

# 新增遠端（請改成你的 GitHub 帳號與倉庫名稱）
git remote add origin https://github.com/你的帳號/MahlePartNumberSearch.git

# 加入所有檔案（.gitignore 已排除 runs/、__pycache__ 等）
git add .
git commit -m "Initial commit: Mahle 批次查詢網頁版"

# 推送
git push -u origin main
```

若 GitHub 倉庫使用 `master` 分支，請改用：
```bash
git branch -M master
git push -u origin master
```

### 3. 建立 GitHub 倉庫（若尚未建立）

1. 登入 https://github.com
2. 點「New repository」
3. 倉庫名稱：`MahlePartNumberSearch`（或自訂）
4. 可選 Public
5. **不要**勾選 Initialize with README（本地已有專案）
6. 建立後，依畫面指示設定 remote 與 push

---

## 二、Cloudflare 部署說明（重要限制）

### 目前專案無法直接部署到 Cloudflare

本專案使用：

- **Python** FastAPI 後端
- **Playwright**（需 Chromium 瀏覽器）
- **背景執行緒**、**本機檔案儲存**（`runs/`）

Cloudflare 的產品限制如下：

| 產品 | 說明 | 是否適用 |
|------|------|----------|
| Cloudflare Pages | 靜態網站、部分 Serverless | 否（無法跑 Python 後端） |
| Cloudflare Workers | 僅支援 JavaScript/TypeScript | 否 |
| Cloudflare Browser Rendering | 有 Playwright，但為 **Node.js** 版本 | 否（本專案為 Python） |

**結論**：現有 Python + Playwright 架構無法在 Cloudflare 上執行。

### 替代部署方案（支援 Python + Playwright）

以下平台可部署本專案：

| 平台 | 說明 | 備註 |
|------|------|------|
| **Railway** | 支援 Docker、Python、背景工作 | 有免費額度 |
| **Render** | 支援 Python Web Service | 免費方案有冷啟動 |
| **Fly.io** | 支援 Docker、持久化磁碟 | 適合長時間任務 |
| **Google Cloud Run** | 容器化部署 | 用量計費 |
| **VPS / 雲端主機** | 自行安裝 Python、Chromium | 最彈性 |

### Cloudflare Workers 版本（已提供）

專案內已包含 **Cloudflare 可部署版本**，位於 `cloudflare-deploy/` 目錄：

- **TypeScript + @cloudflare/playwright** 重寫
- 使用 **R2** 存放檔案、**KV** 存任務狀態、**Queue** 背景執行批次
- 需 **Cloudflare Workers Paid** 方案（Browser Rendering + 較長執行時間）

部署步驟請參考：**[cloudflare-deploy/README.md](cloudflare-deploy/README.md)**

---

## 三、若選擇 Railway 快速部署（建議）

1. 在專案根目錄新增 `Dockerfile`（需建立）
2. 連接 GitHub 倉庫到 Railway
3. Railway 會自動 build 與 deploy

若需要，我可以幫你撰寫 `Dockerfile` 與 Railway 設定檔（`railway.json`）。
