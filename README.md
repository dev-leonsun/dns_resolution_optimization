# DNS Resolution Optimization Tool

这是一个基于 Python 的 DNS 解析优化工具，可以帮助您测试和分析不同 IP 地址在中国各地区节点的网络延迟情况。该工具使用多个运营商（电信、联通、移动）的测试节点，提供全面的网络质量评估。

## 功能特点

- 支持批量 IP 地址测试
- 覆盖中国三大运营商的多个测试节点
- 自动分批处理大量 IP 地址
- 实时显示测试进度和结果
- 支持延迟排序和结果分析
- 完整的错误处理机制

## 系统要求

- Python 3.7+
- pip 包管理工具

## 安装依赖

```bash
pip install -r requirements.txt
快速开始
克隆仓库：
bash
git clone https://github.com/dev-leonsun/dns_resolution_optimization.git
cd dns_resolution_optimization
安装依赖：
pip install -r requirements.txt
运行测试：
Python
from services.ping_service import PingService
from services.result_service import ResultService

# 准备要测试的IP地址列表
test_ips = [
    "8.8.8.8",
    "1.1.1.1",
    # 添加更多IP...
]

# 创建服务实例并执行测试
ping_service = PingService(test_ips)
results = ping_service.test_all_nodes()

# 保存和显示结果
result_service = ResultService()
result_service.save_results(results)
result_service.print_summary(results)
详细使用说明
1. IP地址格式
IP地址可以通过以下两种方式提供：

字符串列表：["8.8.8.8", "1.1.1.1"]
换行符分隔的字符串："8.8.8.8\n1.1.1.1"
2. 批量处理
工具会自动将IP列表分批处理：

默认每批最多处理 256 个IP
可以通过修改 chunk_size 调整批量大小
批次之间有 1 秒的延迟，避免请求过快
3. 节点选择
测试节点包括：

电信：全国 37 个节点
联通：全国 31 个节点
移动：全国 32 个节点
4. 结果格式
每个测试结果包含：

IP 地址
节点名称
延迟（毫秒）
地理位置信息
示例代码
基本使用
Python
# main.py
from services.ping_service import PingService
from services.result_service import ResultService

def main(ips):
    # 创建服务实例
    ping_service = PingService(ips)
    
    # 执行测试
    all_results = ping_service.test_all_nodes()
    
    # 保存和显示结果
    result_service = ResultService()
    result_service.save_results(all_results)
    result_service.print_summary(all_results)

if __name__ == '__main__':
    test_ips = [
        "8.8.8.8",
        "1.1.1.1"
    ]
    
    main(test_ips)
自定义回调处理
Python
def custom_callback(result):
    print(f"测试结果: IP={result.ip}, "
          f"延迟={result.delay}ms, "
          f"地址={result.address}")

ping_service = PingService(test_ips)
results = ping_service.test_node("1274", "贵州贵阳 - 电信", custom_callback)
配置说明
主要配置项：

timeout: 请求超时时间（默认 10 秒）
chunk_size: 每批处理的IP数量（默认最大 256）
delay_between_batches: 批次间延迟（默认 1 秒）
delay_between_nodes: 节点切换延迟（默认 2 秒）
错误处理
工具包含完整的错误处理机制：

网络请求错误
无效的IP地址格式
WebSocket 通信错误
节点响应超时
注意事项
建议控制并发请求数量，避免对服务器造成过大压力
部分节点可能暂时无法访问，程序会自动跳过并继续测试
测试结果会受网络状况影响，建议多次测试取平均值
IP地址数量较大时，完整测试可能需要较长时间
