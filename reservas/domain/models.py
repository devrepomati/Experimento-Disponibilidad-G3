from enum import Enum
from typing import List, Optional


class ReserveStatus(str, Enum):
    CREADA = "CREADA"
    BLOQUEADA = "BLOQUEADA"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    EXPIRADA = "EXPIRADA"


class TripOperatorType(str, Enum):
    HOTEL = "HOTEL"
    HOSTAL = "HOSTAL"
    OPERADOR_TURISTICO = "OPERADOR_TURISTICO"
    AGENCIA_VIAJES = "AGENCIA_VIAJES"
    AEROLINEA = "AEROLINEA"


class TripStatus(str, Enum):
    BORRADOR = "BORRADOR"
    COTIZADO = "COTIZADO"
    CHECKING_OUT = "CHECKING_OUT"
    PAYED = "PAYED"
    CANCELLED = "CANCELLED"


class TripOperator:
    def __init__(self, operator_id: str, name: str, operator_type: TripOperatorType):
        self.operator_id = operator_id
        self.name = name
        self.operator_type = operator_type


class TripItem:
    def __init__(self, item_id: str, description: str, quantity: int, price: float):
        self.item_id = item_id
        self.description = description
        self.quantity = quantity
        self.price = price


class Trip:
    def __init__(
        self,
        trip_id: str,
        operator: TripOperator,
        items: List[TripItem],
        status: TripStatus = TripStatus.BORRADOR,
    ):
        self.trip_id = trip_id
        self.operator = operator
        self.items = items
        self.status = status


class Reserve:
    def __init__(
        self,
        reserve_id: str,
        username: str,
        identificacion: str,
        trips: List[Trip],
        status: ReserveStatus = ReserveStatus.CREADA,
    ):
        self.reserve_id = reserve_id
        self.username = username
        self.identificacion = identificacion
        self.trips = trips
        self.status = status