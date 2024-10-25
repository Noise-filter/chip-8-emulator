from chip8.input.input import PygameInput
from chip8.emulator.emulator import Emulator
from chip8.renderer.pygame_renderer import PygameRenderer

# fmt: off
font = [
    0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
    0x20, 0x60, 0x20, 0x20, 0x70,  # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
    0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
    0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
    0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
    0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
    0xF0, 0x80, 0xF0, 0x80, 0x80,  # F
]


# fmt: on


def load_rom(path: str) -> list[int]:
    with open(path, "rb") as file:
        return list(file.read())


def main():
    rom_bytes = load_rom(r"C:\Users\pontusfr\Downloads\chip-8 roms\Pong (alt).ch8")
    # rom_bytes = load_rom(r"C:\Users\pontusfr\Downloads\AC8E-master\roms\games\TETRIS")
    # rom_bytes = load_rom(r"C:\Users\pontusfr\Downloads\roms\programs\SQRT Test [Sergey Naydenov, 2010].ch8")

    background_color = (0, 0, 0)
    sprite_color = (255, 255, 255)

    renderer = PygameRenderer("CHIP-8 Emulator", background_color, sprite_color)
    # renderer = RendererInterface()

    input_handler = PygameInput()

    emulator = Emulator(renderer, input_handler)
    emulator.load_font(font)
    emulator.load_rom(rom_bytes)
    emulator.run()


if __name__ == "__main__":
    main()
