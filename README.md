# evrmem

> QMD - 本地化 AI 向量记忆系统 / Fully Local AI Vector Memory System

[![GitHub stars](https://img.shields.io/github/stars/zhzgao/evrmem?style=social)](https://github.com/zhzgao/evrmem/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/zhzgao/evrmem?style=social)](https://github.com/zhzgao/evrmem/network/members)
[![PyPI version](https://img.shields.io/pypi/v/evrmem?color=blue)](https://pypi.org/project/evrmem/)
[![PyPI downloads](https://img.shields.io/pypi/dm/evrmem?color=green)](https://pypi.org/project/evrmem/)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GitHub Actions Status](https://img.shields.io/github/actions/workflow/status/zhzgao/evrmem/deploy-pages.yml)](https://github.com/zhzgao/evrmem/actions)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://zhzgao.github.io/evrmem)
[![Offline](https://img.shields.io/badge/100%25-Offline-green)](https://github.com/zhzgao/evrmem)
[![Chinese](https://img.shields.io/badge/中文-优化-orange)](https://github.com/zhzgao/evrmem)

---

📖 **在线文档**: https://zhzgao.github.io/evrmem

---

## English

### What is evrmem?

evrmem (pronounced "e-vee-are-mem") is a **fully local AI vector memory system** designed for developers and AI agents. It stores, retrieves, and reasons over personal knowledge using semantic vector search — no cloud, no API keys, 100% offline.

Built on [ChromaDB](https://www.trychroma.com/) + [text2vec-base-chinese](https://huggingface.co/shibing624/text2vec-base-chinese), evrmem is optimized for **Chinese semantic understanding** and works entirely offline after initial model setup.

### Features

- **Semantic Search** — Natural language queries with Chinese-optimized embeddings
- **Structured Query** — Filter by project, date, tags, or type
- **RAG Retrieval** — Generate context-augmented prompts for LLMs
- **100% Offline** — Works without internet after model is cached
- **Single Command CLI** — `evrmem add / search / rag / query / stats`
- **Python API** — Embed in any Python project

### Quick Start

```bash
# Install (from source)
pip install -e .

# Add a memory
evrmem add "React StrictMode causes Form.useForm warning" --project mes-demo --tags react,antd

# Search memories
evrmem search "React form warning fix"

# RAG: generate LLM prompt with context
evrmem rag "how to fix the form warning" --prompt

# View stats
evrmem stats

# Structured query
evrmem query --project mes-demo
```

### Installation

#### Option A: pip install (recommended)

```bash
pip install evrmem
```

#### Option B: Install from source

```bash
git clone https://github.com/zhzgao/evrmem.git
cd evrmem
pip install -e .
```

#### Dependencies

- Python 3.9+
- `chromadb` — Vector database
- `sentence-transformers` — Embedding model
- `pyyaml` — Config file support

Embedding model (`shibing624/text2vec-base-chinese`, ~400MB) is downloaded automatically on first run.

### Configuration

Config file `config.yaml` (in project root or `~/.evrmem/config.yaml`):

```yaml
vector_db:
  persist_directory: "~/.evrmem/data/qmd_memory"

embedding:
  model_name: "shibing624/text2vec-base-chinese"  # HuggingFace model
  cache_folder: "~/.evrmem/models"                  # Local model cache
  device: "cpu"                                     # or "cuda"

rag:
  top_k: 5
  min_similarity: 0.5

logging:
  level: "WARNING"
```

Environment variables override config file (highest priority):

| Variable | Config Key | Description |
|----------|-----------|-------------|
| `EVREM_MODEL_NAME` | `embedding.model_name` | HuggingFace model name |
| `EVREM_LOCAL_MODEL` | `embedding.local_path` | Local model path (highest priority) |
| `EVREM_DEVICE` | `embedding.device` | `cpu` or `cuda` |
| `EVREM_DATA_DIR` | `vector_db.persist_directory` | Data directory |
| `EVREM_TOP_K` | `rag.top_k` | Default retrieval count |
| `EVREM_LOG_LEVEL` | `logging.level` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `EVREM_LOCAL_FILES_ONLY` | - | Set to `true` to disable network access (default: `false`) |
| `HF_ENDPOINT` | - | HuggingFace mirror endpoint (e.g., `https://hf-mirror.com` for China users) |

### CLI Reference

```bash
# Add memory
evrmem add "content here" [-p project] [-t tags] [-d date] [-f file]

# Semantic search
evrmem search "query" [-k top_k] [-s min_similarity] [-v]
evrmem search              # Interactive mode

# RAG retrieval
evrmem rag "query" [-k top_k] [-s min_similarity] [-p]  # -p = generate full prompt
evrmem rag                # Interactive mode

# Structured query
evrmem query [--project name] [--date YYYY-MM-DD] [--tag tag] [--type type]
evrmem query --list-projects
evrmem query --list-tags

# Stats & init
evrmem stats
evrmem init

# Help & version
evrmem --help
evrmem -v
```

### Python API

```python
from qmd.core.vector_db import vector_db
from qmd.core.embedding import get_embedding_model

# Add
memory_id = vector_db.add_memory(
    "React StrictMode causes Form.useForm warning",
    metadata={"project": "mes-demo", "tags": "react,antd", "date": "2026-03-27"}
)

# Semantic search
results = vector_db.search("react antd form warning", top_k=5)

# Metadata query
results = vector_db.query_by_metadata({"project": "mes-demo"})

# Get embedding model directly
emb = get_embedding_model()
vec = emb.encode("hello world")
print(f"Dimension: {emb.dimension}")  # 768
```

### Architecture

```
User Input / CLI
      │
      ▼
┌──────────────┐
│   qmd.cli    │  ← argparse-based unified CLI
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌────────────────────────────┐
│  VectorDB    │────▶│ ChromaDB (PersistentClient) │
│  (singleton) │     └────────────────────────────┘
└──────┬───────┘
       │ embed()
       ▼
┌──────────────────────────────────────────────────┐
│ EmbeddingModel (lazy-loaded)                     │
│  ├─ SentenceTransformer (text2vec-base-chinese)  │
│  ├─ _resolve_local_model() [offline support]    │
│  └─ local_files_only=True [no network calls]     │
└──────────────────────────────────────────────────┘
```

### License

MIT — see [LICENSE](LICENSE).

---

## 中文

### 什么是 evrmem？

evrmem 是一个**完全本地化的 AI 向量记忆系统**，专为开发者和 AI 智能体设计。通过语义向量搜索存储、检索和推理个人知识——无需云服务、无需 API Key、100% 离线运行。

基于 [ChromaDB](https://www.trychroma.com/) + [text2vec-base-chinese](https://huggingface.co/shibing624/text2vec-base-chinese) 构建，针对**中文语义理解**深度优化，首次配置后完全离线工作。

### 特性

- **语义搜索** — 自然语言查询，中文语义优先
- **结构化查询** — 按项目、日期、标签等维度筛选
- **RAG 增强** — 生成带上下文的 LLM 提示词
- **100% 离线** — 模型缓存后无需网络
- **单命令 CLI** — `evrmem add / search / rag / query / stats`
- **Python API** — 嵌入任意 Python 项目

### 快速开始

```bash
# 从源码安装
pip install -e .

# 添加记忆
evrmem add "React StrictMode 导致 Form.useForm 警告" --project mes-demo --tags react,antd

# 语义搜索
evrmem search "React 表单警告修复"

# RAG：生成带上下文的 LLM 提示词
evrmem rag "如何修复表单警告" --prompt

# 查看统计
evrmem stats

# 结构化查询
evrmem query --project mes-demo
```

### 安装

#### 方式 A：pip 安装（推荐）

```bash
pip install evrmem
```

#### 方式 B：从源码安装

```bash
git clone https://github.com/zhzgao/evrmem.git
cd evrmem
pip install -e .
```

#### 依赖

- Python 3.9+
- `chromadb` — 向量数据库
- `sentence-transformers` — Embedding 模型
- `pyyaml` — 配置文件支持

Embedding 模型（`shibing624/text2vec-base-chinese`，约 400MB）首次运行自动下载。

### 配置

配置文件 `config.yaml`（项目根目录或 `~/.evrmem/config.yaml`）：

```yaml
vector_db:
  persist_directory: "~/.evrmem/data/qmd_memory"

embedding:
  model_name: "shibing624/text2vec-base-chinese"  # HuggingFace 模型名
  cache_folder: "~/.evrmem/models"                  # 本地模型缓存目录
  device: "cpu"                                     # 或 "cuda"

rag:
  top_k: 5
  min_similarity: 0.5

logging:
  level: "WARNING"
```

环境变量优先级最高（覆盖配置文件）：

| 变量 | 配置项 | 说明 |
|------|--------|------|
| `EVREM_MODEL_NAME` | `embedding.model_name` | HuggingFace 模型名 |
| `EVREM_LOCAL_MODEL` | `embedding.local_path` | 本地模型路径（优先级最高） |
| `EVREM_DEVICE` | `embedding.device` | `cpu` 或 `cuda` |
| `EVREM_DATA_DIR` | `vector_db.persist_directory` | 数据目录 |
| `EVREM_TOP_K` | `rag.top_k` | 默认检索条数 |
| `EVREM_LOG_LEVEL` | `logging.level` | `DEBUG`、`INFO`、`WARNING`、`ERROR` |

### CLI 命令参考

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

### Python API

```python
from qmd.core.vector_db import vector_db
from qmd.core.embedding import get_embedding_model

# 添加记忆
memory_id = vector_db.add_memory(
    "React StrictMode 导致 Form.useForm 警告",
    metadata={"project": "mes-demo", "tags": "react,antd", "date": "2026-03-27"}
)

# 语义搜索
results = vector_db.search("react antd form warning", top_k=5)

# 按元数据查询
results = vector_db.query_by_metadata({"project": "mes-demo"})

# 直接使用 Embedding 模型
emb = get_embedding_model()
vec = emb.encode("你好世界")
print(f"向量维度: {emb.dimension}")  # 768
```

### 技术架构

```
用户输入 / CLI 命令
      │
      ▼
┌──────────────┐
│   qmd.cli    │  ← 基于 argparse 的统一 CLI 入口
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌────────────────────────────┐
│  VectorDB    │────▶│ ChromaDB (PersistentClient) │
│  (单例模式)   │     └────────────────────────────┘
└──────┬───────┘
       │ embed()
       ▼
┌──────────────────────────────────────────────────┐
│ EmbeddingModel（延迟加载）                        │
│  ├─ SentenceTransformer (text2vec-base-chinese)  │
│  ├─ _resolve_local_model() [离线路径解析]         │
│  └─ local_files_only=True [零网络请求]           │
└──────────────────────────────────────────────────┘
```

### 项目结构

```
evrmem/
├── src/qmd/              # 源码包
│   ├── __init__.py
│   ├── __main__.py       # python -m qmd 入口
│   ├── cli.py             # CLI 主逻辑
│   ├── core/
│   │   ├── config.py      # 配置加载器
│   │   ├── embedding.py   # Embedding 模型封装
│   │   └── vector_db.py   # ChromaDB 封装
│   └── utils/
│       └── console.py     # 跨平台控制台编码
├── docs/                 # 开发文档
│   ├── index.md          # 文档导航
│   └── DEVELOPMENT.md    # 开发指南
├── config.yaml           # 配置文件
├── pyproject.toml        # pip 包配置
├── LICENSE               # MIT 协议
├── README.md             # 本文档（中英双语）
├── CONTRIBUTING.md        # 贡献指南
├── CHANGELOG.md          # 更新日志
├── evrmem.bat            # Windows 快捷命令
└── evrmem.sh             # Unix 快捷命令
```

### 协议

MIT — 详见 [LICENSE](LICENSE)。
