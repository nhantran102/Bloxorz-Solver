import json

class Block:
    def __init__(self, r, c, orientation="standing"):
        self.r = r
        self.c = c
        self.orientation = orientation

    def get_occupied_cells(self):
        if self.orientation == "standing":
            return [(self.r, self.c)]
        elif self.orientation == "horizontal":
            return [(self.r, self.c), (self.r, self.c + 1)]
        elif self.orientation == "vertical":
            return [(self.r, self.c), (self.r + 1, self.c)]

    def move(self, direction):
        d = direction.upper()
        r, c, o = self.r, self.c, self.orientation
        if o == "standing":
            if d == "UP":    return Block(r - 2, c, "vertical")
            if d == "DOWN":  return Block(r + 1, c, "vertical")
            if d == "LEFT":  return Block(r, c - 2, "horizontal")
            if d == "RIGHT": return Block(r, c + 1, "horizontal")
        elif o == "horizontal":
            if d == "UP":    return Block(r - 1, c, "horizontal")
            if d == "DOWN":  return Block(r + 1, c, "horizontal")
            if d == "LEFT":  return Block(r, c - 1, "standing")
            if d == "RIGHT": return Block(r, c + 2, "standing")
        elif o == "vertical":
            if d == "UP":    return Block(r - 1, c, "standing")
            if d == "DOWN":  return Block(r + 2, c, "standing")
            if d == "LEFT":  return Block(r, c - 1, "vertical")
            if d == "RIGHT": return Block(r, c + 1, "vertical")
        return self

    # --- BỔ SUNG ĐỂ HỖ TRỢ THUẬT TOÁN TÌM KIẾM ---
    def __eq__(self, other):
        if not isinstance(other, Block): return False
        return self.r == other.r and self.c == other.c and self.orientation == other.orientation

    def __hash__(self):
        return hash((self.r, self.c, self.orientation))


class GameState:
    def __init__(self, map_file_path):
        with open(map_file_path, 'r') as f:
            map_data = json.load(f)
        
        self.grid = map_data["grid"]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0]) if self.rows > 0 else 0
        
        start_r, start_c = map_data["start_pos"]
        self.start_r, self.start_c = start_r, start_c  # nhớ vị trí start để tách khối
        self.block = Block(start_r, start_c, "standing")
        
        # --- CHUẨN BỊ CHO TÍNH NĂNG NÂNG CAO ---
        # Lưu trạng thái các cây cầu dưới dạng dict để dễ thay đổi: { "bridge_id": True/False (đóng/mở) }
        self.bridges_state = map_data.get("initial_bridges", {}) 
        # Lưu thông tin thiết kế của công tắc từ JSON
        self.switches = map_data.get("switches", [])

        # --- TÁCH KHỐI (SPLIT) ---
        # split_cells = None  -> đang là 1 khối 1x2 bình thường (dùng self.block)
        # split_cells = [[r,c],[r,c]] -> đã tách thành 2 khối con 1x1
        self.split_cells = None
        self.active = 0  # chỉ số khối con (0/1) đang được điều khiển

    def is_valid_move(self, next_block):
        occupied = next_block.get_occupied_cells()
        
        for r, c in occupied:
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                return False
            
            cell_type = self.grid[r][c]
            
            # Nếu là ô trống (Void) -> Không hợp lệ
            if cell_type == " ":
                return False
                
            # Nếu đi vào ô Cầu ('B'), phải kiểm tra xem cầu đó đang ĐÓNG hay MỞ
            if cell_type.startswith("B_"): 
                bridge_id = cell_type # Ví dụ đặt tên trong grid là "B_1"
                if not self.bridges_state.get(bridge_id, False): # Nếu cầu đang đóng
                    return False
                
        if next_block.orientation == "standing":
            r, c = occupied[0]
            if self.grid[r][c] == "F": # Ô fragile
                return False  
                
        return True

    def _trigger_switch_at(self, r, c, is_heavy_press):
        """Kích hoạt công tắc (nếu có) tại ô (r, c).
        is_heavy_press: khối hiện tại có đủ 'nặng' để đạp công tắc loại heavy không
        (chỉ khối 1x2 đứng thẳng mới nặng; khối nằm hoặc khối con 1x1 thì không)."""
        for switch in self.switches:
            sr, sc = switch["pos"]
            if (sr, sc) == (r, c):
                # Công tắc nặng chỉ kích hoạt bởi lực đè tập trung (đứng thẳng)
                if switch["type"] == "heavy" and not is_heavy_press:
                    continue
                for target_bridge in switch["target_bridges"]:
                    if switch["action"] == "toggle":
                        self.bridges_state[target_bridge] = not self.bridges_state.get(target_bridge, False)
                    elif switch["action"] == "open":
                        self.bridges_state[target_bridge] = True

    def _check_and_trigger_switches(self):
        """Hàm nội bộ kiểm tra xem vị trí hiện tại của Block có kích hoạt công tắc nào không"""
        standing = self.block.orientation == "standing"
        for r, c in self.block.get_occupied_cells():
            self._trigger_switch_at(r, c, is_heavy_press=standing)

    # ==========================================
    #  TÁCH KHỐI (SPLIT) — cơ chế 2 khối con 1x1
    # ==========================================
    def is_split(self):
        return self.split_cells is not None

    def _split_from_pad(self, r, c):
        """Tách khối khi ĐỨNG trên ô nút tách (P):
        - 1 khối con giữ ở ngay ô nút (r, c)
        - 1 khối con xuất hiện ở vị trí start của màn"""
        sr, sc = self.start_r, self.start_c
        if (r, c) == (sr, sc):
            return  # nút trùng vị trí start -> bỏ qua để tránh 2 khối chồng nhau
        self.split_cells = [[r, c], [sr, sc]]
        self.active = 0

    def toggle_active(self):
        """Đổi khối con đang điều khiển (khi đã tách)."""
        if self.is_split():
            self.active = 1 - self.active

    def try_rejoin(self):
        """Nếu 2 khối con đang kề nhau -> hợp nhất lại thành 1 khối 1x2 nằm.
        Trả về True nếu hợp nhất thành công."""
        if not self.is_split():
            return False
        (r1, c1), (r2, c2) = self.split_cells
        if r1 == r2 and abs(c1 - c2) == 1:
            self.block = Block(r1, min(c1, c2), "horizontal")
        elif c1 == c2 and abs(r1 - r2) == 1:
            self.block = Block(min(r1, r2), c1, "vertical")
        else:
            return False  # hai khối chưa kề nhau
        self.split_cells = None
        self.active = 0
        return True

    def move_split(self, direction):
        """Di chuyển khối con đang active 1 ô.
        Trả về: 'ok' (đã đi), 'blocked' (bị chặn, không đổi), 'fell' (rơi khỏi map -> thua)."""
        deltas = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}
        dr, dc = deltas[direction.upper()]
        ar, ac = self.split_cells[self.active]
        nr, nc = ar + dr, ac + dc
        other = self.split_cells[1 - self.active]

        # Ra ngoài bản đồ hoặc rơi vào ô trống (Void) -> rơi
        if not (0 <= nr < self.rows and 0 <= nc < self.cols) or self.grid[nr][nc] == " ":
            return "fell"

        cell = self.grid[nr][nc]
        # Cầu đang đóng -> coi như tường, bị chặn
        if cell.startswith("B_") and not self.bridges_state.get(cell, False):
            return "blocked"
        # Không được chồng lên khối con kia
        if [nr, nc] == other:
            return "blocked"

        self.split_cells[self.active] = [nr, nc]
        # Khối con 1x1 KHÔNG đủ nặng cho công tắc heavy
        self._trigger_switch_at(nr, nc, is_heavy_press=False)
        return "ok"

    def check_win(self):
        # Đang tách thì chưa thể thắng — phải hợp nhất và đứng trên đích
        if self.is_split():
            return False
        if self.block.orientation == "standing":
            r, c = self.block.r, self.block.c
            if self.grid[r][c] == "G":
                return True
        return False

    def update_move(self, direction):
        next_block = self.block.move(direction)
        if self.is_valid_move(next_block):
            self.block = next_block
            # Kích hoạt công tắc sau khi di chuyển hợp lệ thành công
            self._check_and_trigger_switches()

            # Tách khối khi ĐỨNG thẳng trên ô nút tách (P)
            if not self.is_split() and self.block.orientation == "standing":
                r, c = self.block.r, self.block.c
                if self.grid[r][c] == "P":
                    self._split_from_pad(r, c)

            if self.check_win():
                print("Victory!")
            return True
        return False