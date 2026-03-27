# 安装指南

## 系统要求

- Python 3.9+
- Windows / macOS / Linux

## 安装方式

### 方式 A：从源码安装（推荐开发者和贡献者）

```bash
git clone https://github.com/zhzgao/evrmem.git
cd evrmem
pip install -e .
```

### 方式 B：pip 安装（待发布后可用）

```bash
pip install evrmem
```

## 依赖说明

| 依赖 | 版本 | 说明 |
|------|------|------|
| chromadb | >= 0.4.0 | 向量数据库 |
| sentence-transformers | >= 2.0.0 | Embedding 模型 |
| pyyaml | >= 6.0 | 配置文件支持 |

## 首次运行

首次运行时会自动下载 Embedding 模型（约 400MB）：

```
📦 正在加载配置...
🔍 正在加载向量模型 (~6秒)...
✅ 系统初始化完成
```

> **提示**：下载后的模型会缓存到本地，后续运行无需网络。

## 离线使用

一旦模型缓存完成，evrmem 可以完全离线工作：

```bash
# 设置离线模式环境变量（可选，已自动启用）
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1
```

## 验证安装

```bash
evrmem -v
# 输出: evrmem v0.0.1

evrmem init
# 输出: ✅ 系统已就绪
```
