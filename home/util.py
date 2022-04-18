from .models import *
from .views import *

from django.http import HttpRequest

def impersonate(username, chantcode, gabc, source, sourcepage, mode, differentia, comment):
  """Allows the server shell to send a proposal creation/update in the name of a specific user
  username, chantcode : self-explanatory.
  gabc, source, sourcepage, mode, differentia, comment : human-readable strings as entered in a proposal_edit form."""
  r = HttpRequest()
  r.method = "POST"
  u = User.objects.get(username=username)
  r.user = u
  r.POST["gabc"] = gabc
  r.POST["source"] = source
  r.POST["sourcepage"] = sourcepage
  r.POST["mode"] = mode
  r.POST["differentia"] = differentia
  r.POST["comment"] = comment
  edit_proposal(r, chantcode)


