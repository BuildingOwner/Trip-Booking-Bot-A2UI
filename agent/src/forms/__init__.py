"""폼 생성기 패키지

JSON 설정 기반의 동적 폼 생성 시스템.
forms/config/*.json 파일을 추가하면 자동으로 새 폼 타입이 등록됩니다.
"""

from .generator import DynamicFormGenerator, get_form_generator

# 레거시 호환성을 위해 기존 클래스도 export (추후 삭제 예정)
from .base import BaseFormGenerator

__all__ = [
    "DynamicFormGenerator",
    "get_form_generator",
    "BaseFormGenerator",
]
