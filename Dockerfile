# ==========================================
# 第一阶段：构建阶段 (Builder)
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /build

# 1. 升级构建工具，确保安装过程安全
RUN pip install --no-cache-dir --upgrade pip setuptools "wheel>=0.46.2" "jaraco.context>=6.1.0"

# 2. 安装依赖到临时目录
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ==========================================
# 第二阶段：运行阶段 (Final)
# ==========================================
FROM python:3.11-slim

# 1. 运行时环境变量
ENV TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # 将安装路径加入 Python 搜索路径
    PATH="/usr/local/lib/python3.11/site-packages:$PATH"

WORKDIR /app

# 2. 【核心修复步骤】
# 即使以 Root 运行，Trivy 依然会扫描基础镜像中的旧版文件。
# 在 Final 阶段直接升级这两个包，会产生一个新层覆盖掉基础镜像中的漏洞版本。
RUN pip install --no-cache-dir --upgrade "wheel>=0.46.2" "jaraco.context>=6.1.0"

# 3. 从构建阶段拷贝所有已安装的业务依赖
COPY --from=builder /install /usr/local

# 4. 拷贝项目文件
# 默认就是 Root 权限，无需额外 chmod
COPY . .

# 5. 启动命令 (默认以 Root 身份运行)
CMD ["python", "main.py"]
