<div align="center">
  <img 
      src="doc/LOGO.svg" 
      alt="Logo" 
      style="vertical-align: middle; margin-right: 0;" 
    >

**一个基于渐进式搜索和交叉评估的轻量级深度研究框架。**

[![License](https://img.shields.io/badge/license-apache2.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/github/v/release/iflytek/DeepResearch)](https://github.com/iflytek/DeepResearch/releases)
[![GitHub Stars](https://img.shields.io/github/stars/iflytek/DeepResearch?style=social)](https://github.com/iflytek/DeepResearch/stargazers)
</div>

## 概述

DeepResearch 是一个深度研究框架，支持多个大语言模型协同工作，集成搜索工具进行全面研究并生成可视化报告。它通过"任务规划 → 工具调用 → 评估与迭代"的智能工作流解决复杂信息分析问题。

**核心特性：**
- 无需模型定制即可获得高质量结果
- 大小模型协同工作，兼顾效率与成本控制
- 通过知识提取和交叉评估减少幻觉
- 轻量级部署，配置灵活

**框架：**
<div align="center">
   <img 
      src="doc/framework.png" 
      alt="framework" 
      style="width: 600px; height: 450px; vertical-align: middle; margin-right: 0;" 
    >
</div>

**示例报告：**

- [深度研究产品全球及国内格局分析](https://deep-report-file.xf-yun.com/Deep%20Research%20Products%20Global%20and%20Domestic%20Landscape%20Analysis.html)
- [全球 AI Agent 产品全景分析](https://deep-report-file.xf-yun.com/Global%20AI%20Agent%20Products%20Panoramic%20Analysis%20Core%20Capabilities%20and%20Application%20Scenarios.html)

## 快速开始

```bash
# 克隆仓库
git clone git@github.com:DaoField/DeepResearch.git
cd DeepResearch

# 安装
pip install -e .

# 运行
deepresearch
```

📖 **[详细文档](doc/intro.md)** - 完整的安装说明、配置指南和使用示例。

🌐 **[在线体验](https://xinghuo.xfyun.cn/desk)** - 在讯飞星火桌面版中体验"分析与研究"功能。

## 贡献

我们欢迎贡献！请参阅[贡献指南](CONTRIBUTING.md)。

## 支持

- [GitHub Discussions](https://github.com/iflytek/DeepResearch/discussions)
- [Issues](https://github.com/iflytek/DeepResearch/issues)

## 许可证

[Apache 2.0 许可证](LICENSE)
