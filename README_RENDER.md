# Render 部署說明

## 前置需求

- GitHub 帳號
- Render 帳號（https://render.com 註冊免費）

## 部署步驟

### 1. 將程式上傳到 GitHub

若尚未上傳，請先將專案 push 到 GitHub（參考 `DEPLOY.md`）。

### 2. 在 Render 建立新服務

1. 登入 https://dashboard.render.com
2. 點選 **New** → **Web Service**
3. 連接你的 GitHub 倉庫（或輸入倉庫 URL）
4. 選擇此專案所在倉庫與分支（通常為 `main`）

### 3. 設定服務

| 欄位 | 值 |
|------|-----|
| **Name** | `mahle-batch-search`（或自訂） |
| **Region** | 選離你較近的區域 |
| **Branch** | `main` |
| **Runtime** | **Docker** |
| **Dockerfile Path** | `Dockerfile`（預設即可） |
| **Plan** | **Free** |

其他欄位使用預設即可，不需設定環境變數。

### 4. 部署

點選 **Create Web Service**，Render 會自動：

1. 拉取程式碼
2. 建立 Docker 映像（內含 Chromium）
3. 啟動服務

首次部署約需 5–10 分鐘。

### 5. 取得網址

完成後會得到類似：

```
https://mahle-batch-search-xxxx.onrender.com
```

開啟此網址即可使用批次查詢功能。

---

## 免費方案注意事項

- **休眠**：約 15 分鐘無存取會休眠，下次連線需約 30–60 秒喚醒
- **月時數**：每月約 750 小時，單一服務通常足夠
- **記憶體**：約 512MB，Chromium 可運行，建議一次不超過約 20 筆查詢

---

## 使用 Blueprint（選用）

若專案中已有 `render.yaml`，可在 Render Dashboard 選擇 **New** → **Blueprint**，選取倉庫後自動依 YAML 建立服務。
