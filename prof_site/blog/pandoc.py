import pypandoc
from django.conf import settings

yaml = """
---
link-citations: true
top-level-division: section
...
"""

def pandocify(content, csl, bib):
    if len(bib) > 0:
        filters = ['pandoc-citeproc']
        extra_args = ['--mathjax',
                 '--smart',
                 '--bibliography='+settings.BASE_DIR+bib,
                 '--csl='+settings.BASE_DIR+csl]
        content = content + "\n\r### References"
    else:
        filters = []
        extra_args = ['--mathjax',
                    '--smart']
    return pypandoc.convert_text(
        yaml + content,
        'html5',
        format='md',
        extra_args = extra_args,
        filters = filters
    )
