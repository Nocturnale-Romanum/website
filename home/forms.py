from django import forms
from home.models import *

mode_list = [
    ('',"(none)"),
    ('1',"1"),
    ('2',"2"),
    ('3',"3"),
    ('4',"4"),
    ('5',"5"),
    ('6',"6"),
    ('7',"7"),
    ('8',"8"),
    ('C',"C"),
    ('D',"D"),
    ('E',"E"),
    ('P',"T.pereg."),
    ('irreg.', "irreg."),
  ]

diff_list = [
    ('',"(none)"),
    ('a',"a"),
    ('a*',"a*"),
    ('a2',"a2"),
    ('a3',"a3"),
    ('b',"b"),
    ('c',"c"),
    ('c2',"c2"),
    ('d','d'),
    ('d-','d-'),
    ('d2','d2'),
    ('e','e'),
    ('f','f'),
    ('f2', 'f2'),
    ('f3', 'f3'),
    ('g','g'),
    ('g*','g*'),
    ('g2','g2'),
    ('g3','g3'),
    ('a','a'),
  ]

class ProposalEditForm(forms.Form):
  mode = forms.ChoiceField(choices = mode_list, required=False)
  diff = forms.ChoiceField(label='Differentia', choices = diff_list, required=False)
  nabcstatus = forms.ChoiceField(label="NABC status", choices = [
    ('none', "No NABC"),
    ('auth', "From a manuscript"),
    ('arfv', "R. from a manuscript, V. synthetic"),
    ('fake', "Synthetic/Contrafactum"),
  ], required=False)
  gabc = forms.CharField(label='GABC code', widget=forms.Textarea(attrs={'rows':18}) )
  source = forms.ChoiceField(choices = [('','')] + [ (source.siglum, source.siglum) for source in Source.objects.all().order_by('siglum') ], required=False)
  sourcepage = forms.CharField(label='Source page', required=False)
  comment = forms.CharField(label='Summary of changes', required=True)

class CommentForm(forms.Form):
  comment = forms.CharField(label='Add comment:', widget=forms.Textarea(attrs={'rows':8}), required=True)

class CommentEditForm(forms.Form):
  comment = forms.CharField(label='Edit comment:', widget=forms.Textarea(attrs={'rows':8}), required=True)

class TableForm(forms.Form):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Add the `multiple` attribute to allow selecting multiple files
    self.fields["tables"].widget.attrs.update({"multiple": "true"})
  tables = forms.FileField(label="Upload comparative tables: images, PDF or ZIP, max. size 50 Mo, name should only contain letters and underscores.", max_length=100, required=False)

class VersifyForm(forms.Form):
  mode = forms.ChoiceField(choices = [
    ('1','1'),
    ('2','2'),
    ('3','3'),
    ('4','4'),
    ('5','5'),
    ('6','6'),
    ('7','7'),
    ('8','8'),
  ], required=True, label='Mode')
  rsigns = forms.BooleanField(label='Use rhythmic signs', initial = True, required=False)
  neumes = forms.BooleanField(label='Use sangallian neumes', initial = True, required=False)
  input = forms.CharField(label='Text to versify', widget=forms.Textarea(attrs={'rows':8}), required=False)

class TransposeForm(forms.Form):
  gabc = forms.CharField(label='GABC without text or NABC', widget=forms.Textarea(attrs={'rows':8}), required=False)
  offset = forms.ChoiceField(label='Offset', choices = [
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (-1, '-1'),
    (-2, '-2'),
    (-3, '-3'),
    (-4, '-4'),
  ], required=True)

class RemoveNabcHeightsForm(forms.Form):
  nabc = forms.CharField(label='NABC without text or GABC', widget=forms.Textarea(attrs={'rows':8}), required=False)

class RemoveRsignsForm(forms.Form):
  gabc = forms.CharField(label='Full GABC (with text, with or without NABC)', widget=forms.Textarea(attrs={'rows':8}), required=False)

class GABCSearchForm(forms.Form):
  search_text = forms.CharField(label="GABC to be searched", required=True)
  scope_choices = [
    ('u', "Search my contributions"),
    ('a', "Search all contributions"),
    ('s', "Search contributions from those users:"),
  ]
  search_scope = forms.ChoiceField(widget=forms.RadioSelect, choices=scope_choices)
  search_mode = forms.ChoiceField(label="Search only pieces of this mode:", choices = [('all', "all")] + mode_list)
  search_officepart = forms.ChoiceField(label="Search only pieces of this type:", choices = [('all', "all"), ('re', "Resp."), ('an', "Ant."), ('in', "Inv."), ('hy', "Hy."), ('ps', "Ps."), ('or', "Toni")])
  search_contributors = forms.ChoiceField(label="", widget=forms.SelectMultiple, choices=[(u.id, u.username) for u in User.objects.all() if u.proposals.all()], required=False)
