import re
import json
import hashlib
import asyncio
import websockets
import requests
from typing import Callable, Union, List
from datetime import datetime

class BatchPingError(Exception):
    """批量ping操作的自定义异常"""
    pass

class BatchPing:
    """批量Ping测试服务类"""
    
    def __init__(self, timeout: int = 10):
        """
        初始化BatchPing服务

        Args:
            timeout (int): 请求超时时间（秒）
        """
        self.base_url = 'https://www.itdog.cn/batch_ping/'
        self.headers = {
            'Referer': self.base_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        }
        self.token_suffix = "token_20230313000136kwyktxb0tgspm00yo5"
        self.timeout = timeout

    def _prepare_request_data(self, host: str, node_id: str, cidr_filter: bool = True, gateway: str = "last") -> dict:
        """
        准备POST请求数据

        Args:
            host: IP地址列表（换行符分隔的字符串）
            node_id: 节点ID
            cidr_filter: 是否过滤CIDR格式
            gateway: 网关地址位置（"last"或"first"）

        Returns:
            dict: 请求数据字典
        """
        return {
            'host': host,
            'node_id': node_id,
            'cidr_filter': 'true' if cidr_filter else 'false',
            'gateway': gateway
        }

    def _parse_response(self, response_text: str) -> tuple:
        """
        解析响应内容，获取WebSocket URL和任务ID

        Args:
            response_text: 响应文本

        Returns:
            tuple: (websocket_url, task_id)

        Raises:
            BatchPingError: 解析失败时抛出
        """
        # 检查错误信息
        error_pattern = re.compile(r"""err_tip_more\("<li>(.*)</li>"\)""")
        if error_match := error_pattern.search(response_text):
            raise BatchPingError(error_match.group(1))

        # 获取WebSocket URL和任务ID
        try:
            wss_pattern = re.compile(r"""var wss_url='(.*)';""")
            task_pattern = re.compile(r"""var task_id='(.*)';""")
            
            wss_url = wss_pattern.search(response_text).group(1)
            task_id = task_pattern.search(response_text).group(1)
            
            return wss_url, task_id
        except (AttributeError, IndexError) as e:
            raise BatchPingError(f"解析响应失败: {str(e)}")

    def _generate_task_token(self, task_id: str) -> str:
        """
        生成任务token

        Args:
            task_id: 任务ID

        Returns:
            str: 生成的token
        """
        full_token = task_id + self.token_suffix
        return hashlib.md5(full_token.encode()).hexdigest()[8:-8]

    async def _handle_websocket_communication(self, websocket, task_id: str, 
                                           task_token: str, callback: Callable):
        """
        处理WebSocket通信

        Args:
            websocket: WebSocket连接对象
            task_id: 任务ID
            task_token: 任务token
            callback: 结果回调函数
        """
        message_data = json.dumps({"task_id": task_id, "task_token": task_token})
        await websocket.send(message_data)

        message = {}
        while not ("type" in message and message['type'] == "finished"):
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=self.timeout)
                try:
                    message = json.loads(message)
                    if not ("type" in message and message['type'] == "finished"):
                        callback(message)
                except json.JSONDecodeError:
                    print(f"警告: 收到无效的JSON消息: {message}")
                    break
            except asyncio.TimeoutError:
                await websocket.send(message_data)
            except Exception as e:
                print(f"WebSocket通信错误: {str(e)}")
                break

    async def _run_websocket_client(self, wss_url: str, task_id: str, 
                                  task_token: str, callback: Callable):
        """
        运行WebSocket客户端

        Args:
            wss_url: WebSocket服务器URL
            task_id: 任务ID
            task_token: 任务token
            callback: 结果回调函数
        """
        try:
            async with websockets.connect(wss_url) as websocket:
                await self._handle_websocket_communication(
                    websocket, task_id, task_token, callback
                )
        except Exception as e:
            raise BatchPingError(f"WebSocket连接失败: {str(e)}")

    def execute(self, host: str, node_id: str, callback: Callable, 
                cidr_filter: bool = True, gateway: str = "last"):
        """
        执行批量ping测试

        Args:
            host: IP地址列表（换行符分隔的字符串）
            node_id: 节点ID
            callback: 结果回调函数
            cidr_filter: 是否过滤CIDR格式
            gateway: 网关地址位置

        Raises:
            BatchPingError: 测试过程中的错误
        """
        try:
            # 准备并发送POST请求
            data = self._prepare_request_data(host, node_id, cidr_filter, gateway)
            response = requests.post(self.base_url, headers=self.headers, data=data)
            response.raise_for_status()

            # 解析响应获取必要信息
            wss_url, task_id = self._parse_response(response.text)
            task_token = self._generate_task_token(task_id)

            # 执行WebSocket通信
            asyncio.run(self._run_websocket_client(wss_url, task_id, task_token, callback))

        except requests.RequestException as e:
            raise BatchPingError(f"HTTP请求失败: {str(e)}")
        except Exception as e:
            raise BatchPingError(f"执行过程发生错误: {str(e)}")

def batch_ping(host: Union[str, List[str]], node_id: str, callback: Callable, 
               cidr_filter: bool = True, gateway: str = "last", timeout: int = 10):
    """
    批量Ping测试的便捷函数

    Args:
        host: IP地址或IP地址列表
        node_id: 节点ID
        callback: 结果回调函数
        cidr_filter: 是否过滤CIDR格式
        gateway: 网关地址位置
        timeout: 超时时间（秒）

    Raises:
        ValueError: 参数错误
        BatchPingError: 测试过程中的错误
    """
    # 参数验证
    if not host or not node_id or not callback:
        raise ValueError("host、node_id和callback参数都不能为空")

    # 处理输入的IP地址格式
    if isinstance(host, list):
        host = "\r\n".join(host)
    elif not isinstance(host, str):
        raise ValueError("host参数必须是字符串或字符串列表")

    # 创建BatchPing实例并执行测试
    batch_ping_service = BatchPing(timeout=timeout)
    batch_ping_service.execute(host, node_id, callback, cidr_filter, gateway)

