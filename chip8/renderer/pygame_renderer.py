import pygame


class NullRenderer:
    def render_screen(self, display: list[list[int]]) -> None:
        pass

    def sync(self, fps: int) -> None:
        pass

    def quit(self) -> None:
        pass


PIXEL_SIZE = 10
WIDTH = 64
HEIGHT = 32


class Square(pygame.sprite.Sprite):
    def __init__(self, color: tuple[int, int, int], size: int):
        super().__init__()
        self.surf = pygame.Surface((size, size))
        self.surf.fill(color)


class PygameRenderer(NullRenderer):
    def __init__(
        self,
        window_name: str,
        background_color: tuple[int, int, int],
        sprite_color: tuple[int, int, int],
    ):
        self.background_color = background_color
        self.sprite = Square(sprite_color, 10)

        pygame.display.init()
        self.display_surface = pygame.display.set_mode(
            (WIDTH * PIXEL_SIZE, HEIGHT * PIXEL_SIZE)
        )
        pygame.display.set_caption(window_name)
        self.fps = pygame.time.Clock()

    def render_screen(self, display: list[list[int]]):
        self.display_surface.fill(self.background_color)
        for x, row in enumerate(display):
            for y, value in enumerate(row):
                if value == 1:
                    self.display_surface.blit(
                        self.sprite.surf, (x * PIXEL_SIZE, y * PIXEL_SIZE)
                    )
        pygame.display.update()

    def sync(self, fps: int) -> None:
        self.fps.tick(fps)

    def quit(self) -> None:
        pygame.quit()
