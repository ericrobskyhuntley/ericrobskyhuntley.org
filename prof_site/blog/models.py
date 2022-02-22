from markdownx.models import MarkdownxField
from django.contrib.gis.db import models
from django.db.models import F
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
from .zotero_update import zotero_pull, zotero_version
from django.conf import settings
from .geocode import geocode_address
import os

class VersionClass(models.Model):
    """
    Defines a default class with created at/modified at fields.
    All the below models inherit this class.
    """
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
        help_text = "Address of the institution.",
        max_length=200, 
        null=False, 
        blank=True, 
        default=''
    )
    room = models.CharField(
        help_text = "Room at which the institution can be reached.",
        max_length=20, 
        null=False, 
        blank=True, 
        default=''
    )
    city = models.CharField(
        help_text = "City in which institution is located.",
        max_length=100
    )
    state = models.CharField(
        help_text = "State in which institution is located.",
        max_length=100
    )
    postal = models.CharField(
        help_text = "Postcode in which institution is located.",
        max_length=20,
        blank=True,
        default=''
    )
    country = models.CharField(
        help_text = "Country in which institution is located.",
        max_length=100
    )
    website = models.URLField(
        help_text = "Institution's website.",
        null=False, 
        blank=True, 
        default=''
    )
    parent = models.ForeignKey(
        'self', 
        help_text = "Parent institution of institution (E.g., 'MIT' is the parent of 'DUSP').",
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )
    location = models.PointField(
        help_text = "Approximate location of institution.",
        null=True,
        blank=True
    )
    def save(self, *args, **kwargs):
        """
        Overwrite save method to update main bibliography when model is saved.
        """
        if self.location:
            pass
        else:
            add_array = [self.address, self.city, self.state, self.postal, self.country]
            query = ','.join(filter(None, add_array))
            self.location = geocode_address(query)
        super(Institution, self).save(*args, **kwargs)
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
    pi_awardee = models.ForeignKey(
        'Person', 
        help_text = "P.I. or awardee.",
        null = True, 
        on_delete = models.SET_NULL
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
    """
    Model describing a person, their (ugh) credentials, social, etc.
    """
    first = models.CharField(
        help_text = "Person's given name.",
        max_length=50
    )
    middle = models.CharField(
        help_text = "Person's middle name(s).",
        max_length=50, 
        blank=True, 
        default=''
    )
    last = models.CharField(
        help_text = "Person's last name(s).",
        max_length=50
    )
    email = models.EmailField(
        help_text = """Personal email. Useful in the absence
        of an affiliated email.""",
        blank=True, 
        default=''
    )
    GENDERS = [
        ('M', 'He/him/his'),
        ('W', 'She/her/hers'),
        ('N', 'He/him/his or They/them/theirs'),
        ('H', 'She/her/hers or They/them/theirs'),
        ('T', 'They/them/theirs'),
    ]
    pronouns = models.CharField(
        help_text = "Preferred pronouns.",
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
        help_text = "Display credential.",
        max_length = 5,
        choices = CREDS,
        blank=True,
        default=''
    )
    bio = MarkdownxField(
        help_text = "Person's short biography.",
        blank=True
    )
    website = models.URLField(
        help_text = "Person's personal website (independent their affiliations).",
        null=False, 
        blank=True, 
        default=''
    ) 
    photo = models.ImageField(
        help_text = "Photo/headshot.",
        null=True, 
        blank=True, 
        upload_to = 'authors/images/%Y/%m/%d'
    )
    orcid = models.CharField(
        help_text = "Person's ORCID.",
        max_length=19, 
        blank=True
    )
    pgp = models.CharField(
        help_text = "Person's PGP key.",
        max_length=50, 
        blank=True
    )
    twitter = models.CharField(
        help_text = "Person's Twitter handle.",
        max_length=50, 
        blank=True
    )
    gitlab = models.CharField(
        help_text = "Person's Gitlab handle.",
        max_length=25, 
        blank=True, 
        default=''
    )
    github = models.CharField(
        help_text = "Person's Github handle.",
        max_length=25, 
        blank=True, 
        default=''
    )
    zotero = models.CharField(
        help_text = "Person's Zotero handle.",
        max_length=25, 
        blank=True, default=''
    )
    linkedin = models.CharField(
        help_text = "Person's LinkedIn handle.",
        max_length=25, 
        blank=True, 
        default=''
    )
    photo_gray = ImageSpecField(source='photo',
        processors=[
            Adjust(color=0,contrast=1.5, brightness=1.5),
            ColorOverlay(color = "#CC003E", overlay_opacity = 0.6 )
        ],
        format='PNG'
    )
    photo_thumb = ImageSpecField(
        source='photo',
        processors=[ResizeToFill(100, 100)],
        format='PNG'
    )
    slug = AutoSlugField(
        populate_from='full_name',
        default=None, 
        always_update=False, 
        max_length=150
    )
    affil = models.ManyToManyField(
        Institution, 
        help_text = "List of person's current and historical affiliations.",
        through='Affiliation'
    )
    vita = models.FileField(
        help_text = "Current curriculum vita.",
        upload_to='authors/vitae/', 
        blank=True, 
        default=''
    )
    page = models.BooleanField(
        help_text = "Does this person have their own detail page?",
        default=False
    )
    @property
    def formatted_markdown(self):
        """
        Formats bio markdown.
        """
        return markdownify(self.bio)

    @property
    def current_affiliations(self):
        """
        Lists current affiliations (i.e., those without a specified end date)
        with primary affiliations first.
        """
        return self.affiliation_set.filter(end = None, show=True, kind='Aff').order_by(F('primary').desc(nulls_last=True),F('start').desc())

    @property
    def current_appointments(self): 
        """
        Lists current appointments (i.e., those without a specified end date)
        with primary affiliations first.
        """
        return self.affiliation_set.filter(end = None, show=True, kind='App').order_by(F('primary').desc(nulls_last=True),F('start').desc())

    @property
    def primary_affiliation(self):
        """
        Returns primary affiliation.
        """
        return self.affiliation_set.filter(primary = True, show=True)

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
    
class Library(VersionClass):
    """
    This model describes a Zotero library.
    """
    name = models.CharField(
        help_text = "Name of this library.",
        max_length = 100,
        null=False,
        blank=False
    )
    zotero_id = models.IntegerField(
        help_text = "What is the Zotero ID of the site bibliography?",
        null = True, 
        blank = True
    )
    KINDS = [
        ('user', 'User'),
        ('group', 'Group'),
        ('', 'None')
    ]
    kind = models.CharField(
        help_text = "Of what kind is this library?",
        max_length = 5,
        choices = KINDS,
        blank=True,
        default=''
    )
    collection = models.CharField(
        help_text = "Specific subcollection id. (N.b., these don't version well.)",
        null = True, 
        blank = True,
        max_length=50
    )
    version = models.IntegerField(
        help_text = "Auto-updated bibliography version.",
        null = True, 
        blank = True
    )
    bib_file = models.FileField(
        help_text = "Auto-updated bibliography file.",
        default='',
        blank=True
    )
    def save(self, *args, **kwargs):
        """
        Overwrite save method to update main bibliography when model is saved.
        """
        library_id = self.zotero_id
        library_kind = self.kind
        library_collection = self.collection
        if self.version:
            db_version = self.version
            current_version = zotero_version(library_id, library_kind, library_collection)
            bib_file = self.bib_file
            if db_version == current_version and os.path.exists(os.path.join(settings.MEDIA_ROOT, str(bib_file))):
                pass
            else: 
                self.version = current_version
                zotero_pull(library_id, library_kind, library_collection)
        else:
            self.version, self.bib_file = zotero_pull(library_id, library_kind, library_collection)
        super(Library, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Zotero Library"
        verbose_name_plural = "Zotero Libraries"

    def __str__(self):
        return self.name

class SiteWideSetting(VersionClass):
    """
    This model describes site-wide settings.
    """
    csl = models.ForeignKey(
        'CitationStyle',
        help_text = "Choose a Citation Style Language (CSL)",
        null = True,
        blank = True,
        on_delete = models.CASCADE
    )
    main_person = models.ForeignKey(
        Person, 
        help_text = "Which person is the focus of this site?",
        null = True, 
        blank = True, 
        on_delete = models.SET_NULL
    )
    library = models.ForeignKey(
        Library,
        help_text = "What Zotero library should this use?",
        null = True, 
        blank = True, 
        on_delete = models.SET_NULL
    )

    class Meta:
        verbose_name = "SiteWideSetting"
        verbose_name_plural = "SiteWideSettings"

    def __str__(self):
        return self.csl.name + " " + self.main_person.full_name
    
class Education(VersionClass):
    """
    Model describes periods of education, with resulting degrees, institutions,
    committees, etc.
    """
    start = models.DateField(
        help_text = "Start of a period of education/degree program.",
        null=False, 
        blank=False
    )
    end = models.DateField(
        help_text = "End of a period of education/degree program.",
        null=True, 
        blank=True
    )
    terminal = models.BooleanField(
        help_text = "Is this the last degree obtained by a person?",
        default=False
    )
    person = models.ForeignKey(
        'Person', 
        help_text = "List of person's current and historical education.",
        on_delete=models.CASCADE,
        related_name="help",
        null=True
    )
    institution = models.ForeignKey(
        Institution, 
        help_text = "Credential-granting institution.",
        on_delete=models.CASCADE
    )
    concentration = models.CharField(
        help_text = "Major, concentration, etc.",
        max_length=150, 
        blank=True
    )
    thesis_title = models.CharField(
        help_text = "Major, concentration, etc.",
        max_length=300, 
        blank=True
    )
    thesis_link = models.URLField(
        help_text = "What is the website _connected to this affiliation_?",
        blank=True,
        default='',
    )
    THESIS_KINDS = [
        ('diss', 'Dissertation'),
        ('mths', "Master's Thesis"),
        ('ugth', "Undergraduate Thesis"),
        ('', 'None')
    ]
    thesis_type = models.CharField(
        help_text = "Major, concentration, etc.",
        choices = THESIS_KINDS,
        max_length=4, 
        blank=True
    )
    desc = MarkdownxField(
        help_text = "Description of the degree or period of education.",
        blank=True
    )
    committee = models.ManyToManyField(
        Person, 
        help_text = "Lists committee members for degree-granting process.",
        through='Committee_Membership'
    )
    show = models.BooleanField(
        help_text = "Show this period of education on the front-end?",
        default=True
    )
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
        help_text = "What type of degree was awarded/is the anticipated result?",
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
    """
    Model relates Person to Education, describing members
    of a degree-granting/guiding committee.
    """
    person = models.ForeignKey(
        Person,
        help_text = "Person related to the degree committee.",
        on_delete=models.CASCADE
    )
    education = models.ForeignKey(
        Education, 
        help_text = "Period of education guided by the degree committee.",
        on_delete=models.CASCADE
    )
    chair = models.BooleanField(
        help_text = "Designates chair/non-chair of the degree committee.",
        default=False
    )

    class Meta:
        verbose_name = "Committee Membership"
        verbose_name_plural = "Committee Memberships"

    def __str__(self):
        return self.person.full_name + ', ' + self.education.degree

class Affiliation(VersionClass):
    """
    These are relationships between individuals and institutions.
    They can (at the moment) take two forms: appointments, which,
    in general, are salaried, and affiliations which, in general, are
    honorary or voluntary.
    """
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
    email = models.EmailField(
        help_text = "Email associated with a given affiliation.",
        blank=True, 
        default=''
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

    def save(self, *args, **kwargs):
        """
        Ensures there can be only one primary affiliation.
        Sets primary to last set primary affil, removing
        setting primary on other affils equal to false.
        """
        if self.primary:
            try:
                temp = Affiliation.objects.get(primary=True)
                if self != temp:
                    temp.primary = False
                    temp.save()
            except Affiliation.DoesNotExist:
                pass
        super(Affiliation, self).save(*args, **kwargs)

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
    """
    This model describes posts announcing or documenting 
    new events, awards, articles, etc.
    """
    title = models.CharField(
        help_text = "Post title (up to 150 chars).",
        max_length=150
    )
    content = MarkdownxField(
        help_text = """Post content (can include Pandoc citations 
            if they appear in the bibliography).""",
    )
    display_datetime = models.DateTimeField(
        help_text = "Datetime that should be displayed for the post.",
    )
    authors = models.ManyToManyField(
        Person,
        help_text = "Authors of this post.",
    )
    banner = models.ImageField(
        help_text = "Image to be displayed across the detail. Best if wide.",
        null=True, 
        upload_to = 'posts/banners/%Y/%m/%d'
    )
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
    content_type = models.ForeignKey(
        ContentType, 
        help_text = """This is one of the fields necessary for GenericForeignKey
             (content_object) to other arbitrary objects.""",
        null=True, 
        blank=True, 
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField(
        help_text = "Unique identifier for arbitrary table.",
        null=True, 
        blank=True
    )
    content_object = GenericForeignKey(
        'content_type', 
        'object_id', 
    )
    bib = models.FileField(
        help_text = "Bibliography file. Formatted in BetterBibLaTex.",
        upload_to='bibs/', 
        blank=True
    )
    attach = models.FileField(
        help_text = "Attachment to this blog post.",
        upload_to='attachments/', 
        blank=True, 
        default=''
    )
    attach_kind = models.CharField(
        help_text = "What kind of thing is the attachment? E.g., syllabus, article).",
        max_length=150,
        blank=True, 
        default='',
        null=True
    )
    slug = AutoSlugField(
        populate_from='title', 
        default=None,
        always_update=False, 
        null=True, 
        max_length=150
    )

    def slugify_function(self, content, words):
        """
        Slugifies title of blog post for URL.
        """
        return "-".join(default_slugify(content).split('-', words)[:words])

    @property
    def date(self):
        """
        Returns the display_datetime date.
        """
        return self.display_datetime.date()

    @property
    def time(self):
        """
        Returns the display_datetime time.
        """
        return self.display_datetime.time()

    @cached_property
    def pandoc_process(self):
        """
        Process the post content using pandoc and the sitewide CSL.
        """
        try:
            csl = SiteWideSetting.objects.all().order_by('-id')[0].csl.file.url
        except:
            csl = None
        try:
            biblio=SiteWideSetting.objects.all().order_by('-id')[0].library.bib_file.url
        except:
            biblio=None
        return pandocify(
            content=self.content,
            csl=settings.BASE_DIR+csl,
            bib=settings.BASE_DIR+biblio
        )

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
    
    def __str__(self):
        return self.title

class CitationStyle(VersionClass):
    name = models.CharField(
        max_length=50, 
        unique=True
    )
    file = models.FileField(
        upload_to='citestyles/'
    )

    class Meta:
        verbose_name = "Citation Style"
        verbose_name_plural = "Citation Styles"

    def __str__(self):
        return self.name

class Conference(VersionClass):
    name = models.CharField(
        help_text = "What is the event's title?",
        max_length=100
    )
    organizations = models.ManyToManyField(
        Institution, 
        help_text = "Associated professional orgs?",
        blank=True
    )

    def __str__(self):
        return str(self.name)


class ConferenceInstance(VersionClass):
    start = models.DateField(
        help_text = "On what day does the conference start?"
    )
    end = models.DateField(
        help_text = "On what day does the conference end?"
    )
    conference = models.ForeignKey(
        Conference,
        help_text = "Which conference is this a part of?",
        blank=True,
        default='',
        on_delete = models.SET_DEFAULT
    )
    virtual = models.BooleanField(
        help_text = "Check this box if the conference is virtual.",
        default=False
    )
    website = models.URLField(
        help_text = "Provide a link to the conference website.",
        blank=True, 
        default=''
    )
    address = models.CharField(
        help_text = "Address of the institution.",
        max_length=200, 
        null=False, 
        blank=True, 
        default=''
    )
    city = models.CharField(
        help_text = "City in which institution is located.",
        max_length=100
    )
    state = models.CharField(
        help_text = "State in which institution is located.",
        max_length=100
    )
    postal = models.CharField(
        help_text = "Postcode in which institution is located.",
        max_length=20,
        blank=True,
        default=''
    )
    country = models.CharField(
        help_text = "Country in which institution is located.",
        max_length=100
    )
    location = models.PointField(
        help_text = "Approximate location of institution.",
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        """
        Overwrite save method to update main bibliography when model is saved.
        """
        if self.location:
            pass
        else:
            add_array = [self.address, self.city, self.state, self.postal, self.country]
            query = ','.join(filter(None, add_array))
            self.location = geocode_address(query)
        super(ConferenceInstance, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Conference Instance"
        verbose_name_plural = "Conferences Instances"

    def __str__(self):
        return str(self.start.year) + " " + self.conference.name


class Event(VersionClass):
    banner = models.ImageField(
        help_text = "Event banner image.",
        null=True, 
        blank=True, 
        upload_to = 'events/banners/%Y/%m/%d'
    )
    day = models.DateField(
        help_text = "On what day does the event take place?"
    )
    start = models.TimeField(
        help_text = "Provide start time."
    )
    end = models.TimeField(
        help_text = "Provide end time."
    )
    title = models.CharField(
        help_text = "What is the event's title?",
        max_length=100
    )
    website = models.URLField(
        help_text = "Provide a link to the event website.",
        blank=True, 
        default=''
    )
    desc = MarkdownxField(
        help_text = "Describe the event (markdown-enabled)."
    )
    participant = models.ManyToManyField(
        Person, 
        help_text = "Associate individual participants with the event by their role.",
        through='Role'
    )
    virtual_url = models.URLField(
        help_text = "What is the URL of the virtual event (if this applies...)",
        blank=True, 
        default=''
    )
    conference = models.ForeignKey(
        ConferenceInstance,
        help_text = "Is the event part of a conference?",
        null=True,
        blank=True,
        default='',
        on_delete = models.SET_DEFAULT
    )
    sponsors = models.ManyToManyField(
        Institution, 
        help_text = "What are the sponsoring institutions?",
        blank=True
    )
    cancel = models.BooleanField(
        help_text = "Check this box if the event is canceled.",
        default=False
    )

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self):
        return self.title

class Role(VersionClass):
    participant = models.ForeignKey(
        Person, 
        help_text = "Person participating in a given event.",
        on_delete=models.CASCADE
    )
    event = models.ForeignKey(
        Event, 
        help_text = "Event in which a person is participating.",
        on_delete=models.CASCADE
    )
    ROLES = [
        ('O', 'Organizer'),
        ('D', 'Discussant'),
        ('M', 'Moderator'),
        ('P', 'Panelist'),
        ('R', 'Presenter'),
        ('I', 'Introducer'),
        ('W', 'Workshop Leader')
    ]
    role = models.CharField(
        help_text = "What is the person's role in the event?",
        max_length=1,
        choices=ROLES,
        default='L',
    )

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
    
    def __str__(self):
        return self.role