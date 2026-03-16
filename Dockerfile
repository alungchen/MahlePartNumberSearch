# Mahle 批次查詢 - Render 部署用
# 使用 Playwright 官方 Python 映像（內含 Chromium）
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# 安裝 Python 相依
COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

# Chromium 已在映像內，無需 playwright install

# 複製專案
COPY . .

# Render 會設定 PORT 環境變數
ENV HOST=0.0.0.0
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "python -c \"import os; exec(open('web_app.py').read().replace('127.0.0.1', os.environ.get('HOST', '0.0.0.0')).replace('8000', str(int(os.environ.get('PORT', 8000)))))\""]
