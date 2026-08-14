# PPO 强化学习笔记

## 什么是 PPO

PPO（Proximal Policy Optimization，近端策略优化）是 OpenAI 提出的
一种基于策略梯度的强化学习算法（2017）。
它在 TRPO（Trust Region Policy Optimization）的基础上简化了实现，
通过裁剪（Clipping）目标函数来限制每次更新的步长，
保证训练稳定。

## 核心思想

策略梯度方法直接对策略 π(a|s) 求梯度来优化奖励期望。
PPO 使用重要性采样（Importance Sampling）复用旧数据，
并通过裁剪项防止策略更新过大：

```
L^CLIP(θ) = E[ min( r(θ) A, clip(r(θ), 1-ε, 1+ε) A ) ]
```

其中 r(θ) 是新旧策略的概率比，A 是优势函数估计。

## Actor-Critic 结构

PPO 通常使用 Actor-Critic 架构：

- **Actor（策略网络）**：输出动作的概率分布
- **Critic（价值网络）**：估计状态价值 V(s)，用于计算优势函数

优势函数使用 GAE（Generalized Advantage Estimation）估计。

## 训练流程

1. 用当前策略与环境交互，收集一批轨迹
2. 计算优势估计（GAE）
3. 用裁剪目标函数更新策略网络若干轮
4. 更新价值网络
5. 重复以上过程

## 应用

- 游戏（Atari、Dota 2、OpenAI Five）
- 机器人控制
- 大语言模型的 RLHF 阶段（作为奖励模型之后的优化算法）

## 关键词

PPO, Proximal Policy Optimization, 强化学习, Reinforcement Learning,
策略梯度, Policy Gradient, Actor-Critic, GAE, TRPO, RLHF,
近端策略优化, 演员评论家
