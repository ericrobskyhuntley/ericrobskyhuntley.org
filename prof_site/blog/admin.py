from django.contrib import admin
from django.contrib.gis import admin
from markdownx.admin import MarkdownxModelAdmin

from .models import Author, Post, Institution, Affiliation, UrbanArea, CitationStyle, Event, Role

class AffiliationInline(admin.TabularInline):
    model = Affiliation
    extra = 1

class AuthorAdmin(admin.ModelAdmin):
    inlines = (AffiliationInline,)

class RoleInline(admin.TabularInline):
    model = Role
    extra = 1

# class ParticipantInline(admin.TabularInline):
#     model = Author
#     extra = 1

class EventAdmin(admin.ModelAdmin):
    inlines = (RoleInline,)

# Register your models here.
admin.site.register(Author, AuthorAdmin)
admin.site.register(Affiliation)
admin.site.register(UrbanArea)
admin.site.register(Event, EventAdmin)
admin.site.register(Role)
admin.site.register(Institution, admin.OSMGeoAdmin)
admin.site.register(Post, MarkdownxModelAdmin)
admin.site.register(CitationStyle)
