from .models import *
from .forms import *
from .util import *

import os
import shlex
from time import time

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, redirect

# we define some URL prefixes here in case they change down the line
feastURLprefix = "feast"
chantURLprefix = "chant"
indexURLprefix = "index"
contentsURLprefix = "contents"
proposalURLprefix = "proposal"
tablesURLprefix = "tables"

def contents(request, opart=""):
  """Passes to a template the list of feasts that have at least one proper chant, in the order of the book.
  100, 2350, 5290, 6000 are magic values of the 'order' field in the Feasts table, that correspond to the major titles :
  proper of seasons, of saints, and commons"""
  template = loader.get_template('home/contents.html')
  feasts = Feast.objects.filter(chants__isnull=False).distinct().order_by("order")
  if opart == "re":
    feasts = [f for f in feasts if f.chants.filter(office_part="re")]
  if opart == "an":
    feasts = [f for f in feasts if f.chants.exclude(office_part="re")]
  ordinaryFeasts = [f for f in feasts if f.order < 100]
  temporeFeasts = [f for f in feasts if (f.order > 100 and f.order < 2350)]
  sanctisFeasts = [f for f in feasts if (f.order > 2350 and f.order < 5290)]
  communiaFeasts = [f for f in feasts if (f.order > 5290 and f.order < 6000)]
  appendixFeasts = [f for f in feasts if f.order > 6000]
  if opart == "re":
    ordinaryFeasts = [(f, f.re_status) for f in ordinaryFeasts]
    temporeFeasts = [(f, f.re_status) for f in temporeFeasts]
    sanctisFeasts = [(f, f.re_status) for f in sanctisFeasts]
    communiaFeasts = [(f, f.re_status) for f in communiaFeasts]
    appendixFeasts = [(f, f.re_status) for f in appendixFeasts]
  elif opart == "an":
    ordinaryFeasts = [(f, f.an_status) for f in ordinaryFeasts]
    temporeFeasts = [(f, f.an_status) for f in temporeFeasts]
    sanctisFeasts = [(f, f.an_status) for f in sanctisFeasts]
    communiaFeasts = [(f, f.an_status) for f in communiaFeasts]
    appendixFeasts = [(f, f.an_status) for f in appendixFeasts]
  else:
    ordinaryFeasts = [(f, f.status) for f in ordinaryFeasts]
    temporeFeasts = [(f, f.status) for f in temporeFeasts]
    sanctisFeasts = [(f, f.status) for f in sanctisFeasts]
    communiaFeasts = [(f, f.status) for f in communiaFeasts]
    appendixFeasts = [(f, f.status) for f in appendixFeasts]
  context = {
    'contentsURLprefix' : contentsURLprefix,
    'feastURLprefix' : feastURLprefix,
    'indexURLprefix' : indexURLprefix,
    'ordinaryFeasts' : ordinaryFeasts,
    'temporeFeasts' : temporeFeasts,
    'sanctisFeasts' : sanctisFeasts,
    'communiaFeasts' : communiaFeasts,
    'appendixFeasts' : appendixFeasts,
  }
  return HttpResponse(template.render(context, request))

def index(request, opart=""):
  """Passes to a template the list of chants, ordered by incipit.
  Spaces count in the order, which might be bad.
  This view should be optimized because it needs a long time to render."""
  template = loader.get_template('home/index.html')
  if opart not in ['an', 're', 'in', 'hy', 'or', 'ps']:
    chants = Chant.objects.order_by('incipit')
  else:
    chants = Chant.objects.filter(office_part = opart).order_by('incipit')
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
  n_tables = chant.tables.count()
  selected = chant.selected_proposal
  unselected = chant.proposals.all()
  if selected:
    unselected = unselected.exclude(pk=selected.pk)
    selected_source_url = selected.sourceurl()
    selected_img_path = selected.imgurl()
    selected_gabc_path = selected.gabcurl()
    selected_gabc_code = selected.url_encoded_gabc()
    # select the last 3 comments, sorted in chronologic order
    selected_comments = list(selected.comments.order_by('date'))[-3:]
  else:
    selected_img_path = None
    selected_gabc_path = None
    selected_gabc_code = None
    selected_source_url = None
    selected_comments = None
  if request.user.is_authenticated:
    try:
      userproposal = chant.proposals.get(submitter = request.user)
      userproposal_gabc_path = userproposal.gabcurl()
      userproposal_gabc_code = userproposal.url_encoded_gabc()
      userproposal_img_path = userproposal.imgurl()
      userproposal_source_url = userproposal.sourceurl()
      # select the last 3 comments, sorted in chronologic order
      userproposal_comments = list(userproposal.comments.order_by('date'))[-3:]
      unselected = unselected.exclude(pk = userproposal.pk)
    except:
      userproposal = None
      userproposal_img_path = None
      userproposal_gabc_path = None
      userproposal_gabc_code = None
      userproposal_source_url = None
      userproposal_comments = None
  else:
    userproposal = None
    userproposal_img_path = None
    userproposal_gabc_path = None
    userproposal_gabc_code = None
    userproposal_source_url = None
    userproposal_comments = None
  context = {
    'feastURLprefix' : feastURLprefix,
    'tablesURLprefix' : tablesURLprefix,
    'chant' : chant,
    'n_tables' : n_tables,
    'selected' : {'proposal': selected, 'link': selected_img_path, 'sourcelink': selected_source_url, 'comments': selected_comments, 'gabc_url': selected_gabc_path, 'gabc_code': selected_gabc_code},
    'userproposal' : {'proposal': userproposal, 'link': userproposal_img_path, 'sourcelink': userproposal_source_url, 'comments': userproposal_comments, 'gabc_url': userproposal_gabc_path, 'gabc_code': userproposal_gabc_code},
    'unselected' : [{'proposal': p, 'link': p.imgurl(), 'sourcelink': p.sourceurl(), 'comments': list(p.comments.order_by('date'))[-3:], 'gabc_url': p.gabcurl(), 'gabc_code': p.url_encoded_gabc()} for p in unselected],
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
      (gabc, mode, diff) = proposal.gabc_mode_diff()
      nabc_status = proposal.nabc_status
      try:
        source = proposal.source.siglum
      except:
        source = None
      sourcepage = proposal.sourcepage
    else :
      gabc = None
      mode = None
      diff = None
      source = None
      sourcepage = None
      nabc_status = "none"
    form = ProposalEditForm(initial = {'gabc': gabc, 'mode': mode, 'diff': diff, 'source': source, 'sourcepage': sourcepage, 'nabcstatus': nabc_status})
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
    nabc_status = request.POST.get('nabcstatus')
    gabc = request.POST.get('gabc')
    mode = request.POST.get('mode')
    try:
      source = Source.objects.get(siglum = source_siglum)
    except:
      source = None
    proposal.source = source
    proposal.sourcepage = sourcepage
    if '|' not in gabc:
        nabc_status = 'none'
    elif nabc_status == 'none':
        nabc_status = 'fake'
    proposal.nabc_status = nabc_status
    proposal.save()
    commentmsg = request.POST.get('comment')
    comment = Comment(proposal = proposal, text = commentmsg, author = request.user)
    comment.save()
    commitmsg = "{} edited {}: {}".format(request.user.username, chant.code, commentmsg)
    differentia=request.POST.get('diff')
    proposal.update(gabc=gabc.replace('\r\n', '\n'), mode=mode, differentia=differentia, commitmsg=shlex.quote(commitmsg))
    return redirect("/"+chantURLprefix+"/"+hcode+"/")

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
      'feastURLprefix': feastURLprefix,
      'proposal': p,
      'imglink': p.imgurl(),
      'gabc_url': p.gabcurl(),
      'gabc_code': p.url_encoded_gabc(),
      'comments': p.comments.order_by('date'),
      'sourcelink': sourcelink,
      'chant': c,
      'form': form,
    }
    ### we acquit any notifications that might have sent us there
    if request.user.is_authenticated :
      for n in request.user.notifications.filter(is_read=False).filter(comment__proposal=p):
        n.is_read=True
        n.save()
    ### end of notification acquittal
    return HttpResponse(template.render(context, request))
  elif request.method == "POST":
    if request.user.is_authenticated :
      text = request.POST.get("comment")
      c = Comment(proposal = p, text = text, author = request.user)
      c.save()
      ### we create notifications for all users who have previously commented on this proposal
      notified_users = set([c.author for c in p.comments.all()])
      notified_users.remove(request.user)
      for u in notified_users:
        n = Notification(user = u, comment = c)
        n.save()
    return redirect("/"+proposalURLprefix+"/"+hcode+"/"+submitter+"/")

def comment_edit(request, id):
  comment = get_object_or_404(Comment, id=id)
  redirect_url = "/"+proposalURLprefix+"/"+comment.proposal.chant.code+"/"+comment.proposal.submitter.username+"/"
  if not request.user == comment.author:
    return redirect(redirect_url)
  if request.method == "GET":
    template = loader.get_template('home/comment_edit.html')
    form = CommentEditForm(initial= {'comment': comment.text})
    context = {
      'comment': comment,
      'form': form,
    }
    return HttpResponse(template.render(context, request))
  elif request.method == "POST":
    text = request.POST.get("comment")
    comment.text = text
    comment.save()
    return redirect(redirect_url)

def select(request, hcode, submitter):
  if not request.user.is_staff:
    return redirect("/"+chantURLprefix+"/"+hcode)
  c = get_object_or_404(Chant, code=hcode)
  p = get_object_or_404(Proposal, chant=c, submitter__username=submitter)
  c.selected_proposal = p
  c.status = "SELECTED"
  c.save()
  f = c.feast
  if set([cc.status for cc in f.chants.all()]) == {"SELECTED"}: # all chants of the relevant feast are now SELECTED
    f.status = "SELECTED"
    f.save()
  if set([cc.status for cc in f.chants.filter(office_part="re")]) == {"SELECTED"}: # all chants of the relevant feast are now SELECTED
    f.re_status = "SELECTED"
    f.save()
  if set([cc.status for cc in f.chants.exclude(office_part="re")]) == {"SELECTED"}: # all chants of the relevant feast are now SELECTED
    f.an_status = "SELECTED"
    f.save()
  commitmsg = "{} selected {}'s proposal for {}".format(request.user.username, submitter, hcode)
  p.select(commitmsg=shlex.quote(commitmsg)) # this makes p copy its file hcode_submitter.gabc into hcode.gabc and commit that change
  return redirect("/"+chantURLprefix+"/"+hcode)

def comment_delete(request, id):
  comment = get_object_or_404(Comment, id=id)
  hcode = comment.proposal.chant.code
  proposal_submitter = comment.proposal.submitter.username
  if (request.user.is_staff or request.user == comment.author):
    comment.delete()
  return redirect("/"+proposalURLprefix+"/"+hcode+"/"+proposal_submitter+"/")

def tables(request, hcode):
  template = loader.get_template('home/tables.html')
  c = get_object_or_404(Chant, code=hcode)
  if request.method == "GET":
    form = TableForm()
    context = {
      'chantURLprefix': chantURLprefix,
      'feastURLprefix': feastURLprefix,
      'chant':c,
      'form': form,
      'tables':c.tables.all(),
    }
    return HttpResponse(template.render(context, request))
  elif request.method == "POST":
    if request.user.is_authenticated:
      for f in request.FILES.getlist('tables'):
        t = Table(chant=c, uploader=request.user, tablefile=f)
        if t.tablefile.size < 50000000 and t.tablefile.name.split('.')[-1] in ['jpg', 'png', 'pdf', 'zip', 'JPG', 'PNG', 'PDF', 'ZIP']:
          t.save()
    return redirect("/"+tablesURLprefix+"/"+hcode+"/")

def notifications(request):
  if not request.user.is_authenticated :
    return redirect("/")
  notifs = request.user.notifications.order_by('-comment__date')[:100]
  context = {
    'notifs': notifs
  }
  template = loader.get_template('home/notifications.html')
  return HttpResponse(template.render(context, request))

def versify_view(request):
  template = loader.get_template('home/versify.html')
  if request.method == "GET":
    form = VersifyForm()
    answer = ""
  if request.method == "POST":
    mode = request.POST.get("mode")
    text = request.POST.get("input")
    rsigns = request.POST.get("rsigns")
    neumes = request.POST.get("neumes")
    form = VersifyForm(initial = {"mode":mode, "input":text, "rsigns":rsigns, "neumes":neumes})
    filename = str(int(time()*1000))
    f=open(filename, "w")
    f.write(text)
    f.close()
    os.system("./hyphen-la/scripts/syllabify.py -t chant -m liturgical -c - -i {} -o {}_out".format(filename, filename))
    f=open(filename+"_out")
    answer = f.read()
    answer = versify(answer, mode, rsigns=rsigns, neumes=neumes)
    f.close()
    os.remove(filename)
    os.remove(filename+"_out")
  context = {
    'form':form,
    'answer':answer,
  }
  return HttpResponse(template.render(context, request))

def transpose(request):
  template = loader.get_template('home/transpose.html')
  if request.method == "GET":
    form = TransposeForm()
    answer = ""
  if request.method == "POST":
    offset = request.POST.get("offset")
    gabc = request.POST.get("gabc")
    form = TransposeForm(initial = {"offset":offset, "gabc":gabc})
    try:
      answer = transpose_gabc(gabc, int(offset))
    except ValueError:
      answer = "ERROR: some notes were too high or too low to be transposed"
  context = {
    'form':form,
    'answer':answer,
  }
  return HttpResponse(template.render(context, request))

def removenabcheights(request):
  template = loader.get_template('home/removenabcheights.html')
  if request.method == "GET":
    form = RemoveNabcHeightsForm()
    answer = ""
  if request.method == "POST":
    nabc = request.POST.get("nabc")
    form = RemoveNabcHeightsForm(initial = {"nabc":nabc})
    answer = remove_heights_from_nabc_element(nabc)
  context = {
    'form':form,
    'answer':answer,
  }
  return HttpResponse(template.render(context, request))

def removersigns(request):
  template = loader.get_template('home/removersigns.html')
  if request.method == "GET":
    form = RemoveRsignsForm()
    answer = ""
  if request.method == "POST":
    gabc = request.POST.get("gabc")
    form = RemoveRsignsForm(initial = {"gabc":gabc})
    answer = remove_rsigns_string(gabc)
  context = {
    'form':form,
    'answer':answer,
  }
  return HttpResponse(template.render(context, request))

