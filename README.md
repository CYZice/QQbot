# QQ Bot with LangGraph Agent

基于 NapCat 和 LangGraph 的 QQ 群聊机器人，支持对话记忆和智能响应。

## 功能特性

- ✅ 基于 WebSocket 实时接收消息
- ✅ 支持 @ 唤醒和关键词唤醒
- ✅ 使用 LangGraph 管理对话状态和记忆
- ✅ 消息长度和频率限制（安全保护）
- ✅ 模块化设计，易于扩展

## 环境要求

- Python 3.8+
- NapCat（已安装并运行）

## 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

`.env` 文件已包含必要配置：
```
YUNWU_API_KEY = sk-xxx...
API_BASE_URL = https://yunwu.ai/v1
```

### 3. 配置 NapCat

1. 启动 NapCat
2. 访问 WebUI：`http://127.0.0.1:6099/webui/`
3. 在"网络配置"中添加 **WebSocket 服务端**：
   - 启用：是
   - 监听地址：`127.0.0.1`
   - 端口：`3001`
4. 保存配置并重启 NapCat

### 4. 配置 Bot 参数

编辑 `config/bot_config.py`：
```python
# 监听的群号
MONITORED_GROUPS = [1075786046]

# 唤醒关键词
WAKE_WORDS = [
    r"小助手",
    r"bot",
    r"机器人",
    r"助手"
]
```

## 运行

```bash
python main.py
```

## 使用方法

在 QQ 群中：

1. **@ 唤醒**：`@bot 你好`
2. **关键词唤醒**：`小助手，今天天气怎么样？`
3. **对话记忆**：Bot 会记住每个用户的对话历史

## 项目结构

```
QQbot/
├── config/              # 配置文件
│   ├── napcat_config.py # NapCat 连接配置
│   └── bot_config.py    # Bot 行为配置
├── core/                # 核心功能
│   ├── napcat_client.py # WebSocket 客户端
│   ├── message_filter.py# 消息过滤器
│   └── message_handler.py# 消息处理器
├── agents/              # Agent 实现
│   └── simple_chat_agent.py # LangGraph Agent
├── utils/               # 工具模块
│   ├── logger.py        # 日志工具
│   └── security.py      # 安全限制
├── logs/                # 日志目录
├── main.py              # 主程序
└── .env                 # 环境变量
```

## 安全机制

- 消息长度限制：500 字符
- 频率限制：每分钟最多 10 条消息
- 违规 3 次自动暂停服务

## 故障排查

### 1. 无法连接到 NapCat

- 检查 NapCat 是否运行
- 检查 WebSocket 端口是否为 3001
- 查看 `config/napcat_config.py` 中的地址配置

### 2. Bot 不响应消息

- 检查群号是否在 `MONITORED_GROUPS` 中
- 检查是否正确 @ 了 bot 或使用了唤醒词
- 查看日志文件 `logs/bot.log`

### 3. API 调用失败

- 检查 `.env` 中的 API Key 是否正确
- 检查网络连接

## 扩展开发

### 添加新的 Agent

1. 在 `agents/` 目录创建新的 Agent 类
2. 继承或参考 `SimpleChatAgent`
3. 在 `main.py` 中切换 Agent

### 支持多个群

在 `config/bot_config.py` 中添加群号：
```python
MONITORED_GROUPS = [1075786046, 123456789, 987654321]
```

### 添加工具调用

在 LangGraph Agent 中添加 tools，参考 LangGraph 文档。

## 参考文档

- [NapCat 文档](https://napneko.github.io/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [OneBot 11 标准](https://github.com/botuniverse/onebot-11)
