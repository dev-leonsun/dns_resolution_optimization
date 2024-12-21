from typing import Dict, List
from models.ping_result import PingResult
import json
from datetime import datetime

class ResultService:
    @staticmethod
    def save_results(all_results: Dict[str, List[PingResult]], filename: str = None):
        if filename is None:
            filename = f"ping_results_all_nodes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # 转换结果为可序列化的格式
        serializable_results = {
            node_name: [vars(result) for result in results]
            for node_name, results in all_results.items()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {filename}")

    @staticmethod
    def print_summary(all_results: Dict[str, List[PingResult]]):
        print("\n测试总结报告")
        print("=" * 50)
        print(f"测试节点数量: {len(all_results)}")
        
        print("\n各节点下延迟最低的IP:")
        for node_name, results in all_results.items():
            if results:
                best_result = min(results, key=lambda x: x.delay_float)
                print(f"\n{node_name}:")
                print(f"最佳IP: {best_result.ip}")
                print(f"延迟: {best_result.delay}ms")
                print(f"地址: {best_result.address}")