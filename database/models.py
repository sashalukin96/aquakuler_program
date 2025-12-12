from datetime import datetime
from typing import Annotated
from sqlalchemy import Column, Integer, String, Float, DateTime, func, ForeignKey
from sqlalchemy.orm import  Mapped, mapped_column
from database.db import Base


intpk = Annotated[int, mapped_column(primary_key=True)]


class Product(Base):
	__tablename__ = "Товары"

	id_product : Mapped[intpk]
	name_product : Mapped[str]
	price : Mapped[int]


class Client(Base):
	__tablename__ = "Клиенты"

	id_client : Mapped[intpk]
	name : Mapped[str]
	address : Mapped[str]
	contact_person : Mapped[str]
	email: Mapped[str]
	сontract : Mapped[str]
	note : Mapped[str]
	INN : Mapped[int]
	phone : Mapped[int]


class Staff(Base):
	__tablename__ = "Сотрудники"

	id_staff : Mapped[intpk]
	full_name : Mapped[str]
	address_staff : Mapped[str]
	passport : Mapped[str]
	phone: Mapped[int]
	id_post : Mapped[int] = mapped_column(ForeignKey("Должности.id_post"))


class Post(Base):
	__tablename__ = "Должности"

	id_post : Mapped[intpk]
	name_post : Mapped[str]


class ListOrderedGoods(Base):
	__tablename__ = "Список заказанных товаров"

	id_list : Mapped[intpk]
	id_product : Mapped[int] = mapped_column(ForeignKey("Товары.id_product", ondelete="CASCADE"))
	id_order : Mapped[int] = mapped_column(ForeignKey("Заказы.id_order", ondelete="CASCADE"))
	count_product : Mapped[int]


class Order(Base):
	__tablename__ = "Заказы"

	id_order : Mapped[intpk]
	status_order : Mapped[str]
	id_staff : Mapped[int] = mapped_column(ForeignKey("Сотрудники.id_staff"))
	id_client : Mapped[int] = mapped_column(ForeignKey("Клиенты.id_client"))
	price_order : Mapped[int]
	Date_order : Mapped[datetime]











