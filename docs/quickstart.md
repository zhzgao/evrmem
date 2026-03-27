# 快速开始

## 安装

### 从源码安装

```bash
git clone https://github.com/zhzgao/evrmem.git
cd evrmem
pip install -e .
```

### 依赖

- Python 3.9+
- `chromadb` — 向量数据库
- `sentence-transformers` — Embedding 模型
- `pyyaml` — 配置文件支持

Embedding 模型（`shibing624/text2vec-base-chinese`，约 400MB）首次运行自动下载。

## 首次使用

```bash
# 初始化系统
evrmem init

# 添加一条记忆
evrmem add "React StrictMode 导致 Form.useForm 警告" --project mes-demo --tags react,antd

# 语义搜索
evrmem search "React 表单警告修复"

# RAG：生成带上下文的 LLM 提示词
evrmem rag "如何修复表单警告" --prompt

# 查看统计
evrmem stats
```

## CLI 命令

```bash
# 添加记忆
evrmem add "记忆内容" [-p 项目名] [-t 标签] [-d 日期] [-f 文件路径]

# 语义搜索
evrmem search "查询内容" [-k 返回条数] [-s 最小相似度] [-v 详细输出]
evrmem search              # 交互模式

# RAG 检索
evrmem rag "查询内容" [-k 条数] [-s 相似度] [-p 生成完整提示词]
evrmem rag                # 交互模式

# 结构化查询
evrmem query [--project 项目名] [--date YYYY-MM-DD] [--tag 标签] [--type 类型]
evrmem query --list-projects   # 列出所有项目
evrmem query --list-tags       # 列出所有标签

# 统计与初始化
evrmem stats   # 系统状态
evrmem init    # 初始化/查看状态

# 帮助与版本
evrmem --help
evrmem -v
```
