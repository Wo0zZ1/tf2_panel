import config as cfg


class Position:
    def __init__(self, x: int = 0, y: int = 0, index: int = 1):
        self.x = x
        self.y = y
        self.index = index

    def next(self):
        self.index += 1
        if self.x + cfg.WIDTH <= 1920 - cfg.WIDTH:
            self.x += cfg.WIDTH
        elif self.y + cfg.HEIGHT <= 1080 - cfg.HEIGHT:
            self.x = 0
            self.y += cfg.HEIGHT
