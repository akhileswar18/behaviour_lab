from collections.abc import Iterable
from typing import Generic, Optional, TypeVar

from sqlmodel import Session, select

T = TypeVar("T")


class RepositoryBase(Generic[T]):
    def __init__(self, session: Session):
        self.session = session

    def add(self, obj: T) -> T:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def list_all(self, model: type[T]) -> list[T]:
        return list(self.session.exec(select(model)))

    def add_many(self, objs: Iterable[T]) -> None:
        for obj in objs:
            self.session.add(obj)
        self.session.commit()

    def get_optional(self, model: type[T], obj_id) -> Optional[T]:
        return self.session.get(model, obj_id)
