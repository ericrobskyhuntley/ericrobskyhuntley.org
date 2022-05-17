import pypandoc
from django.conf import settings
from re import search

yaml = """
---
link-citations: true
top-level-division: section
...
"""

def pandocify(content, csl, bib):
    if bib and csl:
        filters = []
        extra_args = ['--mathjax',
                '--citeproc',
                '--bibliography='+bib,
                '--csl='+csl]
        cite_reg = "( |\[)-?@"
        if search(cite_reg, content):
            content = content + "\n\n### References"
    else:
        filters = []
        extra_args = ['--mathjax']
    return pypandoc.convert_text(
        yaml + content,
        'html5',
        format = 'md',
        extra_args = extra_args,
        filters = filters
    )
