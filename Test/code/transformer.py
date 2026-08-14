"""A minimal Transformer implementation for learning purposes.

Implements scaled dot-product attention, multi-head attention,
and a tiny Transformer encoder block using only NumPy.
"""

import numpy as np


def softmax(x):
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e_x / np.sum(e_x, axis=-1, keepdims=True)


def scaled_dot_product_attention(Q, K, V, mask=None):
    """Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V"""
    d_k = Q.shape[-1]
    scores = np.matmul(Q, K.transpose(0, 1, 3, 2)) / np.sqrt(d_k)
    if mask is not None:
        scores = np.where(mask == 0, -1e9, scores)
    weights = softmax(scores)
    return np.matmul(weights, V), weights


class MultiHeadAttention:
    def __init__(self, d_model, num_heads):
        assert d_model % num_heads == 0
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        rng = np.random.default_rng(42)
        self.W_q = rng.normal(size=(d_model, d_model)) * 0.02
        self.W_k = rng.normal(size=(d_model, d_model)) * 0.02
        self.W_v = rng.normal(size=(d_model, d_model)) * 0.02
        self.W_o = rng.normal(size=(d_model, d_model)) * 0.02

    def forward(self, x):
        batch, seq, _ = x.shape
        Q = np.matmul(x, self.W_q).reshape(batch, seq, self.num_heads, self.d_k)
        K = np.matmul(x, self.W_k).reshape(batch, seq, self.num_heads, self.d_k)
        V = np.matmul(x, self.W_v).reshape(batch, seq, self.num_heads, self.d_k)
        Q = Q.transpose(0, 2, 1, 3)
        K = K.transpose(0, 2, 1, 3)
        V = V.transpose(0, 2, 1, 3)
        attn_out, _ = scaled_dot_product_attention(Q, K, V)
        attn_out = attn_out.transpose(0, 2, 1, 3).reshape(batch, seq, self.d_model)
        return np.matmul(attn_out, self.W_o)


class FeedForward:
    def __init__(self, d_model, d_ff):
        rng = np.random.default_rng(0)
        self.W1 = rng.normal(size=(d_model, d_ff)) * 0.02
        self.W2 = rng.normal(size=(d_ff, d_model)) * 0.02

    def forward(self, x):
        return np.matmul(np.maximum(np.matmul(x, self.W1), 0), self.W2)


class TransformerBlock:
    def __init__(self, d_model, num_heads, d_ff):
        self.attention = MultiHeadAttention(d_model, num_heads)
        self.ffn = FeedForward(d_model, d_ff)

    def forward(self, x):
        x = x + self.attention.forward(x)  # residual connection
        x = x + self.ffn.forward(x)
        return x


if __name__ == "__main__":
    # quick smoke test: batch=2, seq=4, d_model=8
    rng = np.random.default_rng(1)
    x = rng.normal(size=(2, 4, 8))
    block = TransformerBlock(d_model=8, num_heads=2, d_ff=16)
    out = block.forward(x)
    print("output shape:", out.shape)
