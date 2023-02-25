from django import forms
from monitoring.models import Assets

class AssetsForm(forms.ModelForm):
    class Meta:
        model = Assets
        fields = ['user', 'name', 'access_type', 'ip', 'port', 'username', 'password', 'ssh_key']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
        }
        labels = {
            'name': '이름',
        }
