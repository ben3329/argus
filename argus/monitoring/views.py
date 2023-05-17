from rest_framework import mixins, status, filters
from rest_framework.viewsets import GenericViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import action
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from monitoring.serializers import *
from monitoring.models import *
from monitoring.swagger_schema import *
from monitoring.permissions import *
from monitoring.mixins import *
from monitoring.choices import *

import requests
import logging
from copy import deepcopy
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
                   BulkDeleteMixin,
                   GenericViewSet):
    queryset = Asset.objects.all()
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['author', 'name', 'ip', 'port', 'asset_type', 'access_credential','create_date']
    pagination_class = Pagination
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated, IsAuthor, HasAddPermissionWithPost]
    
    def get_serializer_class(self):
        match self.action:
            case 'list_simple':
                return AssetSerializerSimple 
            case _:
                return AssetViewSetSerializer

    @swagger_auto_schema(
        manual_parameters=[page_param, ordering_param],
        responses=asset_list_api_response)
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
    def create(self, request: Request, *args, **kwargs) -> Response:
        data = deepcopy(request.data)
        data['author'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=asset_create_api_required_properties,
            properties=asset_create_api_properties,
        ),
        responses=asset_create_api_response
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

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

    @swagger_auto_schema(responses=asset_simple_api_response)
    @action(detail=False, methods=['get'], url_path='simple')
    def list_simple(self, request: Request) -> Response:
        # pagination 없이 목록 전부 일부 필드만 가져옴
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AccessCredentialViewSet(mixins.CreateModelMixin,
                              mixins.ListModelMixin,
                              BulkDeleteMixin,
                              GenericViewSet):
    queryset = AccessCredential.objects.all()
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['author', 'name', 'access_type', 'create_date']
    pagination_class = Pagination
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated, IsAuthor, HasAddPermissionWithPost]

    def get_serializer_class(self):
        match self.action:
            case 'list_simple':
                return AccessCredentialSerializerSimple
            case _:
                return AccessCredentialViewSetSerializer

    @swagger_auto_schema(
        manual_parameters=[page_param, ordering_param],
        responses=access_credential_list_api_response)
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
    def create(self, request: Request, *args, **kwargs) -> Response:
        data = deepcopy(request.data)
        data['author'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(responses=access_credential_simple_api_response)
    @action(detail=False, methods=['get'], url_path='simple')
    def list_simple(self, request: Request) -> Response:
        # pagination 없이 목록 전부 일부 필드만 가져옴
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ScriptViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    BulkDeleteMixin,
                    GenericViewSet):
    queryset = UserDefinedScript.objects.all()
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['author', 'name', 'language', 'output_type', 'create_date', 'update_date']
    pagination_class = Pagination
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated, IsAuthor, HasAddPermissionWithPost]

    def get_serializer_class(self):
        match self.action:
            case 'list_simple':
                return UserDefinedScriptSerializerSimple
            case _:
                return UserDefinedScriptViewSetSerializer

    @swagger_auto_schema(
        manual_parameters=[page_param, ordering_param],
        responses=script_list_api_response)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(responses=script_retrieve_api_response)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=script_create_api_required_properties,
            properties=script_create_api_properties,
        ),
        responses=script_create_api_response
    )
    def create(self, request: Request, *args, **kwargs) -> Response:
        data = deepcopy(request.data)
        data['author'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=script_create_api_required_properties,
            properties=script_create_api_properties,
        ),
        responses=script_create_api_response
    )
    def update(self, request: Request, *args, **kwargs) -> Response:
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=script_create_api_required_properties,
            properties=script_create_api_properties,
        ),
        responses=script_create_api_response
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(responses=script_simple_api_response)
    @action(detail=False, methods=['get'], url_path='simple')
    def list_simple(self, request: Request) -> Response:
        # pagination 없이 목록 전부 일부 필드만 가져옴
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class MonitorViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     BulkDeleteMixin,
                     GenericViewSet):
    queryset = Monitor.objects.all()
    serializer_class = MonitorViewSetSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['name', 'author', 'create_date']
    pagination_class = Pagination
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated, IsAuthor, HasAddPermissionWithPost]

    @swagger_auto_schema(
        manual_parameters=[page_param, ordering_param],
        responses=script_list_api_response)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(responses=script_retrieve_api_response)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=script_create_api_required_properties,
            properties=script_create_api_properties,
        ),
        responses=script_create_api_response
    )
    def create(self, request: Request, *args, **kwargs) -> Response:
        data = deepcopy(request.data)
        data['author'] = request.user.id
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
    params = {'page': page_number, 'ordering': '-create_date'}
    api_url = 'http://localhost:8080' + reverse('monitoring:asset-list')
    session = authorize_api(request)
    response = session.get(api_url, params=params)

    data = response.json()
    if response.status_code == status.HTTP_200_OK:
        context = {'user': request.user, 'create_perm': request.user.has_perm('monitoring.add_asset'),
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
    params = {'page': page_number, 'ordering': '-create_date'}
    api_url = 'http://localhost:8080' + \
        reverse('monitoring:accesscredential-list')
    session = authorize_api(request)
    response = session.get(api_url, params=params)

    data = response.json()
    if response.status_code == status.HTTP_200_OK:
        context = {'user': request.user, 'create_perm': request.user.has_perm('monitoring.add_accesscredential'),
                   'data': data, 'current': int(page_number)}
        return render(request, 'monitoring/access_credential.html', context)
    else:
        return HttpResponseBadRequest(data['detail'])


@login_required
def script(request):
    page_number = request.GET.get('page', 1)
    params = {'page': page_number, 'ordering': '-update_date'}
    api_url = 'http://localhost:8080' + reverse('monitoring:script-list')
    session = authorize_api(request)
    response = session.get(api_url, params=params)

    data = response.json()
    if response.status_code == status.HTTP_200_OK:
        context = {'user': request.user, 'create_perm': request.user.has_perm('monitoring.add_script'),
                   'data': data, 'current': int(page_number)}
        return render(request, 'monitoring/script.html', context)
    else:
        return HttpResponseBadRequest(data['detail'])

def get_scrape_choices() -> list:
    result = []
    for category in ScrapeCategoryChoices.choices:
        match category:
            case 'linux_system_memory', ref:
                fields = json.dumps(LinuxSystemMemoryFieldsChoices.names)
                parameters = '[]'
            case _:
                fields = '[]'
                parameters = '[]'
        result.append(list(category) + [fields, parameters])
    return result
        

@login_required
def monitor(request):
    page_number = request.GET.get('page', 1)
    params = {'page': page_number, 'ordering': '-create_date'}
    api_url = 'http://localhost:8080' + reverse('monitoring:monitor-list')
    session = authorize_api(request)
    response = session.get(api_url, params=params)

    data = response.json()
    if response.status_code == status.HTTP_200_OK:
        context = {'user': request.user, 'create_perm': request.user.has_perm('monitoring.add_monitor'),
                   'data': data, 'current': int(page_number),
                   'scrape_choices': get_scrape_choices(), 'report_list': ReportListChoices.choices}
        return render(request, 'monitoring/monitor.html', context)
    else:
        return HttpResponseBadRequest(data['detail'])

@login_required
def config(request):
    context = {'user': request.user}
    return render(request, 'monitoring/config.html', context)
