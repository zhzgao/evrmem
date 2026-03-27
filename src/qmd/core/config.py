"""
QMD 配置加载器
支持 YAML 配置文件 + 环境变量覆盖
优先级: CLI参数 > 环境变量 > 配置文件 > 默认值
"""

import os
import sys
from pathlib import Path
from typing import Optional

import yaml


class Config:
    """QMD 配置类"""

    # 默认配置
    DEFAULTS = {
        # 向量数据库
        "vector_db.type": "chroma",
        "vector_db.persist_directory": str(
            Path.home() / ".evrmem" / "data" / "qmd_memory"
        ),
        # Embedding 模型
        "embedding.model_name": "shibing624/text2vec-base-chinese",
        "embedding.device": "cpu",
        "embedding.cache_folder": str(Path.home() / ".evrmem" / "models"),
        "embedding.local_path": None,  # 本地模型路径（优先级最高）
        # 备份
        "backup.directory": str(Path.home() / ".evrmem" / "data" / "memory_backup"),
        # RAG
        "rag.top_k": 5,
        "rag.min_similarity": 0.5,
        # 日志
        "logging.level": "INFO",
        "logging.file": str(Path.home() / ".evrmem" / "logs" / "qmd.log"),
    }

    def __init__(self, config_file: Optional[str] = None):
        self._config = {}
        self._load_defaults()
        self._load_from_file(config_file)
        self._load_from_env()

    def _load_defaults(self):
        """加载默认配置"""
        for key, value in self.DEFAULTS.items():
            self._config[key] = value

    def _load_from_file(self, config_file: Optional[str] = None):
        """从 YAML 文件加载配置"""
        if config_file is None:
            # 尝试从默认位置加载
            default_locations = [
                Path.cwd() / "config.yaml",
                Path(__file__).parent.parent.parent.parent / "config.yaml",
                Path.home() / ".evrmem" / "config.yaml",
            ]
            for loc in default_locations:
                if loc.exists():
                    config_file = str(loc)
                    break

        if config_file and Path(config_file).exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    yaml_config = yaml.safe_load(f)
                self._merge_yaml(yaml_config)
            except Exception as e:
                print(f"Warning: Failed to load config from {config_file}: {e}")

    def _merge_yaml(self, yaml_config: dict):
        """合并 YAML 配置到扁平字典"""
        def flatten(d, prefix=""):
            result = {}
            for k, v in d.items():
                new_key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    result.update(flatten(v, new_key))
                else:
                    result[new_key] = v
            return result

        flat = flatten(yaml_config)
        for key, value in flat.items():
            if key in self._config or key.startswith(
                ("vector_db", "embedding", "backup", "rag", "logging")
            ):
                self._config[key] = value

    def _load_from_env(self):
        """从环境变量加载配置（优先级最高）"""
        env_mappings = {
            "EVREM_MODEL_NAME": ("embedding.model_name", str),
            "EVREM_LOCAL_MODEL": ("embedding.local_path", str),
            "EVREM_DEVICE": ("embedding.device", str),
            "EVREM_CACHE": ("embedding.cache_folder", str),
            "EVREM_DATA_DIR": ("vector_db.persist_directory", str),
            "EVREM_TOP_K": ("rag.top_k", int),
            "EVREM_MIN_SIM": ("rag.min_similarity", float),
            "EVREM_LOG_LEVEL": ("logging.level", str),
        }

        for env_var, (config_key, type_fn) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                try:
                    self._config[config_key] = type_fn(value)
                except ValueError:
                    pass

    def get(self, key: str, default=None):
        """获取配置值"""
        return self._config.get(key, default)

    def __getitem__(self, key: str):
        return self._config[key]

    def __getattr__(self, name: str):
        # 兼容旧代码：config.xxx → config.get("xxx")
        if name.startswith("_"):
            return super().__getattribute__(name)
        # 尝试直接匹配
        if name in self._config:
            return self._config[name]
        # 尝试 legacy 方式（直接属性访问）
        return self.get(name)


# 全局配置实例（延迟加载）
_config: Optional[Config] = None


def get_config(config_file: Optional[str] = None) -> Config:
    """获取配置单例"""
    global _config
    if _config is None:
        _config = Config(config_file)
    return _config


def reload_config(config_file: Optional[str] = None):
    """重新加载配置"""
    global _config
    _config = Config(config_file)
    return _config
