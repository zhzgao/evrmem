# Development Guide / 开发指南

> 本文档面向希望深入了解、定制或贡献 evrmem 源码的开发者。
> This document is for developers who want to understand, customize, or contribute to evrmem.

---

## English

### Project Structure

```
evrmem/
├── src/qmd/                    # Source package
│   ├── __init__.py             # Package metadata (__version__)
│   ├── __main__.py             # Entry point: python -m qmd
│   │                              Sets HF_HUB_OFFLINE before any imports
│   ├── cli.py                  # CLI parser + command routing
│   │                              Global options → subcommand dispatch
│   ├── core/
│   │   ├── config.py           # Config loader (YAML + ENV, lazy singleton)
│   │   ├── embedding.py        # EmbeddingModel class (lazy-loaded ST model)
│   │   └── vector_db.py        # VectorDB class (ChromaDB wrapper, singleton)
│   └── utils/
│       └── console.py          # Windows UTF-8 console fix
├── docs/                       # Documentation
├── config.yaml                 # Default config (in repo root)
├── pyproject.toml              # pip package metadata
├── LICENSE                     # MIT
├── evrmem.bat                  # Windows launcher (sets HF_HUB_OFFLINE)
└── evrmem.sh                   # Unix launcher
```

### Core Components

#### 1. Config Loader (`core/config.py`)

Loads configuration from three sources with cascading priority:

```
CLI arguments  (highest)
    ↓
Environment variables  (e.g. EVREM_MODEL_NAME)
    ↓
YAML config file  (config.yaml in project root or ~/.evrmem/)
    ↓
Hard-coded defaults  (lowest)
```

Key implementation detail: `Config` uses a flat key-value dict with dot notation (e.g., `"embedding.model_name"`). The `_merge_yaml()` method flattens nested YAML dicts automatically.

#### 2. Embedding Model (`core/embedding.py`)

`EmbeddingModel` class wraps `SentenceTransformer` with:

- **Lazy loading**: Model is not loaded until first use (`encode()` or `dimension` property)
- **Offline mode**: `_resolve_local_model()` walks the HuggingFace cache directory structure to find the actual model snapshot path, bypassing the library's network lookup
- **Dimension caching**: `_dimension` is set once after model loads

```python
# Cache dir structure:
# cache_folder/
#   └── models--shibing624--text2vec-base-chinese/
#       └── snapshots/
#           └── {hash}/
#               ├── pytorch_model.bin
#               ├── sentence_bert_config.json  ← key file
#               └── config.json

model_path = _resolve_local_model()
# Returns: "D:/.../models/models--shibing624--text2vec-base-chinese/snapshots/{hash}/"

self._model = SentenceTransformer(
    model_path,
    device=self.device,
    cache_folder=self.cache_folder,
    local_files_only=True,  # Enforce offline
)
```

**Why local_files_only=True?** Because `SentenceTransformer` with just a cache folder path will still attempt network requests to resolve metadata. Adding `local_files_only=True` ensures zero network I/O.

#### 3. VectorDB (`core/vector_db.py`)

`VectorDB` wraps ChromaDB with:

- **Singleton pattern**: Only one `_client` and `_collection` instance per process
- **Lazy DB init**: `_init_db()` called on first operation (not on import)
- **Metadata storage**: Each memory stores arbitrary metadata dict alongside the vector
- **Normalized similarity**: Converts ChromaDB cosine distance to similarity score

```python
# Distance → Similarity conversion
similarity = 1 - distance  # ChromaDB uses L2 distance by default
```

#### 4. CLI (`cli.py`)

Entry flow:

```
py -m qmd stats
    ↓
__main__.py: sets HF_HUB_OFFLINE=1, TRANSFORMERS_OFFLINE=1
    ↓
cli.main(): argparse → parse args
    ↓
reload_config(config_file): rebuild Config singleton
    ↓
setup_logging(level): configure logging (WARNING default)
    ↓
command dispatch: cmd_stats(args) → VectorDB.count + EmbeddingModel.dimension
```

**Why `_get_emb()` instead of importing `get_embedding_model` at top level?**
Because `get_embedding_model()` creates a global singleton. If imported at module level, it runs before `reload_config()`, causing config to use default values instead of CLI overrides.

### Offline Mode Deep Dive

The offline mode works through two layers:

**Layer 1: Environment variables** (set in `__main__.py` / `evrmem.bat`)

```python
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
```

This prevents `transformers` library from making any network requests.

**Layer 2: SentenceTransformer parameters** (in `embedding.py`)

```python
SentenceTransformer(
    model_path,           # Direct snapshot path (not HF model name)
    cache_folder=...,     # Points to local cache
    local_files_only=True # Fails fast if file not found locally
)
```

Together these ensure that even if the library tries to make a request, it fails gracefully and falls back to the local cache.

### Adding a New CLI Command

1. Add handler function in `cli.py`:

```python
def cmd_export(args):
    """Export memories to JSON/CSV"""
    # ... implementation
```

2. Register in `main()` dispatch:

```python
elif args.command == "export":
    cmd_export(args)
```

3. Add subparser in `build_parser()`:

```python
p_export = subparsers.add_parser("export", help="导出记忆")
p_export.add_argument("-f", "--format", choices=["json", "csv"], default="json")
```

### Testing

```bash
# Manual test
py -m qmd stats
py -m qmd search "test query" -k 3
py -m qmd add "test memory" -p test

# Offline mode verification (Wireshark/Fiddler or block network)
# Should see zero HTTP requests to huggingface.co
```

---

## 中文

### 项目结构详解

```
evrmem/
├── src/qmd/
│   ├── __init__.py      # 包元数据（版本号）
│   ├── __main__.py      # python -m qmd 入口
│   │                      在所有导入前设置 HF_HUB_OFFLINE
│   ├── cli.py           # CLI 解析器 + 命令路由
│   ├── core/
│   │   ├── config.py    # 配置加载器（YAML + ENV，延迟单例）
│   │   ├── embedding.py # EmbeddingModel 类（ST 模型延迟加载）
│   │   └── vector_db.py # VectorDB 类（ChromaDB 封装，单例）
│   └── utils/
│       └── console.py   # Windows UTF-8 控制台修复
├── docs/
│   └── DEVELOPMENT.md   # 本文档
├── config.yaml          # 默认配置
├── pyproject.toml       # pip 包配置
├── LICENSE              # MIT 协议
├── evrmem.bat           # Windows 启动器
└── evrmem.sh           # Unix 启动器
```

### 核心组件解析

#### 配置加载器 (`core/config.py`)

三层配置，优先级递减：

```
CLI 参数  (最高)
    ↓
环境变量  (如 EVREM_MODEL_NAME)
    ↓
YAML 文件  (config.yaml)
    ↓
硬编码默认值  (最低)
```

实现要点：`Config` 用扁平字典存储，用点号作为 key（如 `"embedding.model_name"`）。`_merge_yaml()` 自动将嵌套 YAML 扁平化。

#### Embedding 模型 (`core/embedding.py`)

`EmbeddingModel` 对 `SentenceTransformer` 的封装：

- **延迟加载**：模型在使用前不加载（`encode()` 或 `dimension` 属性触发）
- **离线模式**：`_resolve_local_model()` 手动解析 HF 缓存目录结构，找到实际 snapshot 路径
- **维度缓存**：`_dimension` 加载后设置一次，后续访问直接返回

```python
# HuggingFace 缓存目录结构:
# cache_folder/
#   └── models--shibing624--text2vec-base-chinese/
#       └── snapshots/
#           └── {hash}/
#               ├── pytorch_model.bin
#               ├── sentence_bert_config.json  ← 关键文件
#               └── config.json

# 离线加载三保险:
SentenceTransformer(
    model_path,            # 直接传 snapshot 路径，不传 HF 模型名
    cache_folder=...,      # 指向本地缓存目录
    local_files_only=True  # 本地找不到就直接报错，不尝试网络
)
```

#### VectorDB (`core/vector_db.py`)

- **单例模式**：每个进程只有一个 `_client` 和 `_collection`
- **延迟初始化**：不在 import 时初始化，在第一次操作时调用 `_init_db()`
- **相似度转换**：`similarity = 1 - distance`（ChromaDB 默认用 L2 距离）

#### CLI 入口 (`cli.py`)

执行流程：

```
py -m qmd stats
    ↓
__main__.py: 设置 HF_HUB_OFFLINE=1, TRANSFORMERS_OFFLINE=1
    ↓
cli.main(): 解析命令行参数
    ↓
reload_config(): 重建 Config 单例（应用 CLI 参数覆盖）
    ↓
setup_logging(): 配置日志（默认 WARNING 级别）
    ↓
命令分发: cmd_stats(args)
    ↓
VectorDB.count + EmbeddingModel.dimension
```

**为什么用 `_get_emb()` 而不是在顶部导入 `get_embedding_model`？**
因为 `get_embedding_model()` 会创建全局单例。如果在模块顶部导入，会在 `reload_config()` 之前执行，导致 config 使用默认值而非 CLI 参数覆盖的值。

### 添加新 CLI 命令

1. 在 `cli.py` 添加处理函数：

```python
def cmd_export(args):
    """导出记忆到 JSON/CSV"""
    # ... 实现
```

2. 在 `main()` 中注册分发：

```python
elif args.command == "export":
    cmd_export(args)
```

3. 在 `build_parser()` 添加子解析器：

```python
p_export = subparsers.add_parser("export", help="导出记忆")
p_export.add_argument("-f", "--format", choices=["json", "csv"], default="json")
```

### 离线模式原理

两层保证：

**第一层：环境变量**（在 `__main__.py` / `evrmem.bat` 中设置）

```python
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
```

防止 `transformers` 库发起任何网络请求。

**第二层：SentenceTransformer 参数**

```python
SentenceTransformer(
    model_path,           # 直接传 snapshot 路径
    cache_folder=...,    # 指向本地缓存
    local_files_only=True # 本地找不到就直接报错
)
```

两层配合，即使库内部尝试发请求也会快速失败，回退到本地缓存。

### 本地测试

```bash
# 基础功能测试
py -m qmd stats          # 应显示 记忆总数 + 向量维度
py -m qmd search "test"  # 应返回语义相关记忆
py -m qmd add "测试记忆" -p test  # 应成功添加

# 离线验证（抓包工具观察）
# 应看到零次到 huggingface.co 的 HTTP 请求
```

### 下一步开发方向

- [ ] 添加单元测试（pytest + pytest-cov）
- [ ] 支持更多 Embedding 模型（bilingual / multilingual）
- [ ] 记忆导入/导出（JSON、Markdown）
- [ ] Git 集成（自动记录代码变更上下文）
- [ ] Web UI 界面
- [ ] 多工作区支持
