import json
import statistics
import math

# 读取测试结果
def load_results(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

# 计算两个版本之间的性能变化百分比
def calculate_performance_change(baseline, current):
    changes = {}
    
    # 计算响应时间变化
    baseline_time = baseline['response_time']['avg']
    current_time = current['response_time']['avg']
    if baseline_time > 0:
        time_change = ((current_time - baseline_time) / baseline_time) * 100
    else:
        time_change = 0
    changes['response_time'] = time_change
    
    # 计算CPU使用率变化
    baseline_cpu = baseline['cpu']['avg']
    current_cpu = current['cpu']['avg']
    if baseline_cpu > 0:
        cpu_change = ((current_cpu - baseline_cpu) / baseline_cpu) * 100
    else:
        cpu_change = 0
    changes['cpu'] = cpu_change
    
    # 计算内存使用率变化
    baseline_memory = baseline['memory']['avg']
    current_memory = current['memory']['avg']
    if baseline_memory > 0:
        memory_change = ((current_memory - baseline_memory) / baseline_memory) * 100
    else:
        memory_change = 0
    changes['memory'] = memory_change
    
    return changes

# 执行t检验
def t_test(sample1, sample2):
    mean1 = statistics.mean(sample1)
    mean2 = statistics.mean(sample2)
    std1 = statistics.stdev(sample1) if len(sample1) > 1 else 0
    std2 = statistics.stdev(sample2) if len(sample2) > 1 else 0
    n1 = len(sample1)
    n2 = len(sample2)
    
    # 计算标准误差
    se = math.sqrt((std1**2 / n1) + (std2**2 / n2))
    if se == 0:
        return 0, 1.0
    
    # 计算t统计量
    t_stat = (mean1 - mean2) / se
    
    # 计算自由度
    df = n1 + n2 - 2
    
    # 这里简化处理，返回t统计量和自由度
    return t_stat, df

# 主分析函数
def analyze_performance(baseline_file, current_file):
    baseline_results = load_results(baseline_file)
    current_results = load_results(current_file)
    
    analysis_results = []
    
    for i, (baseline_test, current_test) in enumerate(zip(baseline_results, current_results)):
        print(f"\n分析测试用例 {i+1}: {baseline_test['test_name']}")
        print(f"查询: {baseline_test['query']}")
        
        # 计算性能变化
        changes = calculate_performance_change(baseline_test, current_test)
        
        # 提取响应时间样本
        # 注意：这里我们只有每个测试用例的统计数据，没有原始样本
        # 所以我们无法执行真正的t检验，只能基于平均值进行比较
        
        print(f"响应时间变化: {changes['response_time']:.2f}%")
        print(f"CPU使用率变化: {changes['cpu']:.2f}%")
        print(f"内存使用率变化: {changes['memory']:.2f}%")
        
        analysis_results.append({
            "test_name": baseline_test['test_name'],
            "query": baseline_test['query'],
            "changes": changes,
            "baseline": baseline_test,
            "current": current_test
        })
    
    # 计算总体平均变化
    total_changes = {
        "response_time": [],
        "cpu": [],
        "memory": []
    }
    
    for result in analysis_results:
        total_changes['response_time'].append(result['changes']['response_time'])
        total_changes['cpu'].append(result['changes']['cpu'])
        total_changes['memory'].append(result['changes']['memory'])
    
    print("\n总体平均变化:")
    print(f"平均响应时间变化: {statistics.mean(total_changes['response_time']):.2f}%")
    print(f"平均CPU使用率变化: {statistics.mean(total_changes['cpu']):.2f}%")
    print(f"平均内存使用率变化: {statistics.mean(total_changes['memory']):.2f}%")
    
    return analysis_results

if __name__ == "__main__":
    baseline_file = "performance_results_77f43d9e3586ac4dfc6afbf079561badfb53a54e.json"
    current_file = "performance_results_665266b76df3c6ebac1d8a8b5972f44cebc1c712.json"
    
    analyze_performance(baseline_file, current_file)
