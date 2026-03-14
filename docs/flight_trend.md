# Naver API 통합 문서: Flight Trend 분석용

본 문서는 `flight_260312` 프로젝트의 항공 트렌드 분석을 위해 네이버 개발자 센터의 주요 API 정보를 정리한 문서입니다.

---

## 1. 네이버 여행/항공권 API 조사 결과

네이버 개발자 센터를 통해 공식적으로 외부 개발자에게 공개된 **'항공권 API'** 또는 **'여행 상품 API'**는 현재 존재하지 않는 것으로 확인되었습니다.

- **조사 내용**: 네이버 항공권 서비스(travel.naver.com)는 내부적으로 GraphQL 기반의 비공개 API를 사용하고 있습니다.
- **활용 대안**: 항공권 직접 데이터 대신, 아래의 **데이터랩(DataLab)** 및 **쇼핑 검색 API**를 활용하여 여행/항공 관련 검색 트렌드 및 쇼핑 클릭 추이를 분석하는 방식으로 접근해야 합니다.

---

## 2. 네이버 데이터랩 (DataLab) API

### 2.1 통합검색어 트렌드
네이버 통합검색에서 발생하는 검색어를 세분화해서 조회할 수 있습니다.
- **특징**:
    - 연령별(5세 단위), 성별, 기기별(PC/모바일) 세분화 가능.
    - 최대 5개의 주제어 세트(주제어당 최대 20개 키워드) 비교 가능.
    - 절대적 수치가 아닌, 요청 기간 내 최고 검색 횟수를 100으로 둔 **상대적 값** 제공.
- **요청 URL**: `https://openapi.naver.com/v1/datalab/search` (POST)

### 2.2 쇼핑인사이트
네이버쇼핑 검색 결과에서 사용자가 클릭한 데이터를 조회합니다.
- **특징**:
    - 쇼핑 분야별(카테고리), 연령별, 성별, 기기별 클릭 트렌드 제공.
    - 특정 카테고리 내 키워드별 클릭 추이 확인 가능.
    - 소상공인의 재고 관리 및 마케팅 타깃 설정에 유용.
- **요청 URL**: 
    - 분야별 트렌드: `https://openapi.naver.com/v1/datalab/shopping/categories` (POST)
    - 키워드별 트렌드: `https://openapi.naver.com/v1/datalab/shopping/category/keywords` (POST)

---

## 3. 네이버 검색 > 쇼핑 API

네이버 쇼핑의 검색 결과를 반환하는 API입니다. 여행 관련 상품(예: 여행 캐리어, 항공권 예약 서비스 상품 등)의 검색 결과를 확인하는 데 활용할 수 있습니다.

- **요청 URL**: 
    - JSON: `https://openapi.naver.com/v1/search/shop.json` (GET)
    - XML: `https://openapi.naver.com/v1/search/shop.xml` (GET)
- **주요 파라미터**:
    - `query`: 검색어 (UTF-8 인코딩)
    - `display`: 검색 결과 출력 건수 (최대 100)
    - `start`: 검색 시작 위치 (최대 1000)
    - `sort`: 정렬 상세 (sim: 유사도순, date: 날짜순, asc/dsc: 가격순)

---

## 4. 오픈 API 이용 가이드 (비로그인 방식)

본 프로젝트에서 활용하려는 데이터랩 및 검색 API는 모두 **'비로그인 방식 오픈 API'**에 해당합니다.

### 4.1 특징
- 네이버 아이디로 로그인을 통한 접근 토큰 발급 과정이 필요 없습니다.
- HTTP 요청 헤더에 **Client ID**와 **Client Secret**만 포함하면 즉시 호출 가능합니다.

### 4.2 호출 시 필수 헤더
| 헤더 필드명 | 값 |
| :--- | :--- |
| `X-Naver-Client-Id` | 내 애플리케이션의 Client ID |
| `X-Naver-Client-Secret` | 내 애플리케이션의 Client Secret |
| `Content-Type` | `application/json` (POST 요청 시) |

### 4.3 오류 코드 참고
- `401 (Unauthorized)` : 클라이언트 아이디/시크릿 오류
- `403 (Forbidden)` : API 권한 설정 오류 또는 호출 한도 초과
- `429 (Too Many Requests)` : 초당 호출 제한 초과
- `500 (Internal Server Error)` : 네이버 서버 내부 오류

---
**문서 생성 일시**: 2026-03-14
**참고 URL**:
- [데이터랩 개요](https://developers.naver.com/products/service-api/datalab/datalab.md)
- [쇼핑인사이트 가이드](https://developers.naver.com/docs/serviceapi/datalab/shopping/shopping.md)
- [쇼핑 검색 API 가이드](https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md)
