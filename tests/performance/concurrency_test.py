#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from langchain_core.messages import HumanMessage

from deepresearch import build_agent


class ConcurrencyTest:
    def __init__(self):
        self.test_results = []
        self.agent = build_agent()

    def call_agent_sync(self, user_id: int, query: str) -> dict[str, Any]:
        start_time = time.time()
        try:
            messages = [HumanMessage(content=query)]
            config = {"configurable": {"depth": 1, "save_as_html": False}}
            for _ in self.agent.stream(input={"messages": messages}, config=config):
                pass
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
            "error": error,
        }

    def run_concurrent_test(
        self, concurrency: int, query: str, duration: int = 60
    ) -> dict[str, Any]:
        print(f"\n{'='*80}")
        print(f"运行并发测试: {concurrency} 并发用户")
        print(f"查询: {query}")
        print(f"测试持续时间: {duration} 秒")
        print(f"{'='*80}")

        results = []
        start_time = time.time()
        end_time = start_time + duration

        def worker(user_id: int):
            while time.time() < end_time:
                result = self.call_agent_sync(user_id, query)
                results.append(result)

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(worker, i) for i in range(concurrency)]
            for future in futures:
                future.result()

        response_times = [r["response_time"] for r in results if r["success"]]
        success_count = sum(1 for r in results if r["success"])
        error_count = sum(1 for r in results if not r["success"])

        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            std_response_time = (
                statistics.stdev(response_times) if len(response_times) > 1 else 0
            )
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
                "std": std_response_time,
            },
            "throughput": throughput,
            "timestamp": time.time(),
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
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        print(f"\n测试结果已保存到: {filename}")

    def generate_report(self, filename: str):
        with open(filename, "w", encoding="utf-8") as f:
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
                f.write(
                    f"- 平均响应时间: {result['response_time']['avg']:.2f}s\n"
                )
                f.write(
                    f"- 最大响应时间: {result['response_time']['max']:.2f}s\n"
                )
                f.write(
                    f"- 最小响应时间: {result['response_time']['min']:.2f}s\n"
                )
                f.write(
                    f"- 响应时间标准差: {result['response_time']['std']:.2f}s\n"
                )
                f.write(f"- 吞吐量: {result['throughput']:.2f} 请求/秒\n\n")

            f.write("## 结论\n")
            f.write(
                "根据测试结果，系统在不同并发用户场景下的性能表现如下：\n\n"
            )

            for result in self.test_results:
                f.write(
                    f"- {result['concurrency']} 并发用户：平均响应时间 {result['response_time']['avg']:.2f}s，成功率 {result['success_rate']:.2f}，吞吐量 {result['throughput']:.2f} 请求/秒\n"
                )

        print(f"\n测试报告已生成到: {filename}")


def main():
    test = ConcurrencyTest()

    query = "人工智能的发展趋势"

    concurrency_levels = [10, 50, 100]
    duration = 60

    for concurrency in concurrency_levels:
        test.run_concurrent_test(concurrency, query, duration)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_filename = f"concurrency_test_results_{timestamp}.json"
    test.save_results(results_filename)

    report_filename = f"concurrency_test_report_{timestamp}.md"
    test.generate_report(report_filename)


if __name__ == "__main__":
    main()
