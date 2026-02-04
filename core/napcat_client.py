"""NapCat WebSocket 客户端"""
import json
import asyncio
import websockets
from typing import Optional, Dict, Any, AsyncIterator
from loguru import logger
from config.napcat_config import NAPCAT_WS_URL


class NapCatClient:
    """NapCat WebSocket 客户端"""

    def __init__(self, ws_url: str = NAPCAT_WS_URL):
        """
        初始化 NapCat 客户端

        Args:
            ws_url: WebSocket 服务器地址
        """
        self.ws_url = ws_url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.bot_qq: Optional[int] = None
        self.connected = False

    async def connect(self) -> bool:
        """
        连接到 NapCat WebSocket 服务器

        Returns:
            True 如果连接成功
        """
        try:
            logger.info(f"正在连接到 NapCat WebSocket: {self.ws_url}")
            self.websocket = await websockets.connect(self.ws_url)
            self.connected = True
            logger.success("WebSocket 连接成功")

            # 获取 bot 的 QQ 号
            await self._fetch_bot_qq()

            return True
        except Exception as e:
            logger.error(f"WebSocket 连接失败: {e}")
            self.connected = False
            return False

    async def _fetch_bot_qq(self):
        """获取 bot 的 QQ 号"""
        try:
            login_info = await self.call_api("get_login_info")
            if login_info and "user_id" in login_info:
                self.bot_qq = login_info["user_id"]
                logger.info(f"Bot QQ 号: {self.bot_qq}")
            else:
                logger.warning("无法获取 Bot QQ 号")
        except Exception as e:
            logger.error(f"获取 Bot QQ 号失败: {e}")

    async def call_api(self, action: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        调用 NapCat API

        Args:
            action: API 动作名称
            params: API 参数

        Returns:
            API 响应数据
        """
        if not self.websocket:
            logger.error("WebSocket 未连接")
            return None

        try:
            # 构造请求
            request = {
                "action": action,
                "params": params or {},
                "echo": f"{action}_{asyncio.get_event_loop().time()}"
            }

            # 发送请求
            await self.websocket.send(json.dumps(request))
            logger.debug(f"发送 API 请求: {action}")

            # 等待响应
            # 注意：这里简化处理，实际应该根据 echo 匹配响应
            response_text = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            response = json.loads(response_text)

            # 检查是否是 API 响应（包含 echo 字段）
            if "echo" in response and response.get("status") == "ok":
                logger.debug(f"API 响应成功: {action}")
                return response.get("data")
            elif "echo" in response:
                logger.error(f"API 响应失败: {response}")
                return None

            # 如果不是 API 响应，可能是事件消息，需要继续等待
            # 这里简化处理，实际应该用队列管理
            return None

        except asyncio.TimeoutError:
            logger.error(f"API 调用超时: {action}")
            return None
        except Exception as e:
            logger.error(f"API 调用失败: {action}, 错误: {e}")
            return None

    async def send_group_msg(self, group_id: int, message: str) -> bool:
        """
        发送群消息

        Args:
            group_id: 群号
            message: 消息内容

        Returns:
            True 如果发送成功
        """
        try:
            result = await self.call_api("send_group_msg", {
                "group_id": group_id,
                "message": message
            })

            if result:
                logger.info(f"消息发送成功 -> 群 {group_id}: {message[:50]}")
                return True
            else:
                logger.error(f"消息发送失败 -> 群 {group_id}")
                return False

        except Exception as e:
            logger.error(f"发送群消息异常: {e}")
            return False

    async def listen(self) -> AsyncIterator[Dict[str, Any]]:
        """
        监听消息事件

        Yields:
            消息事件数据
        """
        if not self.websocket:
            logger.error("WebSocket 未连接")
            return

        logger.info("开始监听消息...")

        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)

                    # 过滤掉 API 响应，只处理事件消息
                    if "post_type" in data:
                        yield data

                except json.JSONDecodeError as e:
                    logger.error(f"JSON 解析失败: {e}")
                except Exception as e:
                    logger.error(f"处理消息异常: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket 连接已关闭")
            self.connected = False
        except Exception as e:
            logger.error(f"监听消息异常: {e}")
            self.connected = False

    async def close(self):
        """关闭 WebSocket 连接"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("WebSocket 连接已关闭")

    async def reconnect(self, max_retries: int = 5, delay: int = 5) -> bool:
        """
        重连 WebSocket

        Args:
            max_retries: 最大重试次数
            delay: 重试间隔（秒）

        Returns:
            True 如果重连成功
        """
        for i in range(max_retries):
            logger.info(f"尝试重连 ({i + 1}/{max_retries})...")
            if await self.connect():
                return True
            await asyncio.sleep(delay)

        logger.error("重连失败")
        return False
