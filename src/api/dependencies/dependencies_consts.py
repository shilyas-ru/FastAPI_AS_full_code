# Поиск "pagination_pages" (найдено 16 совпадений в 6 файлах из 37) [Продвинутый: Регистр]
#
# \MyCode_ver_02_context_manager\src\api\dependencies\dependencies.py (совпадений: 4)
# 	Строка  6: from src.api.dependencies.dependencies_consts import pagination_pages
# 	Строка 16: # pagination_pages = {"page": 1,
# 	Строка 28:                           )] = pagination_pages["page"]
# 	Строка 33:                               )] = pagination_pages["per_page"]
#
# \MyCode_ver_02_context_manager\src\api\dependencies\dependencies_consts.py (совпадений: 1)
# 	Строка 1: pagination_pages = {"page": 1,
#
# \MyCode_ver_02_context_manager\src\api\dependencies\__pycache__\dependencies.cpython-311.pyc (совпадений: 1)
# 	Строка 13: __module__Ъ__qualname__Ъpagination_pagesr

# \MyCode_ver_02_context_manager\src\repositories\base.py (совпадений: 6)
# 	Строка   7: from src.api.dependencies.dependencies import pagination_pages
# 	Строка 149:                        per_page=pagination_pages["per_page"],
# 	Строка 150:                        page=pagination_pages["page"],
# 	Строка 151:                        # offset=(pagination_pages["page"] - 1) * pagination_pages["per_page"],
# 	Строка 152:                        # limit=pagination_pages["per_page"],

# \MyCode_ver_02_context_manager\src\repositories\__pycache__\base.cpython-311.pyc (совпадений: 1)
# 	Строка   7: S

pagination_pages = {"page": 1,
                    "per_page": 3,
                    }

# from src.api.dependencies.dependencies import pagination_pages
# Файлы, где используются:
#   - \src\api\dependencies\dependencies.py
#   - \src\repositories\base.py
