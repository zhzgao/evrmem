# CLI 命令参考

## 命令概览

| 命令 | 说明 |
|------|------|
| `evrmem add` | 添加记忆 |
| `evrmem search` | 语义搜索 |
| `evrmem rag` | RAG 检索 |
| `evrmem query` | 结构化查询 |
| `evrmem delete` | 删除记忆 |
| `evrmem stats` | 查看统计 |
| `evrmem init` | 初始化系统 |

## evrmem add

添加新的记忆条目。

```bash
evrmem add "记忆内容" [选项]
```

**选项**：

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--project` | `-p` | 关联项目名 | `-p mes-demo` |
| `--tags` | `-t` | 标签（逗号分隔） | `-t react,antd` |
| `--date` | `-d` | 日期 (YYYY-MM-DD) | `-d 2026-03-27` |
| `--file` | `-f` | 从文件读取内容 | `-f ./note.md` |
| `--list` | `-l` | 从文本文件批量导入（每行一条） | `-l ./memories.txt` |

**示例**：

```bash
# 基本使用
evrmem add "React StrictMode 导致 Form.useForm 警告"

# 带元数据
evrmem add "修复了 Modal.confirm 警告" -p mes-demo -t antd,react

# 从文件导入
evrmem add -f ./API规范.md

# 批量导入（每行一条记忆）
evrmem add -l ./memories.txt
```

## evrmem search

语义搜索记忆。

```bash
evrmem search "查询内容" [选项]
```

**选项**：

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--top-k` | `-k` | 返回条数 | 5 |
| `--min-similarity` | `-s` | 最小相似度（余弦，范围 -1 ~ 1） | 0.0 |
| `--verbose` | `-v` | 详细输出（显示项目/标签/日期） | false |

**示例**：

```bash
# 基本搜索
evrmem search "React 表单警告"

# 精确搜索，显示详细信息
evrmem search "Modal.confirm" -k 3 -v

# 交互模式（不传 query 直接回车）
evrmem search
```

## evrmem rag

RAG 增强检索，生成可用于 LLM 的提示词。

```bash
evrmem rag "查询内容" [选项]
```

**选项**：

| 参数 | 简写 | 说明 |
|------|------|------|
| `--top-k` | `-k` | 检索条数 |
| `--min-similarity` | `-s` | 最小相似度 |
| `--prompt` | `-p` | 生成完整提示词模板 |
| `--verbose` | `-v` | 显示原始检索结果 |

**示例**：

```bash
# 基本 RAG
evrmem rag "如何修复 React 表单警告"

# 生成完整提示词
evrmem rag "解释 styled-jsx 的用法" --prompt

# 详细输出
evrmem rag "React Form 最佳实践" -v
```

## evrmem query

结构化查询，按元数据筛选。

```bash
evrmem query [选项]
```

**选项**：

| 参数 | 说明 |
|------|------|
| `--project <name>` | 按项目筛选 |
| `--tag <tag>` | 按标签筛选 |
| `--date <YYYY-MM-DD>` | 按日期筛选 |
| `--type <type>` | 按类型筛选 |
| `--list-projects` | 列出所有项目 |
| `--list-tags` | 列出所有标签 |

**示例**：

```bash
# 查看某项目所有记忆
evrmem query --project mes-demo

# 查看某标签所有记忆
evrmem query --tag react

# 组合筛选
evrmem query --project mes-demo --tag antd

# 列出所有项目
evrmem query --list-projects
```

## evrmem delete

删除指定 ID 的记忆，删除前会显示预览并请求确认。

```bash
evrmem delete <ID>
```

**参数**：

| 参数 | 说明 |
|------|------|
| `<ID>` | 记忆 ID（通过 `evrmem search -v` 或 `evrmem query` 获取）|
| `-y` / `--yes` | 跳过确认提示，直接删除 |

**示例**：

```bash
# 交互式删除（会显示内容预览并请求确认）
evrmem delete a1b2c3d4-...

# 非交互式删除（用于脚本）
evrmem delete a1b2c3d4-... --yes
```

## evrmem stats

查看系统状态和统计信息。

```bash
evrmem stats
```

**输出示例**：

```
📊 evrmem 统计信息
─────────────────
总记忆数: 42
项目数: 5
标签数: 23
Embedding: text2vec-base-chinese
向量维度: 768
数据目录: ~/.evrmem/data/qmd_memory
```

## evrmem init

初始化或检查系统状态。

```bash
evrmem init
```
