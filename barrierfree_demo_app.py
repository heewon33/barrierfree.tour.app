import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic

st.set_page_config(page_title="♿ 배리어프리 관광지 추천 앱", layout="wide")
st.title("♿ 배리어프리 관광경로 추천 앱 (샘플 버전)")

# 사용자 위치
user_lat = st.number_input("📍 현재 위치 위도", value=37.5665)
user_lon = st.number_input("📍 현재 위치 경도", value=126.9780)
radius_km = st.slider("📏 추천 반경 (km)", 1, 50, 10)
user_location = (user_lat, user_lon)

# 샘플 데이터
sample_data = [
    {"관광지": "서울역사박물관", "위도": 37.5701, "경도": 126.9685, "WCHAIR_HOLD_AT": "Y", "DSPSN_TOILET_AT": "Y"},
    {"관광지": "국립중앙박물관", "위도": 37.5230, "경도": 126.9809, "WCHAIR_HOLD_AT": "Y", "DSPSN_TOILET_AT": "Y"},
    {"관광지": "세종문화회관", "위도": 37.5725, "경도": 126.9768, "WCHAIR_HOLD_AT": "Y", "DSPSN_TOILET_AT": "N"},
    {"관광지": "예술의전당", "위도": 37.4809, "경도": 127.0116, "WCHAIR_HOLD_AT": "N", "DSPSN_TOILET_AT": "Y"},
    {"관광지": "국립현대미술관 서울관", "위도": 37.5776, "경도": 126.9806, "WCHAIR_HOLD_AT": "Y", "DSPSN_TOILET_AT": "Y"},
]
df = pd.DataFrame(sample_data)

# 필터
filter_options = {
    "WCHAIR_HOLD_AT": "♿ 휠체어 이용 가능",
    "DSPSN_TOILET_AT": "🚻 장애인 화장실"
}
selected_filters = st.multiselect(
    "🧩 적용할 조건을 선택하세요:",
    options=list(filter_options.keys()),
    format_func=lambda x: filter_options[x]
)

# 필터링
for f in selected_filters:
    df = df[df[f] == "Y"]

# 거리 계산
df["거리"] = df.apply(lambda row: geodesic(user_location, (row["위도"], row["경도"])).km, axis=1)
result_df = df[df["거리"] <= radius_km].sort_values("거리")

st.success(f"✅ 추천 관광지 수: {len(result_df)}개")

# 지도 시각화
m = folium.Map(location=user_location, zoom_start=13)
folium.Marker(user_location, tooltip="📍 현재 위치", icon=folium.Icon(color="blue")).add_to(m)

route = [user_location]
for _, row in result_df.iterrows():
    folium.Marker(
        location=(row["위도"], row["경도"]),
        tooltip=row["관광지"],
        icon=folium.Icon(color="green")
    ).add_to(m)
    route.append((row["위도"], row["경도"]))

if len(route) > 1:
    folium.PolyLine(route, color="blue", weight=4).add_to(m)

folium_static(m)
