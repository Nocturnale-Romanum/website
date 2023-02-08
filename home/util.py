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

def impersonate_file(username, chantcode, source, sourcepage, comment, filepath):
  (gabc, mode, diff) = parse_gabc_file(filepath)
  impersonate(username, chantcode, gabc, source, sourcepage, mode, diff, comment)

vowels = ['a', 'e', 'i', 'o', 'u', 'y', 'æ', 'œ', 'ë']
accentedvowels = ['á', 'é', 'í', 'ó', 'ú', 'ý', 'ǽ']
upvowels = [x.upper() for x in vowels]
upaccentedvowels = [x.upper() for x in accentedvowels]

mode1Rverserules = [[('otherNotes', 'a')
    ],
    [('otherNotes', 'a')
    ],
    [('otherNotes', 'a')
    ]]
mode2Rverserules = [[('otherNotes', 'a')
    ],
    [('otherNotes', 'a')
    ],
    [('otherNotes', 'a')
    ]]
mode3Rverserules = [[('otherNotes', 'a')
    ],
    [('otherNotes', 'a')
    ],
    [('otherNotes', 'a')
    ]]
mode4Rverserules = [[('otherNotes', 'a')
    ],
    [('otherNotes', 'a')
    ],
    [('otherNotes', 'a')
    ]]
mode5Rverserules = [[('otherNotes', 'a')
    ],
    [('otherNotes', 'a')
    ],
    [('otherNotes', 'a')
    ]]
mode6Rverserules = [[('otherNotes', 'a')
    ],
    [('otherNotes', 'a')
    ],
    [('otherNotes', 'a')
    ]]
mode7Rverserules = [[('otherNotes', 'a')
    ],
    [('otherNotes', 'a')
    ],
    [('otherNotes', 'a')
    ]]
mode8Rverserules = [[('otherNotes', 'a')
    ],
    [('otherNotes', 'a')
    ],
    [('otherNotes', 'a')
    ]]
mode_patterns = {'1':mode1Rverserules,
  '2':mode2Rverserules,
  '3':mode3Rverserules,
  '4':mode4Rverserules,
  '5':mode5Rverserules,
  '6':mode6Rverserules,
  '7':mode7Rverserules,
  '8':mode8Rverserules,
}

def versify(hyphenatedText, mode):
  parts = hyphenatedText.strip().split("*")
  result = apply_pattern(parts[0], mode_patterns[mode][0])
  if len(parts) == 1:
    return result + ' (::)'
  else:
    for x in parts[1:-1]:
      result += ' (;) '
      result += apply_pattern(x, mode_patterns[mode][1])
    result += ' (;) '
    result += apply_pattern(parts[-1], mode_patterns[mode][2])
    return result + ' (::)'

def is_word(word):
  for x in vowels+accentedvowels+upvowels+upaccentedvowels:
    if x in word:
      return True
  return False

def has_accent(word):
  for x in accentedvowels+upaccentedvowels:
    if x in word:
      return True
  return False

def apply_pattern(hyphenatedText, pattern):
    structuredGABC = hyphenatedText.split(" ")
    structuredGABC = [word for word in structuredGABC if is_word(word)]
    structuredGABC = [[{'syllable':syllable, 'gabc':""} for syllable in word.split("-")] for word in structuredGABC]
    for word in structuredGABC:
      if len(word) == 1:
        word[0]['accent'] = 0
      if len(word) == 2:
        word[0]['accent'] = 1
        word[1]['accent'] = -1
      else:
        for syllable in word:
          if has_accent(syllable['syllable']):
            syllable['accent'] = 1
          else:
            syllable['accent'] = -1
    for (rule, value) in pattern:
      structuredGABC = apply_rule(structuredGABC, rule, value)
    gabc = [''.join([syllable['syllable']+'('+syllable['gabc']+')' for syllable in word]) for word in structuredGABC]
    gabc = ' '.join(gabc)
    return gabc

def apply_rule(structuredGABC, rule, value):
  flatStructuredGABC = [x for word in structuredGABC for x in word]
  if rule == "last":
    flatStructuredGABC[-1]['gabc'] = value
  elif rule == "2tolast":
    flatStructuredGABC[-2]['gabc'] = value
  elif rule == "3tolast":
    flatStructuredGABC[-3]['gabc'] = value
  elif rule == "4tolast":
    flatStructuredGABC[-4]['gabc'] = value
  elif rule == "5tolast":
    flatStructuredGABC[-5]['gabc'] = value
  elif rule == "lastAccent":
    if flatStructuredGABC[-2]['accent'] == 1:
      selected = flatStructuredGABC[-2]
    elif flatStructuredGABC[-3]['accent'] == 1:
      selected = flatStructuredGABC[-3]
    else:
      selected = flatStructuredGABC[-2]
    selected['gabc'] = value
  elif rule == "fillerOnLastAccent":
    if flatStructuredGABC[-2]['accent'] == 1:
      pass
    elif flatStructuredGABC[-3]['accent'] == 1:
      flatStructuredGABC[-3]['gabc'] = value
    else:
      pass
  elif rule == "fillerAfterLastAccent":
    if flatStructuredGABC[-2]['accent'] == 1:
      pass
    elif flatStructuredGABC[-3]['accent'] == 1:
      flatStructuredGABC[-2]['gabc'] = value
    else:
      pass
  elif rule == "1BeforeLastAccent":
    if flatStructuredGABC[-2]['accent'] == 1:
      selected = flatStructuredGABC[-3]
    elif flatStructuredGABC[-3]['accent'] == 1:
      selected = flatStructuredGABC[-4]
    else:
      selected = flatStructuredGABC[-3]
    selected['gabc'] = value
  elif rule == "2BeforeLastAccent":
    if flatStructuredGABC[-2]['accent'] == 1:
      selected = flatStructuredGABC[-4]
    elif flatStructuredGABC[-3]['accent'] == 1:
      selected = flatStructuredGABC[-5]
    else:
      selected = flatStructuredGABC[-4]
    selected['gabc'] = value
  elif rule == "3BeforeLastAccent":
    if flatStructuredGABC[-2]['accent'] == 1:
      selected = flatStructuredGABC[-5]
    elif flatStructuredGABC[-3]['accent'] == 1:
      selected = flatStructuredGABC[-6]
    else:
      selected = flatStructuredGABC[-5]
    selected['gabc'] = value
  elif rule == "firstTrueAccent":
    for syllable in flatStructuredGABC:
      if syllable['accent'] == 1:
        syllable['gabc'] = value
        break
  elif rule == "otherTrueAccents":
    for syllable in flatStructuredGABC:
      if syllable['accent'] == 1 and syllable['gabc'] == "":
        syllable['gabc'] = value
  elif rule == "otherNotes":
    for syllable in flatStructuredGABC:
      if syllable['gabc'] == "":
        syllable['gabc'] = value
  return structuredGABC
