"""기본 폼 생성기"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseFormGenerator(ABC):
    """폼 생성기 기본 클래스"""

    @abstractmethod
    def generate(self, entities: Optional[dict] = None) -> list[dict]:
        """A2UI 메시지 리스트 반환

        Args:
            entities: 추출된 엔티티 (departure, arrival, departureDate 등)
        """
        pass

    def create_surface(self, surface_id: str) -> dict:
        """Surface 생성 메시지"""
        return {
            "createSurface": {
                "surfaceId": surface_id,
                "catalogId": "travel-booking"
            }
        }

    def delete_surface(self, surface_id: str) -> dict:
        """Surface 삭제 메시지"""
        return {
            "deleteSurface": {
                "surfaceId": surface_id
            }
        }
