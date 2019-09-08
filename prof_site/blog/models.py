from markdownx.models import MarkdownxField
from django.contrib.gis.db import models
from markdownx.utils import markdownify
from .pandoc import pandocify
from .custom_slug import custom_slugify
# from django.utils.text import slugify
from autoslug import AutoSlugField
from django.utils.functional import cached_property
from django.core.serializers import serialize
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToCover, Adjust, ColorOverlay, SmartResize

class Author(models.Model):
    first = models.CharField(max_length=50)
    middle = models.CharField(max_length=50, blank=True)
    last = models.CharField(max_length=50)
    email = models.EmailField()
    desc = MarkdownxField(max_length=1000, blank=True)
    photo = models.ImageField(null=True, upload_to = 'authors/images/%Y/%m/%d')
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

class Institution(models.Model):
    dpt = models.CharField(max_length=150, null=True)
    inst = models.CharField(max_length=150)
    affiliates = models.ManyToManyField(Author, through='Affiliation')
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    location = models.PointField()

    def __str__(self):
        return self.dpt

class Affiliation(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    primary = models.BooleanField(default=False)
    title = models.CharField(max_length=150)

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

class Post(models.Model):
    title = models.CharField(max_length=150)
    content = MarkdownxField()
    timestamp = models.DateTimeField()
    type = models.CharField(max_length=150)
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
    bib = models.FileField(upload_to='bibs/', null=True)

    slug = AutoSlugField(populate_from='title', 
        default=None,
        always_update=False, 
        null=True, 
        max_length=150,
        slugify=lambda value: custom_slugify(value, words=4)
    )

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
