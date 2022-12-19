import json

import pygame
from types import SimpleNamespace
from maze_utils import generate_maze, resolve_maze


class Game:
    MAP_SIZE = (40, 40)
    MAP_WALL_WIDTH = 2
    PATH_WIDTH = 5
    FRAME_RATE = 60
    TOP_SPACE = 120
    MARGIN = 5

    def __init__(self):
        self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.size_x, self.size_y = self.window.get_size()

        size = self.size_x - 2 * Game.MARGIN, self.size_y - Game.TOP_SPACE - 2 * Game.MARGIN

        limiting_axis = 0 if size[0] / Game.MAP_SIZE[0] < size[1] / Game.MAP_SIZE[1] else 1

        self.unit = size[limiting_axis] / Game.MAP_SIZE[limiting_axis]

        self.width, self.height = (self.unit * Game.MAP_SIZE[0],
                                   self.unit * Game.MAP_SIZE[1])

        self.surface = pygame.surface.Surface((self.width, self.height))

        self.running = False
        self.clock = pygame.time.Clock()
        self.frame_count = 0

        self.map = Map(generate_maze(Game.MAP_SIZE), Game.MAP_SIZE, self.unit, Game.MAP_WALL_WIDTH)
        self.player = Player(*self.map.start, self.unit)
        self.direction = 0

        self.buttons = []

        # New button
        self.create_button((Game.MARGIN, Game.MARGIN),
                           (self.size_x / 3 - 3 * Game.MARGIN, Game.TOP_SPACE - 2 * Game.MARGIN),
                           "New Labyrinth",
                           self.reset)

        # Resolve button
        self.create_button((Game.MARGIN + self.size_x / 3, Game.MARGIN),
                           (self.size_x / 3 - 3 * Game.MARGIN, Game.TOP_SPACE - 2 * Game.MARGIN),
                           "Resolve",
                           self.resolve)

        # Quit button
        self.create_button((Game.MARGIN + self.size_x * 2 / 3, Game.MARGIN),
                           (self.size_x / 3 - 3 * Game.MARGIN, Game.TOP_SPACE - 2 * Game.MARGIN),
                           "Quit",
                           self.stop_running)

    def create_button(self, pos, size, text, action):
        self.buttons.append(Button(self.window, pos, size, text, action))

    def stop_running(self):
        self.running = False

    def loop(self):
        self.running = True

        while self.running:
            self.manage_events()
            self.update()
            self.draw()
            self.clock.tick(Game.FRAME_RATE)
            self.frame_count += 1

    def manage_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                switch_theme()
                self.map.draw()
            if event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT
            ):
                self.frame_count = 0
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    button.click_event(mouse_pos)

        if self.frame_count % 12 == 0:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.direction = 1
            elif keys[pygame.K_RIGHT]:
                self.direction = 2
            elif keys[pygame.K_DOWN]:
                self.direction = 3
            elif keys[pygame.K_LEFT]:
                self.direction = 4
            else:
                self.direction = 0
        else:
            self.direction = 0

    def update(self):
        if self.direction == 1 and not self.map.test_collision(self.player, 1):
            self.player.move_up()
        elif self.direction == 2 and not self.map.test_collision(self.player, 2):
            self.player.move_right()
        elif self.direction == 3 and not self.map.test_collision(self.player, 3):
            self.player.move_down()
        elif self.direction == 4 and not self.map.test_collision(self.player, 4):
            self.player.move_left()

        if (self.player.x, self.player.y) == self.map.finish:
            self.reset()

    def draw(self):
        # Background
        self.window.fill(settings.background_color)
        self.surface.fill(settings.map_bg_color)

        # Buttons
        for button in self.buttons:
            button.render()

        # Player and Labyrinth ; Order depending on player pos
        if (self.player.x, self.player.y) not in [self.map.start, self.map.finish]:
            self.player.render(self.surface)
            self.map.render(self.surface)
        else:
            self.map.render(self.surface)
            self.player.render(self.surface)

        self.window.blit(self.surface, (self.size_x / 2 - self.width / 2, (self.size_y - self.height + 120) / 2))

        # Flip display
        pygame.display.flip()

    def reset(self):
        self.map = Map(generate_maze(Game.MAP_SIZE), Game.MAP_SIZE, self.unit, Game.MAP_WALL_WIDTH)
        self.player.move_to(*self.map.start)

    def resolve(self):
        self.map.resolve()


class Button:

    def __init__(self, surface, pos,
                 size, text, action):
        pygame.font.init()
        self.surface = surface
        self.x, self.y = pos
        self.width, self.height = size
        self.text = text
        self.action = action

    def collide_with(self, pos):
        x, y = pos
        return (self.x < x < self.x + self.width) and (self.y < y < self.y + self.height)

    def click_event(self, pos):
        if self.collide_with(pos):
            self.action()

    def render(self):
        font = pygame.font.SysFont('segoeui', 24)
        img = font.render(self.text, True, settings.button_foreground_color)
        text_width, text_height = img.get_size()
        dx = self.x + self.width / 2 - text_width / 2
        dy = self.y + self.height / 2 - text_height / 2

        pygame.draw.rect(self.surface, settings.button_background_color, pygame.rect.Rect(self.x, self.y, self.width, self.height),
                         0, settings.button_border_radius)
        if settings.button_border_width:
            pygame.draw.rect(self.surface, settings.button_border_color, pygame.rect.Rect(self.x, self.y, self.width, self.height),
                             settings.button_border_width, settings.button_border_radius)
        self.surface.blit(img, (dx, dy))

    def on_click(self):
        self.action()


class Map:

    def __init__(self, map_, size: tuple, unit_size, wall_width=1):
        self.map = map_
        self.width, self.height = size
        self.unit_size = unit_size
        self.wall_width = wall_width
        self.start = (0, 1)
        self.finish = (self.width - 1, self.height - 2)
        self.img = pygame.surface.Surface((self.unit_size * self.width, self.unit_size * self.height))
        self.img.fill((255, 255, 255))
        self.img.set_colorkey((255, 255, 255))
        self.resolution_drawn = False
        self.resolution_lines = []

        self.draw()

    def draw(self):
        self.img.fill((255, 255, 255))
        for x in range(self.width):
            for y in range(self.height):
                if self.map[y][x] & 32:
                    pygame.draw.rect(self.img, settings.map_arrival_color,
                                     pygame.rect.Rect(x * self.unit_size, y * self.unit_size,
                                                      self.unit_size, self.unit_size))
                    self.finish = (x, y)
                elif self.map[y][x] & 16:
                    pygame.draw.rect(self.img, settings.map_start_color,
                                     pygame.rect.Rect(x * self.unit_size, y * self.unit_size,
                                                      self.unit_size, self.unit_size))
                    self.start = (x, y)
                if self.map[y][x] & 8:
                    pygame.draw.line(self.img, settings.map_wall_color,
                                     (x * self.unit_size, y * self.unit_size),
                                     (x * self.unit_size, (y + 1) * self.unit_size),
                                     width=self.wall_width)
                if self.map[y][x] & 4:
                    pygame.draw.line(self.img, settings.map_wall_color,
                                     (x * self.unit_size, (y + 1) * self.unit_size),
                                     ((x + 1) * self.unit_size, (y + 1) * self.unit_size),
                                     width=self.wall_width)
                if self.map[y][x] & 2:
                    pygame.draw.line(self.img, settings.map_wall_color,
                                     ((x + 1) * self.unit_size, y * self.unit_size),
                                     ((x + 1) * self.unit_size, (y + 1) * self.unit_size),
                                     width=self.wall_width)
                if self.map[y][x] & 1:
                    pygame.draw.line(self.img, settings.map_wall_color,
                                     (x * self.unit_size, y * self.unit_size),
                                     ((x + 1) * self.unit_size, y * self.unit_size),
                                     width=self.wall_width)

    def test_collision(self, player, direction):
        """
        Direction
            1
        4   0   2
            3
        """
        if direction == 1:
            return bool(self.map[player.y][player.x] & 1) or player.y - 1 < 0
        if direction == 2:
            return bool(self.map[player.y][player.x] & 2) or player.x + 1 > self.width - 1
        if direction == 3:
            return bool(self.map[player.y][player.x] & 4) or player.y + 1 > self.height - 1
        if direction == 4:
            return bool(self.map[player.y][player.x] & 8) or player.x - 1 < 0

    def render(self, surface: pygame.surface.Surface):
        surface.blit(self.img, (0, 0))

        length = len(self.resolution_lines)
        t = 0

        for line in self.resolution_lines:
            r = t * 255 / length
            g = 255 - t * 255 / length
            b = 255 - abs(255 * (t - length / 2) / length)

            x0, y0, x1, y1 = line

            try:
                pygame.draw.line(surface, (r, g, b),
                                 ((x0 + 0.5) * self.unit_size, (y0 + 0.5) * self.unit_size),
                                 ((x1 + 0.5) * self.unit_size, (y1 + 0.5) * self.unit_size),
                                 width=Game.PATH_WIDTH
                                 )
            except ValueError as e:
                print(r, g, b)
                raise e
            t += 1

    def resolve(self):
        if self.resolution_drawn:
            self.resolution_lines.clear()
        else:
            path = resolve_maze(self.map)
            for i in range(len(path) - 1):
                self.resolution_lines.append((*path[i], *path[i + 1]))

        self.resolution_drawn = not self.resolution_drawn


class Player:

    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

    def render(self, surface):
        pygame.draw.rect(surface, settings.player_color, pygame.rect.Rect(self.x * self.size, self.y * self.size,
                                                                          self.size, self.size))

    def move_up(self):
        self.y -= 1

    def move_down(self):
        self.y += 1

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1

    def move_to(self, x, y):
        self.x, self.y = x, y


if __name__ == '__main__':
    themes = (
        "light_theme.json",
        "dark_theme.json",
        "marine_theme.json"
    )
    themenumber = 0

    with open('../themes/' + themes[0], 'r') as themefile:
        settings = SimpleNamespace(**json.loads(themefile.read()))


    def switch_theme():
        global settings, themenumber
        themenumber = (themenumber + 1) % len(themes)

        with open('../themes/' + themes[themenumber], 'r') as theme_file:
            settings = SimpleNamespace(**json.loads(theme_file.read()))

    Game().loop()
