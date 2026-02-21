# ==========================================
# 第一阶段：构建阶段 (Builder)
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /build

# 1. 升级构建工具
RUN pip install --no-cache-dir --upgrade pip setuptools "wheel>=0.46.2" "jaraco.context>=6.1.0"

# 2. 安装业务依赖到指定前缀目录
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ==========================================
# 第二阶段：运行阶段 (Final)
# ==========================================
FROM python:3.11-slim

# 1. 环境变量
ENV TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # 确保系统优先查找我们拷贝过来的包
    PATH="/usr/local/bin:$PATH"

WORKDIR /app

# 2. 【核心修复：消除漏洞的关键】
# 必须在 Final 阶段直接升级系统自带的这两个包。
# 这会产生一个新层，覆盖掉基础镜像中 /usr/local/lib/python3.11/site-packages/ 下的旧版本。
# 这样 Trivy 扫描时，旧版本的 METADATA 就会被新版本替换。
RUN pip install --no-cache-dir --upgrade "wheel>=0.46.2" "jaraco.context>=6.1.0"

# 3. 从构建阶段拷贝业务依赖
# --prefix=/install 配合这里的拷贝，能保证路径严谨对齐
COPY --from=builder /install /usr/local

# 4. 拷贝项目文件
# 默认 Root 权限，无需 chmod，支持程序后续在 /app 下创建任何文件夹
COPY . .

# 5. 启动命令
CMD ["python", "main.py"]
