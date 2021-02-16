from markdownx.models import MarkdownxField
from django.contrib.gis.db import models
from markdownx.utils import markdownify
from .pandoc import pandocify
from autoslug.settings import slugify as default_slugify
from autoslug import AutoSlugField
from django.utils.functional import cached_property
from django.core.serializers import serialize
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToCover, Adjust, ColorOverlay, SmartResize

class Institution(models.Model):
    dpt = models.CharField(max_length=150, null=False, blank=True)
    inst = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    location = models.PointField()

    def __str__(self):
        return self.dpt

class Author(models.Model):
    first = models.CharField(max_length=50)
    middle = models.CharField(max_length=50, blank=True, default='')
    last = models.CharField(max_length=50)
    email = models.EmailField(blank=True, default='')
    GENDERS = [
        ('M', 'He/him/his'),
        ('W', 'She/her/hers'),
        ('N', 'He/him/his or They/them/theirs'),
        ('H', 'She/her/hers or They/them/theirs'),
        ('T', 'They/them/theirs'),
    ]
    pronouns = models.CharField(
        max_length=1,
        choices=GENDERS,
        default='T',
    )
    CREDS = [
        ('MCP', 'Master of City Planning'),
        ('PhD', 'Doctor of Philosophy'),
        ('MUP', 'Master of Urban Planning'),
        ('MURP', 'Master of Urban and Regional Planning'),
        ('MFA', 'Master of Fine Arts'),
        ('MLA', 'Master of Landscape Architecture'),
        ('MArch', 'Master of Architecture'),
        ('MBA', 'Master of Business Administration'),
        ('MPA', 'Master of Public Administration'),
        ('MDes', 'Master of Design Studies'),
        ('DDes', 'Doctor of Design'),
        ('', 'None'),
    ]
    cred = models.CharField(
        max_length = 5,
        choices = CREDS,
        blank=True,
        default=''
    )
    desc = MarkdownxField(blank=True)
    photo = models.ImageField(null=True, blank=True, upload_to = 'authors/images/%Y/%m/%d')
    orcid = models.CharField(max_length=19, blank=True)
    pgp = models.CharField(max_length=50, blank=True)
    twitter = models.CharField(max_length=50, blank=True)
    gitlab = models.CharField(max_length=25, blank=True, default='')
    github = models.CharField(max_length=25, blank=True, default='')
    zotero = models.CharField(max_length=25, blank=True, default='')
    linkedin = models.CharField(max_length=25, blank=True, default='')
    photo_gray = ImageSpecField(source='photo',
        processors=[
            Adjust(color=0,contrast=1.5, brightness=1.5),
            ColorOverlay(color = "#CC003E", overlay_opacity = 0.6 )
        ],
        format='PNG'
    )
    photo_thumb = ImageSpecField(source='photo',
        processors=[ResizeToFill(100, 100)],
        format='PNG')
    slug = AutoSlugField(populate_from='full_name',
        default=None, 
        always_update=False, 
        max_length=150
    )
    affil = models.ManyToManyField(Institution, through='Affiliation')
    vita = models.FileField(upload_to='authors/vitae/', blank=True, default='')
    page = models.BooleanField(default=False)
    @property
    def formatted_markdown(self):
        return markdownify(self.desc)

    @property
    def sorted_affiliation(self):
        return self.affiliation_set.order_by('-primary')

    @property
    def primary_affiliation(self):
        return self.affiliation_set.filter(primary = True)

    @property
    def loc_geojson(self):
        """
        Returns instution locations serialized as geojson.
        """
        affils = list(self.affiliation_set.all().values_list('institution', flat=True))
        return serialize('geojson', Institution.objects.filter(pk__in=affils), geometry_field='location')

    @property
    def full_name(self):
        """
        Returns full name.
        """
        return '%s %s %s' % (self.first, self.middle, self.last)

    def __str__(self):
        return self.full_name

class Affiliation(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    primary = models.BooleanField(default=False)
    title = models.CharField(max_length=150)
    website = models.URLField(null=False, blank=True)

    def __str__(self):
        return self.title

class UrbanArea(models.Model):
    geom = models.MultiPolygonField()

    def __str__(self):
        return str(self.geom)

class Land(models.Model):
    geom = models.MultiPolygonField()
    name = models.CharField(max_length=28)

    def __str__(self):
        return str(self.geom)


class BathContours(models.Model):
    geom = models.MultiLineStringField()
    depth = models.IntegerField()

    def __str__(self):
        return str(self.geom) 

class ElevContours(models.Model):
    geom = models.MultiLineStringField()
    elev = models.IntegerField()

    def __str__(self):
        return str(self.geom)

class Post(models.Model):
    title = models.CharField(max_length=150)
    content = MarkdownxField()
    timestamp = models.DateTimeField()
    content_type = models.CharField(max_length=150)
    authors = models.ManyToManyField(Author)
    banner = models.ImageField(null=True, upload_to = 'posts/banners/%Y/%m/%d')
    banner_thumb = ImageSpecField(
        source='banner',
        processors=[ResizeToFill(200, 60)],
        format='PNG',
        options={'quality': 60}
    )
    banner_reduced = ImageSpecField(
        source='banner',
        processors=[ResizeToCover(1920, 1080)],
        format='JPEG',
        options={'quality': 60}
    )
    csl = models.ForeignKey(
        'CitationStyle',
        null=True,
        on_delete='CASCADE'
    )
    bib = models.FileField(upload_to='bibs/', blank=True)
    attach = models.FileField(upload_to='attachments/', blank=True, default='')
    slug = AutoSlugField(populate_from='title', 
        default=None,
        always_update=False, 
        null=True, 
        max_length=150
    )

    def slugify_function(self, content, words):
        return "-".join(default_slugify(content).split('-', words)[:words])

    @property
    def date(self):
        return self.timestamp.date()

    @property
    def time(self):
        return self.timestamp.time()

    @cached_property
    def pandoc_process(self):
        try:
            biblio=self.bib.url
            cite=self.csl.file.url
        except:
            biblio=None
            cite=None
        return pandocify(
            content=self.content,
            csl=cite,
            bib=biblio
        )

    def __str__(self):
        return self.title

class CitationStyle(models.Model):
    name = models.CharField(max_length=50, unique=True)
    file = models.FileField(upload_to='citestyles/')

    def __str__(self):
        return self.name

class Event(models.Model):
    banner = models.ImageField(null=True, blank=True, upload_to = 'events/banners/%Y/%m/%d')
    day = models.DateField()
    start = models.TimeField()
    end = models.TimeField()
    title = models.CharField(max_length=100)
    desc = MarkdownxField()
    participant = models.ManyToManyField(Author, through='Role')
    virtual_url = models.URLField(blank=True, default='')
    cost = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=False,
    )
    ticket_url = models.URLField(blank=True, default='')
    venue = models.ForeignKey(Institution, blank=True, null=True, on_delete=models.SET_NULL)
    cancel = models.BooleanField(default=False)

    class Meta:
        verbose_name = "event"
        verbose_name_plural = "events"

    def __str__(self):
        return self.title

class Role(models.Model):
    participant = models.ForeignKey(Author, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ROLES = [
        ('D', 'Discussant'),
        ('M', 'Moderator'),
        ('P', 'Panelist'),
        ('L', 'Lecturer'),
        ('I', 'Introducer'),
        ('W', 'Workshop Leader')
    ]
    role = models.CharField(
        max_length=1,
        choices=ROLES,
        default='L',
    )

    class Meta:
        verbose_name = "role"
        verbose_name_plural = "roles"
    
    def __str__(self):
        return self.role