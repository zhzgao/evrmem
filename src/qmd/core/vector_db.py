"""
QMD VectorDB 模块
基于 ChromaDB 实现向量存储和检索
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings

from ..core.config import get_config
from ..core.embedding import get_embedding_model

logger = logging.getLogger(__name__)


class VectorDB:
    """向量数据库封装"""

    _instance: Optional["VectorDB"] = None
    _client = None
    _collection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _init_db(self):
        """初始化数据库（延迟加载）"""
        if self._client is not None:
            return

        config = get_config()
        persist_dir = config.get(
            "vector_db.persist_directory",
            str(Path.home() / ".evrmem" / "data" / "qmd_memory"),
        )

        # 确保目录存在
        Path(persist_dir).parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"初始化向量数据库: {persist_dir}")

        self._client = chromadb.PersistentClient(
            path=persist_dir, settings=Settings(anonymized_telemetry=False)
        )

        # 获取或创建记忆集合
        # 使用余弦距离：向量已归一化（normalize_embeddings=True），余弦距离 ∈ [0, 2]
        # similarity = 1 - cosine_distance，∈ [-1, 1]，值越大越相关
        self._collection = self._client.get_or_create_collection(
            name="memory",
            metadata={
                "description": "QMD Vector Memory Store",
                "hnsw:space": "cosine",  # 使用余弦距离，比 L2 更适合归一化向量
            },
        )

        logger.info(f"向量数据库初始化完成，集合大小: {self._collection.count()}")

    @property
    def _embedding(self):
        """获取 Embedding 模型（延迟加载）"""
        config = get_config()
        return get_embedding_model(
            model_name=config.get("embedding.model_name"),
            local_path=config.get("embedding.local_path"),
            device=config.get("embedding.device", "cpu"),
            cache_folder=config.get("embedding.cache_folder"),
        )

    def add_memory(
        self, content: str, metadata: Optional[Dict[str, Any]] = None, memory_id: Optional[str] = None
    ) -> str:
        """添加记忆"""
        self._init_db()

        if memory_id is None:
            memory_id = str(uuid.uuid4())

        if metadata is None:
            metadata = {}
        metadata["created_at"] = datetime.now().isoformat()
        metadata["access_count"] = 0

        embedding = self._embedding.encode(content)

        self._collection.add(
            ids=[memory_id],
            embeddings=embedding,
            documents=[content],
            metadatas=[metadata],
        )

        logger.info(f"记忆添加成功: {memory_id}")
        return memory_id

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.0,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """语义搜索记忆"""
        self._init_db()

        query_embedding = self._embedding.encode(query)

        results = self._collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            where=filter_metadata,
            include=["documents", "metadatas", "distances"],
        )

        memories = []
        if results["ids"] and len(results["ids"]) > 0:
            for i, mem_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i]
                # ChromaDB 余弦距离 ∈ [0, 2]，相似度 = 1 - distance，∈ [-1, 1]
                # 值为 1 表示完全相同，0 表示正交，-1 表示完全相反
                similarity = 1 - distance

                if similarity >= min_similarity:
                    memories.append(
                        {
                            "id": mem_id,
                            "content": results["documents"][0][i],
                            "metadata": results["metadatas"][0][i],
                            "similarity": similarity,
                            "distance": distance,
                        }
                    )

        logger.info(f"语义搜索完成: query='{query}', 结果数={len(memories)}")
        return memories

    def query_by_metadata(
        self, filter_metadata: Dict[str, Any], limit: int = 100
    ) -> List[Dict[str, Any]]:
        """按元数据查询记忆"""
        self._init_db()

        results = self._collection.get(
            where=filter_metadata,
            limit=limit,
            include=["documents", "metadatas"],
        )

        memories = []
        if results["ids"]:
            for i, mem_id in enumerate(results["ids"]):
                memories.append(
                    {
                        "id": mem_id,
                        "content": results["documents"][i],
                        "metadata": results["metadatas"][i],
                    }
                )

        logger.info(f"元数据查询完成: filter={filter_metadata}, 结果数={len(memories)}")
        return memories

    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """获取单个记忆"""
        self._init_db()

        results = self._collection.get(
            ids=[memory_id],
            include=["documents", "metadatas"],
        )

        if not results["ids"]:
            return None

        return {
            "id": results["ids"][0],
            "content": results["documents"][0],
            "metadata": results["metadatas"][0],
        }

    def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """更新记忆"""
        self._init_db()

        update_data = {}

        if content is not None:
            embedding = self._embedding.encode(content)
            update_data["embeddings"] = [embedding]
            update_data["documents"] = [content]

        if metadata is not None:
            existing = self.get_memory(memory_id)
            if existing:
                new_metadata = {**existing["metadata"], **metadata}
                update_data["metadatas"] = [new_metadata]

        if update_data:
            self._collection.update(ids=[memory_id], **update_data)
            logger.info(f"记忆更新成功: {memory_id}")
            return True

        return False

    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        self._init_db()

        try:
            self._collection.delete(ids=[memory_id])
            logger.info(f"记忆删除成功: {memory_id}")
            return True
        except Exception as e:
            logger.error(f"记忆删除失败: {e}")
            return False

    def get_all_memories(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """获取所有记忆"""
        self._init_db()

        results = self._collection.get(
            limit=limit,
            include=["documents", "metadatas"],
        )

        memories = []
        if results["ids"]:
            for i, mem_id in enumerate(results["ids"]):
                memories.append(
                    {
                        "id": mem_id,
                        "content": results["documents"][i],
                        "metadata": results["metadatas"][i],
                    }
                )

        return memories

    @property
    def count(self) -> int:
        """获取记忆总数"""
        self._init_db()
        return self._collection.count()


# 全局单例
vector_db = VectorDB()
