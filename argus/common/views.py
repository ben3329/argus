from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from common.forms import UserForm
from django.contrib.auth.views import LoginView
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator


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
    return render(request, 'common/signup.html', {'form':form})


@method_decorator(require_POST, name='post')
class CommonLoginView(LoginView):
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember-me')
        if remember_me:
            self.request.session.set_expiry(604800) # set session expiry to one week
            self.request.session['remember_me'] = True
            self.response = super().form_valid(form)
            self.response.set_cookie('remember_me', 'true', max_age=604800) # set cookie expiry to one week
            return self.response
        else:
            self.request.session.set_expiry(0) # set session expiry to browser session
            self.request.session['remember_me'] = False
            self.response = super().form_valid(form)
            self.response.delete_cookie('remember_me') # delete the cookie if it exists
            return self.response
