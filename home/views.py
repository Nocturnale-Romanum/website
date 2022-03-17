from .models import *
from .forms import *

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, redirect

# we define some URL prefixes here in case they change down the line
feastURLprefix = "feast"
chantURLprefix = "chant"
indexURLprefix = "index"
contentsURLprefix = "contents"
proposalURLprefix = "proposal"

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
  If one proposal is selected, it is singled out for display.
  If the user has submitted a proposal, it is singled out for display."""
  template = loader.get_template('home/chant.html')
  chant = get_object_or_404(Chant, code=hcode)
  selected = chant.selected_proposal
  unselected = chant.proposals.all()
  if selected:
    unselected = unselected.exclude(pk=selected.pk)
    selected_source_url = selected.sourceurl()
    selected_img_path = selected.imgurl()
    selected_comments = selected.comments.order_by('date')
  else:
    selected_img_path = None
    selected_source_url = None
    selected_comments = None
  if request.user.is_authenticated:
    try:
      userproposal = chant.proposals.get(submitter = request.user)
      userproposal_img_path = userproposal.imgurl()
      userproposal_source_url = userproposal.sourceurl()
      userproposal_comments = userproposal.comments.order_by('date')
      unselected = unselected.exclude(pk = userproposal.pk)
    except:
      userproposal = None
      userproposal_img_path = None
      userproposal_source_url = None
      userproposal_comments = None
  else:
    userproposal = None
    userproposal_img_path = None
    userproposal_source_url = None
  context = {
    'feastURLprefix' : feastURLprefix,
    'chant' : chant,
    'selected' : {'proposal': selected, 'link': selected_img_path, 'sourcelink': selected_source_url, 'comments': selected_comments},
    'userproposal' : {'proposal': userproposal, 'link': userproposal_img_path, 'sourcelink': userproposal_source_url, 'comments': userproposal_comments},
    'unselected' : [{'proposal': p, 'link': p.imgurl(), 'sourcelink': p.sourceurl(), 'comments': p.comments.order_by('date')} for p in unselected],
  }
  return HttpResponse(template.render(context, request))

def edit_proposal(request, hcode, cloned=""):
  """If the user is authenticated, passes to a template the necessary informations to edit their proposal.
  If the user is not authenticated, redirects to the relevant chant's page."""
  template = loader.get_template('home/edit_proposal.html')
  chant = get_object_or_404(Chant, code=hcode)
  if not request.user.is_authenticated :
    return redirect("/"+chantURLprefix+"/"+hcode)
  if request.method == "GET":
    clonedUser = User.objects.filter(username=cloned)
    if clonedUser: # a valid user was passed: we fetch their proposal
      proposalSet = chant.proposals.filter(submitter = clonedUser[0])
    else: # no valid user was passed: we fetch the request user's proposal
      proposalSet = chant.proposals.filter(submitter = request.user)
    if proposalSet : # we found an existing proposal, from the request user, or another user that was passed
      proposal = proposalSet[0]
      f = open(proposal.filepath()).read().split("%%")
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
      try:
        source = proposal.source.siglum
      except:
        source = None
      sourcepage = proposal.sourcepage
    else :
      gabc = None
      mode = None
      diff = None
    form = ProposalEditForm(initial = {'gabc': gabc, 'mode': mode, 'diff': diff, 'source': source, 'sourcepage': sourcepage})
    context = {
      'chantURLprefix' : chantURLprefix,
      'chant' : chant,
      'form' : form,
    }
    return HttpResponse(template.render(context, request))
  elif request.method == "POST":
    try:
      proposal = chant.proposals.get(submitter = request.user)
    except:
      proposal = Proposal(submitter = request.user, chant = chant)
    source_siglum = request.POST.get('source')
    sourcepage = request.POST.get('sourcepage')
    try:
      source = Source.objects.get(siglum = source_siglum)
    except:
      source = None
    proposal.source = source
    proposal.sourcepage = sourcepage
    proposal.makefile(request.POST.get('gabc'), request.POST.get('mode'), request.POST.get('differentia'))
    proposal.save()
    proposal.makepng()
    return redirect("/"+chantURLprefix+"/"+hcode)

def proposal(request, hcode, submitter):
  template = loader.get_template('home/proposal.html')
  c = get_object_or_404(Chant, code=hcode)
  p = get_object_or_404(Proposal, chant=c, submitter__username=submitter)
  if request.method == "GET":
    try:
      sourcelink = p.sourceurl()
    except:
      sourcelink = None
    form = CommentForm()
    context = {
      'chantURLprefix': chantURLprefix,
      'proposal': p,
      'imglink': p.imgurl(),
      'comments': p.comments.order_by('date'),
      'sourcelink': sourcelink,
      'chant': c,
      'form': form,
    }
    return HttpResponse(template.render(context, request))
  elif request.method == "POST":
    if request.user.is_authenticated :
      text = request.POST.get("comment")
      c = Comment(proposal = p, text = text, author = request.user)
      c.save()
    return redirect("/"+proposalURLprefix+"/"+hcode+"/"+submitter)
