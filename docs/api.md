# Python API

evrmem 提供完整的 Python API，可嵌入到任何 Python 项目中。

## 核心模块

### 向量数据库

```python
from qmd.core.vector_db import vector_db

# 添加记忆，返回记忆 ID（UUID 字符串）
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

# 语义搜索，返回列表
# 每条结果包含: id, content, metadata, similarity, distance
results = vector_db.search(
    query="react antd form warning",
    top_k=5,
    min_similarity=0.5
)
for r in results:
    print(f"内容: {r['content']}")
    print(f"相似度: {r['similarity']:.4f}")  # 余弦相似度，范围 [-1, 1]，越大越相关
    print(f"元数据: {r['metadata']}")
    print("---")

# 按元数据查询
results = vector_db.query_by_metadata({
    "project": "mes-demo",
    "tags": {"$contains": "react"}
})

# 获取所有记忆（可设置上限）
all_memories = vector_db.get_all_memories(limit=1000)

# 获取单条记忆，不存在返回 None
memory = vector_db.get_memory(memory_id)
if memory:
    print(memory["content"])
    print(memory["metadata"])

# 更新记忆
vector_db.update_memory(
    memory_id=memory_id,
    content="新的内容（可选）",
    metadata={"tags": "react,antd,bugfix"}  # 会与原有元数据合并
)

# 删除记忆，返回 True/False
ok = vector_db.delete_memory(memory_id)
print("删除成功" if ok else "删除失败")

# 获取记忆总数
print(f"总记忆数: {vector_db.count}")
```

### Embedding 模型

```python
from qmd.core.embedding import get_embedding_model

# 获取模型实例（延迟加载，首次调用时加载模型）
emb = get_embedding_model()

# 编码文本，返回 List[List[float]]
# 单个文本会被包装成列表，始终返回二维结构
vecs = emb.encode("你好世界")   # → [[0.01, -0.23, ...]]
vecs = emb.encode(["文本1", "文本2"])  # → [[...], [...]]

# 查看向量维度
print(f"向量维度: {emb.dimension}")  # 768

# 查看模型信息
print(emb.model_info)
# {
#   "model_name": "shibing624/text2vec-base-chinese",
#   "local_path": None,
#   "device": "cpu",
#   "dimension": 768
# }
```

### 配置管理

```python
from qmd.core.config import get_config, reload_config

# 获取配置单例
config = get_config()

# 访问配置项（点分隔键）
print(config.get("embedding.model_name"))        # shibing624/text2vec-base-chinese
print(config.get("embedding.device"))            # cpu
print(config.get("rag.top_k"))                   # 5
print(config.get("vector_db.persist_directory")) # ~/.evrmem/data/qmd_memory

# 带默认值
print(config.get("rag.min_similarity", 0.5))

# 重新加载配置（指定配置文件路径或 None 表示自动查找）
config = reload_config("/path/to/config.yaml")
```

## 完整示例

```python
from qmd.core.vector_db import vector_db

# 1. 添加记忆（首次调用会自动初始化数据库和加载模型）
ids = []
for content, meta in [
    ("Ant Design Form.useForm 在 React.StrictMode 下会报警告",
     {"project": "mes-demo", "tags": "antd,react", "type": "bugfix"}),
    ("styled-jsx 需要安装 styled-jsx 包才能使用 jsx 属性",
     {"project": "mes-demo", "tags": "css,styled-jsx", "type": "note"}),
]:
    ids.append(vector_db.add_memory(content, meta))

# 2. 语义搜索
results = vector_db.search("React 表单警告解决方法", top_k=3, min_similarity=0.4)
for r in results:
    print(f"[{r['similarity']:.1%}] {r['content']}")

# 3. 构建 LLM 提示词
context = "\n".join(f"- {r['content']}" for r in results)
user_question = "antd form 有什么常见问题？"
prompt = f"""基于以下记忆回答问题：

{context}

---

问题：{user_question}

回答："""
print(prompt)

# 4. 清理（可选）
for mid in ids:
    vector_db.delete_memory(mid)
```

## 错误处理

evrmem 目前不抛出自定义异常类，错误通过以下方式处理：

- **`vector_db.get_memory()`**：找不到时返回 `None`，不抛异常
- **`vector_db.delete_memory()`**：失败时返回 `False`，不抛异常
- **模型加载失败**：若 `local_files_only=True` 且本地无缓存，会抛出 `OSError`

```python
# 推荐的错误处理方式
memory = vector_db.get_memory(some_id)
if memory is None:
    print("记忆不存在")
else:
    print(memory["content"])

# 模型加载可能的错误
try:
    results = vector_db.search("查询", top_k=3)
except OSError as e:
    print(f"模型加载失败，请检查缓存目录: {e}")
except Exception as e:
    print(f"搜索出错: {e}")
```
