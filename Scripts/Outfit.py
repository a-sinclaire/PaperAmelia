import pygame


def scale_img(img, scale):
    return pygame.transform.scale(img, (img.get_width() / scale, img.get_height() / scale))


class Article:
    def __init__(self, layer, file_path, priority, scale=4.0):
        self.layer = layer
        self.file_path = file_path
        self.priority = priority
        self.sprite = None
        self.scale = scale

    def load_sprite(self):
        self.sprite = pygame.image.load(self.file_path)
        self.sprite = scale_img(self.sprite, self.scale)
        print(f'LOADED: {self.file_path}')

    def draw(self, screen):
        if self.sprite is None:
            self.load_sprite()
        screen.blit(self.sprite, (0, 0))


class Outfit:
    def __int__(self):
        pass
