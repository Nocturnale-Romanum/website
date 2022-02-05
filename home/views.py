from .models import *
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404

feastURLprefix = "feast"
chantURLprefix = "chant"
indexURLprefix = "index"
contentsURLprefix = "contents"

def contents(request):
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
  pass


