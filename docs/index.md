# evrmem

> QMD - 本地化 AI 向量记忆系统，100% 离线运行

![GitHub stars](https://img.shields.io/github/stars/zhzgao/evrmem)
![License](https://img.shields.io/badge/license-MIT-blue)

**evrmem** 是一个完全本地化的 AI 向量记忆系统，专为开发者和 AI 智能体设计。通过语义向量搜索存储、检索和推理个人知识——无需云服务、无需 API Key、100% 离线运行。

## 特性

- :mag: **语义搜索** — 自然语言查询，中文语义优先
- :card_file_box: **结构化查询** — 按项目、日期、标签等维度筛选
- :robot: **RAG 增强** — 生成带上下文的 LLM 提示词
- :wifi_off: **100% 离线** — 模型缓存后无需网络
- :keyboard: **单命令 CLI** — `evrmem add / search / rag / query / stats`
- :snake: **Python API** — 嵌入任意 Python 项目

## 快速开始

```bash
# 安装
pip install -e .

# 添加记忆
evrmem add "React StrictMode 导致 Form.useForm 警告" -p mes-demo -t react,antd

# 语义搜索
evrmem search "React 表单警告修复"

# RAG 检索
evrmem rag "如何修复表单警告" --prompt
```

## 技术栈

- [ChromaDB](https://www.trychroma.com/) — 向量数据库
- [text2vec-base-chinese](https://huggingface.co/shibing624/text2vec-base-chinese) — 中文语义 Embedding 模型

## 文档导航

- [安装指南](install.md) — 完整安装说明
- [快速开始](quickstart.md) — 5 分钟上手教程
- [CLI 命令](cli.md) — 命令行工具完整参考
- [Python API](api.md) — Python 接口文档
- [配置指南](config.md) — 配置文件和环境变量
- [开发指南](DEVELOPMENT.md) — 源码架构和开发指南

## 相关链接

- [GitHub 仓库](https://github.com/zhzgao/evrmem)
- [GitHub Pages 文档](https://zhzgao.github.io/evrmem)
- [PyPI 包](https://pypi.org/project/evrmem/)

