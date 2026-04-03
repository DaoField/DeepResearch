#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
性能分析脚本，用于分析 DeepResearch 系统的性能瓶颈
"""

import cProfile
import pstats
from io import StringIO
import asyncio
from langchain_core.messages import HumanMessage
from deepresearch.run import call_agent


def run_performance_analysis():
    """运行性能分析"""
    # 准备测试输入
    messages = [
        HumanMessage(content="人工智能的发展趋势")
    ]
    
    # 使用 cProfile 进行性能分析
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        # 执行 agent 调用
        asyncio.run(call_agent(messages=messages, max_depth=1, save_as_html=False))
    except Exception as e:
        print(f"执行过程中出现错误: {e}")
    finally:
        profiler.disable()
    
    # 分析性能数据
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats()
    
    # 保存性能分析结果
    with open('performance_analysis.txt', 'w', encoding='utf-8') as f:
        f.write(s.getvalue())
    
    print("性能分析完成，结果已保存到 performance_analysis.txt")


if __name__ == "__main__":
    run_performance_analysis()
