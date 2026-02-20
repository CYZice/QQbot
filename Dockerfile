FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量：时区、Python 输出不缓冲、不生成 pyc
ENV TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 安装基础依赖（如果你的插件需要编译 C 扩展，才需要安装 build-essential）
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# 1. 先拷贝依赖文件并安装（利用 Docker 缓存机制）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. 拷贝项目所有文件
COPY . .

# 启动命令
CMD ["python", "main.py"]
