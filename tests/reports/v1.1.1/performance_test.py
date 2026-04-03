import time
import psutil
import json
import statistics
from datetime import datetime
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage
from src.agent.agent import build_agent
import asyncio

class PerformanceTest:
    def __init__(self):
        self.graph = build_agent()
        self.test_results = []
    
    async def call_agent(self, messages, max_depth=3, save_as_html=True):
        state = {
            "messages": messages
        }
        config = {
            "configurable": {
                "depth": max_depth,
                "save_as_html": save_as_html,
                "save_path": "./example/report"
            }
        }
        output = ""
        start_time = time.time()
        
        # 监控系统资源
        cpu_percentages = []
        memory_percentages = []
        process = psutil.Process()
        
        def monitor_resources():
            while True:
                cpu_percentages.append(process.cpu_percent(interval=0.1))
                memory_percentages.append(process.memory_percent())
                time.sleep(0.1)
        
        import threading
        monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
        monitor_thread.start()
        
        try:
            for message in self.graph.stream(
                input=state, config=config, stream_mode="values"
            ):
                if isinstance(message, dict) and "output" in message and isinstance(message["output"], dict):
                    if "message" in message["output"]:
                        output = message["output"]["message"]
        finally:
            end_time = time.time()
            
        response_time = end_time - start_time
        
        # 计算资源使用情况
        avg_cpu = statistics.mean(cpu_percentages) if cpu_percentages else 0
        max_cpu = max(cpu_percentages) if cpu_percentages else 0
        min_cpu = min(cpu_percentages) if cpu_percentages else 0
        
        avg_memory = statistics.mean(memory_percentages) if memory_percentages else 0
        max_memory = max(memory_percentages) if memory_percentages else 0
        min_memory = min(memory_percentages) if memory_percentages else 0
        
        return {
            "response_time": response_time,
            "cpu": {
                "avg": avg_cpu,
                "max": max_cpu,
                "min": min_cpu
            },
            "memory": {
                "avg": avg_memory,
                "max": max_memory,
                "min": min_memory
            },
            "output_length": len(output)
        }
    
    async def run_test(self, test_name, query, iterations=1):
        print(f"Running test: {test_name}")
        print(f"Query: {query}")
        
        test_iterations = []
        for i in range(iterations):
            print(f"Iteration {i+1}/{iterations}")
            messages = [HumanMessage(content=query)]
            result = await self.call_agent(messages)
            test_iterations.append(result)
            print(f"  Response time: {result['response_time']:.2f}s")
            print(f"  Avg CPU: {result['cpu']['avg']:.2f}%")
            print(f"  Avg Memory: {result['memory']['avg']:.2f}%")
        
        # 计算统计数据
        response_times = [r['response_time'] for r in test_iterations]
        cpu_avgs = [r['cpu']['avg'] for r in test_iterations]
        memory_avgs = [r['memory']['avg'] for r in test_iterations]
        
        stats = {
            "test_name": test_name,
            "query": query,
            "iterations": iterations,
            "response_time": {
                "avg": statistics.mean(response_times),
                "max": max(response_times),
                "min": min(response_times),
                "std": statistics.stdev(response_times) if len(response_times) > 1 else 0
            },
            "cpu": {
                "avg": statistics.mean(cpu_avgs),
                "max": max([r['cpu']['max'] for r in test_iterations]),
                "min": min([r['cpu']['min'] for r in test_iterations])
            },
            "memory": {
                "avg": statistics.mean(memory_avgs),
                "max": max([r['memory']['max'] for r in test_iterations]),
                "min": min([r['memory']['min'] for r in test_iterations])
            },
            "timestamp": datetime.now().isoformat()
        }
        
        self.test_results.append(stats)
        print(f"Test completed. Avg response time: {stats['response_time']['avg']:.2f}s")
        print("=" * 60)
        return stats
    
    def save_results(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        print(f"Results saved to {filename}")
    
    def load_results(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            self.test_results = json.load(f)
        print(f"Results loaded from {filename}")

async def main():
    test = PerformanceTest()
    
    # 定义测试用例
    test_cases = [
        {
            "name": "公司研究",
            "query": "请介绍阿里巴巴公司，并分析其发展前景。"
        },
        {
            "name": "技术趋势",
            "query": "分析2026年人工智能领域的主要技术趋势。"
        },
        {
            "name": "市场分析",
            "query": "分析中国新能源汽车市场的现状和未来发展。"
        }
    ]
    
    # 运行测试
    for test_case in test_cases:
        await test.run_test(test_case["name"], test_case["query"], iterations=3)
    
    # 保存结果
    commit_hash = "665266b76df3c6ebac1d8a8b5972f44cebc1c712"
    filename = f"performance_results_{commit_hash}.json"
    test.save_results(filename)

if __name__ == "__main__":
    asyncio.run(main())
