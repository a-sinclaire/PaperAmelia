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
    high_color = (249, 249, 249),
    mid_color = (192, 192, 192)
    low_color = (84, 84, 84)
    hov_color = (200, 200, 200)

    def __init__(self, rect, callback, active=False, text='', icon_path=None):
        super().__init__()
        Button.n_buttons += 1
        self.active = active
        self.rect = rect

        self.icon_path = icon_path
        self.has_icon = self.icon_path is not None
        self.icon_sprite = None

        self.org = Button.create_basic_button(self.rect, text=text)
        self.hov = Button.create_basic_button(self.rect, mid_color=Button.hov_color, text=text)

        if self.has_icon and self.active:
            self.load_icon()
        if self.has_icon and self.icon_sprite is not None:
            self.blit_sprite(self.org)
            self.blit_sprite(self.hov)

        self.image = self.org
        self.callback = callback

    def load_icon(self):
        if self.has_icon and self.icon_sprite is None:
            self.icon_sprite = pygame.image.load(self.icon_path)
            print(f'LOADED: {self.icon_path}')

    def blit_sprite(self, surface):
        sprite_rect = self.icon_sprite.get_rect(center=self.rect.center)
        surface.blit(self.icon_sprite, (sprite_rect[0] - self.rect[0], sprite_rect[1] - self.rect[1]))
        surface.blit(self.icon_sprite, (sprite_rect[0] - self.rect[0], sprite_rect[1] - self.rect[1]))

    def toggle_active(self):
        self.active = not self.active
        if self.has_icon and self.icon_sprite is None and self.active:
            self.load_icon()

    def caller(self):
        self.callback()

    def update_image(self, pos=None, hit=None):
        if pos is None:
            pos = pygame.mouse.get_pos()
        if hit is None:
            hit = self.rect.collidepoint(pos)
        self.image = self.hov if hit else self.org

    def update(self, events):
        if self.active:
            pos = pygame.mouse.get_pos()
            hit = self.rect.collidepoint(pos)
            self.update_image()
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and hit:
                    self.caller()
        if self.has_icon and self.icon_sprite is None:
            self.load_icon()
            self.blit_sprite(self.org)
            self.blit_sprite(self.hov)

    def draw(self, screen):
        if self.active:
            screen.blit(self.image, self.rect.topleft)

    @staticmethod
    def create_basic_button(rect, high_color=None, mid_color=None, low_color=None, text=''):
        if high_color is None:
            high_color = Button.high_color
        if mid_color is None:
            mid_color = Button.mid_color
        if low_color is None:
            low_color = Button.low_color
        b = pygame.Surface(rect.size)
        square_dim = min(rect.w, rect.h)//2
        top_left = (0, 0)
        top_right = (rect.topright[0] - rect.topleft[0], 0)
        bottom_left = (0, rect.bottomleft[1] - rect.topleft[1])
        middle_top_right = (top_right[0]-square_dim, square_dim)
        middle_bottom_left = (square_dim, bottom_left[1] - square_dim)
        bottom_right = (top_right[0], bottom_left[1])
        padding = 3
        mid_rect = pygame.Rect(padding, padding, rect.w-padding*2, rect.h-padding*2)
        pygame.draw.polygon(b, high_color, [top_left, top_right, middle_top_right, middle_bottom_left, bottom_left])
        pygame.draw.polygon(b, low_color, [top_right, bottom_right, bottom_left, middle_bottom_left, middle_top_right])
        pygame.draw.rect(b, mid_color, mid_rect, border_radius=padding)
        text_surf = Button.font.render(text, True, pygame.Color('black'))
        text_rect = text_surf.get_rect(center=rect.center)
        text_pos = (text_rect.topleft[0] - rect.topleft[0], text_rect.topleft[1] - rect.topleft[1])
        b.blit(text_surf, text_pos)
        return b


class ToggleButton(Button):
    def __init__(self, rect, callback, active=False, text='', icon_path=None):
        super().__init__(rect, callback, active, text, icon_path)

        self.is_toggled = False
        self.is_toggleable = True

        self.tog = Button.create_basic_button(self.rect, high_color=Button.low_color, low_color=Button.high_color, text=text)
        self.tog_hov = Button.create_basic_button(self.rect, high_color=Button.low_color, mid_color=Button.hov_color, low_color=Button.high_color, text=text)

        self.gray_out = pygame.Surface(self.rect.size)
        self.gray_out.set_alpha(128)
        self.gray_out.fill((0, 0, 0))

        if self.has_icon and self.active:
            self.load_icon()
        if self.has_icon and self.icon_sprite is not None:
            self.blit_sprite(self.tog)
            self.blit_sprite(self.tog_hov)

    def update(self, events):
        if self.active:
            pos = pygame.mouse.get_pos()
            hit = self.rect.collidepoint(pos)
            self.update_image()
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and hit:
                    self.is_toggled = not self.is_toggled
                    self.caller()
        if self.has_icon and self.icon_sprite is None:
            self.load_icon()
            self.blit_sprite(self.org)
            self.blit_sprite(self.hov)
            self.blit_sprite(self.tog)
            self.blit_sprite(self.tog_hov)

    def update_image(self, pos=None, hit=None):
        if pos is None:
            pos = pygame.mouse.get_pos()
        if hit is None:
            hit = self.rect.collidepoint(pos)
        if self.is_toggled:
            self.image = self.tog_hov if hit else self.tog
        else:
            self.image = self.hov if hit else self.org
        if not self.is_toggleable:
            self.image = self.tog if self.is_toggled else self.org

    def draw(self, screen):
        if self.active:
            screen.blit(self.image, self.rect)
            if not self.is_toggleable:
                screen.blit(self.gray_out, self.rect)


class ArticleButton(ToggleButton):
    article_thumbs_file_path = None

    def __init__(self, rect, callback, outfit, article, active=False, text=''):
        file_name = article.csv_data.split(',')[1]
        icon_path = os.path.join(str(ArticleButton.article_thumbs_file_path), file_name)
        self.rect = rect
        self.outfit = outfit
        self.article = article
        if not os.path.isfile(icon_path):
            self.generate_thumbnail(icon_path)

        super().__init__(rect, callback, active, text, icon_path)
        self.is_toggled = self.article in self.outfit.articles
        self.is_toggleable = not self.article.is_locked(self.outfit)

    def caller(self):
        self.callback(article=self.article)

    def update(self, events, paper_amelia):
        super().update(events)
        self.is_toggled = self.article in self.outfit.articles
        self.is_toggleable = not self.article.is_locked(self.outfit)
        self.active = self.article.layer == paper_amelia.current_layer_id

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
        side_length += int(padding * 2)
        result = Image.new(im2.mode, (side_length, side_length), (0, 0, 0, 0))
        result.paste(im2, ((side_length // 2) - (width // 2), (side_length // 2) - (height // 2)))
        result.thumbnail(size)
        result.save(save_path)
