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
| **Tab** | Đổi khối con đang điều khiển (khi đã tách) |
| **Space** | **Hợp nhất** 2 khối con lại (khi chúng kề nhau) |
| R | Chơi lại màn |
| Enter / Backspace | Màn kế / màn trước |

## Tính năng tách khối (Split)

Trên bản đồ có thể đặt **ô nút tách** (ký hiệu `"P"` trong file level, hiển thị
màu **tím** với biểu tượng ⊟). Cơ chế:

- Khi khối 1×2 **đứng thẳng** trên ô nút → **tự động tách** thành 2 khối con 1×1:
  - 1 khối con giữ nguyên ở **ô nút**,
  - 1 khối con xuất hiện ở **vị trí start** của màn.
- Dùng **Tab** để chọn khối con điều khiển (khối đang chọn có viền vàng).
- Mỗi khối con 1×1 nhẹ hơn: **đứng được trên ô Fragile (F)** mà khối đầy đủ sẽ làm vỡ,
  nhưng **không đủ nặng để đạp công tắc loại `heavy`**.
- Khi 2 khối con nằm **kề nhau**, nhấn **Space** để **hợp nhất** lại thành khối 1×2.
- Chỉ **thắng** khi khối đã hợp nhất và đứng thẳng trên đích (G).

**Màn demo:** `level13` — có ô nút tách ngay đầu hành lang Fragile rộng 1 ô.
Khối đầy đủ không thể qua hành lang; phải đứng lên nút để tách, đưa từng khối
con qua rồi hợp nhất lại đứng lên đích.

### Định dạng ô trong file level (`levels/*.json`)

| Ký hiệu | Ý nghĩa |
|---------|---------|
| `" "` | Ô trống (rơi) |
| `"O"` | Sàn thường |
| `"F"` | Ô dễ vỡ (khối đứng thẳng sẽ vỡ; khối con 1×1 đứng được) |
| `"G"` | Đích |
| `"P"` | Ô nút tách khối |
| `"B_x"` | Cầu (đóng/mở theo công tắc) |
