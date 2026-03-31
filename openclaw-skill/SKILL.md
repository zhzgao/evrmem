---
name: evrmem-openclaw
description: OpenClaw skill for evrmem - Local Chinese vector memory system. Enables semantic memory search and storage for AI agents.
version: 1.0.0
---

# Evrmem OpenClaw Skill

OpenClaw skill for [evrmem](https://github.com/zhzgao/evrmem) - 本地化中文向量记忆系统。

## Overview

This skill integrates evrmem with OpenClaw, providing:
- 🔍 **Semantic Memory Search** - Search memories using natural language
- 💾 **Memory Storage** - Save important information to vector database
- 🏷️ **Tag-based Organization** - Organize memories by projects and tags
- 📊 **RAG Support** - Context-augmented generation for LLMs

## Prerequisites

1. Install evrmem:
```bash
pip install evrmem
```

2. Initialize evrmem (downloads ~400MB model on first run):
```bash
evrmem init
```

For users in China, use mirror:
```bash
export HF_ENDPOINT=https://hf-mirror.com
evrmem init
```

## Usage

### Search Memories

```bash
# Semantic search
evrmem search "React form warning"

# Search within project
evrmem search "deployment issue" --project myproject

# Interactive mode
evrmem search
```

### Add Memory

```bash
# Add memory with metadata
evrmem add "React StrictMode causes Form.useForm warning" \
  --project mes-demo \
  --tags react,antd

# Add from file
evrmem add -f ./notes.md --project docs --tags meeting
```

### Structured Query

```bash
# Query by project
evrmem query --project mes-demo

# Query by tag
evrmem query --tag react

# List all projects
evrmem query --list-projects

# List all tags
evrmem query --list-tags
```

### RAG Retrieval

```bash
# Generate context-augmented prompt
evrmem rag "how to fix the form warning" --prompt

# Interactive RAG
evrmem rag
```

### Statistics

```bash
evrmem stats
```

## Configuration

Create `~/.evrmem/config.yaml`:

```yaml
vector_db:
  persist_directory: "~/.evrmem/data/qmd_memory"

embedding:
  model_name: "shibing624/text2vec-base-chinese"
  device: "cpu"  # or "cuda"
  cache_folder: "~/.evrmem/models"

rag:
  top_k: 5
  min_similarity: 0.5

logging:
  level: "WARNING"
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `EVREM_DATA_DIR` | Data directory | `~/.evrmem/data/qmd_memory` |
| `EVREM_MODEL_NAME` | HuggingFace model name | `shibing624/text2vec-base-chinese` |
| `EVREM_LOCAL_MODEL` | Local model path (highest priority) | - |
| `EVREM_DEVICE` | Device for inference | `cpu` |
| `EVREM_TOP_K` | Default retrieval count | `5` |
| `EVREM_MIN_SIM` | Minimum similarity threshold | `0.5` |
| `EVREM_LOG_LEVEL` | Logging level | `WARNING` |
| `EVREM_LOCAL_FILES_ONLY` | Disable network access | `false` |
| `HF_ENDPOINT` | HuggingFace mirror endpoint | - |

## Python API

```python
from qmd.core.vector_db import vector_db
from qmd.core.embedding import get_embedding_model

# Add memory
memory_id = vector_db.add_memory(
    "React StrictMode causes Form.useForm warning",
    metadata={"project": "mes-demo", "tags": "react,antd"}
)

# Search
results = vector_db.search("react form warning", top_k=5)

# Query by metadata
results = vector_db.query_by_metadata({"project": "mes-demo"})

# Get embedding model
emb = get_embedding_model()
vec = emb.encode("hello world")
print(f"Dimension: {emb.dimension}")  # 768
```

## Integration with OpenClaw

When this skill is loaded, OpenClaw agents can:

1. **Recall past interactions** - Search for relevant memories before answering
2. **Store new knowledge** - Save important information for future use
3. **Maintain context** - Use RAG to augment responses with stored knowledge

Example workflow:
```
User: "How do I fix the React form warning?"
Agent: [searches evrmem for "React form warning"]
Agent: [finds relevant memory about StrictMode]
Agent: [provides answer based on stored knowledge]
Agent: [optionally saves new findings to evrmem]
```

## Troubleshooting

### Model Download Issues

If model download fails:
```bash
# Use Chinese mirror
export HF_ENDPOINT=https://hf-mirror.com
evrmem init
```

### NumPy Compatibility

If you encounter NumPy errors:
```bash
pip install "numpy<2" --force-reinstall
```

### Offline Mode

For air-gapped environments:
1. Download model on a connected machine
2. Copy `~/.evrmem/models` to the offline machine
3. Set `EVREM_LOCAL_FILES_ONLY=true`

## License

MIT - See [LICENSE](../LICENSE)

## Contributing

Contributions welcome! See [CONTRIBUTING.md](../CONTRIBUTING.md)