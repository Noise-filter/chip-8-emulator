import dataclasses
import sys
import time

import pygame
from pygame.locals import *

from chip8.emulator.interpreter import (
    Interpreter,
    UnknownInstructionError,
    InterpreterConfiguration,
)
from chip8.input.input import NullInput
from chip8.renderer.pygame_renderer import NullRenderer

CATEGORY_MASK = 0xF000
BACKGROUND_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
PIXEL_SIZE = 10
CLOCK_HZ = 60.0
CLOCK_RATE = 1.0 / CLOCK_HZ


@dataclasses.dataclass
class EmulatorConfiguration:
    instructions_per_second: int = 700
    shift_set_vx: bool = False
    store_and_load_increment_i: bool = False
    display_width: int = 64
    display_height: int = 32


class Emulator:
    def __init__(self, renderer: NullRenderer, input_handler: NullInput):
        self.renderer = renderer
        self.input_handler = input_handler

        self.configuration = EmulatorConfiguration(
            instructions_per_second=700,
            shift_set_vx=False,
            store_and_load_increment_i=False,
            display_width=64,
            display_height=32,
        )
        self.interpreter_configuration = InterpreterConfiguration(
            shift_set_vx=self.configuration.shift_set_vx,
            store_and_load_increment_i=self.configuration.store_and_load_increment_i,
            display_width=self.configuration.display_width,
            display_height=self.configuration.display_height,
        )
        self.interpreter = Interpreter(self.interpreter_configuration)

        self.tick_timer: float = 0

        self.debug = False
        self.step_through = False
        self.break_point = False

    def load_font(self, font: list[int]):
        self.interpreter.load_font(font)

    def load_rom(self, rom: list[int]):
        self.interpreter.load_rom(rom)

    def run(self):
        self.tick_timer = time.time()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit_emulator()
                elif event.type == KEYDOWN:
                    if event.key == K_n:
                        self.step_through = True
                    elif event.key == K_b:
                        self.break_point = not self.break_point

            if self.debug and self.break_point:
                if self.step_through:
                    self.step_through = False
                else:
                    time.sleep(0.01)
                    continue

            keys: list[bool] = self.input_handler.get_key_presses()
            if keys[-1]:
                self.quit_emulator()

            op_code = self.interpreter.fetch()
            if self.debug:
                print(self.interpreter.registers)
                print(hex(op_code.full()))
            try:
                self.interpreter.decode_execute(op_code, keys[:-1])
            except UnknownInstructionError as e:
                print(e, file=sys.stderr)
                self.quit_emulator()

            if self.interpreter.display_update:
                self.renderer.render_screen(self.interpreter.get_display())

            self.renderer.sync(self.configuration.instructions_per_second)
            self.tick()

    def tick(self):
        new_time = time.time()
        if new_time - self.tick_timer >= CLOCK_RATE:
            self.tick_timer = new_time
            self.interpreter.tick_timers()

    def quit_emulator(self):
        self.renderer.quit()
        sys.exit()
