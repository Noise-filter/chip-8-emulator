import dataclasses
import random

from chip8.input.key_codes import key_codes
from chip8.emulator.op_code import OpCode


class UnknownInstructionError(Exception):
    def __init__(self, message, operation_hex_code):
        super().__init__(message)
        self.operation_hex_code: int = operation_hex_code


@dataclasses.dataclass
class InterpreterConfiguration:
    shift_set_vx: bool = False
    store_and_load_increment_i: bool = False
    display_width: int = 64
    display_height: int = 32


class Interpreter:
    def __init__(self, configuration: InterpreterConfiguration):
        self.configuration: InterpreterConfiguration = configuration

        self.memory: list[int] = [0] * 4096
        self.display: list[list[int]] = []
        for i in range(64):
            self.display.append([0] * 32)
        self.pc: int = 512
        self.index_register: int = 0
        self.stack: list[int] = []
        self.delay_timer: int = 0
        self.sound_timer: int = 0
        self.registers: list[int] = [0] * 16

        self.display_update = False

        self.START_MEMORY_ADDRESS = 512

    def load_font(self, font: list[int]):
        self.memory[0 : len(font)] = font

    def load_rom(self, rom: list[int]):
        self.memory[
            self.START_MEMORY_ADDRESS : self.START_MEMORY_ADDRESS + len(rom)
        ] = rom

    def fetch(self) -> OpCode:
        op_code = OpCode(self.memory[self.pc], self.memory[self.pc + 1])
        self.pc += 2
        return op_code

    def decode_execute(self, op_code: OpCode, keys: list[bool]):
        self.display_update = False
        match op_code.op():
            case 0x0:
                if op_code.x() != 0x0:
                    print("")
                elif op_code.full() == 0x00E0:
                    self.display_update = True
                    self.display = []
                    for i in range(64):
                        self.display.append([0] * 32)
                elif op_code.full() == 0x00EE:
                    self.pc = self.stack.pop()
                else:
                    self.unknown_instruction(op_code)
            case 0x1:
                self.pc = op_code.nnn()
            case 0x2:
                self.stack.append(self.pc)
                self.pc = op_code.nnn()
            case 0x3:
                if self.registers[op_code.x()] == op_code.nn():
                    self.pc += 2
            case 0x4:
                if self.registers[op_code.x()] != op_code.nn():
                    self.pc += 2
            case 0x5:
                if self.registers[op_code.x()] == self.registers[op_code.y()]:
                    self.pc += 2
            case 0x6:
                self.registers[op_code.x()] = op_code.nn()
            case 0x7:
                self.registers[op_code.x()] += op_code.nn()
                self.registers[op_code.x()] %= 256
            case 0x8:
                match op_code.n():
                    case 0x0:
                        self.registers[op_code.x()] = self.registers[op_code.y()]
                    case 0x1:
                        self.registers[op_code.x()] |= self.registers[op_code.y()]
                    case 0x2:
                        self.registers[op_code.x()] &= self.registers[op_code.y()]
                    case 0x3:
                        self.registers[op_code.x()] ^= self.registers[op_code.y()]
                    case 0x4:
                        x = op_code.x()
                        self.registers[x] += self.registers[op_code.y()]
                        self.set_overflow(self.registers[x] > 255)
                        self.registers[x] = (self.registers[x] % 255) - 1
                    case 0x5:
                        x = op_code.x()
                        y = op_code.y()
                        if self.registers[x] >= self.registers[y]:
                            self.set_overflow(True)
                        else:
                            self.set_overflow(False)
                        self.registers[x] -= self.registers[y]
                        if self.registers[x] < 0:
                            self.registers[x] = 256 + self.registers[x]
                    case 0x6:
                        x = op_code.x()
                        if self.configuration.shift_set_vx:
                            self.registers[x] = self.registers[op_code.y()]
                        self.set_overflow(self.registers[x] & 1 == 1)
                        self.registers[x] >>= 1
                    case 0x7:
                        x = op_code.x()
                        y = op_code.y()
                        if self.registers[y] >= self.registers[x]:
                            self.set_overflow(True)
                        else:
                            self.set_overflow(False)
                        self.registers[x] = self.registers[y] - self.registers[x]
                    case 0xE:
                        x = op_code.x()
                        if self.configuration.shift_set_vx:
                            self.registers[x] = self.registers[op_code.y()]
                        self.set_overflow(self.registers[x] & 128 == 128)
                        self.registers[x] <<= 1
                        self.registers[x] &= 0xFF
                    case _:
                        self.unknown_instruction(op_code)
            case 0x9:
                if self.registers[op_code.x()] != self.registers[op_code.y()]:
                    self.pc += 2
            case 0xA:
                self.index_register = op_code.nnn()
            case 0xB:
                self.pc = op_code.nnn() + self.registers[0]
                # TODO: Implement a configurable different way
            case 0xC:
                self.registers[op_code.x()] = random.randint(0, 255) & op_code.nn()
            case 0xD:
                self.display_operation(op_code)
            case 0xE:
                match op_code.nn():
                    case 0x9E:
                        vx = self.registers[op_code.x()]
                        if keys[vx]:
                            self.pc += 2
                    case 0xA1:
                        vx = self.registers[op_code.x()]
                        if not keys[vx]:
                            self.pc += 2
                    case _:
                        self.unknown_instruction(op_code)
            case 0xF:
                match op_code.nn():
                    case 0x1E:
                        self.index_register = (
                            self.index_register + self.registers[op_code.x()]
                        ) % 2048
                    case 0x0A:
                        key_pressed = False
                        for index, key in enumerate(keys):
                            if key:
                                self.registers[op_code.x()] = list(key_codes.values())[
                                    index
                                ]
                                key_pressed = True
                                break
                        if not key_pressed:
                            self.pc -= 2
                    case 0x29:
                        self.index_register = (self.registers[op_code.x()] & 0x0F) * 5
                    case 0x33:
                        value = self.registers[op_code.x()]
                        for i in range(3):
                            self.memory[self.index_register + (2 - i)] = value % 10
                            value = int(value / 10)
                    case 0x55:
                        for i in range(0, op_code.x() + 1):
                            self.memory[self.index_register + i] = self.registers[i]
                        if self.configuration.store_and_load_increment_i:
                            self.index_register += op_code.x() + 1
                    case 0x65:
                        for i in range(0, op_code.x() + 1):
                            self.registers[i] = self.memory[self.index_register + i]
                        if self.configuration.store_and_load_increment_i:
                            self.index_register += op_code.x() + 1
                    case 0x07:
                        self.registers[op_code.x()] = self.delay_timer
                    case 0x15:
                        self.delay_timer = self.registers[op_code.x()]
                    case 0x18:
                        self.sound_timer = self.registers[op_code.x()]
                    case _:
                        self.unknown_instruction(op_code)
            case _:
                self.unknown_instruction(op_code)

    def display_operation(self, op_code: OpCode):
        self.display_update = True
        start_x = self.registers[op_code.x()] % self.configuration.display_width
        start_y = self.registers[op_code.y()] % self.configuration.display_height
        n = op_code.n()
        self.registers[-1] = 0

        y = start_y
        for i in range(n):
            if y >= self.configuration.display_height:
                break

            font_byte = self.memory[self.index_register + i]
            bits = bin(font_byte)[2:].zfill(8)

            x = start_x
            for bit in bits:
                if x >= self.configuration.display_width:
                    break

                bit = int(bit)
                old_pixel = self.display[x][y]
                self.display[x][y] = old_pixel ^ bit
                self.registers[-1] = (old_pixel & bit) | self.registers[-1]
                x += 1
            y += 1

    def set_overflow(self, value: bool):
        self.registers[-1] = int(value)

    def tick_timers(self):
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def has_display_updated(self) -> bool:
        return self.display_update

    def get_display(self) -> list[list[int]]:
        return self.display

    @staticmethod
    def unknown_instruction(op_code: OpCode):
        instruction = op_code.full()
        raise UnknownInstructionError(
            f"Unknown instruction: {hex(instruction)}", instruction
        )
