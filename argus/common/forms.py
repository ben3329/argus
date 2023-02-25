from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.utils.translation import gettext as _


class UserForm(UserCreationForm):
    email = forms.EmailField(label="이메일")

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "email")


class CommonPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )

    def get_user(self, email):
        """
        Given an email, return matching user (or None).
        """
        UserModel = User
        try:
            return UserModel.objects.get(email__iexact=email)
        except UserModel.DoesNotExist:
            return None

    def clean_email(self):
        email = self.cleaned_data['email']
        self.user = self.get_user(email)
        if self.user is None:
            raise forms.ValidationError(
                _("This email address is not associated with any user account."))
        return email
