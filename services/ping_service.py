# services/ping_service.py

from typing import List, Callable
from batch_ping import batch_ping
from models.ping_result import PingResult
from config.nodes import NodesConfig
import time

class PingService:
    def __init__(self, ips: List[str]):
        """
        初始化 PingService
        
        Args:
            ips: 要测试的IP地址列表
        """
        self.ips = ips
        # 根据IP列表长度动态设置chunk_size
        self.chunk_size = min(len(ips), 256)

    def _create_callback(self, node_name: str, results: List[PingResult]) -> Callable:
        """创建回调函数"""
        def callback(message: dict):
            try:
                result = PingResult(
                    ip=message["ip"],
                    node_name=node_name,
                    delay=message["result"],
                    address=message.get("address", "未知")
                )
                results.append(result)
                print(f"测试结果: IP={result.ip}, "
                      f"延迟={result.delay}ms, "
                      f"地址={result.address}")
            except Exception as e:
                print(f"处理结果时出错: {e}")
                print(f"原始消息: {message}")
        return callback

    def test_node(self, node_id: str, node_name: str) -> List[PingResult]:
        """
        使用指定节点测试所有IP
        
        Args:
            node_id: 节点ID
            node_name: 节点名称
            
        Returns:
            List[PingResult]: 测试结果列表
        """
        results = []
        callback = self._create_callback(node_name, results)

        # 将IP列表分成大小为chunk_size的批次
        for i in range(0, len(self.ips), self.chunk_size):
            chunk = self.ips[i:i + self.chunk_size]
            ips_str = "\r\n".join(chunk)
            
            print(f"\n正在使用节点 {node_name} 测试 {len(chunk)} 个IP...")
            print(f"IP列表: {', '.join(chunk)}")
            
            try:
                batch_ping(ips_str, node_id, callback)
                print(f"\n该批次测试完成")
            except Exception as e:
                print(f"测试出错: {e}")
                continue
            
            time.sleep(1)  # 避免请求过快

        return sorted(results, key=lambda x: x.delay_float)

    def test_all_nodes(self):
        """
        使用所有节点依次测试IP列表
        
        Returns:
            Dict[str, List[PingResult]]: 按节点名称组织的测试结果
        """
        all_results = {}
        all_nodes = NodesConfig.get_all_nodes()
        total_nodes = len(all_nodes)

        print(f"\n开始测试 {len(self.ips)} 个IP")
        print(f"每批测试IP数量: {self.chunk_size}")
        print(f"总节点数量: {total_nodes}")

        for index, (node_id, node_name) in enumerate(all_nodes, 1):
            print(f"\n[{index}/{total_nodes}] 使用节点: {node_name}")
            
            try:
                results = self.test_node(node_id, node_name)
                all_results[node_name] = results
                
                # 显示当前节点的测试结果
                if results:
                    print(f"\n节点 {node_name} 测试结果:")
                    top_n = min(10, len(results))
                    print(f"延迟最低的 {top_n} 个IP:")
                    for i, result in enumerate(results[:top_n], 1):
                        print(f"{i}. IP={result.ip}: {result.delay}ms ({result.address})")
                
                print("=" * 50)
                time.sleep(2)  # 节点切换间隔
                
            except Exception as e:
                print(f"节点 {node_name} 测试失败: {e}")
                print("=" * 50)
                continue

        return all_results
