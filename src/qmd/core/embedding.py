"""
QMD Embedding 模块
支持本地模型和 HuggingFace 模型
"""

import os
from pathlib import Path
from typing import List, Optional, Union


class EmbeddingModel:
    """
    向量嵌入模型封装

    支持两种模式：
    1. 本地模型：指定 local_path，优先使用
    2. HuggingFace 模型：通过 model_name 下载/加载
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        local_path: Optional[str] = None,
        device: str = "cpu",
        cache_folder: Optional[str] = None,
    ):
        """
        Args:
            model_name: HuggingFace 模型名称（如 shibing624/text2vec-base-chinese）
            local_path: 本地模型路径（优先于 model_name）
            device: 设备（cpu/cuda）
            cache_folder: 模型缓存目录
        """
        self.model_name = model_name or "shibing624/text2vec-base-chinese"
        self.local_path = local_path
        self.device = device
        self.cache_folder = cache_folder

        self._model = None
        self._dimension = None

    def _load_model(self):
        """延迟加载模型"""
        if self._model is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "请安装 sentence-transformers: pip install sentence-transformers"
            )

        # 确定模型路径（优先用 cache_folder + 自动解析，确保传给 ST 的是实际 snapshot 目录）
        if self.local_path:
            model_path = self.local_path
            print(f"  ⏳ 加载本地模型: {model_path}", flush=True)
        elif self.cache_folder:
            model_path = self._resolve_local_model()
            print(f"  ⏳ 加载向量模型（首次约需 5~10 秒，请稍候）...", flush=True)
        else:
            model_path = self.model_name
            print(f"  ⏳ 加载向量模型: {model_path}（首次约需 5~10 秒）...", flush=True)

        self._model = SentenceTransformer(
            model_path,
            device=self.device,
            cache_folder=self.cache_folder,
            local_files_only=True,
        )
        self._dimension = self._model.get_sentence_embedding_dimension()
        print(f"  ✅ 模型加载完成（维度: {self._dimension}）", flush=True)

    def _resolve_local_model(self) -> str:
        """
        从 cache_folder 解析本地模型路径
        sentence-transformers 5.x 的 HF 模型名缓存有兼容性问题，
        缓存目录格式是: cache_folder/models--{org}--{name}/snapshots/{hash}/
        """
        if not self.cache_folder:
            return self.model_name

        cache_root = Path(self.cache_folder)
        # HuggingFace 缓存目录命名格式: models--{org}--{name}
        # 例如: models--shibing624--text2vec-base-chinese
        model_dir_name = f"models--{self.model_name.replace('/', '--')}"
        model_dir = cache_root / model_dir_name

        if not model_dir.exists():
            return self.model_name

        # 查找 snapshot
        snapshots = model_dir / "snapshots"
        if snapshots.exists():
            for snap in snapshots.iterdir():
                if snap.is_dir():
                    # 检查是否有 sentence-transformers 配置
                    config_file = snap / "sentence_bert_config.json"
                    if config_file.exists():
                        return str(snap)

        return self.model_name

    def encode(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """
        将文本编码为向量

        Args:
            texts: 单个文本或文本列表

        Returns:
            向量列表，每个向量为 float 列表
        """
        self._load_model()

        if isinstance(texts, str):
            texts = [texts]

        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        """获取向量维度"""
        self._load_model()
        return self._dimension

    @property
    def model_info(self) -> dict:
        """获取模型信息"""
        return {
            "model_name": self.model_name,
            "local_path": self.local_path,
            "device": self.device,
            "dimension": self.dimension if self._model else "未加载",
        }


# 全局实例（延迟加载）
_embedding_model: Optional[EmbeddingModel] = None


def get_embedding_model(
    model_name: Optional[str] = None,
    local_path: Optional[str] = None,
    device: str = "cpu",
    cache_folder: Optional[str] = None,
) -> EmbeddingModel:
    """获取 Embedding 模型单例"""
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = EmbeddingModel(
            model_name=model_name,
            local_path=local_path,
            device=device,
            cache_folder=cache_folder,
        )

    return _embedding_model
