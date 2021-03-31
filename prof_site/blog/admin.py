from django.contrib import admin
from django.contrib.gis import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Award, Conference, ConferenceInstance, Library, Person, Post, Institution, Education, Committee_Membership, Affiliation, CitationStyle, Event, Role,SiteWideSetting

class AffiliationInline(admin.TabularInline):
    model = Affiliation
    extra = 1

class EducationInline(admin.TabularInline):
    model = Education
    extra = 1

class PersonAdmin(admin.ModelAdmin):
    inlines = (EducationInline, AffiliationInline,)

class CommitteeInline(admin.TabularInline):
    model = Committee_Membership
    extra = 1

class EducationAdmin(admin.ModelAdmin):
    inlines = (CommitteeInline,)

class RoleInline(admin.TabularInline):
    model = Role
    extra = 1

class EventAdmin(admin.ModelAdmin):
    inlines = (RoleInline,)

class PostAdmin(admin.ModelAdmin):
    autocomplete_lookup_fields = {
        'generic': [['content_type', 'object_id']],
    }

# Register your models here.
admin.site.register(Library)
admin.site.register(Award)
admin.site.register(Conference)
admin.site.register(ConferenceInstance)
admin.site.register(Person, PersonAdmin)
admin.site.register(Education, EducationAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(SiteWideSetting)
admin.site.register(Institution, admin.OSMGeoAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(CitationStyle)
