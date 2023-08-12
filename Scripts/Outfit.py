import pygame


def scale_img(img, scale):
    return pygame.transform.scale(img, (img.get_width() / scale, img.get_height() / scale))


class Article:
    articles = []

    def __init__(self, layer, file_path, priority=0, scale=4.0):
        self.layer = layer
        self.file_path = file_path
        self.priority = priority
        self.sprite = None
        self.scale = scale
        Article.articles.append(self)

    def load_sprite(self):
        self.sprite = pygame.image.load(self.file_path)
        self.sprite = scale_img(self.sprite, self.scale)
        print(f'LOADED: {self.file_path}')

    def draw(self, screen):
        if self.sprite is None:
            self.load_sprite()
        screen.blit(self.sprite, (0, 0))


class Outfit:
    def __init__(self, articles=[]):
        self.articles = articles

    def toggle_article(self, article):
        if article in self.articles:
            self.articles.remove(article)
            return
        self.articles.append(article)

    def draw(self, screen):
        for a in self.articles:
            a.draw(screen)

