# A2UI 메시지 스펙

이 문서는 여행 예약 봇에서 사용하는 A2UI 메시지의 상세 스펙을 정의합니다.

---

## 1. 메시지 타입 개요

### Server → Client

| 메시지 | 설명 |
|--------|------|
| `createSurface` | 새 UI Surface 생성 |
| `updateComponents` | 컴포넌트 추가/업데이트 |
| `updateDataModel` | 데이터 모델 업데이트 |
| `deleteSurface` | Surface 제거 |

### Client → Server

| 메시지 | 설명 |
|--------|------|
| `userAction` | 사용자 상호작용 (버튼 클릭, 폼 제출 등) |

---

## 2. 여행 타입 선택 UI

### 2.1 Surface 생성

```json
{
  "createSurface": {
    "surfaceId": "travel-type-selector",
    "catalogId": "travel-booking"
  }
}
```

### 2.2 컴포넌트 정의

```json
{
  "updateComponents": {
    "surfaceId": "travel-type-selector",
    "components": [
      {
        "id": "root",
        "component": "Column",
        "children": ["header", "type-cards"]
      },
      {
        "id": "header",
        "component": "Text",
        "text": "어떤 여행을 계획하고 계신가요?",
        "style": "headline"
      },
      {
        "id": "type-cards",
        "component": "Row",
        "children": ["flight-card", "hotel-card", "car-card", "package-card"]
      },
      {
        "id": "flight-card",
        "component": "Card",
        "children": ["flight-icon", "flight-label"],
        "action": "select-flight"
      },
      {
        "id": "flight-icon",
        "component": "Icon",
        "icon": "airplane"
      },
      {
        "id": "flight-label",
        "component": "Text",
        "text": "항공권"
      },
      {
        "id": "hotel-card",
        "component": "Card",
        "children": ["hotel-icon", "hotel-label"],
        "action": "select-hotel"
      },
      {
        "id": "hotel-icon",
        "component": "Icon",
        "icon": "hotel"
      },
      {
        "id": "hotel-label",
        "component": "Text",
        "text": "호텔"
      },
      {
        "id": "car-card",
        "component": "Card",
        "children": ["car-icon", "car-label"],
        "action": "select-car"
      },
      {
        "id": "car-icon",
        "component": "Icon",
        "icon": "car"
      },
      {
        "id": "car-label",
        "component": "Text",
        "text": "렌터카"
      },
      {
        "id": "package-card",
        "component": "Card",
        "children": ["package-icon", "package-label"],
        "action": "select-package"
      },
      {
        "id": "package-icon",
        "component": "Icon",
        "icon": "package"
      },
      {
        "id": "package-label",
        "component": "Text",
        "text": "패키지"
      }
    ]
  }
}
```

### 2.3 userAction (타입 선택 시)

```json
{
  "userAction": {
    "surfaceId": "travel-type-selector",
    "componentId": "flight-card",
    "action": "select-flight"
  }
}
```

---

## 3. 항공권 예약 폼

### 3.1 Surface 생성

```json
{
  "createSurface": {
    "surfaceId": "flight-booking",
    "catalogId": "travel-booking"
  }
}
```

### 3.2 컴포넌트 정의

```json
{
  "updateComponents": {
    "surfaceId": "flight-booking",
    "components": [
      {
        "id": "root",
        "component": "Column",
        "children": ["header", "trip-type", "route", "dates", "passengers", "class", "actions"]
      },
      {
        "id": "header",
        "component": "Text",
        "text": "항공권 검색",
        "style": "headline"
      },
      {
        "id": "trip-type",
        "component": "ChoicePicker",
        "label": "여행 유형",
        "mode": "single",
        "options": [
          {"value": "roundtrip", "label": "왕복"},
          {"value": "oneway", "label": "편도"}
        ],
        "binding": "/flight/tripType"
      },
      {
        "id": "route",
        "component": "Row",
        "children": ["departure", "swap-btn", "arrival"]
      },
      {
        "id": "departure",
        "component": "ChoicePicker",
        "label": "출발지",
        "options": "/airports",
        "binding": "/flight/departure",
        "searchable": true
      },
      {
        "id": "swap-btn",
        "component": "Button",
        "icon": "swap",
        "variant": "icon",
        "action": "swap-route"
      },
      {
        "id": "arrival",
        "component": "ChoicePicker",
        "label": "도착지",
        "options": "/airports",
        "binding": "/flight/arrival",
        "searchable": true
      },
      {
        "id": "dates",
        "component": "Row",
        "children": ["departure-date", "return-date"]
      },
      {
        "id": "departure-date",
        "component": "DateTimeInput",
        "label": "출발일",
        "mode": "date",
        "binding": "/flight/departureDate",
        "minDate": "today"
      },
      {
        "id": "return-date",
        "component": "DateTimeInput",
        "label": "귀국일",
        "mode": "date",
        "binding": "/flight/returnDate",
        "minDate": "/flight/departureDate",
        "visible": "/flight/tripType == 'roundtrip'"
      },
      {
        "id": "passengers",
        "component": "Row",
        "children": ["adults", "children", "infants"]
      },
      {
        "id": "adults",
        "component": "Stepper",
        "label": "성인",
        "min": 1,
        "max": 9,
        "binding": "/flight/passengers/adults"
      },
      {
        "id": "children",
        "component": "Stepper",
        "label": "아동 (2-11세)",
        "min": 0,
        "max": 9,
        "binding": "/flight/passengers/children"
      },
      {
        "id": "infants",
        "component": "Stepper",
        "label": "유아 (0-2세)",
        "min": 0,
        "max": 9,
        "binding": "/flight/passengers/infants"
      },
      {
        "id": "class",
        "component": "ChoicePicker",
        "label": "좌석 등급",
        "options": [
          {"value": "economy", "label": "이코노미"},
          {"value": "premium", "label": "프리미엄 이코노미"},
          {"value": "business", "label": "비즈니스"},
          {"value": "first", "label": "퍼스트"}
        ],
        "binding": "/flight/class"
      },
      {
        "id": "actions",
        "component": "Row",
        "children": ["back-btn", "search-btn"]
      },
      {
        "id": "back-btn",
        "component": "Button",
        "label": "이전",
        "variant": "outlined",
        "action": "back"
      },
      {
        "id": "search-btn",
        "component": "Button",
        "label": "항공편 검색",
        "variant": "filled",
        "action": "search-flights"
      }
    ]
  }
}
```

### 3.3 초기 데이터 모델

```json
{
  "updateDataModel": {
    "surfaceId": "flight-booking",
    "operations": [
      {
        "op": "add",
        "path": "/flight",
        "value": {
          "tripType": "roundtrip",
          "departure": "",
          "arrival": "",
          "departureDate": "",
          "returnDate": "",
          "passengers": {
            "adults": 1,
            "children": 0,
            "infants": 0
          },
          "class": "economy"
        }
      },
      {
        "op": "add",
        "path": "/airports",
        "value": [
          {"value": "ICN", "label": "인천국제공항 (ICN)"},
          {"value": "GMP", "label": "김포국제공항 (GMP)"},
          {"value": "CJU", "label": "제주국제공항 (CJU)"},
          {"value": "PUS", "label": "김해국제공항 (PUS)"},
          {"value": "NRT", "label": "도쿄 나리타 (NRT)"},
          {"value": "KIX", "label": "오사카 간사이 (KIX)"},
          {"value": "BKK", "label": "방콕 수완나품 (BKK)"}
        ]
      }
    ]
  }
}
```

### 3.4 userAction (검색 버튼 클릭)

```json
{
  "userAction": {
    "surfaceId": "flight-booking",
    "componentId": "search-btn",
    "action": "search-flights",
    "data": {
      "flight": {
        "tripType": "roundtrip",
        "departure": "ICN",
        "arrival": "CJU",
        "departureDate": "2025-01-15",
        "returnDate": "2025-01-18",
        "passengers": {
          "adults": 2,
          "children": 0,
          "infants": 0
        },
        "class": "economy"
      }
    }
  }
}
```

---

## 4. 호텔 예약 폼

### 4.1 컴포넌트 정의

```json
{
  "updateComponents": {
    "surfaceId": "hotel-booking",
    "components": [
      {
        "id": "root",
        "component": "Column",
        "children": ["header", "destination", "dates", "rooms", "guests", "options", "actions"]
      },
      {
        "id": "header",
        "component": "Text",
        "text": "호텔 검색",
        "style": "headline"
      },
      {
        "id": "destination",
        "component": "TextField",
        "label": "목적지",
        "hint": "도시, 지역 또는 호텔명",
        "binding": "/hotel/destination",
        "icon": "search"
      },
      {
        "id": "dates",
        "component": "Row",
        "children": ["checkin", "checkout"]
      },
      {
        "id": "checkin",
        "component": "DateTimeInput",
        "label": "체크인",
        "mode": "date",
        "binding": "/hotel/checkinDate",
        "minDate": "today"
      },
      {
        "id": "checkout",
        "component": "DateTimeInput",
        "label": "체크아웃",
        "mode": "date",
        "binding": "/hotel/checkoutDate",
        "minDate": "/hotel/checkinDate"
      },
      {
        "id": "rooms",
        "component": "Stepper",
        "label": "객실 수",
        "min": 1,
        "max": 10,
        "binding": "/hotel/rooms"
      },
      {
        "id": "guests",
        "component": "Row",
        "children": ["adults", "children"]
      },
      {
        "id": "adults",
        "component": "Stepper",
        "label": "성인",
        "min": 1,
        "max": 10,
        "binding": "/hotel/guests/adults"
      },
      {
        "id": "children",
        "component": "Stepper",
        "label": "아동",
        "min": 0,
        "max": 10,
        "binding": "/hotel/guests/children"
      },
      {
        "id": "options",
        "component": "Column",
        "children": ["breakfast", "free-cancel", "pet-friendly"]
      },
      {
        "id": "breakfast",
        "component": "CheckBox",
        "label": "조식 포함",
        "binding": "/hotel/options/breakfast"
      },
      {
        "id": "free-cancel",
        "component": "CheckBox",
        "label": "무료 취소 가능",
        "binding": "/hotel/options/freeCancel"
      },
      {
        "id": "pet-friendly",
        "component": "CheckBox",
        "label": "반려동물 동반 가능",
        "binding": "/hotel/options/petFriendly"
      },
      {
        "id": "actions",
        "component": "Row",
        "children": ["back-btn", "search-btn"]
      },
      {
        "id": "back-btn",
        "component": "Button",
        "label": "이전",
        "variant": "outlined",
        "action": "back"
      },
      {
        "id": "search-btn",
        "component": "Button",
        "label": "호텔 검색",
        "variant": "filled",
        "action": "search-hotels"
      }
    ]
  }
}
```

### 4.2 초기 데이터 모델

```json
{
  "updateDataModel": {
    "surfaceId": "hotel-booking",
    "operations": [
      {
        "op": "add",
        "path": "/hotel",
        "value": {
          "destination": "",
          "checkinDate": "",
          "checkoutDate": "",
          "rooms": 1,
          "guests": {
            "adults": 2,
            "children": 0
          },
          "options": {
            "breakfast": false,
            "freeCancel": false,
            "petFriendly": false
          }
        }
      }
    ]
  }
}
```

---

## 5. 렌터카 예약 폼

### 5.1 컴포넌트 정의

```json
{
  "updateComponents": {
    "surfaceId": "car-rental",
    "components": [
      {
        "id": "root",
        "component": "Column",
        "children": ["header", "same-location", "pickup", "dropoff", "dates", "car-type", "options", "actions"]
      },
      {
        "id": "header",
        "component": "Text",
        "text": "렌터카 검색",
        "style": "headline"
      },
      {
        "id": "same-location",
        "component": "CheckBox",
        "label": "동일 장소 반납",
        "binding": "/car/sameLocation"
      },
      {
        "id": "pickup",
        "component": "ChoicePicker",
        "label": "픽업 장소",
        "options": "/locations",
        "binding": "/car/pickupLocation",
        "searchable": true
      },
      {
        "id": "dropoff",
        "component": "ChoicePicker",
        "label": "반납 장소",
        "options": "/locations",
        "binding": "/car/dropoffLocation",
        "searchable": true,
        "visible": "/car/sameLocation == false"
      },
      {
        "id": "dates",
        "component": "Row",
        "children": ["pickup-datetime", "dropoff-datetime"]
      },
      {
        "id": "pickup-datetime",
        "component": "DateTimeInput",
        "label": "픽업 일시",
        "mode": "datetime",
        "binding": "/car/pickupDateTime",
        "minDate": "today"
      },
      {
        "id": "dropoff-datetime",
        "component": "DateTimeInput",
        "label": "반납 일시",
        "mode": "datetime",
        "binding": "/car/dropoffDateTime",
        "minDate": "/car/pickupDateTime"
      },
      {
        "id": "car-type",
        "component": "ChoicePicker",
        "label": "차종",
        "options": [
          {"value": "compact", "label": "소형"},
          {"value": "mid", "label": "중형"},
          {"value": "full", "label": "대형"},
          {"value": "suv", "label": "SUV"},
          {"value": "van", "label": "밴/미니밴"},
          {"value": "luxury", "label": "프리미엄"}
        ],
        "binding": "/car/type"
      },
      {
        "id": "options",
        "component": "Column",
        "children": ["insurance", "gps", "child-seat"]
      },
      {
        "id": "insurance",
        "component": "CheckBox",
        "label": "완전 자차 보험",
        "binding": "/car/options/insurance"
      },
      {
        "id": "gps",
        "component": "CheckBox",
        "label": "GPS 네비게이션",
        "binding": "/car/options/gps"
      },
      {
        "id": "child-seat",
        "component": "CheckBox",
        "label": "유아용 카시트",
        "binding": "/car/options/childSeat"
      },
      {
        "id": "actions",
        "component": "Row",
        "children": ["back-btn", "search-btn"]
      },
      {
        "id": "back-btn",
        "component": "Button",
        "label": "이전",
        "variant": "outlined",
        "action": "back"
      },
      {
        "id": "search-btn",
        "component": "Button",
        "label": "렌터카 검색",
        "variant": "filled",
        "action": "search-cars"
      }
    ]
  }
}
```

### 5.2 초기 데이터 모델

```json
{
  "updateDataModel": {
    "surfaceId": "car-rental",
    "operations": [
      {
        "op": "add",
        "path": "/car",
        "value": {
          "sameLocation": true,
          "pickupLocation": "",
          "dropoffLocation": "",
          "pickupDateTime": "",
          "dropoffDateTime": "",
          "type": "mid",
          "options": {
            "insurance": false,
            "gps": false,
            "childSeat": false
          }
        }
      },
      {
        "op": "add",
        "path": "/locations",
        "value": [
          {"value": "ICN", "label": "인천공항"},
          {"value": "GMP", "label": "김포공항"},
          {"value": "CJU", "label": "제주공항"},
          {"value": "JEJU_CITY", "label": "제주시내"},
          {"value": "SEOGWIPO", "label": "서귀포"}
        ]
      }
    ]
  }
}
```

---

## 6. 검색 결과 리스트

### 6.1 항공편 검색 결과

```json
{
  "updateComponents": {
    "surfaceId": "flight-results",
    "components": [
      {
        "id": "root",
        "component": "Column",
        "children": ["header", "result-list", "actions"]
      },
      {
        "id": "header",
        "component": "Text",
        "text": "검색 결과 (3건)",
        "style": "headline"
      },
      {
        "id": "result-list",
        "component": "List",
        "itemTemplate": "flight-item",
        "binding": "/searchResults"
      },
      {
        "id": "flight-item",
        "component": "Card",
        "children": ["flight-info", "flight-price", "select-btn"]
      },
      {
        "id": "flight-info",
        "component": "Column",
        "children": ["airline", "schedule"]
      },
      {
        "id": "airline",
        "component": "Text",
        "binding": "airline",
        "style": "subtitle"
      },
      {
        "id": "schedule",
        "component": "Text",
        "binding": "schedule"
      },
      {
        "id": "flight-price",
        "component": "Text",
        "binding": "price",
        "style": "price"
      },
      {
        "id": "select-btn",
        "component": "Button",
        "label": "선택",
        "action": "select-flight",
        "actionData": "id"
      },
      {
        "id": "actions",
        "component": "Row",
        "children": ["back-btn"]
      },
      {
        "id": "back-btn",
        "component": "Button",
        "label": "검색 조건 수정",
        "variant": "outlined",
        "action": "back-to-search"
      }
    ]
  }
}
```

### 6.2 검색 결과 데이터

```json
{
  "updateDataModel": {
    "surfaceId": "flight-results",
    "operations": [
      {
        "op": "add",
        "path": "/searchResults",
        "value": [
          {
            "id": "FL001",
            "airline": "대한항공 KE1201",
            "schedule": "08:00 ICN → 09:10 CJU",
            "price": "89,000원"
          },
          {
            "id": "FL002",
            "airline": "아시아나 OZ8941",
            "schedule": "10:30 ICN → 11:40 CJU",
            "price": "95,000원"
          },
          {
            "id": "FL003",
            "airline": "제주항공 7C101",
            "schedule": "14:00 GMP → 15:05 CJU",
            "price": "65,000원"
          }
        ]
      }
    ]
  }
}
```

---

## 7. 예약 완료 UI

```json
{
  "updateComponents": {
    "surfaceId": "booking-confirmation",
    "components": [
      {
        "id": "root",
        "component": "Column",
        "children": ["success-icon", "title", "booking-info", "actions"]
      },
      {
        "id": "success-icon",
        "component": "Icon",
        "icon": "check-circle",
        "size": "large",
        "color": "success"
      },
      {
        "id": "title",
        "component": "Text",
        "text": "예약이 완료되었습니다!",
        "style": "headline"
      },
      {
        "id": "booking-info",
        "component": "Card",
        "children": ["booking-number", "booking-details"]
      },
      {
        "id": "booking-number",
        "component": "Text",
        "binding": "/booking/confirmationNumber",
        "style": "subtitle"
      },
      {
        "id": "booking-details",
        "component": "Text",
        "binding": "/booking/summary"
      },
      {
        "id": "actions",
        "component": "Row",
        "children": ["home-btn", "details-btn"]
      },
      {
        "id": "home-btn",
        "component": "Button",
        "label": "처음으로",
        "variant": "outlined",
        "action": "go-home"
      },
      {
        "id": "details-btn",
        "component": "Button",
        "label": "예약 상세",
        "variant": "filled",
        "action": "view-details"
      }
    ]
  }
}
```

---

## 8. 컴포넌트 레퍼런스

### 8.1 사용되는 컴포넌트 목록

| 컴포넌트 | 용도 | 주요 속성 |
|----------|------|-----------|
| `Column` | 수직 레이아웃 | `children` |
| `Row` | 수평 레이아웃 | `children` |
| `Card` | 카드 컨테이너 | `children`, `action` |
| `Text` | 텍스트 표시 | `text`, `binding`, `style` |
| `Icon` | 아이콘 | `icon`, `size`, `color` |
| `TextField` | 텍스트 입력 | `label`, `hint`, `binding` |
| `ChoicePicker` | 선택 드롭다운 | `options`, `binding`, `searchable` |
| `DateTimeInput` | 날짜/시간 선택 | `mode`, `binding`, `minDate` |
| `Stepper` | 숫자 증감 | `min`, `max`, `binding` |
| `CheckBox` | 체크박스 | `label`, `binding` |
| `Button` | 버튼 | `label`, `variant`, `action` |
| `List` | 동적 리스트 | `itemTemplate`, `binding` |

### 8.2 조건부 속성

| 속성 | 설명 | 예시 |
|------|------|------|
| `visible` | 조건부 표시 | `"/flight/tripType == 'roundtrip'"` |
| `minDate` | 최소 날짜 | `"today"` 또는 `"/flight/departureDate"` |

### 8.3 바인딩 경로

| 경로 형식 | 설명 |
|-----------|------|
| `/flight/tripType` | 절대 경로 (루트 데이터 모델) |
| `airline` | 상대 경로 (List 아이템 내) |
