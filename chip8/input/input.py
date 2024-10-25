import pygame

from chip8.input.key_codes import key_codes


class NullInput:
    def get_key_presses(self) -> list[bool]:
        return [False] * len(key_codes)


class PygameInput(NullInput):
    def __init__(self):
        pass

    def get_key_presses(self) -> list[bool]:
        pressed_keys = pygame.key.get_pressed()
        keys = [False] * len(key_codes)
        for index, key_code in enumerate(key_codes.keys()):
            keys[index] = pressed_keys[key_code]
        return keys
