from django import forms


class DataForm(forms.Form):
    filename = forms.FileField(max_length=200,widget=(forms.FileInput(attrs={'class':'form-control','placeholder':'Choose a file'})))