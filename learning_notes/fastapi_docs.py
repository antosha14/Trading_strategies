from enum import Enum
from typing import Annotated, Any

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr, Field

app = FastAPI()
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


# Используем для валидации параметров в путях
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/items/admin")
async def read_item():
    return {"message": "Yo man"}


@app.get("/items/{model_name}")
async def read_item(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


# тип, когда нужно чтобы после слеша тоже был путь
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


# пример параметров после знака ? в URL (по умолчанию всегда строки, но если ставим типы, то автоматически конвертируются и валидируются)
# а также необязательного параметра
@app.get("/itemongo/")
async def query_params_ex(nonessential: int | None, skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]


""" 
Использование пайдантик для валидации тела запроса  
А также через параметр model config задаётся cхема для документации
C помощью поля можно задавать прмеры
"""


class Item(BaseModel):
    name: str = Field(examples=["Foo"])
    description: str | None = None
    price: float
    tax: float | None = None
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ]
        }
    }


# Три точки делают параметр обязательным, даже если он может быть None
# Также можно в аннотейтед задать тип list[str], но так как валидация идёт по квери, смотеть будет именно в квери параметры, и занесёт все встреченные q в список


@app.post("/items/")
async def create_item(q: Annotated[str | None, Query(max_length=50)] = ...):
    dicts = {"item": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    return dicts


# Можно также задавать дефолтное значение списком
@app.get("/items/")
async def read_items1(q: Annotated[list[str], Query()] = ["foo", "bar"]):
    query_items = {"q": q}
    return query_items


# alies используется если нужно достать в переменную невалидное для питона имя
@app.get("/items/")
async def read_items2(q: Annotated[str | None, Query(alias="item-query")] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Чтобы апи ожидал не просто словарь (стандартное поведение если определена только одна модель), а словарь, где переменна - это ключ, то используем параметр embeded item: Item = Body(embed=True)

app = FastAPI()


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


# C помощью параметра response_model, можно задать модель ответа (например в текущем прмере выслать обратно юзера, но уже без пароля), но такой подход не даст полной поддержки
@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn) -> Any:
    return user


# Подход через наследование позволяет сделать то же самое, но с поддержкой IDE и схемой в Open API
# В свою очредь респонз модел нан исползуется чтобы сказать фреймворку скипнуть проверку типов ответа
# Параметр пути response_model_exclude_unset=True сделает так, чтобы поля со стандартными значениями если их не предоставил пользователь не попадут в ответ
# Но если значения, такие же как дефолтные были всётаки переданы и совпадают с дефолтными, с этим параметром мы всё равно их вернём, так как пайдантик поймёт, что они были выставлены
"""
class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn(BaseUser):
    password: str


@app.post("/user/", response_model=None)
async def create_user(user: UserIn) -> BaseUser:
    return user
"""

# Можно определеить тип возврата как Юнион мжду двумя моделями, в доках пометится как any of
# Если не знаем на перёд тип инпута и ответа можно использовать просто dict[str, float]
"""
@app.get("/items/{item_id}", response_model=Union[PlaneItem, CarItem])
async def read_item(item_id: str):
    return items[item_id]
"""

# С помощью параметра пути status_code можно определеить какой статус код вернуть
"""
@app.post("/items/", status_code=201)
async def create_item(name: str):
    return {"name": name}
"""

# C помощью status из fastapi мы имеем доступ к удобному хранилищу HTTP статусов
"""
from fastapi import FastAPI, status

app = FastAPI()


@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(name: str):
    return {"name": name}
"""


# Ксласс HTTPException используется для возврата ошибок в правильном формате её нужно именно raise. В ошибку также можно добавить кастомные хэдэры с помощью доп параметра headers
"""
@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found", headers={"X-Error": "There goes my error"})
    return {"item": items[item_id]}
"""


# Кастомные ошибки, возвращаемые к примеру фреймворками можно обрабатывать на уровне приложения с помощью exception_handler
"""
@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )
"""

# Можно переделывать стандартные ошибки с помощью хендлера, но ВАЖНО в хендлере задать именно ошибку из старлита, а поднять ошибку фастапи
"""
For example, you could want to return a plain text response instead of JSON for these errors:


from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id == 3:
        raise HTTPException(status_code=418, detail="Nope! I don't like 3.")
    return {"item_id": item_id}
"""

# В параметрах пути можно добавлять tags, description, summary, response_description, deprecated=True
# Дескрипшн также подхватит из Docstrings , более того в докстринге можно даже использовать маркдаун


# С помощью функции jsonable_encoder можно отформатировать данные в формат JSON, например для отправки или занесения в базу данных
# Далее можно сериализировать (в биты) с помощью стандартного json.dumps()
"""
from fastapi.encoders import jsonable_encoder

@app.put("/items/{id}")
def update_item(id: str, item: Item):
    json_compatible_item_data = jsonable_encoder(item)
    fake_db[id] = json_compatible_item_data
"""

# для приложения можно задать мидлвейр, который будет работать для всех функций
# функция call_next - это и есть наш пас (get, post, put), например мы к ответу можем добавить кастомный хэдэр (с префиксом Х)
"""
from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
"""

# Если нам нужно получить валидацию от пайдантик, но вернуть не пайдантик модель мы используем тип Any, а пайдантик модель засовываем в response_model
"""
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []


@app.post("/items/", response_model=Item)
async def create_item(item: Item) -> Any:
    return item


@app.get("/items/", response_model=list[Item])
async def read_items() -> Any:
    return [
        {"name": "Portal Gun", "price": 42.0},
        {"name": "Plumbus", "price": 32.0},
    ]
"""

# Можно редиректить на другой адрес и отвечать JSONOm
"""
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse, RedirectResponse

app = FastAPI()


@app.get("/portal")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return JSONResponse(content={"message": "Here's your interdimensional portal."})
"""

# This will make FastAPI skip the response model generation and that way you can have any return type annotations you need without it affecting your FastAPI application
"""
from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse

app = FastAPI()


@app.get("/portal", response_model=None)
async def get_portal(teleport: bool = False) -> Response | dict:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return {"message": "Here's your interdimensional portal."}
"""

# Параметр response_model_exclude_unset - отвечает за то, чтобы не включать в ответ параметры, имеющие дефолтные значения, которые были непосредственно заданы
# C помощью response_model_include={"name", "description"} можно задать ключи параметров, котоыре мы хотим засунуть в респонз
"""
@app.get("/items/{item_id}", response_model=Item, response_model_exclude_unset=True)
async def read_item(item_id: str):
    return items[item_id]
"""

# Если нужно сделать что-то высоконагруженное, но юзеру можно вернуть ответ уже сейчас, то используем BackgroundTasks
"""
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()


def write_notification(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)


@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}
"""

# Можно создавать метаданные, отображаемые в документации к API
'''
from fastapi import FastAPI

description = """
ChimichangApp API helps you do awesome stuff. 🚀

## Items

You can **read items**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""

app = FastAPI(
    title="ChimichangApp",
    description=description,
    summary="Deadpool's favorite app. Nuff said.",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Deadpoolio the Amazing",
        "url": "http://x-force.example.com/contact/",
        "email": "dp@x-force.example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",#Можно также использовать параметр identifier: 'MIT' 
    },
)


@app.get("/items/")
async def read_items():
    return [{"name": "Katana"}]
'''


# Также эндпоинтам можно задавать ТЭГи, описывать их в отдельном словаре, и передав приложению параметр open_api_tags добавим метаданные каждому тэгу
# Порядок внутри словоря с метаданными определяет порядок появления роутов в документации
# Можно также в параметрах саамого приложения поменять адрес схемы апи через параметр openapi_url="/api/v1/openapi.json" или вообще её убрать с параметром None
# Также с помощью параметров приложения docs_url и redoc_url можно менять адреса других документаций (мейн доку я бы оставил)
"""
from fastapi import FastAPI

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]

app = FastAPI(openapi_tags=tags_metadata)


@app.get("/users/", tags=["users"])
async def get_users():
    return [{"name": "Harry"}, {"name": "Ron"}]


@app.get("/items/", tags=["items"])
async def get_items():
    return [{"name": "wand"}, {"name": "flying broom"}]
"""

# Статику можно раздавать через отдельное приложение на эндпоинте, при таком подходе управление полностью передаётся в другое приложение в данном случае Старлит, сначала эндпоинт, далее приложение
# ему передаётся адрес папки откуда брать статику, и имя приложения для fastapi
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
"""

# чтобы иметь Возможность дебажить приложение нужно запустить ювикорн через нэйм равно мэйн, а потом запустить файл через обычный питон (нэём равно мейн исполниться только для запущенного файла и
# не запуститься для других модулей, импортирующих файл с точкой входа
"""
import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    a = "a"
    b = "b" + a
    return {"hello world": b}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

# функции для тестирования определяются префиксом test_ , но такой подход работает только с синхронными функциями
# To pass a path or query parameter, add it to the URL itself.
# To pass a JSON body, pass a Python object (e.g. a dict) to the parameter json.
# If you need to send Form Data instead of JSON, use the data parameter instead.
# To pass headers, use a dict in the headers parameter.
# For cookies, a dict in the cookies parameter.
# pip install pytest потом результаты тестов можно автоматически получать через пакет pytest
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/")
async def read_main():
    return {"msg": "Hello World"}


client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
"""

# С помощью пустых файлов __init__ в питоне объявляются пакеты (нужно для импортов), .py файлы внутри первого уровня инит - это модули, то что в папках с инитами - это сабмодули, а сами папки это сабпэкеджи
"""
.
├── app                  # "app" is a Python package
│   ├── __init__.py      # this file makes "app" a "Python package"
│   ├── main.py          # "main" module, e.g. import app.main
│   ├── dependencies.py  # "dependencies" module, e.g. import app.dependencies
│   └── routers          # "routers" is a "Python subpackage"
│   │   ├── __init__.py  # makes "routers" a "Python subpackage"
│   │   ├── items.py     # "items" submodule, e.g. import app.routers.items
│   │   └── users.py     # "users" submodule, e.g. import app.routers.users
│   └── internal         # "internal" is a "Python subpackage"
│       ├── __init__.py  # makes "internal" a "Python subpackage"
│       └── admin.py     # "admin" submodule, e.g. import app.internal.admin
"""

# не в мейн файле, а в сабмодуле users, чтобы сделать раутинг используем класс апи роутер и каждый роут создаём с ним
# данный класс настраивает префиксы пути для каждого раута, тэги и зависимости
"""
from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_token_header

router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.get("/")
async def read_items():
    return fake_items_db


@router.get("/{item_id}")
async def read_item(item_id: str):
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"name": fake_items_db[item_id]["name"], "item_id": item_id}


@router.put(
    "/{item_id}",
    tags=["custom"],
    responses={403: {"description": "Operation forbidden"}},
)
async def update_item(item_id: str):
    if item_id != "plumbus":
        raise HTTPException(
            status_code=403, detail="You can only update the item: plumbus"
        )
    return {"item_id": item_id, "name": "The great Plumbus"}
"""

# Главный файл, причём импортировать нужно одновременно (так как одинаковые названия переменных роутер)
"""
from .routers import items, users

app = FastAPI(dependencies=[Depends(get_query_token)])


app.include_router(users.router)
app.include_router(items.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)

"""

# Посмотреть OSI model, TCP/IP
# The HTTPS certificates "certify" a certain domain, but the protocol and encryption happen at the TCP level, before knowing which domain is being dealt with.

# Obtain domain name
# configure it in DNS server
# Server with fixed public ip
# Один IP адрес и порт может слушать только 1 процесс

# Зависимость - это операция(любой колабл в питоне в том числе и класс), которую нужно выполнить перед выполнением другой операции
# в фаст апи прокидываются с помощью специального класса Depends(callable), при наличии в пути управление вместе с параметрами пути перейдёт в зависимость и после выполнения
# зависимости результат выполнгения передасться на мессто Depends в функцию пути
# у зависимостей тоже могут быть зависимости, тем самым выстраивается дерево зависимостей
# стандартно если зависимость используется несколько раз для одного пути она вызовется один раз и закэширруется, если хотим, чтобы она вызывалась каждый раз задаём параметр
# use_cache=False
# зависимости можно также прокидывать в само приложение и они в таком случае будут рабоать на все пути
"""
from typing import Annotated

from fastapi import Cookie, Depends, FastAPI

async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: Annotated[str, Header()]):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])

def query_extractor(q: str | None = None):
    return q


def query_or_cookie_extractor(
    q: Annotated[str, Depends(query_extractor)],
    last_query: Annotated[str | None, Cookie()] = None,
):
    if not q:
        return last_query
    return q


@app.get("/items/")
async def read_query(
    query_or_default: Annotated[str, Depends(query_or_cookie_extractor)]
):
    return {"q_or_cookie": query_or_default}
"""

# Если результат зависимостей нам не нужно использовать в функции для пути, то их можно задать параметром пути dependencies, принимающим словарь Depends
"""
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI()


async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: Annotated[str, Header()]):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


@app.get("/items/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]
"""

# Ключевое слово yield используется для создания генераторов, и результат выполения функции будет представлять собой генератор (итерируемый объкт с реализованной функцией next)
# При вызове next(y_funktion) произойдёт возврат первого yeild peremennaya и выполнение функции со всем контекстом заморозится, следующий вызов некст пойдёт выполнять код послe
# строки с yield до следующего yield, это будет продолжаться до тех пор пока функция не будет закончена, и тогда следующий вызов next вернёт ошибку
# по элементам генератора можно пройти только 1 раз
