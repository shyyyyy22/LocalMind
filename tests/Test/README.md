# Test 测试文件夹

这个文件夹用于 LocalMind 开发阶段的测试语料库。

## 用途

- 文件扫描与索引测试
- 文件名 / 扩展名 / 路径 / 时间 / 大小过滤测试
- 全文搜索与语义搜索测试
- 重复文件检测（见 `duplicates/`）
- 相似文件检测（见 `similar/`）
- 中文文件名与内容处理测试
- 大文件与深层嵌套目录测试

## 结构

```text
Test/
├── README.md            本文件
├── docs/                文档类（.md / .txt）
├── code/                代码类（.py / .cpp / .h / .java）
├── data/                数据类（.csv / .json）
├── duplicates/          完全相同的重复文件
├── similar/             内容接近的相似文件
├── special/             特殊文件（空文件 / 无扩展名 / 带空格 / 隐藏文件）
├── big/                 大文件（约 2MB）
├── nested/              深层嵌套目录
└── mixed/               中文文件名与英文混合
```

## 典型测试查询

- "找一下我以前做过的五子棋 AI" → `code/gomoku.py`
- "找出我电脑里所有关于 Transformer 的资料" → `docs/transformer_notes.md`、`code/transformer.py`
- "我之前有没有保存过 PPO 的论文" → `docs/ppo_paper_summary.txt`、`docs/ppo_notes.md`
