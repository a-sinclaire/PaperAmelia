import pygame
import os


def scale_img(img, scale):
    return pygame.transform.scale(img, (img.get_width() / scale, img.get_height() / scale))


class Article:
    csv_titles = ''
    articles = []
    asset_path = ''

    def __init__(self, layer, file_path, csv_data, priority=0, scale=4.0):
        self.layer = layer
        self.file_path = file_path
        self.csv_data = csv_data
        self.priority = priority
        self.sprite = None
        self.scale = scale
        Article.articles.append(self)

    def load_sprite(self):
        self.sprite = pygame.image.load(self.file_path)
        self.sprite = scale_img(self.sprite, self.scale)
        print(f'LOADED: {self.file_path}')

    @staticmethod
    def search(csv_data):
        for article in Article.articles:
            if article.csv_data == csv_data:
                return article
        return None

    def draw(self, screen):
        if self.sprite is None:
            self.load_sprite()
        screen.blit(self.sprite, (0, 0))

    @staticmethod
    def load_articles(asset_path, csv_file_path):
        Article.asset_path = asset_path
        with open(csv_file_path, 'r') as f:
            lines = f.readlines()

        Article.csv_titles = lines[0]
        for line in lines[1:]:
            Article.load_article(line)

    @staticmethod
    def load_article(csv_line):
        if csv_line.strip() == '':  # ignore blank lines
            return

        properties = csv_line.split(',')
        layer = properties[0]
        article_file_path = os.path.join(Article.asset_path, properties[1])

        return Article(layer, article_file_path, csv_line)


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
        for line in lines[1:]:  # first line has header data for *some reason*
            article = Article.search(line)
            if article is None:
                article = Article.load_article(line)
            self.toggle_article(article)
