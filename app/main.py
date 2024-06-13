from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from fastapi_utils.openapi import simplify_operation_ids

from app.config import config
from app.models.exceptions import add_exception_handlers, catch_unhandled_exceptions
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.data_sources import router as data_sources_router
from app.routers.data_source_metas import router as data_source_metas_router
from app.routers.utils import router as utils_router
from app.routers.source_layers import router as source_layers_router
from app.routers.geocode import router as geocode_router
from app.routers.schedule import router as schedule_router
from app.routers.manuals import router as manuals_router

tags_metadata = [
    {"name": "Авторизация", "description": "Авторизация"},
    {"name": "Пользователи", "description": "Работа с пользователями"},
    {"name": "Источники данных", "description": "Работа с источниками данных"},
    {"name": "Поля источников данных", "description": "Работа с полями источников данных"},
    {"name": "Отладка", "description": "Отладка и утилиты"},
    {"name": "Исходные слои", "description": "Работа с слоями источников данных"},
    {"name": "Геокодирование", "description": "Геокодирование и реверс-геокодирование"},
    {"name": "Расписание", "description": "Настройка расписания для автоматизированного проведения работ"},
    {"name": "Справочники", "description": "Работа со справочниками"}
]

app = FastAPI(
    docs_url=None,
    redoc_url="/redoc",
    debug=config.DEBUG,
    openapi_tags=tags_metadata,
    openapi_url=f"{config.BACKEND_PREFIX}/openapi.json", 
    title=config.BACKEND_TTILE,
    #description=config.BACKEND_DESCRIPTION,
    description="""
<section>
  <h1>
    Краткая справка по реализованным методам API
  </h1>
  <details>
    <summary>Авторизация</summary>
    <p>
    POST /signin: Аутентификация пользователей по логину и паролю.
    POST /signup: Выход пользователя из системы.
    POST /register: Регистрация нового пользователя.
    </p>
  </details>
  <details>
    <summary>Пользователи</summary>
    <p>
    GET /users: Получение списка всех пользователей.
    GET /users/{id}: Получение пользователя по его id.
    POST /users: Создание нового пользователя.
    PUT /users/{id}: Изменение пользователя по его id.
    DELETE /users/{id}: Удаление пользователя по его id.
    </p>
    </details>
    <details>
    <summary>Источники данных</summary>
    <p> 
    GET /data_sources: Получение списка всех источников данных.
    GET /data_sources/{id}: Получение источника данных по его id.
    POST /data_sources: Создание нового источника данных.
    PUT /data_sources/{id}: Изменение источника данных по его id.
    DELETE /data_sources/{id}: Удаление источника данных по его id.
    </p>
      </details>
  <details>
    <summary>Поля источников данных</summary>
    <p>
    GET /data_source_metas: Получение списка всех полей источников данных.
    GET /data_source_metas/{id}: Получение поля источника данных по его id.
    POST /data_source_metas: Создание нового поля источника данных.
    PUT /data_source_metas/{id}: Изменение поля источника данных по его id.
    DELETE /data_source_metas/{id}: Удаление поля источника данных по его id.
    </p>
    </details>
  <details>
    <summary>Утилиты</summary>
    <p>
    GET /utils/health: Проверка доступности сервиса.
    GET /utils/status: Эхо-метод для отладки.
    POST /utils/cookie: Установка куки.
    </p>
    </details>
  <details>
    <summary>Слои источников данных</summary>
    <p>
    
    </p>
    </details>
  <details>
    <summary>Геокодирование</summary>
    <p>
    POST /geocode: Геокодирование адреса.
    POST /reverse_geocode: Реверс-геокодирование координат.
    </p>
    </details>
  <details>
    <summary>Расписание</summary>
    <p>
    POST /schedule: Настройка расписания для автоматизированного проведения работ.
    GET /schedule: Получение текущих настроек расписания.
    PUT /schedule: Изменение настроек расписания.
    </p>
  </details>

</section>"""
)

app.middleware("http")(catch_unhandled_exceptions)
add_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Mount static files
app.mount(f"{config.BACKEND_PREFIX}/static", StaticFiles(directory="./app/docs"), name="static")

@app.get(f"{config.BACKEND_PREFIX}/docs", include_in_schema=False)
async def api_documentation(request: Request):
    return HTMLResponse("""
<!doctype html>
<html lang="ru">
  <head>
    <link rel="icon" href="static/favicon.ico">
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>EXILON</title>
    <script src="https://unpkg.com/@stoplight/elements/web-components.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/@stoplight/elements/styles.min.css">
    <style>
      html, body {
        height: 100%;
        margin: 0;
        display: flex;
        flex-direction: column;
      }
      #container {
        flex: 1;
        display: flex;
        flex-direction: column;
      }
      elements-api {
        flex: 1;
      }
    </style>
  </head>
  <body>
    <div id="container">
      <elements-api
        apiDescriptionUrl="openapi.json"
        router="hash"
      />
    </div>
  </body>
</html>""")

app.include_router(auth_router, tags=["Авторизация"])
app.include_router(users_router, tags=["Пользователи"])
app.include_router(data_sources_router, tags=["Источники данных"])
app.include_router(data_source_metas_router, tags=["Поля источников данных"])
app.include_router(utils_router, tags=["Отладка"])
app.include_router(source_layers_router, tags=["Исходные слои"])
app.include_router(geocode_router, tags=["Геокодирование"])
app.include_router(schedule_router, tags=["Расписание"])
app.include_router(manuals_router, tags=["Справочники"])


print("app.main.py: app created.")

#simplify_operation_ids(app)