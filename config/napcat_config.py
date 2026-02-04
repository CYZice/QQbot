# NapCat WebSocket 配置
# 注意：这些是 OneBot 协议的端口，不是 WebUI 端口（WebUI 默认是 6099）
# 你需要在 NapCat WebUI (http://127.0.0.1:6099/webui/) 中配置并启用 WebSocket 服务端

# WebSocket 服务端地址（正向 WS）
# 默认端口是 3001，如果你在 WebUI 中修改了端口，请在这里同步修改
NAPCAT_WS_URL = "ws://127.0.0.1:3001"

# HTTP API 地址（可选，用于某些 HTTP 接口调用）
# 默认端口是 3000
NAPCAT_HTTP_URL = "http://127.0.0.1:3000"
