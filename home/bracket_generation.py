##### to be imported into a django shell for the nocturnale website
import time
from home.models import *

def bracketize_gabc(gabc):
  """Takes GABC code without headers and with NABC present.
     Outputs the same GABC code, with NABC brackets inserted at the beginning and end."""
  if "|" not in gabc:
    raise ValueError("no pipe in gabc")
  ### first, we insert "ob" after the first pipe (at the beginning of the first NABC snippet),
  ### possibly also after some negative or positive horizontal whitespace inserted at the beginning of said NABC
  cur_index=gabc.index("|") + 1
  while gabc[cur_index] in ['/', '`']:
    cur_index += 1
  gabc = gabc[:cur_index]+"ob"+gabc[cur_index:]
  ### then, we insert "cb" immediately before the parenthese that closes the last NABC snippet (following the last pipe)
  gabc_l = gabc.split("|")
  last_snippet = gabc_l[-1]
  idx = last_snippet.index(")")
  last_snippet = last_snippet[:idx]+"cb"+last_snippet[idx:]
  gabc_l[-1] = last_snippet
  gabc = "|".join(gabc_l)
  return gabc

def bracketize_verse(gabc):
  """Takes GABC code without headers and with NABC present, containing at least one <sp>V/</sp> string.
     Outputs the same GABC code, with NABC brackets inserted opening at the first verse sign and closing at the first double bar following it."""
  if "<sp>V/</sp>" not in gabc:
    raise ValueError("no verse sign in gabc")
  gabc_splitverses = gabc.split("<sp>V/</sp>")
  verse = gabc_splitverses[1]
  verse_splitbars = verse.split("::")
  verse_splitbars[0] = bracketize_gabc(verse_splitbars[0])
  verse = "::".join(verse_splitbars)
  gabc_splitverses[1] = verse
  gabc = "<sp>V/</sp>".join(gabc_splitverses)
  return gabc

def bracketize_gp(gabc):
  """Takes GABC code without headers and with NABC present, containing at least two <sp>V/</sp> strings.
     Outputs the same GABC code, with NABC brackets inserted opening at the last verse sign and closing at the first double bar following it."""
  if gabc.count("<sp>V/</sp>") < 2:
    raise ValueError("no second verse sign in gabc")
  gabc_splitverses = gabc.split("<sp>V/</sp>")
  verse = gabc_splitverses[-1]
  verse_splitbars = verse.split("::")
  verse_splitbars[0] = bracketize_gabc(verse_splitbars[0])
  verse = "::".join(verse_splitbars)
  gabc_splitverses[-1] = verse
  gabc = "<sp>V/</sp>".join(gabc_splitverses)
  return gabc

def run_bracketization():
  """Applies the relevant bracketization to all responsories that have NABC"""
  proposals = Proposal.objects.filter(chant__office_part="re")
  proposals = proposals.exclude(nabc_status="none")
  modified_proposals = set()
  for p in proposals:
    (gabc, mode, diff) = p.gabc_mode_diff()
    if p.nabc_status == "fake":
      gabc = bracketize_gabc(gabc)
      modified_proposals.add(p)
    else:
      if "V Gloria" in p.chant.incipit:
        try:
          gabc = bracketize_gp(gabc)
        except Exception as e:
          print("ERROR on GP bracketization for {}".format(str(p)))
        modified_proposals.add(p)
      if p.nabc_status == "arfv":
        gabc = bracketize_verse(gabc)
        modified_proposals.add(p)
    p.makefile(gabc, mode, diff)
  for p in modified_proposals:
    p.makepng()
    time.sleep(5*60)
