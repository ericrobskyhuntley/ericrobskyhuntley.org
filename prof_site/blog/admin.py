from django.contrib.gis import admin
from markdownx.admin import MarkdownxModelAdmin

from .models import Author, Post, Institution, Affiliation, UrbanArea, CitationStyle

# Register your models here.
admin.site.register(Author)
admin.site.register(Affiliation)
admin.site.register(UrbanArea)
admin.site.register(Institution, admin.OSMGeoAdmin)
admin.site.register(Post, MarkdownxModelAdmin)
admin.site.register(CitationStyle)
