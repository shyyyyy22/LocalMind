[TOC]
# LocalMind

> **LocalMind — Privacy-Preserving AI File Management & Knowledge Retrieval System**

一个运行在个人电脑上的本地 AI 文件管理与知识检索系统。  
目标是让用户可以通过**关键词、自然语言和 AI Agent**理解、搜索、整理自己的电脑文件，同时默认保证文件数据留在本地。

---

## 1. 项目定位

LocalMind 不是简单的“ChatGPT 文件问答”，而是一个逐步演进的本地文件智能管理系统：

```text
文件系统
   ↓
文件索引
   ↓
全文搜索
   ↓
语义搜索
   ↓
Hybrid Retrieval
   ↓
RAG
   ↓
Agent
   ↓
受控文件操作
   ↓
个人知识库
```

核心设计原则：

- **Local-first**：优先本地运行
- **Privacy-first**：文件内容默认不离开用户电脑
- **Search-first**：搜索系统是核心，而不是 LLM
- **AI-assisted**：AI 负责增强，而不是取代基础系统
- **Human-in-the-loop**：危险文件操作必须经过用户确认
- **Evaluable**：所有重要 AI 能力都应该有可量化的评测

---

# 2. 最终产品目标

用户可以直接使用自然语言操作自己的文件：

```text
“找一下我以前做过的五子棋 AI。”

“找出我电脑里所有关于 Transformer 的资料。”

“我之前有没有保存过 PPO 的论文？”

“总结这个文件夹里的所有学习资料。”

“找出完全重复的 PDF。”

“把 Downloads 里的论文整理到论文文件夹。”
```

LocalMind 最终可以：

- 搜索文件名
- 搜索文件内容
- 语义搜索
- 按时间、大小、类型、路径筛选
- PDF / Markdown / Word / Excel / PPT / 源代码解析
- 文件摘要
- 文件夹摘要
- 重复文件检测
- 相似文件检测
- 文件关系发现
- RAG 问答
- Agent 工具调用
- 自动生成文件整理方案
- 用户确认后执行移动 / 重命名等操作
- 操作历史
- Undo
- 本地 LLM
- 离线运行
- 搜索和 RAG Evaluation

---

# 3. 最终系统架构

```text
                         ┌─────────────────┐
                         │   Web / Desktop │
                         │       UI        │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    API Layer    │
                         │     FastAPI     │
                         └────────┬────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
                ▼                 ▼                 ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │ Search Engine│  │ Agent Engine │  │ File Manager │
        └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
               │                 │                 │
               ▼                 ▼                 ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │Keyword Search│  │  LLM / Local │  │ File System  │
        │    BM25      │  │     Model    │  │              │
        └──────┬───────┘  └──────────────┘  └──────────────┘
               │
               ▼
        ┌─────────────────────────────────┐
        │          Retrieval Layer        │
        │                                 │
        │ SQLite FTS5 + Vector + Reranker │
        └───────────────┬─────────────────┘
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
 ┌─────────────────┐         ┌─────────────────┐
 │ Metadata Store  │         │ Vector Storage  │
 │     SQLite      │         │ FAISS / Qdrant  │
 └─────────────────┘         └─────────────────┘
```

底层文件处理：

```text
                 Local File System
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
      PDF              Code             Office
       │                │                │
       └────────────────┼────────────────┘
                        ▼
                 Document Parser
                        │
                        ▼
                    Chunking
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
          Metadata              Embedding
             │                     │
             ▼                     ▼
          SQLite                Vector DB
```

---

# 4. 核心模块

LocalMind 分为 9 个主要模块：

```text
LocalMind
│
├── 1. File Scanner
├── 2. File Index
├── 3. Document Parser
├── 4. Search Engine
├── 5. Semantic Retrieval
├── 6. AI / RAG
├── 7. Agent
├── 8. File Operations
└── 9. Evaluation
```

---

# 5. Module 1：File Scanner

## 5.1 功能

扫描用户指定目录：

```text
C:/
D:/
Documents/
Downloads/
Projects/
...
```

记录：

```text
path
filename
extension
size
created_at
modified_at
mime_type
hash
```

示例：

```json
{
    "path": "D:/学习/深度学习/Transformer.pdf",
    "name": "Transformer.pdf",
    "extension": ".pdf",
    "size": 1827364,
    "modified_at": "...",
    "hash": "..."
}
```

## 5.2 文件监听

不能每次启动都重新扫描整个电脑。

使用文件系统监听：

```text
File System
     │
     ▼
 Watchdog
     │
     ├── CREATE
     ├── MODIFY
     ├── DELETE
     └── MOVE
```

新文件出现后：

```text
New File
   ↓
Parse
   ↓
Index
   ↓
Embedding
```

---

# 6. Module 2：Metadata Database

第一阶段使用 SQLite，后期根据需求再考虑 PostgreSQL。

## 6.1 files

```text
files
-------------------------
id
path
name
extension
size
mime_type
created_at
modified_at
hash
status
```

## 6.2 documents

```text
documents
-------------------------
id
file_id
title
author
language
page_count
word_count
content_hash
```

## 6.3 chunks

```text
chunks
-------------------------
id
document_id
chunk_index
content
token_count
```

## 6.4 tags

```text
tags
-------------------------
id
name
```

## 6.5 file_tags

```text
file_tags
-------------------------
file_id
tag_id
```

## 6.6 operations

```text
operations
-------------------------
id
operation_type
source
destination
status
created_at
```

用于：

- 操作历史
- 审计
- Undo

---

# 7. Module 3：Document Parser

不要针对每种格式编写完全不同的调用方式。

设计统一接口：

```text
DocumentParser
       │
 ┌─────┼──────────┐
 ↓     ↓          ↓
PDF   DOCX       Markdown
Parser Parser     Parser
```

统一：

```python
parse(file) -> Document
```

返回：

```text
Document
├── metadata
├── text
└── structure
```

## 支持计划

### V1

```text
.txt
.md
.py
.cpp
.h
.java
.json
.csv
```

### V2

```text
.pdf
.docx
.xlsx
.pptx
```

### V3

```text
.html
.epub
```

---

# 8. Module 4：Search Engine

LocalMind 的核心不是 LLM，而是搜索。

设计三层搜索。

## 8.1 Exact Search

例如：

```text
transformer.py
```

直接匹配：

- 文件名
- 路径
- 扩展名

## 8.2 Keyword Search

使用：

**SQLite FTS5 / BM25**

例如：

```text
reinforcement learning
```

找到：

```text
强化学习笔记.pdf
DQN.pdf
RL_notes.md
```

## 8.3 Semantic Search

例如用户搜索：

```text
“我以前学过让 AI 自己玩游戏的方法”
```

可以找到：

```text
AlphaZero.pdf
Monte Carlo Tree Search.pdf
Self-play RL.md
```

即使文件中没有完全相同的关键词。

---

# 9. Hybrid Retrieval

最终搜索架构：

```text
                Query
                  │
       ┌──────────┴──────────┐
       ▼                     ▼
    BM25 Search          Vector Search
       │                     │
       │                     │
       └──────────┬──────────┘
                  ▼
                Fusion
                  │
                  ▼
              Reranker
                  │
                  ▼
             Top-K Results
```

可以实验：

```text
BM25       40%
Semantic   40%
Metadata   20%
```

最终权重应该通过实验确定，而不是固定认为这个比例最好。

---

# 10. Module 5：Embedding

文档 chunk：

```text
Transformer is a neural network architecture...
```

转换成向量：

```text
[0.12, -0.32, 0.91, ...]
```

搜索：

```text
“注意力机制”
```

同样转换为向量，再计算相似度。

---

# 11. Chunking Strategy

需要进行实验，而不是简单固定字符数。

## Strategy A

```text
500 characters
```

## Strategy B

```text
1000 characters
overlap 100
```

## Strategy C

根据文档结构：

```text
标题
段落
代码函数
PDF 页面
```

进行切分。

最终通过 Evaluation 比较：

```text
Chunk Strategy
      ↓
Retrieval Accuracy
      ↓
Answer Quality
```

---

# 12. Module 6：RAG

标准流程：

```text
Query
 ↓
Retriever
 ↓
Top-K
 ↓
Context
 ↓
LLM
 ↓
Answer
```

例如：

```text
“我之前关于 PPO 的笔记里面提到 Actor-Critic 吗？”
```

回答：

```text
是，在 RL/PPO_notes.md 的第 4 节提到……
```

并返回来源：

```text
Source:
RL/PPO_notes.md
Line: 142-167
```

原则：

> 所有知识型回答尽可能提供来源，避免无法验证的回答。

---

# 13. Module 7：Agent

Agent 后期加入。

Agent 可以调用：

```text
search_files()
semantic_search()
read_file()
read_folder()
get_metadata()
find_duplicates()
summarize_folder()
```

危险操作：

```text
move_file()
rename_file()
delete_file()
create_folder()
```

必须单独处理。

---

# 14. File Operation Safety

AI 不能直接拥有无限文件权限。

标准流程：

```text
User Request
     ↓
Agent
     ↓
Operation Plan
     ↓
Risk Check
     ↓
Preview
     ↓
User Confirmation
     ↓
Execute
```

例如：

```text
建议操作

1. Transformer.pdf
   → D:/学习/深度学习/

2. DQN.pdf
   → D:/学习/强化学习/

3. test.py
   → D:/项目/Python/

共 3 项

[取消] [执行]
```

---

# 15. Undo System

操作记录：

```text
Operation #103
MOVE

A.pdf
↓
学习/A.pdf
```

数据库：

```text
operation_id = 103
source = Downloads/A.pdf
destination = 学习/A.pdf
```

Undo：

```text
学习/A.pdf
↓
Downloads/A.pdf
```

目标：

> 任何自动文件操作都可以追踪，并尽可能支持撤销。

---

# 16. Module 8：Duplicate Detection

三级检测。

## Level 1：文件大小

```text
size
```

## Level 2：Hash

```text
SHA-256
```

## Level 3：内容相似

```text
Embedding
```

结果：

```text
Exact Duplicate
    A.pdf
    B.pdf

Similar Document
    C.pdf
```

---

# 17. Knowledge Graph

后期功能。

示例：

```text
Transformer.pdf
      │
      ├── mentions → Attention
      │
      ├── related → BERT.pdf
      │
      └── code → transformer.py
```

可以建立：

```text
File
Chunk
Concept
Project
Tag
```

之间的关系。

搜索 Transformer 后显示：

```text
Transformer

相关文件：
├── Transformer.pdf
├── Attention.md
├── BERT.pdf
└── transformer.py

相关概念：
├── Attention
├── Encoder
├── Decoder
└── Positional Encoding
```

---

# 18. Module 9：Evaluation

这是 LocalMind 非常重要的一部分。

不能只说：

> “搜索效果很好。”

需要建立测试数据集。

例如：

```text
100 queries
```

包括：

```text
“找我的强化学习资料”
“之前关于 PPO 的笔记”
“Transformer 的代码”
“我去年写的 ResNet 项目”
...
```

比较：

```text
                 Recall@5
Keyword Search     62%
Vector Search      78%
Hybrid Search      89%
Hybrid + Reranker  94%
```

以上数据只是示例，实际项目必须通过实验获得。

---

# 19. Evaluation Metrics

## Retrieval

```text
Precision@K
Recall@K
MRR
NDCG
```

## RAG

```text
Answer Relevance
Faithfulness
Context Recall
Citation Accuracy
```

## System

```text
Search Latency
Indexing Speed
Memory Usage
CPU Usage
```

---

# 20. 项目目录结构

```text
LocalMind/
│
├── app/
│   ├── api/
│   │   ├── routes/
│   │   └── dependencies.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── security.py
│   │
│   ├── database/
│   │   ├── models.py
│   │   ├── repository.py
│   │   └── database.py
│   │
│   ├── scanner/
│   │   ├── scanner.py
│   │   ├── watcher.py
│   │   └── hasher.py
│   │
│   ├── parser/
│   │   ├── base.py
│   │   ├── pdf.py
│   │   ├── markdown.py
│   │   ├── office.py
│   │   └── code.py
│   │
│   ├── retrieval/
│   │   ├── keyword.py
│   │   ├── vector.py
│   │   ├── hybrid.py
│   │   └── reranker.py
│   │
│   ├── embedding/
│   │   ├── model.py
│   │   └── index.py
│   │
│   ├── rag/
│   │   ├── retriever.py
│   │   ├── context.py
│   │   └── generator.py
│   │
│   ├── agent/
│   │   ├── agent.py
│   │   ├── planner.py
│   │   └── tools/
│   │       ├── search.py
│   │       ├── read.py
│   │       ├── summarize.py
│   │       └── file_ops.py
│   │
│   ├── operations/
│   │   ├── executor.py
│   │   ├── history.py
│   │   └── undo.py
│   │
│   └── evaluation/
│       ├── dataset.py
│       ├── retrieval.py
│       └── rag.py
│
├── frontend/
│
├── tests/
│
├── experiments/
│   ├── chunking/
│   ├── embedding/
│   ├── retrieval/
│   └── reranking/
│
├── scripts/
├── docs/
├── data/
├── docker/
│
├── README.md
├── pyproject.toml
├── docker-compose.yml
└── LICENSE
```

---

# 21. 推荐技术栈

| 模块 | 技术 |
|---|---|
| 主语言 | Python |
| 后端 | FastAPI |
| 数据库 | SQLite |
| ORM | SQLAlchemy |
| 文件监听 | watchdog |
| PDF | PyMuPDF |
| 全文搜索 | SQLite FTS5 |
| Embedding | Sentence Transformers |
| Vector Search | FAISS |
| Reranker | Cross-Encoder |
| LLM | Ollama / API |
| Agent | 前期自己实现，后期 LangGraph |
| 前端 | React / 简单 Web UI |
| 测试 | pytest |
| 部署 | Docker |
| 版本控制 | Git |

前期不要为了“AI 项目”而堆很多框架。

---

# 22. Provider 抽象

LLM 不应该和具体服务绑定。

设计：

```text
LLMProvider
     │
 ┌───┼──────────────┐
 ↓   ↓              ↓
Local API       Cloud API       Other
```

Embedding 同样：

```text
EmbeddingProvider
        │
 ┌──────┼───────────┐
 ↓      ↓           ↓
Local   API       Custom
```

这样可以支持：

```text
Offline Mode
Online Mode
```

---

# 23. 三种运行模式

## Basic Mode

完全不用 AI：

```text
文件索引
+
全文搜索
+
重复检测
```

## Local AI Mode

```text
LocalMind
+
Local Embedding
+
Local LLM
```

## Cloud AI Mode

```text
LocalMind
+
API LLM
```

核心数据仍然由本地索引系统管理。

---

# 24. 版本路线

## V0.1 — Local File Indexer

目标：

- 选择目录
- 扫描文件
- SQLite 索引
- 文件 Hash
- 文件变化监听
- 基础搜索

---

## V0.2 — Full Text Search

加入：

- PDF Parser
- Markdown Parser
- Code Parser
- Office Parser
- SQLite FTS5
- 文件内容搜索

---

## V0.3 — Semantic Search

加入：

- Embedding
- Vector Search
- FAISS
- Semantic Search

---

## V0.4 — Hybrid RAG

加入：

- BM25
- Dense Retrieval
- Hybrid Retrieval
- Reranker
- RAG
- Citation

---

## V0.5 — Agent

加入：

- Tool Calling
- Planning
- Search Tool
- Read Tool
- Summarization Tool
- Duplicate Detection Tool

---

## V0.6 — File Management Agent

加入：

- Move
- Rename
- Create Folder
- Operation Preview
- Confirmation
- Operation Log
- Undo

---

## V0.7 — Knowledge Graph

加入：

- Concept Extraction
- Entity Linking
- File Relationship
- Knowledge Graph
- Related Files

---

## V1.0 — Complete LocalMind

目标：

```text
File Management
+
Search
+
Semantic Retrieval
+
RAG
+
Agent
+
Knowledge Graph
+
Evaluation
+
Offline Mode
```

---

# 25. 项目驱动学习路线

不要先学完所有知识再做项目。

采用：

> **遇到问题 → 学知识 → 实现 → 测试 → 总结**

例如：

### 第 1 周

文件扫描需求

→ 学 `pathlib`

### 第 2 周

数据库需求

→ 学 SQLite / SQL

### 第 3 周

文件变化检测

→ 学 watchdog / 文件系统事件

### 第 4 周

PDF 搜索

→ 学 PDF Parsing

### 第 5 周

关键词搜索

→ 学 TF-IDF / BM25 / FTS

### 第 6 周

语义搜索

→ 学 Embedding

### 第 7 周

大规模向量搜索

→ 学 ANN / FAISS

### 第 8 周

搜索结果质量不足

→ 学 Reranker

### 第 9 周

AI 回答会产生幻觉

→ 学 RAG / Grounding / Evaluation

### 第 10 周

Agent 权限问题

→ 学 Tool Calling / Permission / Sandbox

### 第 11 周

搜索速度问题

→ 学 Cache / Async / Profiling

### 第 12 周

项目变复杂

→ 学 Architecture / Testing / Design Patterns

---

# 26. 第一阶段学习重点

第一阶段不要碰大模型。

只学习：

```text
Python
│
├── pathlib
├── os
├── hashlib
├── threading / asyncio
│
├── SQLite
├── SQL
├── SQLAlchemy
│
├── FastAPI
├── pytest
└── Git
```

目标：

> 做出一个可靠的本地文件索引器。

---

# 27. 第一阶段 Milestone

## LocalMind V0.1

功能：

- [x] 选择需要管理的目录
- [x] 扫描文件
- [x] 建立 SQLite 数据库
- [x] 保存文件名
- [x] 保存完整路径
- [x] 保存扩展名
- [x] 保存文件大小
- [x] 保存创建时间
- [x] 保存修改时间
- [x] 计算 SHA-256
- [x] 文件变化监听
- [x] 新文件自动加入索引
- [x] 删除文件自动同步
- [x] 文件移动自动同步
- [x] 文件名搜索
- [x] 扩展名过滤
- [x] 路径过滤
- [x] 时间过滤
- [x] 大小过滤
- [x] 基础 Web UI
- [x] pytest 测试

---

# 28. 后续实验方向

为了提高科研 / 简历含金量，建立 `experiments/`：

```text
experiments/
├── chunking/
├── embedding/
├── retrieval/
├── reranking/
├── latency/
└── llm/
```

可以研究：

### Chunking

```text
500 chars
vs
1000 chars
vs
semantic chunking
```

### Embedding

```text
Model A
vs
Model B
```

### Retrieval

```text
BM25
vs
Vector
vs
Hybrid
```

### Reranking

```text
Without Reranker
vs
Cross Encoder
```

### RAG

```text
Different prompts
Different Top-K
Different context sizes
```

最终得到真实实验数据。

---

# 29. GitHub 项目要求

最终 GitHub 不应该只有：

```text
main.py
requirements.txt
```

而应该包含：

```text
Architecture
Technology Selection
Installation
Usage
Experiments
Benchmark
Screenshots
API Documentation
Security Model
Offline Mode
Limitations
Future Work
```

建议 README 最终包含：

1. 项目介绍
2. Features
3. Architecture
4. Demo
5. Installation
6. Quick Start
7. Configuration
8. Offline Mode
9. Search Architecture
10. Agent Architecture
11. Evaluation
12. Benchmark
13. Security
14. Development
15. Roadmap
16. License

---

# 30. 简历定位

完成 V3：

> Built a local semantic file retrieval system using embedding-based vector search.

完成 V4：

> Designed a hybrid retrieval pipeline combining BM25, dense embeddings, metadata filtering and reranking for personal document search.

完成 V5：

> Implemented an agentic architecture with tool calling for natural-language document retrieval and analysis.

完成 V6：

> Developed a privacy-preserving local AI file management agent with semantic retrieval, RAG, controlled file operations, operation history and undo capabilities.

加入 Evaluation：

> Evaluated BM25, dense retrieval and hybrid retrieval approaches using Recall@K, MRR and NDCG, and analyzed retrieval quality under different chunking, embedding and reranking strategies.

---

# 31. 项目与个人学习的关系

LocalMind 可以把多个 AI / CS 方向串起来：

```text
                 LocalMind
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
      Python       数据结构       Linux
        │            │            │
        └────────────┼────────────┘
                     ↓
                  数据库
                     │
                     ↓
                 搜索算法
                     │
          ┌──────────┴──────────┐
          ↓                     ↓
       BM25                  Embedding
          │                     │
          └──────────┬──────────┘
                     ↓
                Hybrid Search
                     │
                     ↓
                  Reranker
                     │
                     ↓
                    RAG
                     │
                     ↓
                    LLM
                     │
                     ↓
                  Agent
                     │
             ┌───────┴───────┐
             ↓               ↓
          Tool Use        Planning
             │               │
             └───────┬───────┘
                     ↓
              File Operations
                     │
                     ↓
                Evaluation
```

---

# 32. 最终目标

LocalMind 最终应该达到：

> **一个真正可以每天使用的本地 AI 文件管理系统。**

它不是：

```text
“调用一个 LLM API + 一个向量数据库”
```

而是完整的：

```text
File System
+
Database
+
Search
+
Information Retrieval
+
Embedding
+
Reranking
+
RAG
+
LLM
+
Agent
+
Knowledge Graph
+
Security
+
Evaluation
+
Software Engineering
```

这也是这个项目最有价值的地方。

---

# 33. 开发原则

整个项目始终遵循：

1. **先基础系统，后 AI**
2. **先搜索，后 Agent**
3. **先可用，后复杂**
4. **所有 AI 能力必须可以评测**
5. **危险操作必须 Human-in-the-loop**
6. **默认本地运行**
7. **核心模块保持 Provider 无关**
8. **每个版本都应该能独立使用**
9. **每个阶段都记录实验结果**
10. **最终形成完整 GitHub 项目和技术文档**

---

# 34. 当前第一步

不要直接开发 V0.2、V0.3。

当前只做：

```text
LocalMind V0.1
```

目标：

```text
选择目录
    ↓
扫描文件
    ↓
计算 Hash
    ↓
写入 SQLite
    ↓
监听文件变化
    ↓
同步数据库
    ↓
搜索文件
```

完成之后再进入：

```text
V0.2 → 全文搜索
V0.3 → 语义搜索
V0.4 → RAG
V0.5 → Agent
V0.6 → 文件操作
V0.7 → Knowledge Graph
V1.0 → 完整 LocalMind
```

**第一阶段最重要的不是“做出 AI”，而是做出一个你自己愿意每天使用的文件索引和搜索系统。**
