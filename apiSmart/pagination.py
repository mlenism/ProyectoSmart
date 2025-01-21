from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'  # Parámetro de consulta para definir el tamaño de la página
    page_query_param = 'page'  # Parámetro de consulta para definir el número de la página
    max_page_size = 2000  # Tamaño máximo de la página
