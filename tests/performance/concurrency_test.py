#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
并发性能测试脚本
模拟不同级别（低、中、高）的用户并发访问场景
"""

import time
import asyncio
import statistics
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage
from deepresearch.run import call_agent


class ConcurrencyTest:
    """并发性能测试类"""

    def __init__(self):
        self.test_results = []

    async def call_agent_async(self, user_id: int, query: str) -> Dict[str, Any]:
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
            "user_id": user_id,
            "response_time": response_time,
            "success": success,
            "error": error
        }

    async def run_concurrent_test(self, concurrency: int, query: str, duration: int = 60) -> Dict[str, Any]:
        """运行并发测试"""
        print(f"\n{'='*80}")
        print(f"运行并发测试: {concurrency} 并发用户")
        print(f"查询: {query}")
        print(f"测试持续时间: {duration} 秒")
        print(f"{'='*80}")

        results = []
        start_time = time.time()
        end_time = start_time + duration

        async def worker(user_id: int):
            """测试工作线程"""
            while time.time() < end_time:
                result = await self.call_agent_async(user_id, query)
                results.append(result)

        # 创建并启动多个协程
        tasks = []
        for i in range(concurrency):
            task = asyncio.create_task(worker(i))
            tasks.append(task)

        # 等待所有任务完成
        await asyncio.gather(*tasks)

        # 计算统计数据
        response_times = [r['response_time'] for r in results if r['success']]
        success_count = sum(1 for r in results if r['success'])
        error_count = sum(1 for r in results if not r['success'])

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

        throughput = len(results) / duration

        stats = {
            "concurrency": concurrency,
            "query": query,
            "duration": duration,
            "total_requests": len(results),
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": success_count / len(results) if results else 0,
            "response_time": {
                "avg": avg_response_time,
                "max": max_response_time,
                "min": min_response_time,
                "std": std_response_time
            },
            "throughput": throughput,
            "timestamp": time.time()
        }

        self.test_results.append(stats)
        print(f"\n{'='*80}")
        print(f"测试完成: {concurrency} 并发用户")
        print(f"总请求数: {len(results)}")
        print(f"成功数: {success_count}")
        print(f"错误数: {error_count}")
        print(f"成功率: {stats['success_rate']:.2f}")
        print(f"平均响应时间: {avg_response_time:.2f}s")
        print(f"最大响应时间: {max_response_time:.2f}s")
        print(f"最小响应时间: {min_response_time:.2f}s")
        print(f"响应时间标准差: {std_response_time:.2f}s")
        print(f"吞吐量: {throughput:.2f} 请求/秒")
        print(f"{'='*80}")
        return stats

    def save_results(self, filename: str):
        """保存测试结果"""
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        print(f"\n测试结果已保存到: {filename}")

    def generate_report(self, filename: str):
        """生成测试报告"""
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 并发性能测试报告\n\n")
            f.write("## 测试概述\n")
            f.write("本报告记录了 DeepResearch 系统在不同并发用户场景下的性能表现。\n\n")
            
            for result in self.test_results:
                f.write(f"## {result['concurrency']} 并发用户\n")
                f.write(f"- 查询: {result['query']}\n")
                f.write(f"- 测试持续时间: {result['duration']} 秒\n")
                f.write(f"- 总请求数: {result['total_requests']}\n")
                f.write(f"- 成功数: {result['success_count']}\n")
                f.write(f"- 错误数: {result['error_count']}\n")
                f.write(f"- 成功率: {result['success_rate']:.2f}\n")
                f.write(f"- 平均响应时间: {result['response_time']['avg']:.2f}s\n")
                f.write(f"- 最大响应时间: {result['response_time']['max']:.2f}s\n")
                f.write(f"- 最小响应时间: {result['response_time']['min']:.2f}s\n")
                f.write(f"- 响应时间标准差: {result['response_time']['std']:.2f}s\n")
                f.write(f"- 吞吐量: {result['throughput']:.2f} 请求/秒\n\n")
            
            f.write("## 结论\n")
            f.write("根据测试结果，系统在不同并发用户场景下的性能表现如下：\n\n")
            
            for result in self.test_results:
                f.write(f"- {result['concurrency']} 并发用户：平均响应时间 {result['response_time']['avg']:.2f}s，成功率 {result['success_rate']:.2f}，吞吐量 {result['throughput']:.2f} 请求/秒\n")
        
        print(f"\n测试报告已生成到: {filename}")


async def main():
    """主函数"""
    test = ConcurrencyTest()
    
    # 测试查询
    query = "人工智能的发展趋势"
    
    # 测试不同并发级别
    concurrency_levels = [10, 50, 100]
    duration = 60  # 每个测试持续 60 秒
    
    for concurrency in concurrency_levels:
        await test.run_concurrent_test(concurrency, query, duration)
    
    # 保存测试结果
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_filename = f"concurrency_test_results_{timestamp}.json"
    test.save_results(results_filename)
    
    # 生成测试报告
    report_filename = f"concurrency_test_report_{timestamp}.md"
    test.generate_report(report_filename)


if __name__ == "__main__":
    asyncio.run(main())
