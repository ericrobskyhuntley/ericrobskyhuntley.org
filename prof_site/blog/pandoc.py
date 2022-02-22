import pypandoc
from django.conf import settings

yaml = """
---
link-citations: true
top-level-division: section
...
"""

def pandocify(content, csl, bib):
    if bib:
        filters = []
        extra_args = ['--mathjax',
                '--citeproc',
                '--bibliography='+bib,
                '--csl='+csl]
        content = content + "<br> <h3>References</h3>"
    else:
        filters = []
        extra_args = ['--mathjax']
    return pypandoc.convert_text(
        yaml + content,
        'html5',
        format='md',
        extra_args = extra_args,
        filters = filters
    )
