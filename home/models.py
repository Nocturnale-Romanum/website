from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel


class HomePage(Page):
    """Somewhat generic page model"""
    templates = "home/home_page.html"

    text = RichTextField(blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    content_panels = Page.content_panels + [
        ImageChooserPanel("image"),
        FieldPanel("text"),
    ]

class Proposal(models.Model):
    chant = models.ForeignKey("Chant", related_name="proposals", null=False, on_delete=models.CASCADE)
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="proposals", null=False, on_delete=models.PROTECT)
    version = models.CharField(max_length=100, blank=True)
    def create(self, **obj_data):
      obj_data['version'] = obj_data['version'].strip()
      if obj_data['version'] == "":
        obj_data['version'] = obj_data['submitter'].username
      c = obj_data['chant']
      if c.status == "MISSING":
        c.status = "POPULATED"
        c.save()
      super().create(**obj_data)
    def filename(self):
      return self.chant.feast.code + self.chant.code + "_" + self.version + ".gabc"

class Chant(models.Model):
    """Basic chant entry model"""
    selected_proposal = models.ForeignKey("Proposal", null=True, on_delete=models.SET_NULL, related_name="chant_where_this_is_selected")
    feast = models.ForeignKey("Feast", null=False, on_delete=models.PROTECT, related_name="chants")
    code = models.CharField(max_length=20, null=False, default="ERROR", unique=True)
    feast_position = models.IntegerField(null=False, default=0)
    incipit = models.CharField(max_length=100, null=False, blank=False, default="REMOVE_ME")
    cantus_id = models.CharField(max_length=20, null=True, blank=True)
    office_part = models.CharField(max_length=10, null=False, blank=False, default="ERROR")
    related_chants_class = models.ForeignKey("RelatedChantsClass", null=True, on_delete=models.SET_NULL, related_name="chants")
    status = models.CharField(max_length=10, choices=[(x,x) for x in ["DEFINITIVE", "REVIEWED", "SELECTED", "POPULATED", "MISSING"]], null=False, blank=False, default="MISSING")

class RelatedChantsClass(models.Model):
    pass

class TexSnippet(models.Model):
    """Tex snippet entry model"""
    tex_code = models.TextField()
    feast = models.ForeignKey("Feast", null=False, on_delete=models.PROTECT)
    code = models.CharField(max_length=10)
    feast_position = models.IntegerField()
    def filename(self):
      return self.feast.code + self.code + ".tex"

class Feast(models.Model):
    """Basic feast model"""
    day = models.CharField(max_length = 300, null=True, blank=True)
    title = models.CharField(max_length = 300, null=False, default="REMOVE_ME")
    rank_54 = models.CharField(max_length = 200, null=True, blank=True)
    rank_60 = models.CharField(max_length = 200, null=True, blank=True)
    code = models.CharField(max_length = 10, null=False, default="ERROR", unique=True)
    order = models.IntegerField(null=False, default=0)
    # currently, ordinary = 10, tempore = 100, psanctis = 2350, csanctis = 5290
    header = models.CharField(max_length = 200, null=True, blank=True)
    title_level = models.IntegerField(null=False, default=1)

