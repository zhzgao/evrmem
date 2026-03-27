# 配置指南

## 配置文件

evrmem 支持通过 YAML 配置文件进行自定义设置。

**配置文件路径**（按优先级）：

1. `./config.yaml`（项目根目录）
2. `~/.evrmem/config.yaml`（用户目录）

## 完整配置示例

```yaml
# config.yaml

vector_db:
  persist_directory: "~/.evrmem/data/qmd_memory"  # 数据持久化目录

embedding:
  model_name: "shibing624/text2vec-base-chinese"  # HuggingFace 模型名
  cache_folder: "~/.evrmem/models"                # 本地模型缓存目录
  device: "cpu"                                     # 计算设备: cpu 或 cuda
  local_files_only: true                            # 强制离线模式

rag:
  top_k: 5                   # 默认检索条数
  min_similarity: 0.5        # 最小相似度阈值
  prompt_template: |         # 可选：自定义提示词模板
    基于以下记忆回答问题：
    {context}
    
    ---
    问题：{query}
    
    回答：

logging:
  level: "WARNING"           # 日志级别: DEBUG, INFO, WARNING, ERROR
  file: "~/.evrmem/logs/qmd.log"  # 日志文件路径
```

## 配置项说明

### vector_db

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `persist_directory` | string | `~/.evrmem/data/qmd_memory` | ChromaDB 数据持久化目录 |

### embedding

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `model_name` | string | `shibing624/text2vec-base-chinese` | HuggingFace 模型名称 |
| `cache_folder` | string | `~/.evrmem/models` | 本地模型缓存目录 |
| `device` | string | `cpu` | 计算设备 (`cpu` 或 `cuda`) |
| `local_files_only` | bool | `true` | 强制离线模式，不下载模型 |

### rag

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `top_k` | int | `5` | 默认检索返回条数 |
| `min_similarity` | float | `0.5` | 最小相似度 (0-1) |

### logging

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `level` | string | `WARNING` | 日志级别 |
| `file` | string | - | 日志文件路径（可选） |

## 环境变量

环境变量优先级最高，会覆盖配置文件中的设置。

| 环境变量 | 配置项 | 说明 |
|----------|--------|------|
| `EVREM_MODEL_NAME` | `embedding.model_name` | HuggingFace 模型名 |
| `EVREM_LOCAL_MODEL` | `embedding.local_path` | 本地模型路径（最高优先级） |
| `EVREM_DEVICE` | `embedding.device` | 计算设备 |
| `EVREM_DATA_DIR` | `vector_db.persist_directory` | 数据目录 |
| `EVREM_TOP_K` | `rag.top_k` | 默认检索条数 |
| `EVREM_LOG_LEVEL` | `logging.level` | 日志级别 |

**示例**：

```bash
# Linux/macOS
export EVREM_DEVICE=cuda
export EVREM_TOP_K=10

# Windows
set EVREM_DEVICE=cuda
set EVREM_TOP_K=10
```

## 模型路径解析

evrmem 支持多种模型指定方式，按优先级排序：

1. **环境变量** `EVREM_LOCAL_MODEL`
2. **配置文件** `embedding.local_path`
3. **HuggingFace 缓存** `~/.cache/huggingface/hub/`
4. **项目缓存** `embedding.cache_folder`

离线模式下，优先从本地缓存加载模型。
