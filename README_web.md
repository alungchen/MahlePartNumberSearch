# Mahle 批次查詢 Web 版

## 1) 安裝套件

```bash
pip install -r requirements-web.txt
playwright install chromium
```

## 2) 啟動

```bash
python web_app.py
```

開啟瀏覽器進入：

- [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 3) 使用

1. 上傳 `Input.xlsx`（Sheet1 需有 `Search_No` 欄位）
   - 可先下載頁面上的「上傳範例檔」
2. 點選「開始執行」
3. 觀察進度與任務狀態
4. 可在執行中按「取消任務」
5. 任務完成（或取消）後按「下載」

## 4) 任務檔案位置

- 每次任務會建立於 `runs/<task_id>/`
- 輸入檔：`Input.xlsx`
- 輸出檔：`Output.xlsx`
- 錯誤截圖/HTML 與 log 也會在該任務目錄產生
