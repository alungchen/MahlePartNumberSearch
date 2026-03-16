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

ENV HOST=0.0.0.0
ENV PORT=8000
EXPOSE 8000

# Render 會注入 PORT，web_app.py 會讀取
CMD ["python", "web_app.py"]
