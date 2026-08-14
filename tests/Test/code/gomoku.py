"""五子棋 AI：一个简单的基于极小化极大搜索的五子棋程序。

棋盘 15x15，黑棋先手。AI 使用带 alpha-beta 剪枝的
极小化极大搜索 + 简单的棋型评估函数。
"""

EMPTY, BLACK, WHITE = 0, 1, 2
BOARD_SIZE = 15


def create_board():
    return [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]


def evaluate_line(line):
    """简单的棋型评估：连五、活四、冲四、活三等。"""
    score = 0
    # 简化实现：统计连续同色棋子数
    for color in (BLACK, WHITE):
        cnt = 0
        for cell in line:
            if cell == color:
                cnt += 1
            else:
                if cnt >= 5:
                    score += 10000 if color == BLACK else -10000
                elif cnt == 4:
                    score += 1000 if color == BLACK else -1000
                elif cnt == 3:
                    score += 100 if color == BLACK else -100
                cnt = 0
    return score


def evaluate(board):
    """评估整个棋盘对当前玩家的有利程度。"""
    total = 0
    # 行
    for row in board:
        total += evaluate_line(row)
    # 列
    for col in range(BOARD_SIZE):
        total += evaluate_line([board[r][col] for r in range(BOARD_SIZE)])
    # 对角线（略）
    return total


def minimax(board, depth, alpha, beta, is_maximizing):
    if depth == 0:
        return evaluate(board)
    # 简化：只搜索有棋子的附近位置
    if is_maximizing:
        best = -float("inf")
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] == EMPTY:
                    board[r][c] = BLACK
                    best = max(best, minimax(board, depth - 1, alpha, beta, False))
                    board[r][c] = EMPTY
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        break
        return best
    else:
        best = float("inf")
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] == EMPTY:
                    board[r][c] = WHITE
                    best = min(best, minimax(board, depth - 1, alpha, beta, True))
                    board[r][c] = EMPTY
                    beta = min(beta, best)
                    if beta <= alpha:
                        break
        return best


def ai_move(board, depth=2):
    """返回 AI 的最佳落子位置 (row, col)。"""
    best_score = -float("inf")
    best_pos = (BOARD_SIZE // 2, BOARD_SIZE // 2)
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == EMPTY:
                board[r][c] = BLACK
                score = minimax(board, depth - 1, -float("inf"), float("inf"), False)
                board[r][c] = EMPTY
                if score > best_score:
                    best_score = score
                    best_pos = (r, c)
    return best_pos


if __name__ == "__main__":
    board = create_board()
    print("五子棋 AI 已就绪，黑棋先手")
    print("AI 推荐落子:", ai_move(board, depth=2))
