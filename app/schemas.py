from pydantic import BaseModel

# Именно пайдантик модели
# И внутри Пайдантик моделей, которые будут представлять и объекты БД нужно добавить класс Config с единственным параметром orm_module = True
# Данная настройка сделает так, что пайдантик будет читать информацию, даже если она не dict
# И это как раз соединяет пайдантик и модели БД и позволяет использовать пайдантик модели в качестве типов ответа, возвращая модели базы данных


class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        from_attributes = True
