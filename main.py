from typing import List
from services.ping_service import PingService
from services.result_service import ResultService

def main(ips: List[str]):
    # 创建服务实例
    ping_service = PingService(ips)
    
    # 执行测试
    all_results = ping_service.test_all_nodes()
    
    # 保存和显示结果
    result_service = ResultService()
    result_service.save_results(all_results)
    result_service.print_summary(all_results)

if __name__ == '__main__':
    # 测试IP列表
    test_ips = [
        "8.8.8.8",
        "8.8.4.4",
        "1.1.1.1",
        "1.0.0.1",
    ]
    
    main(test_ips)