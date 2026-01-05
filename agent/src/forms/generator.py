"""동적 폼 생성기 - JSON 설정 기반"""

import json
import copy
from pathlib import Path
from typing import Optional, Any


class DynamicFormGenerator:
    """JSON 설정 파일을 읽어서 A2UI 메시지를 생성하는 동적 폼 생성기"""

    CONFIG_DIR = Path(__file__).parent / "config"

    def __init__(self, form_type: str):
        """
        Args:
            form_type: 폼 타입 (flight, hotel, car 등)
        """
        self.form_type = form_type
        self.config = self._load_config(form_type)

    def _load_config(self, form_type: str) -> dict:
        """JSON 설정 파일 로드"""
        config_path = self.CONFIG_DIR / f"{form_type}.json"
        if not config_path.exists():
            raise FileNotFoundError(f"Form config not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def generate(self, entities: Optional[dict] = None) -> list[dict]:
        """A2UI 메시지 리스트 생성

        Args:
            entities: 추출된 엔티티 (사용자 입력에서 추출한 값들)

        Returns:
            A2UI 메시지 리스트 [createSurface, updateComponents, updateDataModel]
        """
        entities = entities or {}
        messages = []

        # 1. Surface 생성
        messages.append({
            "createSurface": {
                "surfaceId": self.config["surfaceId"],
                "catalogId": self.config.get("catalogId", "travel-booking")
            }
        })

        # 2. 컴포넌트 업데이트
        messages.append({
            "updateComponents": {
                "surfaceId": self.config["surfaceId"],
                "components": self.config["components"]
            }
        })

        # 3. 데이터 모델 업데이트
        messages.append({
            "updateDataModel": {
                "surfaceId": self.config["surfaceId"],
                "operations": self._build_data_operations(entities)
            }
        })

        return messages

    def _build_data_operations(self, entities: dict) -> list[dict]:
        """데이터 모델 초기화 연산 생성"""
        operations = []

        # 기본 데이터 모델 복사 (원본 수정 방지)
        data_model = copy.deepcopy(self.config.get("dataModel", {}))

        # entities를 데이터 모델에 매핑
        entity_mapping = self.config.get("entityMapping", {})
        for entity_key, model_path in entity_mapping.items():
            if entity_key in entities:
                self._set_nested_value(data_model, model_path, entities[entity_key])

        # 각 최상위 키를 별도 operation으로 추가
        for key, value in data_model.items():
            operations.append({
                "op": "add",
                "path": f"/{key}",
                "value": value
            })

        # 옵션 데이터 추가 (airports, cities 등)
        options = self.config.get("options", {})
        for option_key, option_value in options.items():
            operations.append({
                "op": "add",
                "path": f"/{option_key}",
                "value": option_value
            })

        return operations

    def _set_nested_value(self, obj: dict, path: str, value: Any) -> None:
        """중첩 객체에 값 설정 (예: "flight.passengers.adults")"""
        keys = path.split(".")
        current = obj

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # 타입 검증
        final_key = keys[-1]
        if final_key in current:
            expected_type = type(current[final_key])
            if expected_type == int and isinstance(value, str):
                try:
                    value = int(value)
                except ValueError:
                    pass
            elif expected_type == bool and isinstance(value, str):
                value = value.lower() in ("true", "1", "yes")

        current[final_key] = value

    @classmethod
    def get_available_forms(cls) -> list[str]:
        """사용 가능한 폼 타입 목록 반환"""
        forms = []
        for config_file in cls.CONFIG_DIR.glob("*.json"):
            forms.append(config_file.stem)
        return forms

    @classmethod
    def get_form_metadata(cls, form_type: str) -> dict:
        """폼 메타데이터 반환 (id, label, icon)"""
        config_path = cls.CONFIG_DIR / f"{form_type}.json"
        if not config_path.exists():
            return {}

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        return {
            "id": config.get("id", form_type),
            "label": config.get("label", form_type),
            "icon": config.get("icon", "default"),
            "surfaceId": config.get("surfaceId", f"{form_type}-booking")
        }

    @classmethod
    def get_all_form_metadata(cls) -> list[dict]:
        """모든 폼의 메타데이터 반환"""
        return [cls.get_form_metadata(form_type) for form_type in cls.get_available_forms()]


def get_form_generator(form_type: str) -> DynamicFormGenerator | None:
    """폼 타입에 맞는 생성기 반환 (하위 호환성)"""
    try:
        return DynamicFormGenerator(form_type)
    except FileNotFoundError:
        return None
