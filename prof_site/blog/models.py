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
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class VersionClass(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Institution(VersionClass):
    name = models.CharField(
        help_text="Name of the institution.",
        max_length=150, 
        null=False, 
        blank=False
        )
    address = models.CharField(
        max_length=200, 
        null=False, 
        blank=True, 
        default=''
        )
    room = models.CharField(
        max_length=20, 
        null=False, 
        blank=True, 
        default=''
        )
    city = models.CharField(
        max_length=100
        )
    state = models.CharField(
        max_length=100
        )
    postal = models.CharField(
        max_length=20
        )
    country = models.CharField(
        max_length=100
        )
    website = models.URLField(
        null=False, 
        blank=True, 
        default=''
        )
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
        )
    location = models.PointField()

    class Meta:
        verbose_name = "Institution"
        verbose_name_plural = "Institutions"

    def __str__(self):
        return self.name

class Award(VersionClass):
    """
    Describes awards and honors given to persons included
    in Persons.
    """
    start = models.DateField(
        help_text = "Start of the award term.",
        null = False, 
        blank = False
        )
    end = models.DateField(
        help_text = "End of the award term.",
        null = True, 
        blank = True
        )
    name = models.CharField(
        help_text = "Name of the award.",
        max_length = 200, 
        null = False, 
        blank = False
        )
    KINDS = [
        ('A', 'Awards and Honors'),
        ('F', 'Funding'),
        ('', 'None')
    ]
    kind = models.CharField(
        help_text = "Make the distinction between funding and awards/honors.",
        max_length = 3,
        choices = KINDS,
        null = False,
        blank = True,
        default = ''
    )
    amount = models.IntegerField(
        help_text = "The amount of money awarded, in its given currency (see next field).",
        null=True, 
        blank=True
    )
    CURRENCY = [
        ('CAD', 'Canadian Dollar'),
        ('USD', 'United States Dollar'),
    ]
    currency = models.CharField(
        help_text = "The currency in which the award/grant is given.",
        max_length = 3,
        choices = CURRENCY,
        null = False,
        blank = True,
        default = 'USD'
    )
    grantees = models.ManyToManyField(
        Institution,
        help_text = "All institutions who received the award/grant.", 
        blank=True
    )
    grantor = models.ForeignKey(
        Institution, 
        help_text = "All institutions who received the award/grant.",
        null = True, 
        on_delete = models.SET_NULL, 
        related_name='grantor'
    )
    show = models.BooleanField(
        help_text = "Indicates the visibility of this award on the frontend.",
        null=False, 
        default=True
    )

    class Meta:
        verbose_name = "Award"
        verbose_name_plural = "Awards"

    def __str__(self):
        return self.name

class Person(VersionClass):
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
        ('MCP', 'M. City Planning'),
        ('PhD', 'Ph.D.'),
        ('MUP', 'M. Urban Planning'),
        ('MURP', 'M. Urban and Regional Planning'),
        ('MFA', 'M. Fine Arts'),
        ('MLA', 'M. Landscape Architecture'),
        ('MArch', 'M. Architecture'),
        ('MBA', 'M. Business Administration'),
        ('MPA', 'M. Public Administration'),
        ('MDes', 'M. Design Studies'),
        ('DDes', 'D.Des.'),
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
    def current_affiliations(self):
        return self.affiliation_set.filter(end = None).order_by('-primary')

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
        t = ''
        if self.first:
            t = t + self.first + ' '
        if self.middle:
            t = t + self.middle + ' '
        if self.last:
            t = t + self.last
        return t

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"

    def __str__(self):
        return self.full_name

class SiteWideSetting(VersionClass):
    csl = models.ForeignKey(
        'CitationStyle',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    main_person = models.ForeignKey(Person, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = "SiteWideSetting"
        verbose_name_plural = "SiteWideSettings"

    def __str__(self):
        return self.csl.name + " " + self.main_person.full_name
    
class Education(VersionClass):
    start = models.DateField(null=False, blank=False)
    end = models.DateField(null=True, blank=True)
    terminal = models.BooleanField(default=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    concentration = models.CharField(max_length=150, blank=True)
    desc = MarkdownxField(blank=True)
    committee = models.ManyToManyField(Person, through='Committee_Membership')
    show = models.BooleanField(default=True)
    DEGREES = [
        ('MCP', 'M. City Planning'),
        ('PhD', 'Ph.D.'),
        ('MUP', 'M. Urban Planning'),
        ('MURP', 'M. Urban and Regional Planning'),
        ('MFA', 'M. Fine Arts'),
        ('MLA', 'M. Landscape Architecture'),
        ('MArch', 'M. Architecture'),
        ('MBA', 'M. Business Administration'),
        ('MPA', 'M. Public Administration'),
        ('MDes', 'M. Design Studies'),
        ('DDes', 'D.Des.'),
        ('BFA', 'B. Fine Arts'),
        ('BA', 'B. Arts'),
        ('BS', 'B. Science'),
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

class Committee_Membership(VersionClass):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    education = models.ForeignKey(Education, on_delete=models.CASCADE)
    chair = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Committee Membership"
        verbose_name_plural = "Committee Memberships"

    def __str__(self):
        return self.person.full_name + ', ' + self.education.degree

class Affiliation(VersionClass):
    start = models.DateField(
        help_text = "Start of the affiliation.",
        null=False, 
        blank=False
    )
    end = models.DateField(
        help_text = """End of the affiliation 
            (past affiliations will not be displayed on the front-end).""",
        null=True, 
        blank=True
    )
    person = models.ForeignKey(
        Person,
        help_text = "To which person does this affiliation apply?",
        on_delete=models.CASCADE
    )
    institution = models.ForeignKey(
        Institution, 
        help_text = "To which institution is the person affiliated?",
        on_delete=models.CASCADE, 
        null=True
    )
    primary = models.BooleanField(
        help_text = "Is this the person's primary affiliation?",
        default=False
    )
    title = models.CharField(
        help_text = "What is the person's title?",
        max_length=150, 
        blank=True
    )
    website = models.URLField(
        help_text = "What is the website _connected to this affiliation_?",
        null=False, 
        blank=True
    )
    KINDS = [
        ('App', 'Appointment'),
        ('Aff', 'Affiliation'),
        ('', 'None'),
    ]
    kind = models.CharField(
        help_text = """Is this affiliation a formal (generally, paid) 
            appointment or an affiliation?""",
        max_length = 5,
        choices = KINDS,
        blank = True,
        default = ''
    )
    desc = MarkdownxField(
        help_text = "Describe the affiliation.",
        blank=True
    )
    show = models.BooleanField(
        help_text = "Should this affiliation appear on the front-end?",
        default=False
    )

    class Meta:
        verbose_name = "Affiliation"
        verbose_name_plural = "Affiliation"

    def __str__(self):
        return self.title

class UrbanArea(VersionClass):
    geom = models.MultiPolygonField()

    def __str__(self):
        return str(self.geom)

class Land(VersionClass):
    geom = models.MultiPolygonField()
    name = models.CharField(max_length=28)

    def __str__(self):
        return str(self.geom)


class BathContours(VersionClass):
    geom = models.MultiLineStringField()
    depth = models.IntegerField()

    def __str__(self):
        return str(self.geom) 

class ElevContours(VersionClass):
    geom = models.MultiLineStringField()
    elev = models.IntegerField()

    def __str__(self):
        return str(self.geom)

class Post(VersionClass):
    title = models.CharField(
        help_text = "Post title (up to 150 chars).",
        max_length=150
    )
    content = MarkdownxField(
        help_text = """Post content (can include Pandoc citations 
            if they appear in the bibliography).""",
    )
    display_datetime = models.DateTimeField()
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
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    bib = models.FileField(upload_to='bibs/', blank=True)
    attach = models.FileField(upload_to='attachments/', blank=True, default='')
    attach_kind = models.CharField(max_length=150)
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
        return self.display_datetime.date()

    @property
    def time(self):
        return self.display_datetime.time()

    @cached_property
    def pandoc_process(self):
        csl = SiteWideSetting.objects.all().order_by('-id')[0].csl.file.url
        try:
            biblio=self.bib.url
        except:
            biblio=None
        return pandocify(
            content=self.content,
            csl=csl,
            bib=biblio
        )

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title

class CitationStyle(VersionClass):
    name = models.CharField(max_length=50, unique=True)
    file = models.FileField(upload_to='citestyles/')

    class Meta:
        verbose_name = "Citation Style"
        verbose_name_plural = "Citation Styles"

    def __str__(self):
        return self.name

class Event(VersionClass):
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

class Role(VersionClass):
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