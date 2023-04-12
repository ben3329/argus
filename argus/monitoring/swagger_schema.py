from drf_yasg import openapi
from .models import *

pagination_properties = {
    'links': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'next': openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, nullable=True,
                description="Link to the next page of results, if available"),
            'previous': openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, nullable=True,
                description="Link to the previous page of results, if available")
        }
    ),
    'total_pages': openapi.Schema(
        type=openapi.TYPE_INTEGER, description="The total number of pages"),
    'total_items': openapi.Schema(
        type=openapi.TYPE_INTEGER, description="Total number of object that can be listed"),
}

user_detail_properties = {
    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="The unique identifier of the user"),
    'username': openapi.Schema(type=openapi.TYPE_STRING, description="The name of user"),
    'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description="User's email")
}

delete_bulk_api_properties = {
    'ids[]': openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(type=openapi.TYPE_INTEGER),
        description="An array of unique identifiers of the objects to be deleted"
    )
}

access_credential_list_api_response_properties = {
    'id': openapi.Schema(
        type=openapi.TYPE_INTEGER, description="The unique identifier of the access credential"),
    'user': openapi.Schema(
        type=openapi.TYPE_INTEGER, description="The ID of the user that owns the access credential"),
    'name': openapi.Schema(
        type=openapi.TYPE_STRING,
        description="The name of the access credential"),
    'access_type': openapi.Schema(
        type=openapi.TYPE_STRING,
        enum=[choice.value for choice in AccessType],
        default=AccessType.ssh_id_password.value,
        description="A access type of credential."),
    'username': openapi.Schema(
        type=openapi.TYPE_STRING,
        description="The username to be used for login with this access credential. Required if access_type ends with '_id_password'."),
    'password': openapi.Schema(
        type=openapi.TYPE_STRING,
        description="The password to be used for login with this access credential. Required if access_type ends with '_id_password'."),
    'secret': openapi.Schema(
        type=openapi.TYPE_STRING,
        description="The secret to be used for login with this access credential. Required if access_type does not end with '_id_password'."),
    'note': openapi.Schema(
        type=openapi.TYPE_STRING,
        description="Additional notes about the access credential"),
    'create_date': openapi.Schema(
        type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
        description="The date and time the access credential was created"),
}

access_credential_list_api_response = {
    200: openapi.Response(
        description='List of Access Credentail',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                **pagination_properties,
                'results': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties=access_credential_list_api_response_properties
                    )
                )
            }
        )
    )
}

access_credential_create_api_required_properties = [
    'name',
]

access_credential_create_api_properties = dict(
    filter(
        lambda x: x[0] in ['name', 'access_type',
                           'username', 'password', 'secret', 'note'],
        access_credential_list_api_response_properties.items()))

access_credential_create_api_response = {
    201: openapi.Response(
        description='The created access credential object with its properties',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=access_credential_list_api_response_properties
        )
    )
}

access_credential_simple_api_response_properties = {
    'id': openapi.Schema(type=openapi.TYPE_INTEGER,
                         description="An inherent id of access credential"),
    'name': openapi.Schema(type=openapi.TYPE_STRING,
                           description="A name of access credential"),
    'access_type': openapi.Schema(type=openapi.TYPE_STRING,
                                  enum=[choice.value for choice in AccessType],
                                  default=AccessType.ssh_id_password.value,
                                  description="A access type of credential."),
}

access_credential_simple_api_response = {
    200: openapi.Response(
        description="Simple list of Access Credentail. The parameter 'page' is not used.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=access_credential_simple_api_response_properties
        ),
    )
}

asset_list_api_response_properties = {
    'id': openapi.Schema(
        type=openapi.TYPE_INTEGER, description="The unique identifier of the asset"),
    'user': openapi.Schema(
        type=openapi.TYPE_INTEGER, description="The ID of the user that owns the asset"),
    'user_detail': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=user_detail_properties),
    'name': openapi.Schema(
        type=openapi.TYPE_STRING,
        description="The name of the asset"),
    'ip': openapi.Schema(
        type=openapi.TYPE_STRING, format=openapi.FORMAT_IPV4,
        description="The IP address of the asset for access"),
    'port': openapi.Schema(minimum=1, maximum=65535,
                           type=openapi.TYPE_INTEGER, default=22,
                           description="The port number of the asset for access"),
    'asset_type': openapi.Schema(type=openapi.TYPE_STRING,
                                 enum=[choice.value for choice in AssetType],
                                 default=AssetType.linux.value,
                                 description="The type of asset, like an operating system"),
    'access_credential': openapi.Schema(
        type=openapi.TYPE_INTEGER,
        description="The ID of the access credential used to access the asset"),
    'access_credential_detail': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=access_credential_simple_api_response_properties,
        description="Detailed information about the access credential"),
    'note': openapi.Schema(
        type=openapi.TYPE_STRING,
        description="Additional notes about the asset"),
    'create_date': openapi.Schema(
        type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
        description="The date and time the asset was created"),
}

asset_list_api_response = {
    200: openapi.Response(
        description='List of Asset. Can list all if the user is super user.',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                **pagination_properties,
                'results': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties=asset_list_api_response_properties
                    )
                )
            }
        )
    )
}

asset_create_api_required_properties = [
    'name', 'ip', 'access_credential'
]

asset_create_api_properties = dict(
    filter(
        lambda x: x[0] in ['name', 'ip', 'port',
                           'asset_type', 'access_credential', 'note'],
        asset_list_api_response_properties.items()))

asset_create_api_response = {
    201: openapi.Response(
        description='The created asset object with its properties',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=asset_list_api_response_properties
        )
    )
}

asset_update_api_response = {
    200: openapi.Response(
        description='The updated asset object with its properties',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=asset_list_api_response_properties
        )
    )
}


script_list_api_response_properties = {
    'id': openapi.Schema(
        type=openapi.TYPE_INTEGER, description="The unique identifier of the script"),
    'user': openapi.Schema(
        type=openapi.TYPE_INTEGER, description="The ID of the user that owns the script"),
    'user_detail': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=user_detail_properties),
    'name': openapi.Schema(type=openapi.TYPE_STRING,
                           description="A name of script"),
    'note': openapi.Schema(
        type=openapi.TYPE_STRING,
        description="Additional notes about the script"),
}

script_list_api_response = {
    200: openapi.Response(
        description='List of Script',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                **pagination_properties,
                'results': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties=script_list_api_response_properties
                    )
                )
            }
        )
    )
}
