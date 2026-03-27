# Contributing to evrmem / 贡献指南

English | [中文](#中文)

---

## English

### How to Contribute

We welcome contributions! Here's how to get started:

#### Reporting Bugs

- Search existing issues first to avoid duplicates
- Use the bug report template
- Include: Python version, OS, error message, and reproduction steps
- Tag: `bug`

#### Suggesting Features

- Open a discussion first to gauge interest
- Describe the use case clearly
- Tag: `enhancement`

#### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests (if any): `pytest`
5. Commit with clear messages: `git commit -m "feat: add xxx"`
6. Push and open a PR

#### Code Style

- Follow [PEP 8](https://pep8.org/)
- Use type hints where possible
- Max line length: 88 characters (Black default)

```bash
# Format code
pip install black isort
black src/
isort src/

# Type check
pip install mypy
mypy src/
```

#### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat:     new feature
fix:      bug fix
docs:     documentation only
refactor: code change that neither fixes a bug nor adds a feature
test:     adding or updating tests
chore:    maintenance tasks
```

---

## 中文

### 如何贡献

欢迎各种形式的贡献！

#### 报告 Bug

- 先搜索现有 issues，避免重复
- 使用 Bug 报告模板
- 包含：Python 版本、操作系统、错误信息、重现步骤
- 标签：`bug`

#### 功能建议

- 先开 Discussion 讨论需求
- 清晰描述使用场景
- 标签：`enhancement`

#### 提交 Pull Request

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/你的功能名`
3. 进行修改
4. 运行测试（如有）：`pytest`
5. 提交，消息清晰：`git commit -m "feat: 新增 xxx"`
6. Push 并发起 PR

#### 代码风格

- 遵循 [PEP 8](https://pep8.org/)
- 尽量使用类型提示
- 最大行长：88 字符（Black 默认）

```bash
# 格式化代码
pip install black isort
black src/
isort src/

# 类型检查
pip install mypy
mypy src/
```

#### 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/zh/)：

```
feat:     新功能
fix:      Bug 修复
docs:     仅文档修改
refactor: 重构（不修复 Bug，不新增功能）
test:     测试相关
chore:    维护性任务
```

---

## Development Setup / 开发环境搭建

```bash
# Clone
git clone https://github.com/pink/evrmem.git
cd evrmem

# Install in editable mode
pip install -e ".[dev]"

# Or install dev dependencies separately
pip install -e .
pip install black isort mypy pytest

# Run tests
pytest

# Format
black src/
isort src/

# Type check
mypy src/
```

## License / 协议

By contributing, you agree that your contributions will be licensed under the MIT License.
