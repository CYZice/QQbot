FROM python:3.11-slim AS builder

WORKDIR /build
RUN pip install --no-cache-dir --upgrade pip setuptools "wheel>=0.46.2" "jaraco.context>=6.1.0"
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local

# ✨ 必须最后运行升级命令，确保完全覆盖旧版本
RUN pip install --no-cache-dir --upgrade "wheel>=0.46.2" "jaraco.context>=6.1.0"

COPY . .

CMD ["python", "main.py"]
