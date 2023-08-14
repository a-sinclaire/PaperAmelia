#
# Author: Amelia Sinclaire
# Copyright 2023
#

import pygame
import os
from PIL import Image, ImageOps

pygame.font.init()


class Button(pygame.sprite.Sprite):
    font = pygame.font.SysFont('comicsans', 12)
    n_buttons = 0

    def __init__(self, rect, callback, active=False, text='', icon_path=None):
        super().__init__()
        Button.n_buttons += 1
        self.active = active
        self.rect = rect
        self.text = text
        text_surf = Button.font.render(self.text, True, pygame.Color('black'))
        text_rect = text_surf.get_rect(center=self.rect.center)
        self.text_pos = (text_rect.topleft[0] - self.rect.topleft[0], text_rect.topleft[1] - self.rect.topleft[1])

        self.icon_path = icon_path
        self.has_icon = self.icon_path is not None
        self.icon_sprite = None

        self.org = pygame.Surface(self.rect.size)
        self.org.fill((111, 111, 111))
        self.org.blit(text_surf, self.text_pos)

        self.hov = pygame.Surface(self.rect.size)
        self.hov.fill((160, 160, 160))
        self.hov.blit(text_surf, self.text_pos)

        if self.has_icon and self.active:
            self.load_icon()

        self.image = self.org
        self.callback = callback

    def load_icon(self):
        if self.icon_sprite is not None:
            return
        self.icon_sprite = pygame.image.load(self.icon_path)
        self.org.blit(self.icon_sprite, (0, 0))
        self.hov.blit(self.icon_sprite, (0, 0))
        print(f'LOADED: {self.icon_path}')

    def toggle_active(self):
        self.active = not self.active
        if self.has_icon and self.icon_sprite is None and self.active:
            self.load_icon()

    def caller(self):
        self.callback()

    def update(self, events):
        if self.active:
            pos = pygame.mouse.get_pos()
            hit = self.rect.collidepoint(pos)
            self.image = self.hov if hit else self.org
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and hit:
                    self.caller()

    def draw(self, screen):
        if self.active:
            screen.blit(self.image, self.rect.topleft)


class ArticleButton(Button):
    article_thumbs_file_path = None

    def __init__(self, rect, callback, outfit, article, active=False, text='', icon_path=None):
        self.outfit = outfit
        self.article = article
        file_name = article.csv_data.split(',')[1]
        icon_path = os.path.join(str(ArticleButton.article_thumbs_file_path), file_name)
        if not os.path.isfile(icon_path):
            # TODO: generate icon and save it.
            self.generate_thumbnail(icon_path)
        super().__init__(rect, callback, active, text, icon_path)

    def caller(self):
        self.callback(self.outfit, self.article)

    def draw(self, screen):
        if self.active:
            screen.blit(self.image, self.rect.topleft)
            if self.article in self.outfit.articles:
                pygame.draw.rect(screen, (0, 255, 0), self.rect, width=3)

    def generate_thumbnail(self, save_path):
        size = self.rect.size
        image_array = pygame.surfarray.array2d(self.article.get_sprite())
        im = Image.fromarray(image_array, mode='RGBA')
        im = im.rotate(-90, expand=True)
        im = ImageOps.mirror(im)
        im2 = im.crop(im.getbbox())
        width, height = im2.size
        side_length = max(width, height)
        padding = int(side_length * 0.1)
        side_length += int(padding*2)
        result = Image.new(im2.mode, (side_length, side_length), (0, 0, 0, 0))
        result.paste(im2, ((side_length//2)-(width//2), (side_length//2)-(height//2)))
        result.thumbnail(size)
        result.save(save_path)
