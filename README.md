# LLM Speed Test

这是一个用于测试和比较不同LLM（大语言模型）性能的项目。
（插个广告：目前个人项目和代码首发都在 今日头条:物联全栈123 专注DeepSeek等大模型的RAG知识库和智能体在工业领域的落地开发和分享。欢迎关注。）

## 项目简介

本项目旨在对不同的LLM模型进行性能测试和比较，帮助开发者了解各个模型在实际应用场景中的表现。

## 环境要求

- Python 3.11+
- uv (Python包管理工具)

## 环境配置

1. 安装uv：
```bash
brew install uv
```

2. 创建虚拟环境：
```bash
uv venv
```


3. 激活虚拟环境：
```bash
source .venv/bin/activate
```
4. 安装依赖：
```bash
 uv pip install -r requirements.txt
```

## 项目结构

```
├── app.py          # 演示文件
├── models.csv       # 模型配置文件
├── pyproject.toml   # 项目依赖配置
├── test_results/    # 测试结果目录
└── uv.lock          # 依赖版本锁定文件
```

## 使用说明
将models.csv.example 改为models.csv 并填入自己的apikey信息
```bash
python app.py
```
然后等待完成即可
1. 确保已正确配置环境并激活虚拟环境
2. 运行测试脚本进行性能测试
3. 测试结果将保存在 test_results 目录中

## 测试结果

测试结果将以结构化的形式保存在 test_results 目录中，包含各个模型的性能指标和比较数据。

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进这个项目。

## 许可证

本项目采用 MIT 许可证。
