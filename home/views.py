from .models import *
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, redirect

# we define some URL prefixes here in case they change down the line
feastURLprefix = "feast"
chantURLprefix = "chant"
indexURLprefix = "index"
contentsURLprefix = "contents"

def contents(request):
  """Passes to a template the list of feasts that have at least one proper chant, in the order of the book.
  100, 2350, 5290 are magic values of the 'order' field in the Feasts table, that correspond to the major titles :
  proper of seasons, of saints, and commons"""
  template = loader.get_template('home/contents.html')
  feasts = Feast.objects.filter(chants__isnull=False).distinct().order_by("order")
  ordinaryFeasts = [f for f in feasts if f.order < 100]
  temporeFeasts = [f for f in feasts if (f.order > 100 and f.order < 2350)]
  sanctisFeasts = [f for f in feasts if (f.order > 2350 and f.order < 5290)]
  communiaFeasts = [f for f in feasts if (f.order > 5290)]
  context = {
    'feastURLprefix' : feastURLprefix,
    'indexURLprefix' : indexURLprefix,
    'ordinaryFeasts' : ordinaryFeasts,
    'temporeFeasts' : temporeFeasts,
    'sanctisFeasts' : sanctisFeasts,
    'communiaFeasts' : communiaFeasts,
  }
  return HttpResponse(template.render(context, request))

def index(request):
  """Passes to a template the list of chants, ordered by incipit.
  Spaces count in the order, which might be bad.
  This view should be optimized because it needs a long time to render."""
  template = loader.get_template('home/index.html')
  chants = Chant.objects.order_by('incipit')
  context = {
    'chantURLprefix' : chantURLprefix,
    'feastURLprefix' : feastURLprefix,
    'parentURL' : contentsURLprefix,
    'chants' : chants,
  }
  return HttpResponse(template.render(context, request))

def feast(request, fcode):
  """Passes to a template the contents of a feast, 
  and if a chant in this feast has duplicates, shows in which feasts they are."""
  feast = get_object_or_404(Feast, code=fcode)
  chants = feast.chants.order_by("feast_position")
  template = loader.get_template('home/feast.html')
  chants_and_duplicates = []
  for c in chants:
    if c.related_chants_class :
      duplicates = c.related_chants_class.chants.all().exclude(pk=c.pk)
    else :
      duplicates = None
    chants_and_duplicates.append({"chant": c , "duplicates" : duplicates})
  context = {
    'chantURLprefix' : chantURLprefix,
    'parentURL' : contentsURLprefix,
    'feast' : feast,
    'chants_and_duplicates' : chants_and_duplicates,
  }
  return HttpResponse(template.render(context, request))

def chant(request, hcode):
  """Passes to a template the contents of a chant : metadata and list of associated proposals.
  If one proposal is selected, it is singled out for display."""
  template = loader.get_template('home/chant.html')
  chant = get_object_or_404(Chant, code=hcode)
  selected = chant.selected_proposal
  unselected = chant.proposals.all()
  if selected:
    unselected = unselected.exclude(pk=selected.pk)
  context = {
    'feastURLprefix' : feastURLprefix,
    'chant' : chant,
    'selected' : selected,
    'unselected' : unselected,
  }
  return HttpResponse(template.render(context, request))

def edit_proposal(request, hcode):
  """If the user is authenticated, passes to a template the necessary informations to edit their proposal.
  If the user is not authenticated, redirects to the relevant chant's page."""
  template = loader.get_template('home/edit_proposal.html')
  chant = get_object_or_404(Chant, code=hcode)
  if not request.user.is_authenticated :
    return redirect("/"+chantURLprefix+"/"+hcode)
  context = {
    'chantURLprefix' : chantURLprefix,
    'chant' : chant,
  }
  return HttpResponse(template.render(context, request))
