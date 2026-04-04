#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
长期稳定性测试脚本
实施长时间运行测试，监控系统在持续运行过程中的稳定性指标
"""

import time
import asyncio
import psutil
import statistics
import json
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage
from deepresearch import call_agent


class StabilityTest:
    """长期稳定性测试类"""

    def __init__(self):
        self.monitoring_data = []
        self.test_results = []

    async def call_agent_async(self, query: str) -> Dict[str, Any]:
        """异步调用 agent"""
        start_time = time.time()
        try:
            messages = [HumanMessage(content=query)]
            await call_agent(messages=messages, max_depth=1, save_as_html=False)
            success = True
            error = None
        except Exception as e:
            success = False
            error = str(e)
        end_time = time.time()
        response_time = end_time - start_time
        return {
            "response_time": response_time,
            "success": success,
            "error": error
        }

    async def monitor_system(self) -> Dict[str, Any]:
        """监控系统状态"""
        process = psutil.Process()
        cpu_percent = process.cpu_percent(interval=1)
        memory_percent = process.memory_percent()
        memory_info = process.memory_info()
        disk_io = psutil.disk_io_counters()
        network_io = psutil.net_io_counters()

        return {
            "timestamp": time.time(),
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "memory_rss": memory_info.rss,
            "memory_vms": memory_info.vms,
            "disk_read_bytes": disk_io.read_bytes,
            "disk_write_bytes": disk_io.write_bytes,
            "network_sent_bytes": network_io.bytes_sent,
            "network_recv_bytes": network_io.bytes_recv
        }

    async def run_stability_test(self, duration: int = 3600, interval: int = 60) -> Dict[str, Any]:
        """运行稳定性测试"""
        print(f"\n{'='*80}")
        print(f"运行长期稳定性测试")
        print(f"测试持续时间: {duration} 秒")
        print(f"监控间隔: {interval} 秒")
        print(f"{'='*80}")

        start_time = time.time()
        end_time = start_time + duration

        # 测试查询
        query = "人工智能的发展趋势"

        # 运行测试并监控系统状态
        while time.time() < end_time:
            # 调用 agent
            agent_result = await self.call_agent_async(query)
            
            # 监控系统状态
            system_status = await self.monitor_system()
            
            # 记录监控数据
            monitoring_entry = {
                "timestamp": time.time(),
                "agent_result": agent_result,
                "system_status": system_status
            }
            self.monitoring_data.append(monitoring_entry)
            
            # 打印监控信息
            print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"响应时间: {agent_result['response_time']:.2f}s")
            print(f"成功: {agent_result['success']}")
            print(f"CPU 使用率: {system_status['cpu_percent']:.2f}%")
            print(f"内存使用率: {system_status['memory_percent']:.2f}%")
            print(f"内存 RSS: {system_status['memory_rss'] / 1024 / 1024:.2f} MB")
            print(f"内存 VMS: {system_status['memory_vms'] / 1024 / 1024:.2f} MB")
            print("-" * 80)
            
            # 等待下一个监控周期
            await asyncio.sleep(interval)

        # 计算统计数据
        response_times = [entry['agent_result']['response_time'] for entry in self.monitoring_data if entry['agent_result']['success']]
        success_count = sum(1 for entry in self.monitoring_data if entry['agent_result']['success'])
        error_count = sum(1 for entry in self.monitoring_data if not entry['agent_result']['success'])

        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            std_response_time = statistics.stdev(response_times) if len(response_times) > 1 else 0
        else:
            avg_response_time = 0
            max_response_time = 0
            min_response_time = 0
            std_response_time = 0

        # 计算系统资源使用统计
        cpu_percentages = [entry['system_status']['cpu_percent'] for entry in self.monitoring_data]
        memory_percentages = [entry['system_status']['memory_percent'] for entry in self.monitoring_data]
        memory_rss_values = [entry['system_status']['memory_rss'] for entry in self.monitoring_data]

        if cpu_percentages:
            avg_cpu_percent = statistics.mean(cpu_percentages)
            max_cpu_percent = max(cpu_percentages)
            min_cpu_percent = min(cpu_percentages)
        else:
            avg_cpu_percent = 0
            max_cpu_percent = 0
            min_cpu_percent = 0

        if memory_percentages:
            avg_memory_percent = statistics.mean(memory_percentages)
            max_memory_percent = max(memory_percentages)
            min_memory_percent = min(memory_percentages)
        else:
            avg_memory_percent = 0
            max_memory_percent = 0
            min_memory_percent = 0

        if memory_rss_values:
            avg_memory_rss = statistics.mean(memory_rss_values)
            max_memory_rss = max(memory_rss_values)
            min_memory_rss = min(memory_rss_values)
        else:
            avg_memory_rss = 0
            max_memory_rss = 0
            min_memory_rss = 0

        # 检测内存泄漏
        # 简单的内存泄漏检测：检查内存使用是否持续增长
        memory_leak_detected = False
        if len(memory_rss_values) > 10:
            # 计算内存使用的趋势
            memory_trend = memory_rss_values[-1] - memory_rss_values[0]
            if memory_trend > 10 * 1024 * 1024:  # 内存增长超过 10MB
                memory_leak_detected = True

        stats = {
            "duration": duration,
            "query": query,
            "total_requests": len(self.monitoring_data),
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": success_count / len(self.monitoring_data) if self.monitoring_data else 0,
            "response_time": {
                "avg": avg_response_time,
                "max": max_response_time,
                "min": min_response_time,
                "std": std_response_time
            },
            "cpu": {
                "avg": avg_cpu_percent,
                "max": max_cpu_percent,
                "min": min_cpu_percent
            },
            "memory": {
                "avg_percent": avg_memory_percent,
                "max_percent": max_memory_percent,
                "min_percent": min_memory_percent,
                "avg_rss": avg_memory_rss,
                "max_rss": max_memory_rss,
                "min_rss": min_memory_rss
            },
            "memory_leak_detected": memory_leak_detected,
            "timestamp": time.time()
        }

        self.test_results.append(stats)
        print(f"\n{'='*80}")
        print(f"测试完成: 持续时间 {duration} 秒")
        print(f"总请求数: {len(self.monitoring_data)}")
        print(f"成功数: {success_count}")
        print(f"错误数: {error_count}")
        print(f"成功率: {stats['success_rate']:.2f}")
        print(f"平均响应时间: {avg_response_time:.2f}s")
        print(f"最大响应时间: {max_response_time:.2f}s")
        print(f"最小响应时间: {min_response_time:.2f}s")
        print(f"响应时间标准差: {std_response_time:.2f}s")
        print(f"平均 CPU 使用率: {avg_cpu_percent:.2f}%")
        print(f"最大 CPU 使用率: {max_cpu_percent:.2f}%")
        print(f"平均内存使用率: {avg_memory_percent:.2f}%")
        print(f"最大内存使用率: {max_memory_percent:.2f}%")
        print(f"平均内存 RSS: {avg_memory_rss / 1024 / 1024:.2f} MB")
        print(f"最大内存 RSS: {max_memory_rss / 1024 / 1024:.2f} MB")
        print(f"内存泄漏检测: {'是' if memory_leak_detected else '否'}")
        print(f"{'='*80}")
        return stats

    def save_results(self, filename: str):
        """保存测试结果"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "test_results": self.test_results,
                "monitoring_data": self.monitoring_data
            }, f, ensure_ascii=False, indent=2)
        print(f"\n测试结果已保存到: {filename}")

    def generate_report(self, filename: str):
        """生成测试报告"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 长期稳定性测试报告\n\n")
            f.write("## 测试概述\n")
            f.write("本报告记录了 DeepResearch 系统在长时间运行过程中的稳定性表现。\n\n")
            
            for result in self.test_results:
                f.write(f"## 测试结果\n")
                f.write(f"- 测试持续时间: {result['duration']} 秒\n")
                f.write(f"- 查询: {result['query']}\n")
                f.write(f"- 总请求数: {result['total_requests']}\n")
                f.write(f"- 成功数: {result['success_count']}\n")
                f.write(f"- 错误数: {result['error_count']}\n")
                f.write(f"- 成功率: {result['success_rate']:.2f}\n")
                f.write(f"- 平均响应时间: {result['response_time']['avg']:.2f}s\n")
                f.write(f"- 最大响应时间: {result['response_time']['max']:.2f}s\n")
                f.write(f"- 最小响应时间: {result['response_time']['min']:.2f}s\n")
                f.write(f"- 响应时间标准差: {result['response_time']['std']:.2f}s\n")
                f.write(f"- 平均 CPU 使用率: {result['cpu']['avg']:.2f}%\n")
                f.write(f"- 最大 CPU 使用率: {result['cpu']['max']:.2f}%\n")
                f.write(f"- 平均内存使用率: {result['memory']['avg_percent']:.2f}%\n")
                f.write(f"- 最大内存使用率: {result['memory']['max_percent']:.2f}%\n")
                f.write(f"- 平均内存 RSS: {result['memory']['avg_rss'] / 1024 / 1024:.2f} MB\n")
                f.write(f"- 最大内存 RSS: {result['memory']['max_rss'] / 1024 / 1024:.2f} MB\n")
                f.write(f"- 内存泄漏检测: {'是' if result['memory_leak_detected'] else '否'}\n\n")
            
            f.write("## 结论\n")
            f.write("根据测试结果，系统在长时间运行过程中的稳定性表现如下：\n\n")
            
            for result in self.test_results:
                f.write(f"- 测试持续时间 {result['duration']} 秒：成功率 {result['success_rate']:.2f}，平均响应时间 {result['response_time']['avg']:.2f}s，平均 CPU 使用率 {result['cpu']['avg']:.2f}%，平均内存使用率 {result['memory']['avg_percent']:.2f}%，内存泄漏检测 {'是' if result['memory_leak_detected'] else '否'}\n")
        
        print(f"\n测试报告已生成到: {filename}")


async def main():
    """主函数"""
    test = StabilityTest()
    
    # 测试持续时间：1 小时（3600 秒）
    # 实际测试中可以设置为 72 小时（259200 秒）
    duration = 3600
    interval = 60  # 监控间隔：60 秒
    
    await test.run_stability_test(duration, interval)
    
    # 保存测试结果
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_filename = f"stability_test_results_{timestamp}.json"
    test.save_results(results_filename)
    
    # 生成测试报告
    report_filename = f"stability_test_report_{timestamp}.md"
    test.generate_report(report_filename)


if __name__ == "__main__":
    asyncio.run(main())
