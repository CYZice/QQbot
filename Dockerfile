# ... (前面的 builder 阶段保持不变) ...

# ==========================================
# 第二阶段：运行环境 (Runtime - Distroless)
# ==========================================
FROM gcr.io/distroless/python3-debian12:latest

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai \
    PYTHONPATH=/usr/local/lib/python3.11/site-packages

WORKDIR /app

# 1. 拷贝库文件（保持 root 所有权即可，因为只需读取）
COPY --from=builder /install /usr/local
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo

# 2. 【关键修正】拷贝代码，并显式更改所有者为 65532 (nonroot 用户)
# --chown=65532:65532 是 Distroless 方案中处理权限的标准做法
COPY --from=builder --chown=65532:65532 /app /app

# 3. 切换到非 root 用户
USER 65532

# 4. 启动
ENTRYPOINT ["python3", "main.py"]
