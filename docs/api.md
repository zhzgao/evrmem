# Python API

evrmem 提供完整的 Python API，可嵌入到任何 Python 项目中。

## 核心模块

### 向量数据库

```python
from qmd.core.vector_db import vector_db

# 添加记忆
memory_id = vector_db.add_memory(
    content="React StrictMode 导致 Form.useForm 警告",
    metadata={
        "project": "mes-demo",
        "tags": "react,antd",
        "date": "2026-03-27",
        "type": "bugfix"
    }
)
print(f"记忆 ID: {memory_id}")

# 语义搜索
results = vector_db.search(
    query="react antd form warning",
    top_k=5,
    min_similarity=0.5
)
for r in results:
    print(f"内容: {r['content']}")
    print(f"相似度: {r['distance']:.4f}")
    print(f"元数据: {r['metadata']}")
    print("---")

# 按元数据查询
results = vector_db.query_by_metadata({
    "project": "mes-demo",
    "tags": {"$contains": "react"}
})

# 获取单条记忆
memory = vector_db.get_memory(memory_id)
print(memory)

# 删除记忆
vector_db.delete_memory(memory_id)

# 统计信息
stats = vector_db.get_stats()
print(stats)
```

### Embedding 模型

```python
from qmd.core.embedding import get_embedding_model

# 获取模型实例（延迟加载）
emb = get_embedding_model()

# 编码单个文本
vec = emb.encode("你好世界")
print(f"向量维度: {len(vec)}")  # 768

# 批量编码
texts = ["第一个文本", "第二个文本", "第三个文本"]
vectors = emb.encode(texts)
print(f"向量矩阵形状: {vectors.shape}")  # (3, 768)

# 直接获取原始向量（用于 RAG）
raw_vec = emb.encode_raw("查询文本")
```

### 配置管理

```python
from qmd.core.config import get_config

# 获取配置
config = get_config()

# 访问配置项
print(config.embedding.model_name)      # shibing624/text2vec-base-chinese
print(config.embedding.device)          # cpu
print(config.rag.top_k)                  # 5
print(config.vector_db.persist_directory)

# 重新加载配置
config.reload()
```

## 完整示例

```python
from qmd.core.vector_db import vector_db
from qmd.core.embedding import get_embedding_model

# 1. 初始化系统
vector_db.initialize()

# 2. 添加记忆
vector_db.add_memory(
    content="Ant Design Form.useForm 在 React.StrictMode 下会报警告",
    metadata={"project": "mes-demo", "tags": "antd,react"}
)

# 3. RAG 检索
embedding = get_embedding_model()
query_vec = embedding.encode_raw("React 表单警告解决方法")

results = vector_db.search_by_vector(
    query_vector=query_vec,
    top_k=3
)

# 4. 构建 LLM 提示词
context = "\n".join([r['content'] for r in results])
prompt = f"""基于以下记忆回答问题：

{context}

---

问题：{user_question}

回答："""
print(prompt)
```

## 错误处理

```python
from qmd.core.vector_db import VectorDBError
from qmd.core.embedding import EmbeddingError

try:
    vector_db.add_memory("内容", metadata={})
except VectorDBError as e:
    print(f"向量数据库错误: {e}")

try:
    emb = get_embedding_model()
except EmbeddingError as e:
    print(f"模型加载错误: {e}")
```
