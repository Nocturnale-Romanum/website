import os, shutil, sys
from datetime import datetime

import shlex
import urllib.parse

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel

gabcFolder = os.path.join("nocturnale", "static", "gabc")
pngFolder = os.path.join("nocturnale", "static", "pngs")
pngUrlPrefix = "/static/pngs/"
gabcUrlPrefix = "/static/gabc/"

class HomePage(Page):
    """Somewhat generic page model.
    The parent Page class has a 'title' attribute and the associated content panel, plus metadata."""
    templates = "home/home_page.html"
    # this is the contents of the page
    text = RichTextField(blank=True)
    # this image has its content_panel in the admin, but is not yet used.
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    # added fields should be added there as well in order to be editable in the admin.
    content_panels = Page.content_panels + [
        ImageChooserPanel("image"),
        FieldPanel("text"),
    ]

class Source(models.Model):
    siglum = models.CharField(max_length=100, blank=False)
    # should be of the form http://baseurl.../.../{}/..." where {} will be replaced with the folio number
    urlpattern = models.CharField(max_length=200, blank=True)
    def __str__(self):
      return self.siglum

class Proposal(models.Model):
    """This class represents a bit of GABC code and associated metadata,
    submitted by a user as restitution of a given chant."""
    chant = models.ForeignKey("Chant", related_name="proposals", null=False, on_delete=models.CASCADE)
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="proposals", null=False, on_delete=models.PROTECT)
    # this version field is not used at the time.
    version = models.CharField(max_length=100, blank=True)
    # when a chant gets its first proposal, it should go from MISSING to POPULATED
    source = models.ForeignKey("Source", related_name="proposals", null=True, on_delete=models.SET_NULL)
    sourcepage = models.CharField(max_length=10, blank=True)
    nabc_status = models.CharField(max_length=10, choices=[(x,x) for x in ["none", "auth", "arfv", "fake"]], null=False, blank=False, default="none")
    def save(self, *args, **kwargs):
      if 'submitter' in kwargs:
        self.submitter = kwargs['submitter']
      if 'version' not in kwargs:
        self.version = self.submitter.username
      if 'chant' in kwargs:
        self.chant = kwargs['chant']
      if self.chant.status == "MISSING":
        self.chant.status = "POPULATED"
        self.chant.save()
      super(Proposal, self).save(*args, **kwargs)
    def __str__(self):
      return (self.chant.code + " by " + self.submitter.username)
    def filename(self):
      return self.chant.code + "_" + self.submitter.username + ".gabc"
    def filepath(self):
      return os.path.join(gabcFolder, self.filename())
    def imgname(self):
      return self.chant.code + "_" + self.submitter.username + ".png"
    def imgpath(self):
      return os.path.join(pngFolder, self.imgname())
    def imgurl(self):
      return pngUrlPrefix+self.imgname()
    def gabcurl(self):
      return gabcUrlPrefix+self.filename()
    def makefile(self, gabc, mode, differentia):
      if mode is None:
        mode = ""
      if differentia is None:
        differentia = ""
      f = open(self.filepath(), 'w')
      f.write("name:{};\n".format(self.chant.incipit))
      f.write("office-part:{};\n".format(self.chant.office_part))
      f.write("mode:{}{};\n".format(mode, differentia))
      f.write("submitter:{};\n".format(self.submitter.username))
      if "|" in gabc:
        f.write("nabc-lines:1;\n")
      f.write("%%\n")
      f.write(gabc+"\n")
      f.close()
    def select(self, commitmsg=None):
      fpath = self.filepath()
      new_fpath = os.path.join(gabcFolder, self.chant.code + ".gabc")
      shutil.copyfile(fpath, new_fpath)
      if not commitmsg:
        commitmsg = "'{} was selected from the command line.'".format(self.chant.code)
      try:
        os.system("cd nocturnale/static && git add gabc && git commit -m {} && git fetch && git rebase origin/main && git push".format(commitmsg))
      except:
        pass
    def makepng(self):
      os.system("./tex_build/build.py "+os.path.join(gabcFolder, self.filename())+" "+pngFolder+" &")
    def sourceurl(self):
      if (self.source and self.source.urlpattern):
        return self.source.urlpattern.format(self.sourcepage)
      else:
        return ""
    def gabc_mode_diff(self):
      return parse_gabc_file(self.filepath())
    def url_encoded_gabc(self):
      return urllib.parse.quote(self.gabc_mode_diff()[0])
    def update(self, gabc=None, mode=None, differentia=None, commitmsg=None):
      """General-purpose method for updating an existing proposal. Called with all params upon creation, may be called with less params, in which case current params from the proposal file will be reused."""
      (old_gabc, old_mode, old_diff) = self.gabc_mode_diff()
      if not gabc:
        gabc = old_gabc
      if not mode:
        mode = old_mode
      if not differentia:
        differentia = old_diff
      # if no commit message was provided (e.g. by view edit_proposal) a default one is made
      if not commitmsg:
        commitmsg = self.chant.code + " by " + self.submitter.username + " was updated from the command line."
        commitmsg = shlex.quote(commitmsg)
      self.makefile(gabc, mode, differentia)
      # if the proposal was selected, it must be unselected.
      if self.chant.selected_proposal == self:
        self.chant.selected_proposal = None
        self.chant.status = "POPULATED"
        self.chant.save()
      try:
        os.system("cd nocturnale/static && git add gabc && git commit -m {} --author \"{} <{}@marteo.fr>\"&& git fetch && git rebase origin/main && git push".format(commitmsg, self.submitter.username, self.submitter.username))
      except:
        pass
      self.makepng()


class Chant(models.Model):
    """This class represents a chant entry, that is, a specific sung part of a given day's Matins.
    A number of proposals are associated with a given Chant entry, one of which may be 'selected' (for insertion in the GABC reference files)."""
    selected_proposal = models.ForeignKey("Proposal", null=True, on_delete=models.SET_NULL, related_name="chant_where_this_is_selected")
    feast = models.ForeignKey("Feast", null=False, on_delete=models.PROTECT, related_name="chants")
    code = models.CharField(max_length=20, null=False, default="ERROR", unique=True)
    # never change this value. new chant entries within a feast should be attributed a unique feast_position according to their position.
    feast_position = models.IntegerField(null=False, default=0)
    incipit = models.CharField(max_length=100, null=False, blank=False, default="REMOVE_ME")
    cantus_id = models.CharField(max_length=20, null=True, blank=True)
    # all chants should be of office-part an, ps, hy, re, or; according to Gregobase classification of genres.
    office_part = models.CharField(max_length=10, null=False, blank=False, default="ERROR")
    # if a chant has related chants, e.g. duplicates, or chants that share a common refrain, or are mostly identical, then it will point
    # to a related_chants_class which points back to all the "duplication family"
    related_chants_class = models.ForeignKey("RelatedChantsClass", null=True, on_delete=models.SET_NULL, related_name="chants")
    status = models.CharField(max_length=10, choices=[(x,x) for x in ["DEFINITIVE", "REVIEWED", "SELECTED", "POPULATED", "MISSING"]], null=False, blank=False, default="MISSING")
    def __str__(self):
      return self.code

class RelatedChantsClass(models.Model):
    """This class has no fields, its only role is to point back to the list of chants that point to a given instance of this class,
    in order to easily access duplicates of a given chant."""
    pass

class TexSnippet(models.Model):
    """Tex snippet entry model"""
    tex_code = models.TextField()
    feast = models.ForeignKey("Feast", null=False, on_delete=models.PROTECT)
    code = models.CharField(max_length=10)
    feast_position = models.IntegerField()
    def filename(self):
      return self.code + ".tex"

class Feast(models.Model):
    """This class represents not only a feast, but any liturgical day. All informations pertinent to printing this day in the book are here.
    The book might display the name of this day 'title' (mandatory), its exact calendar day 'day', its rank under both sets of rubrics.
    Every feast has an identification code that will prefix its chants' identification code: F1..F7 for Sun..Sat, A1 for 1st Week of Advent, etc.
    A feasts has chants, and tex snippets (rubrics), which are intertwined according to their 'feast_position' field.
    """
    day = models.CharField(max_length = 300, null=True, blank=True)
    title = models.CharField(max_length = 300, null=False, default="REMOVE_ME")
    rank_54 = models.CharField(max_length = 200, null=True, blank=True)
    rank_60 = models.CharField(max_length = 200, null=True, blank=True)
    code = models.CharField(max_length = 10, null=False, default="ERROR", unique=True)
    # currently, ordinary = 10, tempore = 100, psanctis = 2350, csanctis = 5290
    order = models.IntegerField(null=False, default=0)
    # the contents of 'header' will be displayed on the page's header throughout the feast.
    header = models.CharField(max_length = 200, null=True, blank=True)
    # 1 is for the most solemn occasions, 2 is for all feasts and sundays, 3 is normally for ferias.
    title_level = models.IntegerField(null=False, default=1)
    def __str__(self):
      return self.code

class Comment(models.Model):
    """A basic Comment model"""
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="comments", null=False, on_delete=models.PROTECT)
    date = models.DateTimeField(default=datetime.now)
    text = models.CharField(max_length=2000, null=False, blank=False)
    proposal = models.ForeignKey("Proposal", related_name="comments", null=False, on_delete=models.CASCADE)

def parse_gabc_file(filepath):
  try:
    f = open(filepath).read().split("%%")
  except:
    return (None, None, None)
  header = f[0].strip()
  gabc = "%%".join(f[1:]).strip()
  modediff = header.split("mode:")[1].split(";")[0].strip()
  try:
    mode = modediff[0]
  except:
    mode = None
  try:
    diff = modediff[1:]
  except:
    diff = None
  return (gabc, mode, diff)
