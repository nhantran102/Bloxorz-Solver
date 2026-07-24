import heapq
import copy
from collections import deque
import itertools

# Bộ đếm để giải quyết xung đột khi 2 state có cùng cost trong priority queue
counter = itertools.count()

def get_signature(state):
    """
    Tạo một 'chữ ký' duy nhất đại diện cho trạng thái hiện tại.
    Bao gồm tọa độ Block, hướng xoay, và trạng thái các cây cầu.
    """
    return (
        state.block.r, 
        state.block.c, 
        state.block.orientation, 
        frozenset(state.bridges_state.items())
    )

def clone_state(state):
    """
    Tạo bản sao nhẹ (shallow copy) của GameState để AI chạy thử nghiệm 
    mà không làm thay đổi bản đồ gốc của người chơi.
    """
    new_state = copy.copy(state)
    new_state.block = copy.copy(state.block)
    new_state.bridges_state = state.bridges_state.copy()
    return new_state

def find_goal(state):
    """Tìm tọa độ đích đến (G) để tính toán cho thuật toán A*"""
    for r in range(state.rows):
        for c in range(state.cols):
            if state.grid[r][c] == "G":
                return r, c
    return 0, 0

def heuristic(state, goal_r, goal_c):
    """Tính khoảng cách Manhattan từ Block đến Đích (Sử dụng cho A*)"""
    return abs(state.block.r - goal_r) + abs(state.block.c - goal_c)

def bfs(initial_state):
    queue = deque([(clone_state(initial_state), [])])
    visited = {get_signature(initial_state)}

    while queue:
        state, path = queue.popleft()
        if state.check_win(): return path

        for move in ["UP", "DOWN", "LEFT", "RIGHT"]:
            new_state = clone_state(state)
            if new_state.update_move(move):
                sig = get_signature(new_state)
                if sig not in visited:
                    visited.add(sig)
                    queue.append((new_state, path + [move]))
    return None

def dfs(initial_state, limit=50000):
    stack = [(clone_state(initial_state), [])]
    visited = {get_signature(initial_state)}
    steps = 0

    while stack and steps < limit:
        state, path = stack.pop()
        steps += 1
        if state.check_win(): return path

        # Đảo ngược thứ tự để DFS ưu tiên duyệt chuẩn xác hơn
        for move in ["RIGHT", "LEFT", "DOWN", "UP"]:
            new_state = clone_state(state)
            if new_state.update_move(move):
                sig = get_signature(new_state)
                if sig not in visited:
                    visited.add(sig)
                    stack.append((new_state, path + [move]))
    return None

def ucs(initial_state):
    queue = [(0, next(counter), clone_state(initial_state), [])]
    visited = set()

    while queue:
        cost, _, state, path = heapq.heappop(queue)
        sig = get_signature(state)

        if state.check_win(): return path
        if sig in visited: continue
        visited.add(sig)

        for move in ["UP", "DOWN", "LEFT", "RIGHT"]:
            new_state = clone_state(state)
            if new_state.update_move(move):
                new_sig = get_signature(new_state)
                if new_sig not in visited:
                    heapq.heappush(queue, (cost + 1, next(counter), new_state, path + [move]))
    return None

def astar(initial_state):
    goal_r, goal_c = find_goal(initial_state)
    queue = [(0, 0, next(counter), clone_state(initial_state), [])]
    visited = set()

    while queue:
        f, cost, _, state, path = heapq.heappop(queue)
        sig = get_signature(state)

        if state.check_win(): return path
        if sig in visited: continue
        visited.add(sig)

        for move in ["UP", "DOWN", "LEFT", "RIGHT"]:
            new_state = clone_state(state)
            if new_state.update_move(move):
                new_sig = get_signature(new_state)
                if new_sig not in visited:
                    g = cost + 1
                    h = heuristic(new_state, goal_r, goal_c)
                    heapq.heappush(queue, (g + h, g, next(counter), new_state, path + [move]))
    return None