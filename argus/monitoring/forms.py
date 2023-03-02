from django import forms
from monitoring.models import Asset

class AssetsForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['user', 'name', 'access_type', 'ip', 'port', 'username', 'password', 'ssh_key']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
        }
        labels = {
            'name': '이름',
        }
