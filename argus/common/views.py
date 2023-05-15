from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.urls import reverse_lazy
from rest_framework import filters
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated

from common.forms import UserForm, CommonPasswordResetForm
from common.serializers import UserSerializer

# Create your views here.

def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = UserForm()
    return render(request, 'common/signup.html', {'form': form})


@method_decorator(require_POST, name='post')
class CommonLoginView(LoginView):
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember-me')
        if remember_me:
            # set session expiry to one week
            self.request.session.set_expiry(604800)
            self.request.session['remember_me'] = True
            self.response = super().form_valid(form)
            # set cookie expiry to one week
            self.response.set_cookie('remember_me', 'true', max_age=604800)
            return self.response
        else:
            # set session expiry to browser session
            self.request.session.set_expiry(0)
            self.request.session['remember_me'] = False
            self.response = super().form_valid(form)
            # delete the cookie if it exists
            self.response.delete_cookie('remember_me')
            return self.response


class CommonPasswordResetView(PasswordResetView):
    form_class = CommonPasswordResetForm
    template_name = 'common/password_reset_form.html'
    email_template_name = 'common/password_reset_email.html'
    success_url = reverse_lazy('common:password_reset_done')

    def form_valid(self, form):

        # Send the password reset email
        email = form.cleaned_data.get('email')
        domain = self.request.META['HTTP_HOST']
        protocol = 'https' if self.request.is_secure() else 'http'
        user = form.get_user(email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f'{protocol}://{domain}{reverse("common:password_reset_confirm", kwargs={"uidb64": uid, "token": token})}'

        subject = f'Password reset requested for {user.username}'
        from_email = 'noreply@argus.com'
        to_email = [email]

        # Load the HTML template
        html_content = render_to_string('common/password_reset_email.html', {
            'reset_link': reset_link,
            'uid': uid,
            'token': token,
            'domain': domain,
            'protocol': protocol,
        })

        # Construct the email message with plain text and HTML content
        text_content = f'Follow the link to reset your password: {reset_link}'
        msg = EmailMultiAlternatives(
            subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")

        # Send the email
        msg.send()

        return redirect(self.success_url)


class CommonPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'common/password_reset_confirm.html'
    success_url = reverse_lazy('common:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['uidb64'] = self.kwargs['uidb64']
        context['token'] = self.kwargs['token']
        return context
    

class RecipientsPagination(PageNumberPagination):
    page_size = 5

class RecipientsViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.order_by('username')
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    pagination_class = RecipientsPagination
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
