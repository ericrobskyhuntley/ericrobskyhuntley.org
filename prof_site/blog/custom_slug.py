from autoslug.settings import slugify as default_slugify

def custom_slugify(value, words):
    return "-".join(default_slugify(value).split('-', words)[:words])
