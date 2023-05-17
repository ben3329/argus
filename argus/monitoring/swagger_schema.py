from drf_yasg import openapi
from monitoring.models import *
from monitoring.choices import *
from typing import Dict, List


def filter_properties(fields: List[str], properties: Dict[str, openapi.Schema]) -> Dict[str, openapi.Schema]:
    return {k: v for k, v in properties.items() if k in fields}


page_param = openapi.Parameter(
    'page', in_=openapi.IN_QUERY, description='page number', type=openapi.TYPE_NUMBER
)
ordering_param = openapi.Parameter(
    'ordering', in_=openapi.IN_QUERY,
    description='A comma-separated list of fields to sort by. Use `-` prefix to sort in descending order.',
    type=openapi.TYPE_STRING, example='-field1,field2'
)

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

author_detail_properties = {
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

access_credential_properties = {
    'id': openapi.Schema(
        type=openapi.TYPE_INTEGER, description="The unique identifier of the access credential"),
    'author': openapi.Schema(
        type=openapi.TYPE_INTEGER, description="The ID of the user that creates the access credential"),
    'name': openapi.Schema(
        type=openapi.TYPE_STRING,
        description="The name of the access credential"),
    'access_type': openapi.Schema(
        type=openapi.TYPE_STRING,
        enum=[choice.value for choice in AccessTypeChoices],
        default=AccessTypeChoices.ssh_password.value,
        description="A access type of credential"),
    'username': openapi.Schema(
        type=openapi.TYPE_STRING,
        description="The username to be used for login with this access credential."),
    'password': openapi.Schema(
        type=openapi.TYPE_STRING,
        description="The password to be used for login with this access credential. Required if access_type ends with '_password'"),
    'secret': openapi.Schema(
        type=openapi.TYPE_STRING,
        description="The secret to be used for login with this access credential. Required if access_type does not end with '_password'"),
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
                        properties=access_credential_properties
                    )
                )
            }
        )
    )
}

access_credential_create_api_required_properties = [
    'name', 'assess_type', 'username'
]

access_credential_create_api_properties = filter_properties(
    ['name', 'access_type', 'username', 'password', 'secret', 'note'],
    access_credential_properties)

access_credential_create_api_response = {
    201: openapi.Response(
        description='The created access credential object with its properties',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=access_credential_create_api_properties
        )
    )
}

access_credential_simple_api_response_properties = filter_properties(
    ['id', 'name', 'access_type'],
    access_credential_properties)

access_credential_simple_api_response = {
    200: openapi.Response(
        description="Simple list of Access Credentail.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=access_credential_simple_api_response_properties
        ),
    )
}

asset_properties = {
    'id': openapi.Schema(
        type=openapi.TYPE_INTEGER, description="The unique identifier of the asset"),
    'author': openapi.Schema(
        type=openapi.TYPE_INTEGER, description="The ID of the user that creates the asset"),
    'author_detail': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=author_detail_properties),
    'name': openapi.Schema(
        type=openapi.TYPE_STRING,
        description="The name of the asset"),
    'ip': openapi.Schema(
        type=openapi.TYPE_STRING, format=openapi.FORMAT_IPV4,
        description="The IP address of the asset for access"),
    'port': openapi.Schema(
        minimum=1, maximum=65535, type=openapi.TYPE_INTEGER, default=22,
        description="The port number of the asset for access"),
    'asset_type': openapi.Schema(
        type=openapi.TYPE_STRING,
        enum=[choice.value for choice in AssetTypeChoices],
        default=AssetTypeChoices.linux.value,
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
        description='List of Asset. Can list all if the user is super user',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                **pagination_properties,
                'results': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties=asset_properties
                    )
                )
            }
        )
    )
}

asset_create_api_required_properties = [
    'name', 'ip', 'port', 'asset_type', 'access_credential'
]

asset_create_api_properties = filter_properties(
    ['name', 'ip', 'port', 'asset_type', 'access_credential', 'note'],
    asset_properties)

asset_create_api_response = {
    201: openapi.Response(
        description='The created asset object with its properties',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=asset_create_api_properties
        )
    )
}

asset_update_api_response = {
    200: openapi.Response(
        description='The updated asset object with its properties',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=asset_create_api_properties
        )
    )
}

asset_simple_api_response_properties = filter_properties(
    ['id', 'name'],
    asset_properties)

asset_simple_api_response = {
    200: openapi.Response(
        description="Simple list of Asset.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=asset_simple_api_response_properties
        ),
    )
}


script_properties = {
    'id': openapi.Schema(
        type=openapi.TYPE_INTEGER, description="The unique identifier of the script"),
    'author': openapi.Schema(
        type=openapi.TYPE_INTEGER, description="The ID of the user that creates the script"),
    'author_detail': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=author_detail_properties),
    'name': openapi.Schema(
        type=openapi.TYPE_STRING, description="A name of script"),
    'language': openapi.Schema(
        type=openapi.TYPE_STRING,
        enum=[choice.value for choice in LanguageChoices],
        description="The programming language of the script"),
    'code': openapi.Schema(
        type=openapi.TYPE_STRING, description="The code of the script"),
    'output_type': openapi.Schema(
        type=openapi.TYPE_STRING,
        enum=[choice.value for choice in OutputTypeChoices],
        description="The output type of the script."),
    'note': openapi.Schema(
        type=openapi.TYPE_STRING, description="Additional notes about the script"),
    'create_date': openapi.Schema(
        type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
        description="The date and time when the script was created"),
    'update_date': openapi.Schema(
        type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
        description="The date and time when the script was last updated"),
    'revision': openapi.Schema(
        type=openapi.TYPE_INTEGER, default=1,
        description="The revision number of the script")
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
                        properties=script_properties
                    )
                )
            }
        )
    )
}

script_retrieve_api_response = {
    200: openapi.Response(
        description='List of Script',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=script_properties
        )
    )
}

script_create_api_required_properties = [
    'name', 'language', 'code', 'output_type'
]

script_create_api_properties = filter_properties(
    ['name', 'language', 'code', 'output_type', 'note'],
    script_properties)

script_create_api_response = {
    201: openapi.Response(
        description='The created script object with its properties',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=script_create_api_properties
        )
    )
}

script_simple_api_response_properties = filter_properties(
    ['id', 'name', 'fields', 'parameters'],
    script_properties)

script_simple_api_response = {
    200: openapi.Response(
        description="Simple list of Script.",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=script_simple_api_response_properties
        ),
    )
}