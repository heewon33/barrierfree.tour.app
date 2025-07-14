import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic

st.set_page_config(page_title="배리어프리 관광경로 추천", layout="wide")
st.title("♿ 배리어프리 관광경로 추천 앱")

# 사용자 입력
col1, col2, col3 = st.columns(3)
with col1:
    user_lat = st.number_input("📍 현재 위치 위도", value=37.5665)
with col2:
    user_lon = st.number_input("📍 현재 위치 경도", value=126.9780)
with col3:
    radius_km = st.slider("📏 추천 반경 (km)", 1, 100, 30)

user_location = (user_lat, user_lon)

# 데이터 로딩
file_path = "C:/Users/simam/Downloads/KC_DSPSN_CLTUR_ART_TRRSRT_2023 (1).csv"
bf_df = pd.read_csv(file_path)
bf_df = bf_df.rename(columns={"LC_LA": "위도", "LC_LO": "경도"})
bf_df = bf_df.dropna(subset=["위도", "경도"])

# 관광지명 추정
name_col = [c for c in bf_df.columns if "NM" in c or "명" in c]
if name_col:
    bf_df["관광지"] = bf_df[name_col[0]].astype(str).str.strip()
else:
    bf_df["관광지"] = "이름없음"

# 배리어프리 필터 목록 및 설명
filter_options = {
    "WCHAIR_HOLD_AT": "♿ 휠체어 보유 여부",
    "DSPSN_TOILET_AT": "🚻 장애인 화장실 유무",
    "DSPSN_PRKPLCE_AT": "🅿️ 장애인 주차장 유무",
    "GUID_DOG_ACP_POSBL_AT": "🐶 안내견 동반 가능 여부",
    "BRLL_GUID_AT": "🔠 점자 안내 여부",
    "KLANG_VIC_GUID_AT": "🔊 청각장애인 안내 시스템"
}
st.markdown("### 🔎 배리어프리 조건별 필터 목록:")
for key, label in filter_options.items():
    st.markdown(f"- {label} (`{key}`)")

selected_filters = st.multiselect(
    "적용할 배리어프리 조건을 모두 선택하세요:",
    options=list(filter_options.keys()),
    format_func=lambda x: filter_options[x]
)

# 필터 적용
for col in selected_filters:
    if col in bf_df.columns:
        bf_df = bf_df[bf_df[col].astype(str).str.upper() == 'Y']

st.markdown(f"조건 {', '.join([filter_options[c] for c in selected_filters])} 을(를) 모두 만족하는 관광지 수: **{len(bf_df):,}개**")

# 거리 계산 및 추천 관광지 추출
def calc_distance(row):
    try:
        return geodesic(user_location, (row["위도"], row["경도"])).km
    except:
        return None

bf_df["거리"] = bf_df.apply(calc_distance, axis=1)
result_df = bf_df[(bf_df["거리"] <= radius_km) & (bf_df["거리"].notnull())]
result_df = result_df.sort_values("거리").head(20)

st.success(f"✅ 최종 추천 관광지 수: {len(result_df)}개")

# 지도 시각화
m = folium.Map(location=user_location, zoom_start=12)
folium.Marker(user_location, tooltip="📍 현재 위치", icon=folium.Icon(color="blue")).add_to(m)

route = [user_location]
for _, row in result_df.iterrows():
    folium.Marker(
        location=(row["위도"], row["경도"]),
        tooltip=row["관광지"],
        icon=folium.Icon(color="green", icon="ok-sign")
    ).add_to(m)
    route.append((row["위도"], row["경도"]))

# 경로 선 연결
if len(route) > 1:
    folium.PolyLine(route, color="blue", weight=4, opacity=0.6).add_to(m)

folium_static(m)
