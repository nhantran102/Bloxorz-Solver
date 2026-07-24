# Bloxorz-Solver

Game Bloxorz + AI Solver (BFS / DFS / UCS / A*), giao diện Tkinter.

## Chạy game

```bash
cd Bloxorz-Solver
python main.py
```

## Điều khiển

| Phím | Chức năng |
|------|-----------|
| ← ↑ → ↓ | Lăn khối (hoặc di chuyển khối con khi đã tách) |
| **Space** | **Tách khối** (khi khối đang NẰM) / **Hợp nhất** (khi 2 khối con kề nhau) |
| **Tab** | Đổi khối con đang điều khiển (khi đã tách) |
| R | Chơi lại màn |
| Enter / Backspace | Màn kế / màn trước |

## Tính năng tách khối (Split)

Khối 1×2 khi đang **nằm ngang/dọc** có thể **tách** thành 2 khối con 1×1 độc lập:

- Nhấn **Space** khi khối đang nằm để tách.
- Dùng **Tab** để chọn khối con điều khiển (khối đang chọn có viền vàng).
- Mỗi khối con 1×1 nhẹ hơn: **đứng được trên ô Fragile (F)** mà khối đầy đủ sẽ làm vỡ,
  nhưng **không đủ nặng để đạp công tắc loại `heavy`**.
- Khi 2 khối con nằm **kề nhau**, nhấn **Space** để **hợp nhất** lại thành khối 1×2.
- Chỉ **thắng** khi khối đã hợp nhất và đứng thẳng trên đích (G).

**Màn demo:** `level13` — hành lang Fragile rộng 1 ô, bắt buộc phải tách khối
để đưa từng khối con qua rồi hợp nhất lại đứng lên đích.
