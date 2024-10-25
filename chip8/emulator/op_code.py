import dataclasses


@dataclasses.dataclass(frozen=True)
class OpCode:
    byte1: int
    byte2: int

    def op(self) -> int:
        return (self.byte1 >> 4) & 0xF

    def x(self) -> int:
        return self.byte1 & 0xF

    def y(self) -> int:
        return (self.byte2 >> 4) & 0xF

    def n(self) -> int:
        return self.byte2 & 0xF

    def nn(self) -> int:
        return self.byte2

    def nnn(self) -> int:
        return (self.byte1 & 0xF) << 8 | self.byte2

    def full(self) -> int:
        return self.byte1 << 8 | self.byte2
