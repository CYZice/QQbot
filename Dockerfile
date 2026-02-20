# ==========================================
# 第一阶段：构建环境 (Builder)
# ==========================================
# 必须在这里加上 "AS builder"
FROM python:3.11-slim AS builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖到临时目录
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# 拷贝源代码
COPY . .

# ==========================================
# 第二阶段：运行环境 (Runtime - Distroless)
# ==========================================
FROM gcr.io/distroless/python3-debian12:latest

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai \
    PYTHONPATH=/usr/local/lib/python3.11/site-packages

WORKDIR /app

# 1. 从名为 builder 的阶段拷贝库文件
COPY --from=builder /install /usr/local

# 2. 【关键修正】拷贝代码，并显式更改所有者为 65532 (nonroot 用户)
# 这样 ncatbot 才有权在 /app 下创建 logs 文件夹
COPY --from=builder --chown=65532:65532 /app /app

# 3. 切换到非 root 用户
USER 65532

# 4. 启动
ENTRYPOINT ["python3", "main.py"]
