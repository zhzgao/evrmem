"""
QMD CLI 主入口
统一命令: evrmem add / search / rag / query / stats / init
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from .core.config import get_config, reload_config
from .core.vector_db import vector_db

def _get_emb():
    """获取 Embedding 模型（使用全局配置）"""
    config = get_config()
    from .core.embedding import get_embedding_model
    return get_embedding_model(
        model_name=config.get("embedding.model_name"),
        local_path=config.get("embedding.local_path"),
        device=config.get("embedding.device", "cpu"),
        cache_folder=config.get("embedding.cache_folder"),
    )

# 版本号
__version__ = "0.0.1"

HELP_EPILOG = """
示例:
  evrmem add "今天的修复经验" --project mes-demo --tags react,bugfix
  evrmem search "React表单问题" --top-k 3
  evrmem rag "用户报告Tree报错" --top-k 5
  evrmem query --project mes-demo
  evrmem stats

环境变量:
  EVREM_MODEL_NAME     指定 HuggingFace 模型名称
  EVREM_LOCAL_MODEL    指定本地模型路径（优先）
  EVREM_DEVICE         设备 (cpu/cuda)
  EVREM_DATA_DIR       数据存储目录
  EVREM_TOP_K          默认检索条数
  EVREM_LOG_LEVEL      日志级别
"""


def setup_logging(level: str = "INFO"):
    """设置日志"""
    log_dir = Path.home() / ".evrmem" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # 跨平台 StreamHandler（UTF-8）
    if sys.platform == "win32":
        import io

        stream_handler = logging.StreamHandler(
            stream=io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
        )
    else:
        stream_handler = logging.StreamHandler()

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "qmd.log", encoding="utf-8"),
            stream_handler,
        ],
    )


def cmd_add(args):
    """添加记忆"""
    from datetime import datetime

    config = get_config()
    backup_dir = Path(config.get("backup.directory", str(Path.home() / ".evrmem" / "data" / "memory_backup")))
    backup_dir.mkdir(parents=True, exist_ok=True)

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
        metadata = {"type": "file", "source": args.file}
    elif args.list:
        # 批量添加
        with open(args.list, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        tags = args.tags.split(",") if args.tags else None
        results = []
        for i, line in enumerate(lines, 1):
            meta = {"type": "batch"}
            if args.project:
                meta["project"] = args.project
            if tags:
                meta["tags"] = ",".join(tags)
            mid = vector_db.add_memory(line, meta)
            results.append(mid)
            print(f"  [{i}/{len(lines)}] OK {mid[:8]}...")
        print(f"\n  {len(results)} 条记忆添加完成")
        return
    else:
        content = args.content

    if not content:
        print("  [ERROR] 内容不能为空")
        return

    metadata = {"type": "command"}
    if args.project:
        metadata["project"] = args.project
    if args.tags:
        metadata["tags"] = args.tags
    if args.date:
        metadata["date"] = args.date

    memory_id = vector_db.add_memory(content, metadata)

    # 备份到 Markdown
    date_str = datetime.now().strftime("%Y-%m-%d")
    backup_file = backup_dir / f"{date_str}.md"
    with open(backup_file, "a", encoding="utf-8") as f:
        f.write(f"\n## [{datetime.now().strftime('%H:%M:%S')}] {memory_id}\n\n{content}\n")

    print(f"  [OK] 记忆添加成功")
    print(f"  ID: {memory_id}")


def cmd_search(args):
    """语义搜索"""
    config = get_config()

    if not args.query:
        print("  [INFO] 进入交互模式，输入 q 退出\n")
        while True:
            q = input("  > ").strip()
            if q.lower() in ("q", "quit", "exit"):
                break
            if not q:
                continue
            _do_search(q, args.top_k, args.min_similarity, args.verbose)
        return

    _do_search(args.query, args.top_k, args.min_similarity, args.verbose)


def _do_search(query: str, top_k: int, min_sim: float, verbose: bool):
    results = vector_db.search(query, top_k=top_k, min_similarity=min_sim)
    if not results:
        print("  [EMPTY] 未找到相关记忆\n")
        return

    print(f"\n  找到 {len(results)} 条相关记忆:\n")
    for i, mem in enumerate(results, 1):
        sim = mem["similarity"]
        bar_len = int(sim * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        meta = mem["metadata"]
        content = mem["content"][:120] + "..." if len(mem["content"]) > 120 else mem["content"]

        print(f"  [{i}] 相似度: {bar} {sim:.1%}")
        print(f"      {content}")
        if verbose:
            parts = []
            if "project" in meta:
                parts.append(f"项目:{meta['project']}")
            if "date" in meta:
                parts.append(f"日期:{meta['date']}")
            if "tags" in meta:
                parts.append(f"标签:{meta['tags']}")
            if parts:
                print(f"      {' | '.join(parts)}")
        print()


def cmd_rag(args):
    """RAG 检索"""
    config = get_config()
    top_k = args.top_k or config.get("rag.top_k", 5)
    min_sim = args.min_similarity or config.get("rag.min_similarity", 0.5)

    if not args.query:
        print("  [INFO] 进入交互模式，输入 q 退出\n")
        while True:
            q = input("  > ").strip()
            if q.lower() in ("q", "quit", "exit"):
                break
            if not q:
                continue
            _do_rag(q, top_k, min_sim, args.prompt)
        return

    _do_rag(args.query, top_k, min_sim, args.prompt)


def _do_rag(query: str, top_k: int, min_sim: float, as_prompt: bool):
    results = vector_db.search(query, top_k=top_k, min_similarity=min_sim)
    if not results:
        print("  [EMPTY] 未找到相关记忆\n")
        return

    if as_prompt:
        # 生成完整提示词
        context_parts = []
        for i, mem in enumerate(results, 1):
            meta = mem["metadata"]
            header = f"【记忆 {i}】"
            if "project" in meta:
                header += f" 项目:{meta['project']}"
            if "date" in meta:
                header += f" 日期:{meta['date']}"
            context_parts.append(f"{header}\n{mem['content']}")

        context = "\n\n---\n\n".join(context_parts)
        prompt = f"""你是一个 AI 助手，以下是可能相关的记忆上下文:

---
{context}
---

请结合上述上下文回答用户的问题。

用户问题: {query}"""
        print("\n" + "=" * 60)
        print("生成的提示词")
        print("=" * 60)
        print(prompt)
        print("=" * 60)
    else:
        print(f"\n  RAG 检索结果 (Top {len(results)}):\n")
        for i, mem in enumerate(results, 1):
            meta = mem["metadata"]
            print(f"  【记忆 {i}】 相似度: {mem['similarity']:.1%}")
            parts = []
            if "project" in meta:
                parts.append(f"项目:{meta['project']}")
            if "date" in meta:
                parts.append(f"日期:{meta['date']}")
            if parts:
                print(f"      {' | '.join(parts)}")
            print(f"      {mem['content'][:200]}{'...' if len(mem['content']) > 200 else ''}")
            print()


def cmd_query(args):
    """结构化查询"""
    if args.list_projects:
        _list_projects()
        return
    if args.list_tags:
        _list_tags()
        return

    filters = {}
    if args.project:
        filters["project"] = args.project
    if args.date:
        filters["date"] = args.date
    if args.tag:
        filters["tags"] = {"$contains": args.tag}
    if args.type:
        filters["type"] = args.type

    if filters:
        results = vector_db.query_by_metadata(filters, limit=args.limit)
    else:
        results = vector_db.get_all_memories(limit=args.limit)

    if not results:
        print("  [EMPTY] 未找到记忆\n")
        return

    print(f"\n  找到 {len(results)} 条记忆:\n")
    for i, mem in enumerate(results, 1):
        meta = mem["metadata"]
        content = mem["content"][:100] + "..." if len(mem["content"]) > 100 else mem["content"]
        print(f"  [{i}] {content}")
        parts = []
        if "project" in meta:
            parts.append(f"项目:{meta['project']}")
        if "date" in meta:
            parts.append(f"日期:{meta['date']}")
        if "tags" in meta:
            parts.append(f"标签:{meta['tags']}")
        if parts:
            print(f"      {' | '.join(parts)}")
        print()


def _list_projects():
    all_mem = vector_db.get_all_memories(limit=10000)
    projects = {}
    for mem in all_mem:
        proj = mem["metadata"].get("project", "未分类")
        projects[proj] = projects.get(proj, 0) + 1

    print("\n  项目列表:\n")
    for proj, count in sorted(projects.items(), key=lambda x: -x[1]):
        print(f"    {proj}: {count} 条")
    print()


def _list_tags():
    all_mem = vector_db.get_all_memories(limit=10000)
    tags = {}
    for mem in all_mem:
        tags_str = mem["metadata"].get("tags", "")
        if tags_str:
            for tag in tags_str.split(","):
                tag = tag.strip()
                if tag:
                    tags[tag] = tags.get(tag, 0) + 1

    if not tags:
        print("\n  暂无标签\n")
        return

    print("\n  标签列表:\n")
    for tag, count in sorted(tags.items(), key=lambda x: -x[1]):
        print(f"    {tag}: {count} 条")
    print()


def cmd_stats(args):
    """统计信息"""
    print(f"\n  记忆总数: {vector_db.count}")

    emb = _get_emb()
    # 强制加载以获取维度
    _ = emb.dimension
    info = emb.model_info
    print(f"  模型: {info['model_name']}")
    if info["local_path"]:
        print(f"  本地模型: {info['local_path']}")
    print(f"  向量维度: {info['dimension']}")
    print(f"  设备: {info['device']}")
    print()


def cmd_init(args):
    """初始化向量数据库"""
    config = get_config()
    print(f"\n  向量维度: {_get_emb().dimension}")
    print(f"  记忆总数: {vector_db.count}")
    print(f"  数据库: {config.get('vector_db.persist_directory')}")
    print()


def build_parser() -> argparse.ArgumentParser:
    """构建命令行解析器"""
    parser = argparse.ArgumentParser(
        prog="evrmem",
        description="QMD - 本地化 AI 向量记忆系统",
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--version", "-v", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--config", type=str, help="指定配置文件路径")
    parser.add_argument(
        "--model",
        type=str,
        dest="model_name",
        help="指定 Embedding 模型（HuggingFace 名称或本地路径）",
    )
    parser.add_argument("--local-model", type=str, dest="local_model", help="指定本地模型路径（优先级最高）")
    parser.add_argument("--device", type=str, choices=["cpu", "cuda"], default="cpu", help="设备 (默认 cpu)")
    parser.add_argument("--top-k", type=int, dest="top_k", help="默认检索条数")
    parser.add_argument("--min-sim", type=float, dest="min_similarity", help="最小相似度阈值")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # add
    p_add = subparsers.add_parser("add", help="添加记忆")
    p_add.add_argument("content", nargs="?", help="记忆内容")
    p_add.add_argument("-c", "--content", dest="content_alt", help="记忆内容")
    p_add.add_argument("-p", "--project", type=str, help="项目名称")
    p_add.add_argument("-t", "--tags", type=str, help="标签 (逗号分隔)")
    p_add.add_argument("-d", "--date", type=str, help="日期 (YYYY-MM-DD)")
    p_add.add_argument("-f", "--file", type=str, help="从文件读取")
    p_add.add_argument("-l", "--list", type=str, help="从列表文件批量添加")

    # search
    p_search = subparsers.add_parser("search", help="语义搜索")
    p_search.add_argument("query", nargs="?", help="搜索查询")
    p_search.add_argument("-k", "--top-k", type=int, default=5, help="返回条数 (默认 5)")
    p_search.add_argument("-s", "--min-similarity", type=float, default=0.0, help="最小相似度")
    p_search.add_argument("-v", "--verbose", action="store_true", help="详细输出")

    # rag
    p_rag = subparsers.add_parser("rag", help="RAG 检索")
    p_rag.add_argument("query", nargs="?", help="查询文本")
    p_rag.add_argument("-k", "--top-k", type=int, help="检索条数")
    p_rag.add_argument("-s", "--min-similarity", type=float, help="最小相似度")
    p_rag.add_argument("-p", "--prompt", action="store_true", help="生成完整提示词")

    # query
    p_query = subparsers.add_parser("query", help="结构化查询")
    p_query.add_argument("-p", "--project", type=str, help="按项目查询")
    p_query.add_argument("-d", "--date", type=str, help="按日期查询")
    p_query.add_argument("-t", "--tag", type=str, dest="tag", help="按标签查询")
    p_query.add_argument("--type", type=str, help="按类型查询")
    p_query.add_argument("-l", "--limit", type=int, default=100, help="返回数量限制")
    p_query.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    p_query.add_argument("--list-projects", action="store_true", dest="list_projects", help="列出所有项目")
    p_query.add_argument("--list-tags", action="store_true", dest="list_tags", help="列出所有标签")

    # stats
    subparsers.add_parser("stats", help="统计信息")

    # init
    subparsers.add_parser("init", help="初始化/查看状态")

    return parser


def main():
    """主入口"""
    parser = build_parser()
    args = parser.parse_args()

    # 版本查询
    if "-v" in sys.argv or "--version" in sys.argv:
        print(f"evrmem {__version__}")
        return

    # 无参数时显示帮助
    if len(sys.argv) == 1 or args.command is None:
        parser.print_help()
        return

    # 加载配置
    config = reload_config(args.config)

    # 命令行参数覆盖配置
    if args.model_name:
        config._config["embedding.model_name"] = args.model_name
    if args.local_model:
        config._config["embedding.local_path"] = args.local_model
    if args.device:
        config._config["embedding.device"] = args.device
    if args.top_k:
        config._config["rag.top_k"] = args.top_k
    if args.min_similarity is not None:
        config._config["rag.min_similarity"] = args.min_similarity

    setup_logging(config.get("logging.level", "ERROR"))

    # 路由
    if args.command == "add":
        content = args.content or args.content_alt
        args.content = content
        cmd_add(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "rag":
        cmd_rag(args)
    elif args.command == "query":
        cmd_query(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "init":
        cmd_init(args)
    else:
        parser.print_help()
