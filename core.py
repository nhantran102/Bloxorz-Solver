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
        self.block = Block(start_r, start_c, "standing")
        
        # --- CHUẨN BỊ CHO TÍNH NĂNG NÂNG CAO ---
        # Lưu trạng thái các cây cầu dưới dạng dict để dễ thay đổi: { "bridge_id": True/False (đóng/mở) }
        self.bridges_state = map_data.get("initial_bridges", {}) 
        # Lưu thông tin thiết kế của công tắc từ JSON
        self.switches = map_data.get("switches", []) 

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

    def _check_and_trigger_switches(self):
        """Hàm nội bộ kiểm tra xem vị trí hiện tại của Block có kích hoạt công tắc nào không"""
        occupied = self.block.get_occupied_cells()
        
        for switch in self.switches:
            sr, sc = switch["pos"]
            if (sr, sc) in occupied:
                # Kiểm tra loại công tắc
                if switch["type"] == "heavy" and self.block.orientation != "standing":
                    continue # Công tắc nặng chỉ kích hoạt khi đứng thẳng
                
                # Thực hiện đổi trạng thái của Cầu liên kết (Toggle hoặc Permanent)
                for target_bridge in switch["target_bridges"]:
                    if switch["action"] == "toggle":
                        self.bridges_state[target_bridge] = not self.bridges_state.get(target_bridge, False)
                    elif switch["action"] == "open":
                        self.bridges_state[target_bridge] = True

    def check_win(self):
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
            
            if self.check_win():
                print("Victory!")
            return True
        return False