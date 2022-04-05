from django import forms
from home.models import Source

class ProposalEditForm(forms.Form):
  mode = forms.ChoiceField(choices = [
    ('',''),
    ('1','1'),
    ('2','2'),
    ('2*','2*'),
    ('3','3'),
    ('4','4'),
    ('4*', '4*'),
    ('5','5'),
    ('6','6'),
    ('7','7'),
    ('8','8'),
    ('C','C'),
    ('D','D'),
    ('E','E'),
    ('P','T.pereg.'),
  ], required=False)
  diff = forms.ChoiceField(label='Differentia', choices = [
    ('',''),
    ('a','a'),
    ('a*','a*'),
    ('a2','a2'),
    ('a3','a3'),
    ('b','b'),
    ('c','c'),
    ('c2','c2'),
    ('d','d'),
    ('d-','d-'),
    ('d2','d2'),
    ('e','e'),
    ('f','f'),
    ('g','g'),
    ('g*','g*'),
    ('g2','g2'),
    ('g3','g3'),
    ('a','a'),
  ], required=False)
  gabc = forms.CharField(label='GABC code', widget=forms.Textarea(attrs={'rows':18}) )
  source = forms.ChoiceField(choices = [('','')] + [ (source.siglum, source.siglum) for source in Source.objects.all().order_by('siglum') ], required=False)
  sourcepage = forms.CharField(label='Source page', required=False)
  comment = forms.CharField(label='Summary of changes', required=True)

class CommentForm(forms.Form):
  comment = forms.CharField(label='Add comment:', widget=forms.Textarea(attrs={'rows':8}), required=True)
