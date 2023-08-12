#
# Author: Amelia Sinclaire
# Copyright 2023
#

import pygame
import os


def scale_img(img, scale):
    return pygame.transform.scale(img, (img.get_width() / scale, img.get_height() / scale))


class Article:
    csv_titles = ''
    articles = []
    asset_path = ''
    scale = 4.0
    highest_priority = -1

    def __init__(self, layer, file_path, csv_data, priority=0):
        self.layer = layer
        self.file_path = file_path
        self.csv_data = csv_data
        self.priority = priority
        self.sprite = None
        Article.articles.append(self)

    def load_sprite(self):
        self.sprite = pygame.image.load(self.file_path)
        self.sprite = scale_img(self.sprite, Article.scale)
        print(f'LOADED: {self.file_path}')

    def draw(self, screen):
        if self.sprite is None:
            self.load_sprite()
        screen.blit(self.sprite, (0, 0))

    @staticmethod
    def search(csv_data):
        for article in Article.articles:
            if article.csv_data == csv_data:
                return article
        return None

    @staticmethod
    def load_articles(asset_path, csv_file_path):
        Article.asset_path = asset_path
        with open(csv_file_path, 'r') as f:
            lines = f.readlines()

        Article.csv_titles = lines[0]
        for csv_line in lines[1:]:  # skip csv header
            Article.load_article(csv_line)

    @staticmethod
    def load_article(csv_line):
        if csv_line.strip() == '':  # ignore blank lines
            return None

        properties = csv_line.split(',')
        layer = int(properties[0])
        article_file_path = os.path.join(Article.asset_path, properties[1])

        Article.highest_priority += 1
        return Article(layer, article_file_path, csv_line, priority=Article.highest_priority)


class Outfit:
    def __init__(self, articles=[]):
        self.articles = articles
        self.sorted = False

    def toggle_article(self, article):
        if article is None:
            return

        self.sorted = False
        if article in self.articles:
            self.articles.remove(article)
            return
        self.articles.append(article)

    def sort(self):
        self.articles.sort(key=lambda a: (a.layer, a.priority))
        self.sorted = True

    def draw(self, screen):
        if not self.sorted:
            self.sort()

        for a in self.articles:
            a.draw(screen)

    def save(self, file_path):
        lines = [Article.csv_titles]
        for a in self.articles:
            lines.append(a.csv_data)
        with open(file_path, 'w+') as f:
            f.writelines(lines)

    def load(self, file_path):
        self.articles = []
        with open(file_path, 'r') as f:
            lines = f.readlines()
        for csv_line in lines[1:]:  # first line has header data for *some reason*
            if csv_line.strip() == '':  # ignore blank lines
                continue
            article = Article.search(csv_line)  # check if article is already in Article list
            if article is None:
                article = Article.load_article(csv_line)
            self.toggle_article(article)
