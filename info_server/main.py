from fastapi import FastAPI
from enum import Enum
from pydantic import BaseModel


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

#тип, когда нужно чтобы после слеша тоже был путь
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}

#приме параметров после знака ? в URL (по умолчанию всегда строки, но если ставим типы, то автоматически конвертируются и валидируются)
#а также необязательного параметра
@app.get("/itemongo/")
async def query_params_ex(nonessential: int | None, skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

""" 
Использование пайдантик для валидации тела запроса  
"""
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    
    
@app.post("/items/")
async def create_item(item: Item):
    return item