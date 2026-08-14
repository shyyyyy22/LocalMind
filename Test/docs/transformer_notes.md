# Transformer 学习笔记

## 概述

Transformer 是一种基于自注意力机制（Self-Attention）的神经网络架构，
由 Vaswani 等人在 2017 年的论文 *"Attention Is All You Need"* 中提出。
它抛弃了传统的循环神经网络（RNN）和卷积神经网络（CNN），
完全依赖注意力机制来建模序列中的依赖关系。

## 核心组件

### 1. 自注意力（Self-Attention）

对输入序列中的每个 token，计算 Query、Key、Value 三个向量，
通过缩放点积注意力（Scaled Dot-Product Attention）计算注意力权重：

```
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

### 2. 多头注意力（Multi-Head Attention）

将 Q、K、V 投影到多个子空间分别计算注意力，
最后拼接并线性变换，让模型关注不同位置的不同表示子空间。

### 3. 位置编码（Positional Encoding）

因为注意力机制本身不包含位置信息，
Transformer 使用正弦/余弦函数生成位置编码，
或在后续版本中使用可学习的位置嵌入。

### 4. 前馈网络（Feed-Forward Network）

每个注意力层之后接一个两层的全连接前馈网络，
中间使用 ReLU 激活（后来也有 GELU 等变体）。

### 5. 残差连接与层归一化

每个子层都有残差连接（Residual Connection）和层归一化（LayerNorm），
帮助训练深层网络。

## 架构

```
Input Embedding
      ↓
Positional Encoding
      ↓
┌─────────────────────┐
│  Multi-Head Attention │
│  Add & Norm           │
│  Feed Forward         │
│  Add & Norm           │
└─────────────────────┘
      ↓ (重复 N 层)
Linear + Softmax
      ↓
Output Probabilities
```

## 后续发展

- BERT：双向编码器表示，预训练 + 微调范式
- GPT：自回归生成模型
- ViT：Vision Transformer，把 Transformer 用到图像
- 各种高效的注意力变体（Linformer、Performer 等）

## 关键词

Transformer, Attention, Self-Attention, Multi-Head Attention,
Positional Encoding, Encoder, Decoder, BERT, GPT,
注意力机制, 自注意力, 位置编码, 编码器, 解码器
