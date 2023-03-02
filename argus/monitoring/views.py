from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from django.shortcuts import render, get_object_or_404, redirect
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework import permissions
# from drf_yasg.utils import swagger_auto_schema
# from rest_framework.renderers import JSONRenderer
from django.utils import dateparse
from .engine import *
from .serializers import *
from .models import Asset, Secret, ScrapingCode, Monitor
from .forms import AssetsForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def index(request):
    pass
    # page = request.GET.get('page', '1')
    # asset_list = Asset.objects.all()
    # paginator = Paginator(asset_list, 10)
    # page_obj = paginator.get_page(page)
    # context = {'asset_list': page_obj, 'username':request.user.username}
    # return render(request, 'monitoring/asset_list.html', context)

@login_required
def dashboard(request):
    context = {'username':request.user.username}
    return render(request, 'monitoring/dashboard.html', context)

@login_required
def asset(request):
    context = {'username':request.user.username}
    return render(request, 'monitoring/asset.html', context)

@login_required
def monitor(request):
    context = {'username':request.user.username}
    return render(request, 'monitoring/monitor.html', context)

@login_required
def secret(request):
    context = {'username':request.user.username}
    return render(request, 'monitoring/secret.html', context)

@login_required
def scraping_code(request):
    context = {'username':request.user.username}
    return render(request, 'monitoring/scraping_code.html', context)

@login_required
def config(request):
    context = {'username':request.user.username}
    return render(request, 'monitoring/config.html', context)

@login_required
def detail(request, asset_id):
    asset = get_object_or_404(Asset, pk=asset_id)
    context = {'asset':asset, 'username':request.user.username}
    return render(request, 'monitoring/asset_detail.html', context)

def monitoring_create(request, asset_id):
    asset = get_object_or_404(Asset, pk = asset_id)
    post_data = request.POST
    asset.monitoring_set.create(
        user=asset.user,
        name=post_data.get('name'),
        target_system=post_data.get('target_system')
    )
    return redirect('monitoring:detail', asset_id = asset.id)

def asset_create(request):
    form = AssetsForm()
    if request.method == 'POST':
        form = AssetsForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            return redirect('monitoring:index')
    else:
        form = AssetsForm()
    context = {'form': form}
    return render(request, 'monitoring/asset_form.html', context)

# class AssetViewSet(ModelViewSet):
#     queryset = Asset.objects.all()
#     serializer_class = AssetsSerializer


# class SecretsViewSet(ModelViewSet):
#     queryset = Secret.objects.all()
#     serializer_class = SecretsSerializer


# class ScrapingCodesViewSet(ModelViewSet):
#     queryset = ScrapingCode.objects.all()
#     serializer_class = ScrapingCodesSerializer


# class MonitoringViewSet(ModelViewSet):
#     queryset = Monitor.objects.all()
#     serializer_class = MonitoringSerializer
