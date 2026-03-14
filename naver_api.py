import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드 (스크립트 위치 기반으로 절대 경로 설정)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "").strip()

def get_headers():
    """네이버 API 호출을 위한 공통 헤더 반환"""
    return {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type": "application/json"
    }

def get_datalab_trend(keywords, start_date, end_date, time_unit='month'):
    """
    네이버 데이터랩 통합검색어 트렌드 조회
    :param keywords: 리스트 형태의 키워드 (예: ['인천공항', '항공권'])
    :param start_date: 시작 날짜 (YYYY-MM-DD)
    :param end_date: 종료 날짜 (YYYY-MM-DD)
    :return: 시계열 데이터프레임
    """
    url = "https://openapi.naver.com/v1/datalab/search"
    
    # 주제어 구성
    keyword_groups = [{"groupName": kw, "keywords": [kw]} for kw in keywords]
    
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups
    }
    
    response = requests.post(url, json=body, headers=get_headers())
    
    if response.status_code == 200:
        data = response.json()
        results = data['results']
        
        df_list = []
        for res in results:
            temp_df = pd.DataFrame(res['data'])
            if not temp_df.empty:
                temp_df = temp_df.rename(columns={'ratio': res['title']})
                temp_df = temp_df.set_index('period')
                df_list.append(temp_df)
        
        if df_list:
            final_df = pd.concat(df_list, axis=1)
            final_df.index = pd.to_datetime(final_df.index)
            return final_df
    else:
        # print(f"DataLab API Error [{response.status_code}]: {response.text}")
        pass
    return pd.DataFrame()

def get_datalab_demographic(keywords, start_date, end_date, time_unit='month', device='', gender='', ages=[]):
    """
    네이버 데이터랩 인구통계(성별/연령별) 검색어 트렌드 조회
    """
    url = "https://openapi.naver.com/v1/datalab/search"
    
    keyword_groups = [{"groupName": k, "keywords": [k]} for k in keywords]
    
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups,
        "device": device,
        "gender": gender,
        "ages": ages
    }
    
    response = requests.post(url, json=body, headers=get_headers())
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def get_shopping_insight(category_id, start_date, end_date, time_unit='month', device='', gender='', ages=[]):
    """
    네이버 쇼핑 인사이트 API를 통한 카테고리별 트렌드 조회 (연관어 대용)
    """
    url = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
    
    # 예시 카테고리 ID (면세점/여행 등은 API 가이드 참조 필요)
    # 실제로는 사용자가 선택한 도시/국가와 관련된 카테고리를 매핑해야 함
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "category": category_id,
        "device": device,
        "gender": gender,
        "ages": ages
    }
    
    # 참고: 쇼핑 키워드 API는 별도의 URL과 권한이 필요할 수 있음
    # 여기서는 범용적인 검색 트렌드를 기반으로 시각화함
    return []

def get_search_results(query, category='news', display=5):
    """
    네이버 검색 API 결과 조회 (뉴스, 블로그, 쇼핑)
    :param category: news, blog, shop
    """
    endpoints = {
        'news': 'https://openapi.naver.com/v1/search/news.json',
        'blog': 'https://openapi.naver.com/v1/search/blog.json',
        'shop': 'https://openapi.naver.com/v1/search/shop.json'
    }
    
    url = endpoints.get(category)
    params = {"query": query, "display": display, "sort": "sim"}
    
    response = requests.get(url, params=params, headers=get_headers())
    
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        # print(f"Search API Error ({category}) [{response.status_code}]: {response.text}")
        pass
    return []

def get_search_results_with_period(query, category='news', start_date=None, end_date=None, max_pages=5):
    """
    네이버 검색 API를 사용하여 특정 기간 내의 결과 수집 (최대 max_pages * 100건)
    :param start_date: datetime 객체
    :param end_date: datetime 객체
    """
    endpoints = {
        'news': 'https://openapi.naver.com/v1/search/news.json',
        'blog': 'https://openapi.naver.com/v1/search/blog.json'
    }
    url = endpoints.get(category)
    if not url: return []

    all_items = []
    
    # 네이버 API는 최대 1000등까지만 제공 (start=1000이 한계)
    # 한 번에 100건씩 요청 가능
    for page in range(max_pages):
        params = {
            "query": query,
            "display": 100,
            "start": (page * 100) + 1,
            "sort": "date" # 최신순으로 가져와서 기간 필터링
        }
        
        response = requests.get(url, params=params, headers=get_headers())
        if response.status_code == 200:
            items = response.json().get('items', [])
            if not items: break
            
            # 기간 필터링
            for item in items:
                # 뉴스 pubDate: Tue, 14 Mar 2023 10:00:00 +0900
                # 블로그 postdate: 20230314
                pub_dt = None
                if category == 'news':
                    try:
                        pub_dt = datetime.strptime(item['pubDate'], '%a, %d %b %Y %H:%M:%S +0900')
                    except: pass
                elif category == 'blog':
                    try:
                        pub_dt = datetime.strptime(item['postdate'], '%Y%m%d')
                    except: pass
                
                if pub_dt:
                    # 시간 정규화 (날짜만 비교)
                    pub_date_only = pub_dt.date()
                    if start_date.date() <= pub_date_only <= end_date.date():
                        all_items.append(item)
                    elif pub_date_only < start_date.date():
                        # 최신순 정렬이므로 시작일보다 과거 데이터가 나오면 중단 가능
                        # (단, 가끔 순서가 섞일 수 있으므로 페이지 내에서는 체크 계속)
                        pass
            
            # 마지막 아이템의 날짜가 시작일보다 한참 과거면 루프 종료
            if all_items and pub_dt and pub_dt.date() < start_date.date():
                # 어느 정도 여유를 두고 판단 (뉴스/블로그 특성상 약간의 딜레이 고려)
                if (start_date.date() - pub_dt.date()).days > 7:
                    break
        else:
            break
            
    return all_items

def extract_keywords(items, top_n=10):
    """
    검색 결과 항목들의 제목에서 빈출 키워드 추출 (단순 빈도 기반)
    """
    import re
    from collections import Counter
    
    all_titles = ""
    for item in items:
        # HTML 태그 제거 및 특수문자 제거
        clean_title = re.sub(r'<[^>]*>', '', item['title'])
        clean_title = re.sub(r'[^가-힣a-zA-Z\s]', '', clean_title)
        all_titles += " " + clean_title
        
    words = all_titles.split()
    # 2글자 이상의 의미 있는 단어만 필터링 (조사 등 간단 제거)
    stop_words = ['있는', '대한', '위한', '통해', '관련', '밝혀', '지난', '올해', '최근', '이번', '기자']
    filtered_words = [w for w in words if len(w) > 1 and w not in stop_words]
    
    counts = Counter(filtered_words)
    return counts.most_common(top_n)

if __name__ == "__main__":
    # 모듈 단독 테스트
    print("API 테스트 시작...")
    test_df = get_datalab_trend(['인천공항'], '2023-01-01', '2023-12-31')
    print(test_df.head())
