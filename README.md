# LocalMind

> **Local-first、Privacy-first 的 AI 文件管理与知识检索系统**

LocalMind 是一个运行在个人电脑上的文件智能管理系统，最终目标是让用户通过关键词、自然语言和 AI Agent 理解、搜索、整理自己的文件，同时默认保证文件数据留在本地。

**当前版本：V0.1 —— 本地文件索引器**

## Features（V0.1）

- 递归扫描指定目录，索引文件元数据（路径、名称、扩展名、大小、创建/修改时间）
- SHA-256 内容哈希（分块计算，大文件友好）
- SQLite 元数据存储（SQLAlchemy）
- watchdog 文件监听：新增 / 删除 / 修改 / 移动自动同步数据库
- 组合条件搜索：文件名、扩展名、路径、大小区间、修改时间区间
- 重复扫描幂等：已索引文件自动更新，不产生重复记录
- 命令行工具：`scan` / `search` / `watch` 三个子命令
- pytest 测试套件（测试使用独立临时数据库，不污染真实索引）

## 项目结构

```
LocalMind/
├── app/
│   ├── cli/          # 命令行入口（scan / search / watch 子命令）
│   ├── core/         # 配置（config.py）
│   ├── database/     # SQLAlchemy 模型与引擎
│   ├── scanner/      # 目录扫描、SHA-256 哈希、watchdog 监听
│   └── search/       # 元数据组合搜索
├── tests/            # pytest 测试套件 + 测试数据（tests/Test）
├── docs/coaching/    # 学习过程指导文档
└── LocalMind_Project_Design.md   # 完整项目设计文档
```

## 安装

```bash
# 1. 克隆仓库
git clone git@github.com:shyyyyy22/LocalMind.git
cd LocalMind

# 2. 创建并激活虚拟环境（需要 Python 3.12+）
python -m venv venv
venv\Scripts\activate          # Windows cmd / PowerShell
# source venv/Scripts/activate  # Git Bash

# 3. 安装依赖
pip install -r requirements.txt
```

## 快速开始

```bash
# 1. 扫描目录，建立索引
python -m app.cli scan --path D:\我的文档

# 2. 搜索文件
python -m app.cli search --name 简历 --ext pdf

# 3. 启动文件监听（新增/删除/修改/移动自动同步索引）
python -m app.cli watch --path D:\我的文档
```

## 搜索参数

| 参数 | 说明 |
|---|---|
| `--name` | 文件名关键词，模糊匹配 |
| `--ext` | 扩展名，`pdf` 和 `.pdf` 均可；传空串 `""` 匹配无扩展名文件 |
| `--noext` | 匹配无扩展名文件（`--ext ""` 的终端友好替代） |
| `--path` | 路径关键词，`/` 和 `\` 分隔符均可 |
| `--min_size` / `--max_size` | 文件大小区间（字节） |
| `--mtime_start` / `--mtime_end` | 修改时间区间，格式 `YYYY-MM-DD-HH`（起点含该小时，终点不含） |
| `--limit` | 最多返回条数，默认 50 |

所有条件均可自由组合，不传即不过滤。

示例：

```bash
python -m app.cli search --ext py --min_size 1000 --limit 20
python -m app.cli search --mtime_start 2026-08-01-00 --ext md
python -m app.cli search --name transformer --ext py
```

## 配置

| 环境变量 | 默认值 | 说明 |
|---|---|---|
| `LOCALMIND_DB` | `sqlite:///localmind.db` | SQLite 数据库地址 |

```bash
# Git Bash 示例：使用自定义数据库路径
LOCALMIND_DB=sqlite:///D:/data/myindex.db python -m app.cli scan --path D:\我的文档

# Windows cmd 示例
set LOCALMIND_DB=sqlite:///D:/data/myindex.db && python -m app.cli scan --path D:\我的文档
```

## 运行测试

```bash
python -m pytest -v
```

测试通过 `LOCALMIND_DB` 环境变量 + 系统临时目录实现数据库隔离，每次运行不会污染真实索引数据。

## Roadmap

| 版本 | 内容 | 状态 |
|---|---|---|
| V0.1 | 本地文件索引器 | ✅ 已完成 |
| V0.2 | 全文搜索（文档解析 + SQLite FTS5） | 下一步 |
| V0.3 | 语义搜索（Embedding + 向量检索） | |
| V0.4 | Hybrid 检索 + RAG | |
| V0.5 | Agent（工具调用） | |
| V0.6 | 受控文件操作（预览 / 确认 / 撤销） | |
| V0.7 | 知识图谱 | |
| V1.0 | 完整 LocalMind | |

完整设计见 [LocalMind_Project_Design.md](LocalMind_Project_Design.md)。
