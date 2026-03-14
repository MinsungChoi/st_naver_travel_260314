import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
from datetime import datetime, timedelta
import io
import re

# API 모듈 로드
from naver_api import (
    get_datalab_trend, 
    get_search_results, 
    get_search_results_with_period,
    get_datalab_demographic,
    extract_keywords,
    CLIENT_ID, 
    CLIENT_SECRET
)

# 페이지 설정
st.set_page_config(page_title="항공/여행 360 프리미엄 인사이트", layout="wide", page_icon="✈️")

# CSS 커스텀 스타일링 (Reference Image Style)
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #f1f3f9;
        border-radius: 5px 5px 0 0;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] { background-color: #4e73df; color: white !important; }
    .download-btn { float: right; }
    </style>
    """, unsafe_allow_html=True)

# 유틸리티: HTML 태그 제거
def clean_html(text):
    return re.sub(r'<[^>]*>', '', text)

# 유틸리티: CSV 다운로드 버튼 생성
def download_button(df, filename):
    csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label=f"📥 {filename} 다운로드 (CSV)",
        data=csv,
        file_name=f"{filename}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key=f"btn_{filename}_{hash(filename)}"
    )

# 사이드바 설정
st.sidebar.title("✈️ Trend Intelligence")
if CLIENT_ID and CLIENT_SECRET:
    st.sidebar.success(f"✅ API 연동 활성화")
else:
    st.sidebar.error("❌ API 키 미설정")

st.sidebar.divider()
raw_keywords = st.sidebar.text_area("분석 키워드 (쉼표 구분)", value="인천공항, 제주여행, 일본여행")
keywords = [k.strip() for k in raw_keywords.split(",") if k.strip()]

col_d1, col_d2 = st.sidebar.columns(2)
with col_d1:
    start_dt = st.date_input("시작일", datetime.now() - timedelta(days=90))
with col_d2:
    end_dt = st.date_input("종료일", datetime.now())

time_unit = st.sidebar.selectbox("단위", ['month', 'week', 'daily'], index=1)

# 날짜 객체 변환
start_date_obj = datetime.combine(start_dt, datetime.min.time())
end_date_obj = datetime.combine(end_dt, datetime.max.time())

# 메인 헤더
st.title("🌐 항공/여행 비즈니스 인텔리전스 360")
st.markdown(f"**실시간 데이터 스트리밍:** `{', '.join(keywords)}` | `{start_dt}` ~ `{end_dt}`")

# 상단 핵심 지표 (Metrics)
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.metric("수집 키워드", f"{len(keywords)}건", delta="Active")
with m_col2:
    st.metric("분석 기간", f"{(end_dt - start_dt).days}일", delta="Time Range")
with m_col3:
    st.metric("데이터 소스", "Naver 5.0", delta="Real-time")
with m_col4:
    st.metric("수집 일자", datetime.now().strftime('%Y-%m-%d'))

# 탭 구성
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 트렌드 & 상관분석", 
    "🛍️ 쇼핑 트렌드 리포트", 
    "🗣️ 소셜 보이스 (Keywords)", 
    "🔬 데이터사이언스 EDA"
])

# 데이터 홀더
df_trend = pd.DataFrame()

# --- Tab 1: 트렌드 & 상관분석 ---
with tab1:
    st.subheader("📍 통합 검색 점유율 트렌드")
    if keywords:
        with st.spinner("트렌드 분석 중..."):
            df_trend = get_datalab_trend(keywords, start_dt.strftime('%Y-%m-%d'), end_dt.strftime('%Y-%m-%d'), time_unit)
            if not df_trend.empty:
                fig, ax = plt.subplots(figsize=(14, 5))
                df_trend.plot(ax=ax, marker='o', alpha=0.8, linewidth=2)
                ax.set_title("키워드별 상대 검색량 비교", fontsize=15)
                ax.set_facecolor('#f9f9f9')
                st.pyplot(fig)
                download_button(df_trend.reset_index(), "trend_analysis")
            else: st.warning("데이터가 없습니다.")

# --- Tab 2: 쇼핑 트렌드 리포트 ---
with tab2:
    st.subheader("🛒 실시간 쇼핑 상위 노출 상품")
    if keywords:
        shop_k = st.selectbox("상품 분석 키워드", keywords, key="shop_sel")
        with st.spinner("쇼핑 데이터 로드 중..."):
            shop_items = get_search_results(shop_k, 'shop', 20)
            if shop_items:
                shop_data = []
                for i in shop_items:
                    shop_data.append({
                        "상품명": clean_html(i['title']),
                        "가격": int(i['lprice']),
                        "몰이름": i['mallName'],
                        "카테고리": f"{i['category1']} > {i['category2']}",
                        "링크": i['link']
                    })
                df_shop = pd.DataFrame(shop_data)
                
                # 상위 노출 리스트 (Table)
                st.dataframe(df_shop, width='stretch')
                
                # 다운로드 버튼
                download_button(df_shop, f"shopping_trend_{shop_k}")
                
                # 시각화 (몰별 비중)
                st.write("📊 **주요 유통 채널 분포**")
                mall_counts = df_shop['몰이름'].value_counts()
                fig_mall, ax_mall = plt.subplots(figsize=(10, 4))
                mall_counts.plot(kind='barh', ax=ax_mall, color='#f39c12')
                st.pyplot(fig_mall)
            else: st.info("쇼핑 결과가 없습니다.")

# --- Tab 3: 소셜 보이스 (Keywords) ---
with tab3:
    st.subheader("🗣️ 소셜 보이스 분석 (Social Voice Analysis)")
    if keywords:
        social_k = st.selectbox("보이스 분석 키워드", keywords, key="social_sel")
        
        col_s1, col_s2 = st.columns([2, 1])
        
        with col_s1:
            with st.spinner(f"[{start_dt} ~ {end_dt}] 기간 소셜 데이터 분석 중..."):
                # 기간 필터링된 결과 수집 (최대 500건 중 필터링)
                news_items = get_search_results_with_period(social_k, 'news', start_date_obj, end_date_obj, max_pages=5)
                blog_items = get_search_results_with_period(social_k, 'blog', start_date_obj, end_date_obj, max_pages=5)
                combined_items = news_items + blog_items
                
                # 기간 내 데이터 요약 지표
                st.info(f"📊 해당 기간 내 분석된 뉴스: **{len(news_items)}**건 | 블로그: **{len(blog_items)}**건")

                top_keywords = extract_keywords(combined_items, 20)
                if top_keywords:
                    st.write("🔥 **기간 내 가장 많이 언급된 소셜 핵심 단어**")
                    kw_df = pd.DataFrame(top_keywords, columns=['핵심키워드', '빈도수'])
                    
                    fig_kw, ax_kw = plt.subplots(figsize=(12, 6))
                    colors = plt.cm.Oranges(pd.Series(range(len(kw_df))) / len(kw_df))
                    ax_kw.bar(kw_df['핵심키워드'], kw_df['빈도수'], color=colors[::-1])
                    ax_kw.set_title(f"[{start_dt} ~ {end_dt}] 기간 핵심 이슈 분석", fontsize=15)
                    plt.xticks(rotation=45)
                    st.pyplot(fig_kw)
                    
                    download_button(kw_df, f"social_keywords_{social_k}")
                else: st.info("해당 기간 내 분석할 단어가 부족합니다.")
        
        with col_s2:
            st.write(f"🔍 **핵심 뉴스 동향 ({len(news_items)}건 중 상위)")
            if news_items:
                # 뉴스 전체 데이터 다운로드
                news_df = pd.DataFrame([{
                    "날짜": n.get('pubDate', '-'),
                    "제목": clean_html(n['title']),
                    "내용": clean_html(n['description']),
                    "링크": n['link']
                } for n in news_items])
                download_button(news_df, f"full_news_{social_k}")
                
                for n in news_items[:15]:
                    st.markdown(f"• [{clean_html(n['title'])}]({n['link']})")
            else: st.write("기간 내 뉴스가 없습니다.")
                
    st.divider()
    st.subheader(f"📝 최신 소셜 콘텐츠 리포트 (기간 내 {len(blog_items)}건 분석)")
    if blog_items:
        blog_data = []
        for b in blog_items[:20]: # 상위 20개 노출
            blog_data.append({
                "일시": b.get('postdate', '-'), 
                "제목": clean_html(b['title']), 
                "블로거": b['bloggername'], 
                "링크": b['link']
            })
        full_blog_df = pd.DataFrame([{
            "일시": b.get('postdate', '-'), 
            "제목": clean_html(b['title']), 
            "블로거": b['bloggername'],
            "내용": clean_html(b['description']),
            "링크": b['link']
        } for b in blog_items])
        
        st.table(blog_data)
        download_button(full_blog_df, f"full_blog_report_{social_k}")
    else:
        st.write("기간 내 블로그 포스트가 없습니다.")

# --- Tab 4: 데이터사이언스 EDA ---
with tab4:
    st.subheader("🔬 통계 기반 행동 분석")
    if not df_trend.empty:
        c_eda1, c_eda2 = st.columns(2)
        with c_eda1:
            st.write("📊 **기술 통계 매트릭스**")
            st.dataframe(df_trend.describe().T.style.highlight_max(axis=0, color='#d4edda'), width='stretch')
        with c_eda2:
            st.write("📉 **키워드 상관관계 (Heatmap)**")
            if len(keywords) > 1:
                st.dataframe(df_trend.corr().style.background_gradient(cmap='RdYlGn'), width='stretch')
            else: st.info("상관분석을 위한 데이터가 부족합니다.")
        
        # 전체 분석 데이터 다운로드
        st.divider()
        st.write("💾 **전체 분석 데이터셋 통합 추출**")
        download_button(df_trend.reset_index(), "full_eda_dataset")
    else: st.error("기본 탭에서 데이터를 먼저 확인해 주세요.")
