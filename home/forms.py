from django import forms

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
  diff = forms.ChoiceField(choices = [
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
