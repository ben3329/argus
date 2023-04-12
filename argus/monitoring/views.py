from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import action
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q, Case, When

from .engine import *
from .serializers import *
from .models import *
from .api_params import *

import requests
import logging
from copy import deepcopy
from functools import partial
logger = logging.getLogger(__name__)


class Pagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'total_pages': self.page.paginator.num_pages,
            'total_items': self.page.paginator.count,
            'results': data
        })

class AssetViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.UpdateModelMixin,
                   GenericViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    pagination_class = Pagination
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                queryset = self.queryset.order_by('-create_date')
            else:
                queryset = self.queryset.filter(user=user).order_by('-create_date')
        else:
            queryset = Asset.objects.none()
        return queryset
    
    @swagger_auto_schema(responses=asset_list_api_response)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=asset_create_api_required_properties,
            properties=asset_create_api_properties,
        ),
        responses=asset_create_api_response
    )
    def create(self, request:Request, *args, **kwargs) -> Response:
        data = deepcopy(request.data)
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['ids[]'],
            properties=delete_bulk_api_properties,
        )
    )
    @action(detail=False, methods=['delete'], url_path='delete_bulk')
    def delete_bulk(self, request:Request) -> Response:
        ids = request.data.getlist('ids[]')
        if request.user.is_superuser:
            self.queryset.filter(id__in=ids).delete()
        else:
            self.queryset.filter(id__in=ids, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=asset_create_api_required_properties,
            properties=asset_create_api_properties,
        ),
        responses=asset_create_api_response
    )
    def update(self, request:Request, *args, **kwargs) -> Response:
        data = deepcopy(request.data)
        data['user'] = request.user.id

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=asset_create_api_required_properties,
            properties=asset_create_api_properties,
        ),
        responses=asset_create_api_response
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    


class AccessCredentialViewSet(mixins.CreateModelMixin,
                              mixins.ListModelMixin,
                              GenericViewSet):
    queryset = AccessCredential.objects.all()
    serializer_class = AccessCredentialSerializer
    pagination_class = Pagination
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(
            user=user).order_by('-create_date')
        return queryset
    
    @swagger_auto_schema(responses=access_credential_list_api_response)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=access_credential_create_api_required_properties,
            properties=access_credential_create_api_properties,
        ),
        responses=access_credential_create_api_response
    )
    def create(self, request:Request, *args, **kwargs) -> Response:
        data = deepcopy(request.data)
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['ids[]'],
            properties=delete_bulk_api_properties,
        )
    )
    @action(detail=False, methods=['delete'], url_path='delete_bulk')
    def delete_bulk(self, request:Request) -> Response:
        ids = request.data.getlist('ids[]')
        self.queryset.filter(id__in=ids, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(responses=access_credential_simple_api_response)
    @action(detail=False, methods=['get'], url_path='simple')
    def list_simple(self, request:Request) -> Response:
        # pagination 없이 목록 전부 일부 필드만 가져옴
        user = request.user
        access_credentials = self.queryset.filter(user=user)
        serializer = AccessCredentialSerializerSimple(access_credentials, many=True)
        return Response(serializer.data)

class ScriptViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    GenericViewSet):
    queryset = Script.objects.all()
    pagination_class = Pagination
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        match self.action:
            case 'list':
                return ScriptSerializer
            case 'create':
                return ScriptCreateSerializer
            case _:
                return None

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(
            Q(user=user) | Q(authority=AuthorityChoices.public)).order_by(
                Case(When(user=user, then=0), default=1), 'user', '-update_date'
            )
        return queryset
    
    @swagger_auto_schema(responses=script_list_api_response)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request:Request, *args, **kwargs) -> Response:
        data = deepcopy(request.data)
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        

def authorize_api(request: HttpRequest) -> requests.Session:
    user = request.user
    token = user.auth_token.key
    session = requests.Session()
    session.headers.update({'Authorization': f'Token {token}'})
    return session

@login_required
def dashboard(request):
    context = {'user': request.user}
    return render(request, 'monitoring/dashboard.html', context)

@login_required
def asset(request: HttpRequest) -> HttpResponse:
    page_number = request.GET.get('page', 1)
    params = {'page': page_number}
    api_url = 'http://localhost:8080' + reverse('monitoring:asset-list')
    session = authorize_api(request)
    response = session.get(api_url, params=params)

    data = response.json()
    if response.status_code == status.HTTP_200_OK:
        context = {'user': request.user,
                   'data': data, 'current': int(page_number)}
        return render(request, 'monitoring/asset.html', context)
    else:
        return HttpResponseBadRequest(data['detail'])


@login_required
def monitor(request):
    context = {'user': request.user}
    return render(request, 'monitoring/monitor.html', context)


@login_required
def access_credential(request: HttpRequest) -> HttpResponse:
    page_number = request.GET.get('page', 1)
    params = {'page': page_number}
    api_url = 'http://localhost:8080' + reverse('monitoring:accesscredential-list')
    session = authorize_api(request)
    response = session.get(api_url, params=params)

    data = response.json()
    if response.status_code == status.HTTP_200_OK:
        context = {'user': request.user,
                   'data': data, 'current': int(page_number)}
        return render(request, 'monitoring/access_credential.html', context)
    else:
        return HttpResponseBadRequest(data['detail'])


@login_required
def script(request):
    context = {'user': request.user}
    return render(request, 'monitoring/script.html', context)


@login_required
def config(request):
    context = {'user': request.user}
    return render(request, 'monitoring/config.html', context)


@login_required
def detail(request, asset_id):
    asset = get_object_or_404(Asset, pk=asset_id)
    context = {'asset': asset, 'username': request.user.username}
    return render(request, 'monitoring/asset_detail.html', context)


def monitoring_create(request, asset_id):
    asset = get_object_or_404(Asset, pk=asset_id)
    post_data = request.POST
    asset.monitoring_set.create(
        user=asset.user,
        name=post_data.get('name'),
        target_system=post_data.get('target_system')
    )
    return redirect('monitoring:detail', asset_id=asset.id)
