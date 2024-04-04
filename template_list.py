from typing import Generator, Generic, Type, TypeVar

T = TypeVar('T')
class TemplateList(Generic[T]):
    item_type: Type[T]  # Define the expected type of items the class will handle

    @classmethod
    def all(cls) -> Generator[T, None, None]:
        for attr in dir(cls):
            if isinstance(getattr(cls, attr), cls.item_type):
                yield getattr(cls, attr)

    @classmethod
    def by_name(cls, name: str) -> T:
        for item in cls.all():
            if item.name == name:  #type: ignore
                return item
        raise KeyError(f'No item with name {name}')