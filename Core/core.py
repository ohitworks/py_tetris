"""
The game core.
"""

from collections import deque
from functools import singledispatchmethod


class Line:
    """
    Line 使用双向队列表示每一行的元素
    """
    def __init__(self, width: int):
        """
        """
        self.width = width
        self.value = deque([0 for _ in range(width)], maxlen=width)

    @staticmethod
    def from_integer(value: int, width=None):
        """
        从数字生成
        """
        value = bin(value)[2:]
        if width is None:
            width = len(value)
        else:
            if len(value) > width:
                raise ValueError("The given number %d is too big, should less than 2**%d." % (value, width))
            value = value.rjust(width, "0")
        r = Line(width)
        r.value.extend(1 if i == "1" else 0 for i in value)
        return r

    # --- 算术运算
    def __lshift__(self, times: int):
        """
        左移, 补 0
        """
        for _ in range(times):
            self.value.append(0)
    
    def __rshift__(self, times: int):
        """
        右移, 补 0
        """
        for _ in range(times):
            self.value.appendleft(0)

    @singledispatchmethod
    def __and__(self, value):
        """
        按位与 (&)
        """
        try:
            v = "".join("1" if i else "0" for i in value)
        except TypeError:
            raise TypeError("give iterable object or int")
        else:
            # 将另一个输入转换为整数
            return self & int(v, base=2)
    
    @__and__.register
    def _(self, value: int):
        """
        按位与
        """
        new = int(self) & value
        return Line.from_integer(new, self.width)
    
    @singledispatchmethod
    def __or__(self, value):
        """
        按位或 (|)
        """
        try:
            v = "".join("1" if i else "0" for i in value)
        except TypeError:
            raise TypeError("give iterable object or int")
        else:
            # 将另一个输入转换为整数
            return self | int(v, base=2)
    
    @__or__.register
    def _(self, value: int):
        """
        按位或
        """
        new = int(self) | value
        return Line.from_integer(new, self.width)
    
    @singledispatchmethod
    def __xor__(self, value):
        """
        按位异或 (^)
        """
        try:
            v = "".join("1" if i else "0" for i in value)
        except TypeError:
            raise TypeError("give iterable object or int")
        else:
            # 将另一个输入转换为整数
            return self ^ int(v, base=2)
    
    @__xor__.register
    def _(self, value: int):
        """
        按位异或
        """
        new = int(self) ^ value
        return Line.from_integer(new, self.width)

    def __int__(self):
        """
        转换为整数
        """
        v = "".join("1" if i else "0" for i in self.value)
        return int(v, base=2)

    # --- 队列
    def __iter__(self):
        return iter(self.value)
        
    def __getitem__(self, key):
        return self.value[key]
    
    def __setitem__(self, key, value):
        self.value[key] = value
    
    def __delitem__(self, key):
        del self.value[key]

    # --- Debug
    def __repr__(self) -> str:
        return type(self).__name__ + f"(width={self.width}) -> " + repr(list(self.value))

    # --- 实用功能
    def is_all_true(self) -> bool:
        """
        返回该行是否被"填满"
        """
        return all(self.value)
    
    def is_all_same(self) -> bool:
        return len(set(self.value)) == 1
    

class Item:
    """
    俄罗斯方块的"方块"
    """
    def __init__(self, positions: list[int], pos_x: int, pos_y: int, rotate=0):
        """
        通过 positions 参数描述方块的形状

          0
        0 +----x
          |
          |
          y

        :param positions: 列表, 元素依次表示从上向下每一行的占用情况. 如 [2, 2, 3] 表示一个高度为 3 的 "L" 型结构.
        :param pos_x:     方块(左上角) 的横坐标
        :param pos_y:     方块(左上角) 的纵坐标
        :param rotate:    旋转方向, 0 表示不移动, 每+1表示逆时针 90° 
        """
        self.rotate = rotate % 4
        self.positions: list[int] = [int(i) for i in positions]
        self.width = max(positions).bit_length()
        self.pos_x = pos_x  # pos_x 无法检查, 毕竟 width 都是根据值生成的...

        # pos_y check and setup pos_y
        for i in range(len(positions) - 1):
            if positions[i] == 0:
                self.positions.pop(0)
            else:
                break
        self.pos_y = pos_y + i  # 向下移动 i 格

        # ending 0 line check and length  Note: the tail numbers don't affect pos_y
        while self.positions[-1] == 0:
            self.positions.pop()
        self.length = len(self.positions)

        # 0 on right side check  Note: the right number doesn't affect pos_x
        while all(i % 2 == 0 for i in self.positions):  # i % 2 == 0 说明最右端是 0
            self.positions = [i >> 1 for i in self.positions]
    
    def cut_row(self, index=-1):
        """
        返回相当于 "切下" 此方块的 `index` 行后的新方块
        """
        positions = self.positions.copy()
        positions[index] = 0
        return Item(positions, self.pos_x, self.pos_y, self.rotate)  # 交给 pos_y check 就行
    
    def cut_column(self, index=0):
        """
        返回相当于 "切下" 此方块的 `index` 列后的新方块
        
        :param index: int, 0 代表最左列
        """
        positions = []
        if index < 0:
            k = ((1 << self.width) - 1) ^ (1 << (- index - 1))
            assert k.bit_length() > positions.width, IndexError(index, "<", -self.width)
        else:
            # index >= 0
            try:
                k = ((1 << self.width) - 1) ^ (1 << (self.width - index - 1))
            except ValueError:
                raise IndexError(index, ">=", self.width)
        for i in self.positions:
            positions.append(i & k)

        dx = self.width - max(positions).bit_length()  # calculate detla x
        return Item(positions, self.pos_x + dx, self.pos_y, self.rotate)

    def rotate_90d_counterclockwise(self, geometric_center=True):
        """
        逆时针旋转 90°
        
        :param geometric_center: if True, indicates rotation around the geometric center,
                                 otherwise rotation around the upper left corner.
        """
        positions = []
        for i in range(self.width):
            val = 0
            for t, x in enumerate(self.positions, 1):
                val += ((x >> i) & 1) << (self.length - t)
            positions.append(val)

        if geometric_center:
            pos_x = (self.pos_x + self.width // 2) - self.length // 2
            pos_y = (self.pos_y + self.length // 2) - self.width // 2
        else:
            pos_x = self.pos_x
            pos_y = self.pos_y - self.width 
        return Item(positions, pos_x, pos_y)

    def _get_lines_for_print(self):
        """
        内部工程函数, 不考虑 rotate
        """
        lines = []
        for i in self.positions:
            lines.append(bin(int(i))[2:].replace("1", "◼").replace("0", "◻").rjust(self.width, "◻"))
        return lines
        
    def __repr__(self):
        print(f"Item({self.positions}, pos_x={self.pos_x}, pos_y={self.pos_y}, rotate={self.rotate})")
    
        for _ in range(self.rotate):
            self = self.rotate_90d_counterclockwise()

        return "\n".join(self._get_lines_for_print())


class GameMap:
    """
    游戏地图, 是元素为 Line 的 deque
    """
    def __init__(self, size_x, size_y) -> None:
        """
        :param size_x: 地图的宽度
        :param size_y: 地图的长度
        """
        self.columns = deque([Line(size_x) for _ in range(size_y)], maxsize=size_y)
    
    def show(self):
        """
        显示
        """
        for line in self.columns:
            print("".join("◼" if i else "◻" for i in line))
    
    