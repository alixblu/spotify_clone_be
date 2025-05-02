# # File này dùng để tạo component để thêm extend schema cho các api 

# from drf_spectacular.utils import (
#     extend_schema,
#     OpenApiParameter,
#     OpenApiExample,
#     OpenApiResponse,
#     OpenApiTypes
# )
# from rest_framework import status

# class SchemaFactory:
#     """Factory tạo schema documentation linh hoạt"""
    
#     @staticmethod
#     def auth_schema(
#         request_example=None,
#         success_response=None,
#         error_responses=None,
#         description="",
#         request_serializer=None,
#         method='POST'
#     ):
#         """
#         Tạo schema cho các API Authentication
        
#         Parameters:
#         - request_example: dict (ví dụ request)
#         - success_response: dict (ví dụ response thành công)
#         - error_responses: list[dict] (ví dụ các lỗi)
#         - description: str (mô tả API)
#         - request_serializer: Serializer class
#         - method: HTTP method
#         """
#         examples = []
        
#         # Thêm request example nếu có
#         if request_example:
#             examples.append(
#                 OpenApiExample(
#                     'Request Example',
#                     value=request_example,
#                     request_only=True
#                 )
#             )
        
#         # Thêm success response example
#         if success_response:
#             status_code = status.HTTP_201_CREATED if method == 'POST' else status.HTTP_200_OK
#             examples.append(
#                 OpenApiExample(
#                     'Success Response',
#                     value=success_response,
#                     response_only=True,
#                     status_codes=[str(status_code)]
#                 )
#             )
        
#         # Thêm error response examples
#         if error_responses:
#             for err in error_responses:
#                 examples.append(
#                     OpenApiExample(
#                         err.get('name', 'Error Response'),
#                         value=err['response'],
#                         response_only=True,
#                         status_codes=[str(err['status_code'])]
#                     )
#                 )
        
#         # Xác định responses dict
#         responses = {
#             status.HTTP_200_OK: OpenApiTypes.OBJECT,
#             status.HTTP_201_CREATED: OpenApiTypes.OBJECT,
#         }
#         if error_responses:
#             for err in error_responses:
#                 responses[err['status_code']] = OpenApiTypes.OBJECT
        
#         return extend_schema(
#             request=request_serializer,
#             responses=responses,
#             examples=examples,
#             description=description
#         )

#     @staticmethod
#     def list_schema(
#         item_example,
#         search_fields=None,
#         description="",
#         pagination=True
#     ):
#         """
#         Tạo schema cho API list
        
#         Parameters:
#         - item_example: dict (ví dụ 1 item)
#         - search_fields: list[str] (các trường filter)
#         - description: str (mô tả API)
#         - pagination: bool (có phân trang không)
#         """
#         params = []
#         if search_fields:
#             params.extend([
#                 OpenApiParameter(
#                     name=field,
#                     type=OpenApiTypes.STR,
#                     location=OpenApiParameter.QUERY,
#                     description=f'Filter by {field}'
#                 ) for field in search_fields
#             ])
        
#         if pagination:
#             params.extend([
#                 OpenApiParameter(
#                     name='limit',
#                     type=OpenApiTypes.INT,
#                     location=OpenApiParameter.QUERY,
#                     description='Items per page'
#                 ),
#                 OpenApiParameter(
#                     name='offset',
#                     type=OpenApiTypes.INT,
#                     location=OpenApiParameter.QUERY,
#                     description='Start position'
#                 )
#             ])
        
#         response_value = {
#             "results": [item_example, item_example]
#         }
#         if pagination:
#             response_value.update({
#                 "count": 2,
#                 "next": None,
#                 "previous": None
#             })
        
#         return extend_schema(
#             parameters=params,
#             examples=[
#                 OpenApiExample(
#                     'Success Response',
#                     value=response_value,
#                     response_only=True
#                 )
#             ],
#             description=description
#         )
    













from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    OpenApiTypes
)
from rest_framework import status
from typing import Optional, Dict, List, Any


class SchemaFactory:
    """Factory tạo schema documentation linh hoạt với interface thống nhất"""
    
    @staticmethod
    def _base_schema(
        *,
        request_example: Optional[Dict] = None,
        success_response: Optional[Dict] = None,
        error_responses: Optional[List[Dict]] = None,
        description: str = "",
        request_serializer=None,
        response_serializer=None,
        method: str,
        path_params: Optional[List[Dict]] = None,
        query_params: Optional[List[Dict]] = None
    ):
        """Base method cho tất cả các loại schema"""
        examples = []
        responses = {}
        
        # Request example
        if request_example:
            examples.append(
                OpenApiExample(
                    'Request Example',
                    value=request_example,
                    request_only=True
                )
            )
        
        # Success response
        if success_response:
            status_code = (
                status.HTTP_201_CREATED if method == 'POST' 
                else status.HTTP_200_OK
            )
            examples.append(
                OpenApiExample(
                    'Success Response',
                    value=success_response,
                    response_only=True,
                    status_codes=[str(status_code)]
                )
            )
            responses[status_code] = response_serializer or OpenApiTypes.OBJECT
        
        # Error responses
        if error_responses:
            for err in error_responses:
                examples.append(
                    OpenApiExample(
                        err.get('name', 'Error Response'),
                        value=err['response'],
                        response_only=True,
                        status_codes=[str(err['status_code'])]
                    )
                )
                responses[err['status_code']] = OpenApiTypes.OBJECT
        
        # Default responses
        if method == 'GET':
            responses.setdefault(status.HTTP_200_OK, response_serializer or OpenApiTypes.OBJECT)
        responses.setdefault(status.HTTP_400_BAD_REQUEST, OpenApiTypes.OBJECT)
        responses.setdefault(status.HTTP_404_NOT_FOUND, OpenApiTypes.OBJECT)
        
        # Parameters
        parameters = []
        if path_params:
            for param in path_params:
                parameters.append(
                    OpenApiParameter(
                        name=param['name'],
                        type=param.get('type', OpenApiTypes.STR),
                        location=OpenApiParameter.PATH,
                        description=param.get('description', '')
                    )
                )
        
        if query_params:
            for param in query_params:
                parameters.append(
                    OpenApiParameter(
                        name=param['name'],
                        type=param.get('type', OpenApiTypes.STR),
                        location=OpenApiParameter.QUERY,
                        description=param.get('description', '')
                    )
                )
        
        return extend_schema(
            request=request_serializer,
            responses=responses,
            examples=examples,
            description=description,
            parameters=parameters,
            methods=[method]
        )

    @staticmethod
    def post_schema(
        request_example: Optional[Dict] = None,
        success_response: Optional[Dict] = None,
        error_responses: Optional[List[Dict]] = None,
        description: str = "",
        request_serializer=None,
        response_serializer=None
    ):
        """Tạo schema cho POST API"""
        return SchemaFactory._base_schema(
            request_example=request_example,
            success_response=success_response,
            error_responses=error_responses,
            description=description,
            request_serializer=request_serializer,
            response_serializer=response_serializer,
            method='POST'
        )

    @staticmethod
    def list_schema(
        item_example: Dict,
        search_fields: Optional[List[str]] = None,
        description: str = "",
        pagination: bool = True,
        serializer=None
    ):
        """Tạo schema cho GET list API"""
        query_params = []
        
        if search_fields:
            query_params.extend({
                'name': field,
                'description': f'Filter by {field}'
            } for field in search_fields)
        
        if pagination:
            query_params.extend([
                {'name': 'limit', 'type': OpenApiTypes.INT, 'description': 'Items per page'},
                {'name': 'offset', 'type': OpenApiTypes.INT, 'description': 'Start position'}
            ])
        
        success_response = {
            "results": [item_example, item_example]
        }
        if pagination:
            success_response.update({
                "count": 2,
                "next": None,
                "previous": None
            })
        
        return SchemaFactory._base_schema(
            success_response=success_response,
            description=description,
            response_serializer=serializer,
            query_params=query_params,
            method='GET'
        )

    @staticmethod
    def update_schema(
        item_id_param: str = 'id',
        request_example: Optional[Dict] = None,
        success_response: Optional[Dict] = None,
        error_responses: Optional[List[Dict]] = None,
        description: str = "",
        request_serializer=None,
        response_serializer=None,
        partial: bool = False
    ):
        """Tạo schema cho PUT/PATCH API"""
        return SchemaFactory._base_schema(
            request_example=request_example,
            success_response=success_response,
            error_responses=error_responses,
            description=description,
            request_serializer=request_serializer,
            response_serializer=response_serializer,
            method='PATCH' if partial else 'PUT',
            path_params=[{
                'name': item_id_param,
                'description': f'ID of the item to {"update" if not partial else "partially update"}'
            }]
        )

    @staticmethod
    def delete_schema(
        item_id_param: str = 'id',
        success_response: Optional[Dict] = None,
        error_responses: Optional[List[Dict]] = None,
        description: str = "",
        response_serializer=None
    ):
        """Tạo schema cho DELETE API"""
        return SchemaFactory._base_schema(
            success_response=success_response,
            error_responses=error_responses,
            description=description,
            response_serializer=response_serializer,
            method='DELETE',
            path_params=[{
                'name': item_id_param,
                'description': 'ID of the item to delete'
            }]
        )

    @staticmethod
    def retrieve_schema(
        item_id_param: str = 'id',
        success_response: Optional[Dict] = None,
        error_responses: Optional[List[Dict]] = None,
        description: str = "",
        serializer=None
    ):
        """Tạo schema cho GET detail API"""
        return SchemaFactory._base_schema(
            success_response=success_response,
            error_responses=error_responses,
            description=description,
            response_serializer=serializer,
            method='GET',
            path_params=[{
                'name': item_id_param,
                'description': 'ID of the item to retrieve'
            }]
        )