from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request

from monitoring.swagger_schema import *

import json

class BulkDeleteMixin:
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['ids[]'],
            properties=delete_bulk_api_properties,
        )
    )
    @action(detail=False, methods=['delete'], url_path='delete_bulk')
    def delete_bulk(self, request: Request) -> Response:
        ids = [int(i) for i in request.data.getlist('ids[]')]
        if request.user.is_superuser:
            deleted_ids = set(self.queryset.filter(id__in=ids).values_list('id', flat=True))
            self.queryset.filter(id__in=ids).delete()
        else:
            deleted_ids = set(self.queryset.filter(id__in=ids, author=request.user).values_list('id', flat=True))
            self.queryset.filter(id__in=ids, author=request.user).delete()
        non_deleted_ids = list(set(ids) - deleted_ids)
        if non_deleted_ids:
            return Response({
                "deleted_ids": deleted_ids,
                "non_deleted_ids": non_deleted_ids,
                "detail": "Some or all of the requested items could not be deleted."},
                status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
