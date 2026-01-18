# Файлы, где используются pagination_pages:
#   - \src\api\dependencies\dependencies.py
#      В классе PaginationPagesListParams при задании значений по
#      умолчанию для параметров page и per_page
#   - \src\repositories\base.py
#      В async def get_rows при задании значений по
#      умолчанию для параметров page и per_page
pagination_pages = {"page": 1,
                    "per_page": 3,
                    }


