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
  
def remove_neumes_from_gabc_element(gabc_element):
  l = gabc_element.split('|')
  return '/'.join(l[::2]) # items 0, 2, 4... de l
  
def remove_rsigns_from_gabc_element(gabc_element):
  # this does what it says, however, it does not remove advancedly placed episemata like _[oh:h].
  # we will add support for those if needed.
  l = gabc_element.split('|')
  gabc = l[::2]
  nabc = l[1::2]
  ngabc = []
  for element in gabc:
    for x in ["'", "_0", "_1", "_", "."]:
      element = element.replace(x, '')
    ngabc.append(element)
  # merging ngabc and nabc is delicate, one must manage the case where the last gabc segment has no nabc
  if len(gabc) == len(nabc):
    return "|".join([x for y in zip(ngabc, nabc) for x in y])
  else: # this is the case where len(gabc) = len(nabc) + 1
    result_without_tail = "|".join([x for y in zip(ngabc, nabc) for x in y])
    if result_without_tail == "":
      return ngabc[0] # the only element in ngabc, in fact
    else:
      return result_without_tail + '|' + ngabc[-1]

vowels = ['a', 'e', 'i', 'o', 'u', 'y', 'æ', 'œ', 'ë']
accentedvowels = ['á', 'é', 'í', 'ó', 'ú', 'ý', 'ǽ']
upvowels = [x.upper() for x in vowels]
upaccentedvowels = [x.upper() for x in accentedvowels]

## available rules:
## rules counting back from the end:
# last, 2tolast, 3tolast, 4tolast, 5tolast
## rules around last accent
# lastAccent, fillerOnLastAccent, fillerAfterLastAccent
## rules counting back from last accent
# 1BeforeLastAccent, 2BeforeLastAccent, 3BeforeLastAccent
## rules counting from the beginning
# first, second, firstIfMoreThan7, secondIfMoreThan7
## rules around first accent
# firstTrueAccent, firstDactylUltimate, firstDactylPenultimate, firstSpondaicUltimate
## rules arount the first word
# firstWordLastSyllable, firstLongWordLastSyllable, firstSyllables, firstLongWordNextSyllable
## rules for filling the rest
# otherTrueAccents, otherNotes
## otherNotes is the recitation chord and must be given

mode1Rverserules = [[('firstLongWordLastSyllable', 'hg/hggof|clcl!pi', 'hg/hggof|clcl!pi'),
        ('firstLongWordNextSyllable', 'gh|pe', 'gh~|pe~'),
        ('firstSyllables', 'h|vi', 'h|vi'),
        ('last', 'h.|ta-', 'h.|ta-'),
        ('2tolast', 'ixh/iioh|////ta/pr-', 'ixh/iioh|////ta/pr-'),
        ('fillerOnLastAccent', 'h|ta', 'h|ta'),
        ('1BeforeLastAccent', 'gh|pe', 'gh~|pe~'),
        ('2BeforeLastAccent', 'gh|pe', 'gh~|pe~'),
        ('3BeforeLastAccent', 'hf|cllsc3', 'hf~|cl~'),
        ('otherNotes', 'g', 'g'), 
],
[       ('first', 'hf|cl', 'hf~|cl~'),
        ('second', 'gh|pe', 'g@h>|pe>'),
        ('last', 'h.|ta-', 'h.|ta-'),
        ('2tolast', 'ixh/iioh|////ta/pr-', 'ixh/iioh|////ta/pr-'),
        ('fillerOnLastAccent', 'h|ta', 'h|ta'),
        ('1BeforeLastAccent', 'gh|pe', 'gh~|pe~'),
        ('2BeforeLastAccent', 'gh|pe', 'gh~|pe~'),
        ('3BeforeLastAccent', 'hf|cllsc3', 'hf~|cl~'),
        ('otherTrueAccents', 'ixhi|pe', 'ixhi~|pe~'),
        ('otherNotes', 'h', 'h'),
],
[       ('last', 'gf..|cl-', 'gf..|cl-'),
        ('2tolast', 'hv_GF_Efwg_@hv|vi-su1sut2ql-vihj', 'hv_GF_Efwg_@h>|vi-su1sut2ql-vi>hj'),
        ('3tolast', 'ixf!gwhg/hih|////ql!clppt1tohh', 'ixf!gwhg/hih|////ql!clppt1tohh'),
        ('4tolast', 'hf|cllsc3', 'hf~|cl~'),
        ('5tolast', 'hg/hg|pflsc2', 'hg/hg~|pf~lsc2'),
        ('first', 'hf|cl', 'hf~|cl~'),
        ('second', 'gh|pe', 'g@h>|pe>'),
        ('otherTrueAccents', 'ixhi|pe', 'ixhi~|pe~'),
        ('otherNotes', 'h', 'h'),
]]
mode2Rverserules = [[('otherNotes', 'a', 'a')
    ],
    [('otherNotes', 'a', 'a')
    ],
    [('otherNotes', 'a', 'a')
    ]]
mode3Rverserules = [[('firstTrueAccent', 'ikjjs|tohhsthi', 'ikjjs|tohhsthi'),
        ('firstSyllables', 'i|ta', 'i|ta'),
        ('firstDactylPenultimate', 'h!iwji|qlhh!cl-hhppt1', 'h!iwji|qlhh!cl-hhppt1'), # todo version liquescente à établie par comparaison
        ('firstDactylUltimate', 'hhog|prhh', 'hhog|prhh'),
        ('firstSpondaicUltimate', 'h!iwji/hhog|ql!cl-ppt1prhh', 'h!iwji/hhog|ql!cl-ppt1prhh'),
        ('last', 'ji..|cl-hh', 'ji..|cl-hh'),
        ('2tolast', 'ikjjs|tohisthj', 'ikjjs|tohisthj'),
        ('fillerOnLastAccent', 'i|ta', 'i|ta'),
        ('1BeforeLastAccent', 'j|vihh', 'j|vihh'),
        ('2BeforeLastAccent', 'h|vi', 'h|vi'),
        ('3BeforeLastAccent', 'hg|cllsc3', 'hg~|cl~'),
        ('otherTrueAccents', 'hi|pe', 'hi~|pe~'),
        ('otherNotes', 'h|ta', 'h|ta')
    ],
    [('otherNotes', 'a', 'a')
    ],
    [   ('last', 'hg..|cl-', 'hg..|cl-'),
        ('2tolast', 'jiioh/iv_HGh|////clhh!pihhci-hhvihi', 'jiioh/iv_HGh|////clhh!pihhci-hhvihi'),
        ('3tolast', 'g_h!iwj|qlhhppt2', 'g_h!iwj|qlhhppt2'),
        ('4tolast', 'hg|cllsc3', 'hg~|cl~'),
        ('5tolast', 'ikjjvIH______/iwji|////toShivi-hjsut2qihk!cl-hk', 'ikjjvIH______/iwji|////toShivi-hjsut2qihk!cl-hk'),
        ('firstIfMoreThan7', 'ig|cllsc3', 'ig~|cl~'),
        ('secondIfMoreThan7', 'hi|pe', 'hi~|pe~'),
        ('otherTrueAccents', 'i@jo|vslsc2', 'ij~|pe~'),
        ('otherNotes', 'i|ta', 'i|ta'),
]]
mode4Rverserules = [[('otherNotes', 'a', 'a')
    ],
    [('otherNotes', 'a', 'a')
    ],
    [('otherNotes', 'a', 'a')
    ]]
mode5Rverserules = [[('otherNotes', 'a', 'a')
    ],
    [('otherNotes', 'a', 'a')
    ],
    [('otherNotes', 'a', 'a')
    ]]
mode6Rverserules = [[('otherNotes', 'a', 'a')
    ],
    [('otherNotes', 'a', 'a')
    ],
    [('otherNotes', 'a', 'a')
    ]]
mode7Rverserules = [[
        ('firstTrueAccent', 'i!jwk_JI|vihiql-hnsu2', 'i!jwk_J~I~|vihiql-hnsux1'), # les neumes pour la liq. sont à vérifier par comparaison
        ('firstDactylUltimate', 'h_i/hhog|peSpr', 'h_i/hhog~|peSvs>'),
        ('firstDactylPenultimate', 'hg|cllsc2', 'hg~|cl~'),
        ('firstSpondaicUltimate', 'h_i/hhog|peSpr', 'h_i/hhog~|peSvs>'),
        ('firstSyllables', 'i|ta', 'i|ta'),
        ('3BeforeLastAccent', 'ig|cllsc2', 'ig~|cl~'),
        ('2BeforeLastAccent', 'hi|pe', 'hi~|pe~'),
        ('1BeforeLastAccent', 'hi|pe', 'hi~|pe~'),
        ('fillerOnLastAccent', 'i|ta', 'i|ta'),
        ('last', 'ji..|cl-hh', 'ji..|cl-hh'),
        ('2tolast', 'i!jwkj__|qlhk!cl-hkppt1', 'i!jwkj__|qlhk!cl-hkppt1'),
        ('otherTrueAccents', 'hi|pe', 'hi~|pe~'),
        ('otherNotes', 'h|ta', 'h|ta')
    ],
    [('otherNotes', 'a', 'a')
    ],
    [   ('last', 'iv_HGhg..|//ci-cl-hg', 'iv_HGhg..|//ci-cl-hg'),
        ('2tolast', 'i_h!iwjij|////cl-hhqihi!pohi', 'i_h!iwjij|////cl-hhqihi!pohi'), # sancto n'a pas de liquescence indiquée, à voir aussi par comparaison
        ('3tolast', 'h!iwji/jkj|////qlhi!clhippt1lsc3', 'h!iwji/jkj|////qlhi!clhippt1lsc3'),
        ('4tolast', 'ih|cllsc3', 'ih|cllsc3'),
        ('5tolast', 'ijij_IH|////tr-1su2', 'ijij_I~H~|////tr-1sux1'),
        ('firstIfMoreThan7', 'h_i/hhog|peSpr', 'h_i/hhog~|peSvs>'),
        ('secondIfMoreThan7', 'hih|//to', 'hih|//to'),
        ('otherTrueAccents', 'ij|pe', 'ij~|pe~'),
        ('otherNotes', 'i|vi', 'i|vi'),
    ]]
mode8Rverserules = [[('otherNotes', 'a', 'a')
    ],
    [('otherNotes', 'a', 'a')
    ],
    [('otherNotes', 'a', 'a')
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

def versify(hyphenatedText, mode, rsigns=True, neumes=True):
  parts = hyphenatedText.strip().split("*")
  result = apply_pattern(parts[0], mode_patterns[mode][0], rsigns, neumes)
  if len(parts) == 1:
    return result + ' (::)'
  else:
    for x in parts[1:-1]:
      result += ' (;) '
      result += apply_pattern(x, mode_patterns[mode][1], rsigns, neumes)
    result += ' (;) '
    result += apply_pattern(parts[-1], mode_patterns[mode][2], rsigns, neumes)
    return result + ' (::)'

def is_word(word):
  """takes a string and checks if it has a vowel, otherwise it will be discarded, e.g. <sp>*</sp>"""
  for x in vowels+accentedvowels+upvowels+upaccentedvowels:
    if x in word:
      return True
  return False

def has_accent(word):
  """takes a string (normally a syllable) and checks if it has an accented vowel, making it the accented syllable in its word"""
  for x in accentedvowels+upaccentedvowels:
    if x in word:
      return True
  return False

def isSpondaic(word):
  """takes a structuredGABC element, which is a list of {'syllable':<str>, 'gabc':<str>, 'accent':<int>} forming a word, determines its termination nature"""
  if len(word) < 2:
    return False
  return (word[-2]['accent'] == 1)

def apply_pattern(hyphenatedText, pattern, rsigns, neumes):
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
    for (rule, value, liqvalue) in pattern:
      structuredGABC = apply_rule(structuredGABC, rule, value, liqvalue, rsigns, neumes)
    gabc = [''.join([syllable['syllable']+'('+syllable['gabc']+')' for syllable in word]) for word in structuredGABC]
    gabc = ' '.join(gabc)
    return gabc

def select_value(text, value, liqvalue, rsigns, neumes):
  if not neumes :
    value = remove_neumes_from_gabc_element(value)
    liqvalue = remove_neumes_from_gabc_element(liqvalue)
  if not rsigns :
    value = remove_rsigns_from_gabc_element(value)
    liqvalue = remove_rsigns_from_gabc_element(liqvalue)
  if text[-1] in ['m', 'n', 'l']:
    return liqvalue
  else:
    return value

def apply_rule(structuredGABC, rule, value, liqvalue, rsigns, neumes):
  flatStructuredGABC = [x for word in structuredGABC for x in word]
  if rule == "last":
  # this rule defines the last syllable of the phrase
    flatStructuredGABC[-1]['gabc'] = select_value(flatStructuredGABC[-1]['syllable'], value, liqvalue, rsigns, neumes)
  elif rule == "2tolast":
  # this rule defines the second to last syllable of the phrase
    flatStructuredGABC[-2]['gabc'] = select_value(flatStructuredGABC[-2]['syllable'], value, liqvalue, rsigns, neumes)
  elif rule == "3tolast":
  # this rule defines the third to last syllable of the phrase
    flatStructuredGABC[-3]['gabc'] = select_value(flatStructuredGABC[-3]['syllable'], value, liqvalue, rsigns, neumes)
  elif rule == "4tolast":
  # this rule defines the fourth to last syllable of the phrase
    flatStructuredGABC[-4]['gabc'] = select_value(flatStructuredGABC[-4]['syllable'], value, liqvalue, rsigns, neumes)
  elif rule == "5tolast":
  # this rule defines the fifth to last syllable of the phrase
    flatStructuredGABC[-5]['gabc'] = select_value(flatStructuredGABC[-5]['syllable'], value, liqvalue, rsigns, neumes)
  elif rule == "lastAccent":
  # this rule defines the last accented syllable by the rules of psalmody, which can be a monosyllable
    if flatStructuredGABC[-2]['accent'] == 1:
      selected = flatStructuredGABC[-2]
    elif flatStructuredGABC[-3]['accent'] == 1:
      selected = flatStructuredGABC[-3]
    else:
      selected = flatStructuredGABC[-2]
    selected['gabc'] = select_value(selected['syllable'], value, liqvalue, rsigns, neumes)
  elif rule == "fillerOnLastAccent":
  # if the last accented syllable is the antepenultimate, this rule defines it
    if flatStructuredGABC[-2]['accent'] == 1:
      pass
    elif flatStructuredGABC[-3]['accent'] == 1:
      flatStructuredGABC[-3]['gabc'] = select_value(flatStructuredGABC[-3]['syllable'], value, liqvalue, rsigns, neumes)
    else:
      pass
  elif rule == "fillerAfterLastAccent":
  # if the last accented syllable is the antepenultimate, this rule defines the syllable following it
    if flatStructuredGABC[-2]['accent'] == 1:
      pass
    elif flatStructuredGABC[-3]['accent'] == 1:
      flatStructuredGABC[-2]['gabc'] = select_value(flatStructuredGABC[-2]['syllable'], value, liqvalue, rsigns, neumes)
    else:
      pass
  elif rule == "1BeforeLastAccent":
  # this rule defines the syllable before the last accented syllable by the rules of psalmody
    if flatStructuredGABC[-2]['accent'] == 1:
      selected = flatStructuredGABC[-3]
    elif flatStructuredGABC[-3]['accent'] == 1:
      selected = flatStructuredGABC[-4]
    else:
      selected = flatStructuredGABC[-3]
    selected['gabc'] = select_value(selected['syllable'], value, liqvalue, rsigns, neumes)
  elif rule == "2BeforeLastAccent":
  # this rule defines the second syllable before the last accented syllable by the rules of psalmody
    if flatStructuredGABC[-2]['accent'] == 1:
      selected = flatStructuredGABC[-4]
    elif flatStructuredGABC[-3]['accent'] == 1:
      selected = flatStructuredGABC[-5]
    else:
      selected = flatStructuredGABC[-4]
    selected['gabc'] = select_value(selected['syllable'], value, liqvalue, rsigns, neumes)
  elif rule == "3BeforeLastAccent":
  # this rule defines the third syllable before the last accented syllable by the rules of psalmody
    if flatStructuredGABC[-2]['accent'] == 1:
      selected = flatStructuredGABC[-5]
    elif flatStructuredGABC[-3]['accent'] == 1:
      selected = flatStructuredGABC[-6]
    else:
      selected = flatStructuredGABC[-5]
    selected['gabc'] = select_value(selected['syllable'], value, liqvalue, rsigns, neumes)
  elif rule == "firstTrueAccent":
  # this rule defines the first syllable that is actually accented (i.e. from a two-syllable word or longer)
    for syllable in flatStructuredGABC:
      if syllable['accent'] == 1:
        syllable['gabc'] = select_value(syllable['syllable'], value, liqvalue, rsigns, neumes)
        break
  elif rule == "firstWordLastSyllable":
  # this rule defines the last syllable of the first word, which can be a monosyllable and therefore the first syllable of the phrase
    structuredGABC[0][-1]['gabc'] = select_value(structuredGABC[0][-1]['syllable'], value, liqvalue, rsigns, neumes)
  elif rule in ["firstLongWordLastSyllable", "firstLongWordNextSyllable"]:
  # this rule defines the last syllable of the first word, but avoids it being the first syllable of the phrase,
  # and if the phrase starts with three monosyllables, it will define the third.
    if len(structuredGABC[0]) == 1:
      if len(structuredGABC[1]) == 1:
        if len(structuredGABC[2]) == 1:
          if rule == "firstLongWordLastSyllable":
            structuredGABC[2][0]['gabc'] = select_value(structuredGABC[2][0]['syllable'], value, liqvalue, rsigns, neumes)
          elif rule == "firstLongWordNextSyllable":
            structuredGABC[3][0]['gabc'] = select_value(structuredGABC[3][0]['syllable'], value, liqvalue, rsigns, neumes)
        else:
          if rule == "firstLongWordLastSyllable":
            structuredGABC[1][0]['gabc'] = select_value(structuredGABC[1][0]['syllable'], value, liqvalue, rsigns, neumes)
          elif rule == "firstLongWordNextSyllable":
            structuredGABC[2][0]['gabc'] = select_value(structuredGABC[2][0]['syllable'], value, liqvalue, rsigns, neumes)
      else:
        if rule == "firstLongWordLastSyllable":
          structuredGABC[1][-1]['gabc'] = select_value(structuredGABC[1][-1]['syllable'], value, liqvalue, rsigns, neumes)
        elif rule == "firstLongWordNextSyllable":
          structuredGABC[2][0]['gabc'] = select_value(structuredGABC[2][0]['syllable'], value, liqvalue, rsigns, neumes)
    else:
      if rule == "firstLongWordLastSyllable":
        structuredGABC[0][-1]['gabc'] = select_value(structuredGABC[0][-1]['syllable'], value, liqvalue, rsigns, neumes)
      elif rule == "firstLongWordNextSyllable":
        structuredGABC[1][0]['gabc'] = select_value(structuredGABC[1][0]['syllable'], value, liqvalue, rsigns, neumes)
  elif rule == "firstSyllables":
  # this rule defines all the syllables up to the first one defined by a previous rule
    for syllable in flatStructuredGABC:
      if syllable['gabc'] == '':
        syllable['gabc'] = select_value(syllable['syllable'], value, liqvalue, rsigns, neumes)
      else:
        break
  elif rule == "otherTrueAccents":
  # this rule defines all syllables that are actually accented (i.e. from a two-syllable word or longer) that are not already defined
    for syllable in flatStructuredGABC:
      if syllable['accent'] == 1 and syllable['gabc'] == "":
        syllable['gabc'] = select_value(syllable['syllable'], value, liqvalue, rsigns, neumes)
  elif rule == "otherNotes":
  # this rule defines all syllables that are not already defined
    for syllable in flatStructuredGABC:
      if syllable['gabc'] == "":
        syllable['gabc'] = select_value(syllable['syllable'], value, liqvalue, rsigns, neumes)
  elif rule == "first":
  # this rule defines the first syllable
    flatStructuredGABC[0]['gabc'] = select_value(flatStructuredGABC[0]['syllable'], value, liqvalue, rsigns, neumes)
  elif rule == "firstIfMoreThan7":
  # this rule defines the first syllable only if there are going to be filler syllables between it and the 5-syllable ending
    if len(flatStructuredGABC) > 7:
      flatStructuredGABC[0]['gabc'] = select_value(flatStructuredGABC[0]['syllable'], value, liqvalue, rsigns, neumes)
  elif rule == "second":
  # this rule defines the second syllable
    flatStructuredGABC[1]['gabc'] = select_value(flatStructuredGABC[1]['syllable'], value, liqvalue, rsigns, neumes)
  elif rule == "secondIfMoreThan7":
  # this rule defines the second syllable
    if len(flatStructuredGABC) > 7:
      flatStructuredGABC[1]['gabc'] = select_value(flatStructuredGABC[1]['syllable'], value, liqvalue, rsigns, neumes)
  elif rule in ["firstDactylUltimate", "firstDactylPenultimate", "firstSpondaicUltimate"]:
    for word in structuredGABC:
      if len(word) == 1:
        pass
      else: # word is either dactilyic or spondaic
        if isSpondaic(word):
          if rule == "firstSpondaicUltimate":
            word[-1]['gabc'] = select_value(word[-1]['syllable'], value, liqvalue, rsigns, neumes)
          else:
            pass
        else:
          if rule == "firstDactylUltimate":
            word[-1]['gabc'] = select_value(word[-1]['syllable'], value, liqvalue, rsigns, neumes)
          elif rule == "firstDactylPenultimate":
            word[-2]['gabc'] = select_value(word[-2]['syllable'], value, liqvalue, rsigns, neumes)
          else:
            pass
        break
  return structuredGABC
