# REGISTER_DOCTEST
import pygame

from settings import asset_path

from animations.animated import AnimatedSprite


def sample_program() -> int:
    # Настройки
    TILE_SIZE = 40
    GRID_WIDTH = 15
    GRID_HEIGHT = 10
    SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH
    SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT

    # Цвета
    BLACK = (0, 0, 0)
    BROWN = (139, 69, 19)
    GOLD = (255, 215, 0)
    # BLUE = (0, 0, 255)

    # Инициализация
    pygame.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    TILE_SIZE = min(SCREEN_WIDTH // GRID_WIDTH, SCREEN_HEIGHT // GRID_HEIGHT)
    DIGGER_SPRITE = AnimatedSprite(asset_path("digger"), (TILE_SIZE, TILE_SIZE))
    DIGGER_ANIMATION = DIGGER_SPRITE.create_animation()

    clock = pygame.time.Clock()

    # Игровое поле: 0 — земля, 1 — золото
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    grid[4][7] = 1
    grid[2][3] = 1

    # Игрок
    player_x = 0
    player_y = 0

    direction = "r"
    num_frame = 0
    # Основной цикл
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 0

        # Управление
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            direction = "l"
            player_x -= 1
        if keys[pygame.K_RIGHT] and player_x < GRID_WIDTH - 1:
            direction = "r"
            player_x += 1
        if keys[pygame.K_UP] and player_y > 0:
            direction = "u"
            player_y -= 1
        if keys[pygame.K_DOWN] and player_y < GRID_HEIGHT - 1:
            direction = "d"
            player_y += 1

        DIGGER_ANIMATION.set_direction(direction)
        num_frame += 1

        # Копание: убираем золото
        if grid[player_y][player_x] == 1:
            grid[player_y][player_x] = 0

        # Отрисовка
        screen.fill(BLACK)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if grid[y][x] == 0:
                    pygame.draw.rect(screen, BROWN, rect)
                elif grid[y][x] == 1:
                    pygame.draw.rect(screen, GOLD, rect)

        # Игрок
        DIGGER_ANIMATION.set_position(
            (
                player_x * TILE_SIZE + TILE_SIZE // 2,
                player_y * TILE_SIZE + TILE_SIZE // 2,
            )
        )
        DIGGER_ANIMATION.draw(surface=screen)
        DIGGER_ANIMATION.next_frame()

        pygame.display.flip()
        clock.tick(1)
