# Changelog / 更新日志

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.0.1] - 2026-03-27

### Added / 新增

- **pip 包结构** (`pyproject.toml`)：通过 `pip install -e .` 本地安装
- **统一 CLI 入口**：`evrmem add / search / rag / query / stats / init`
- **完整 Python API**：VectorDB 单例 + EmbeddingModel 懒加载
- **YAML 配置系统**：支持默认值 → YAML → 环境变量 → CLI 参数优先级
- **离线 Embedding 模型加载**：`_resolve_local_model()` 自动解析 HuggingFace 缓存目录
- **跨平台 UTF-8 控制台**：Windows PowerShell 中文/Emoji 正常显示
- **Markdown 备份**：每次添加记忆自动备份到 `data/memory_backup/`
- **交互模式**：search / rag 命令无参数时进入交互模式
- **批量添加**：支持从文本文件批量导入记忆

### Fixed / 修复

- 删除了遮盖 `qmd/` 包的旧占位文件 `qmd.py`
- 修正 HuggingFace 缓存目录名格式：`models--{org}--{name}`（含 `models--` 前缀）
- 修正 `config.yaml` 中 `local_path` 配置（移除误配的缓存根目录）
- 修复日志级别过于冗余（INFO → WARNING）

### Architecture / 架构

```
src/qmd/
├── cli.py           # argparse CLI + 命令路由
├── __main__.py      # python -m qmd 入口（含离线环境变量设置）
├── core/
│   ├── config.py    # 配置加载器（YAML + ENV）
│   ├── embedding.py # Embedding 模型封装
│   └── vector_db.py # ChromaDB 封装
└── utils/
    └── console.py   # Windows UTF-8 控制台修复
```

### Dependencies / 依赖

- `chromadb >= 0.4.0`
- `sentence-transformers >= 2.2.0`
- `pyyaml >= 6.0`

### Known Issues / 已知问题

- Embedding 模型首次加载需联网下载（约 400MB）
- GPU 加速需要 CUDA 环境

---

## [Unreleased] / 未来计划

- [ ] 发布到 PyPI
- [ ] 单元测试覆盖
- [ ] 支持更多 Embedding 模型（如 bilingual / multilingual）
- [ ] Web UI 界面
- [ ] 记忆导入/导出功能
- [ ] Git integration（自动记录代码变更上下文）
- [ ] 多用户/多工作区支持
