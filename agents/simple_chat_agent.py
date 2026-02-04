"""简单的 LangGraph 聊天 Agent"""
from typing import Optional
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from loguru import logger


class SimpleChatAgent:
    """简单的聊天 Agent，使用 LangGraph 管理对话状态"""

    def __init__(self, api_key: str, base_url: str, model: str = "deepseek-v3.2"):
        """
        初始化 Agent

        Args:
            api_key: OpenAI API Key
            base_url: API Base URL
            model: 模型名称
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

        # 初始化 LLM
        self.llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=0.7
        )

        # 初始化记忆存储
        self.memory = MemorySaver()

        # 构建 LangGraph
        self.graph = self._build_graph()

        logger.info(f"SimpleChatAgent 初始化完成，模型: {model}")

    def _build_graph(self):
        """构建 LangGraph 工作流"""
        # 创建状态图
        graph_builder = StateGraph(MessagesState)

        # 添加聊天节点
        graph_builder.add_node("chatbot", self._chatbot_node)

        # 设置边
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)

        # 编译图，启用记忆功能
        graph = graph_builder.compile(checkpointer=self.memory)

        logger.debug("LangGraph 工作流构建完成")
        return graph

    def _chatbot_node(self, state: MessagesState):
        """
        聊天节点 - 调用 LLM 生成回复

        Args:
            state: 当前对话状态

        Returns:
            更新后的状态
        """
        try:
            # 调用 LLM
            response = self.llm.invoke(state["messages"])
            return {"messages": [response]}
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            # 返回错误消息
            return {"messages": [{"role": "assistant", "content": "抱歉，我遇到了一些问题，请稍后再试。"}]}

    async def process_message(self, user_message: str, thread_id: str) -> Optional[str]:
        """
        处理用户消息并生成回复

        Args:
            user_message: 用户消息
            thread_id: 线程 ID（用于区分不同的对话）

        Returns:
            Agent 的回复
        """
        try:
            # 配置 thread_id 以启用记忆功能
            config = {"configurable": {"thread_id": thread_id}}

            # 调用 graph
            result = self.graph.invoke(
                {"messages": [{"role": "user", "content": user_message}]},
                config
            )

            # 提取回复
            if result and "messages" in result and len(result["messages"]) > 0:
                reply = result["messages"][-1].content
                logger.debug(f"Agent 回复: {reply[:100]}")
                return reply
            else:
                logger.warning("Agent 未返回有效回复")
                return None

        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            return "抱歉，我遇到了一些问题，请稍后再试。"

    def get_conversation_state(self, thread_id: str):
        """
        获取对话状态（用于调试）

        Args:
            thread_id: 线程 ID

        Returns:
            对话状态快照
        """
        try:
            config = {"configurable": {"thread_id": thread_id}}
            snapshot = self.graph.get_state(config)
            return snapshot
        except Exception as e:
            logger.error(f"获取对话状态失败: {e}")
            return None
