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
    name = models.CharField(
        help_text="Name of the institution.",
        max_length=150, 
        null=False, 
        blank=False
    )
    address = models.CharField(max_length=200, null=False, blank=True, default='')
    room = models.CharField(max_length=20, null=False, blank=True, default='')
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    website = models.URLField(null=False, blank=True, default='')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    location = models.PointField()

    class Meta:
        verbose_name = "Institution"
        verbose_name_plural = "Institutions"

    def __str__(self):
        return self.name

class Person(models.Model):
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
    website = models.URLField(null=False, blank=True, default='') 
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

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"

    def __str__(self):
        return self.full_name

    
class Education(models.Model):
    start = models.DateField(null=False, blank=False)
    end = models.DateField(null=True, blank=True)
    terminal = models.BooleanField(default=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    concentration = models.CharField(max_length=150, blank=True)
    desc = MarkdownxField(blank=True)
    committee = models.ManyToManyField(Person, through='Committee_Membership')
    show = models.BooleanField(default=True)
    DEGREES = [
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
        ('BFA', 'Bachelor of Fine Arts'),
        ('BA', 'Bachelor of Arts'),
        ('BS', 'Bachelor of Science'),
        ('GC', 'Graduate Certificate'),
        ('UC', 'Undergraduate Certificate'),
        ('', 'None'),
    ]
    degree = models.CharField(
        max_length = 5,
        choices = DEGREES,
        blank=True,
        default=''
    )

    class Meta:
        verbose_name = "Education"
        verbose_name_plural = "Periods of Education"

    def __str__(self):
        return self.degree + ' ' + self.concentration

class Committee_Membership(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    education = models.ForeignKey(Education, on_delete=models.CASCADE)
    chair = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Committee Membership"
        verbose_name_plural = "Committee Memberships"

    def __str__(self):
        return self.person.full_name + ', ' + self.education.degree

class Affiliation(models.Model):
    start = models.DateField(null=False, blank=False)
    end = models.DateField(null=True, blank=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True)
    primary = models.BooleanField(default=False)
    title = models.CharField(max_length=150, blank=True)
    website = models.URLField(null=False, blank=True)
    KINDS = [
        ('App', 'Appointment'),
        ('Aff', 'Affiliation'),
        ('', 'None'),
    ]
    kind = models.CharField(
        max_length = 5,
        choices = KINDS,
        blank = True,
        default = ''
    )
    desc = MarkdownxField(blank=True)
    show = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Affiliation"
        verbose_name_plural = "Affiliation"

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
    authors = models.ManyToManyField(Person)
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

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title

class CitationStyle(models.Model):
    name = models.CharField(max_length=50, unique=True)
    file = models.FileField(upload_to='citestyles/')

    class Meta:
        verbose_name = "Citation Style"
        verbose_name_plural = "Citation Styles"

    def __str__(self):
        return self.name

class Event(models.Model):
    banner = models.ImageField(null=True, blank=True, upload_to = 'events/banners/%Y/%m/%d')
    day = models.DateField()
    start = models.TimeField()
    end = models.TimeField()
    title = models.CharField(max_length=100)
    website = models.URLField(blank=True, default='')
    desc = MarkdownxField()
    participant = models.ManyToManyField(Person, through='Role')
    virtual_url = models.URLField(blank=True, default='')
    host = models.ManyToManyField(Institution, blank=True)
    cancel = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self):
        return self.title

class Role(models.Model):
    participant = models.ForeignKey(Person, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ROLES = [
        ('D', 'Discussant'),
        ('M', 'Moderator'),
        ('P', 'Panelist'),
        ('R', 'Presenter'),
        ('I', 'Introducer'),
        ('W', 'Workshop Leader')
    ]
    role = models.CharField(
        max_length=1,
        choices=ROLES,
        default='L',
    )

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
    
    def __str__(self):
        return self.role