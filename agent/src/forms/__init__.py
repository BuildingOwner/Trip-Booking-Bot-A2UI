"""폼 생성기 패키지"""

from .flight import FlightFormGenerator
from .hotel import HotelFormGenerator
from .car import CarFormGenerator
from .base import BaseFormGenerator


def get_form_generator(travel_type: str) -> BaseFormGenerator | None:
    """여행 타입에 맞는 폼 생성기 반환"""
    generators = {
        "flight": FlightFormGenerator,
        "hotel": HotelFormGenerator,
        "car": CarFormGenerator,
    }

    generator_class = generators.get(travel_type)
    if generator_class:
        return generator_class()
    return None
