import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic

st.set_page_config(page_title="♿ 배리어프리 관광지 추천 앱", layout="wide")
st.title("♿ 배리어프리 관광경로 추천 앱 (확장 필터 버전)")

# 사용자 위치 입력
user_lat = st.number_input("📍 현재 위치 위도", value=37.5665)
user_lon = st.number_input("📍 현재 위치 경도", value=126.9780)
radius_km = st.slider("📏 추천 반경 (km)", 1, 50, 10)
user_location = (user_lat, user_lon)

# 샘플 관광지 데이터
sample_data = [
    {
        "관광지": "서울역사박물관", "위도": 37.5701, "경도": 126.9685,
        "WCHAIR_HOLD_AT": "Y", "DSPSN_TOILET_AT": "Y", "DSPSN_PRKPLCE_AT": "Y",
        "GUID_DOG_ACP_POSBL_AT": "Y", "BRLL_GUID_AT": "Y", "KLANG_VIC_GUID_AT": "Y",
        "DSPSN_TOILET_ATMC_DOOR_AT": "Y", "LRGE_PARKNG_POSBL_AT": "N", "FRE_PARKNG_AT": "Y", "ENTRN_PRICE_AT": "N"
    },
    {
        "관광지": "국립중앙박물관", "위도": 37.5230, "경도": 126.9809,
        "WCHAIR_HOLD_AT": "Y", "DSPSN_TOILET_AT": "Y", "DSPSN_PRKPLCE_AT": "Y",
        "GUID_DOG_ACP_POSBL_AT": "Y", "BRLL_GUID_AT": "Y", "KLANG_VIC_GUID_AT": "N",
        "DSPSN_TOILET_ATMC_DOOR_AT": "Y", "LRGE_PARKNG_POSBL_AT": "Y", "FRE_PARKNG_AT": "N", "ENTRN_PRICE_AT": "Y"
    },
    {
        "관광지": "세종문화회관", "위도": 37.5725, "경도": 126.9768,
        "WCHAIR_HOLD_AT": "Y", "DSPSN_TOILET_AT": "N", "DSPSN_PRKPLCE_AT": "Y",
        "GUID_DOG_ACP_POSBL_AT": "N", "BRLL_GUID_AT": "N", "KLANG_VIC_GUID_AT": "Y",
        "DSPSN_TOILET_ATMC_DOOR_AT": "N", "LRGE_PARKNG_POSBL_AT": "Y", "FRE_PARKNG_AT": "Y", "ENTRN_PRICE_AT": "Y"
    },
]

df = pd.DataFrame(sample_data)

# 확장된 배리어프리 필터 목록
filter_options = {
    "WCHAIR_HOLD_AT": "♿ 휠체어 이용 가능",
    "DSPSN_TOILET_AT": "🚻 장애인 화장실",
    "DSPSN_PRKPLCE_AT": "🅿️ 장애인 주차구역",
    "GUID_DOG_ACP_POSBL_AT": "🐶 안내견 동반 가능",
    "BRLL_GUID_AT": "🔠 점자 안내",
    "KLANG_VIC_GUID_AT": "🔊 청각 장애인 보조",
    "DSPSN_TOILET_ATMC_DOOR_AT": "🚪 자동문 설치",
    "LRGE_PARKNG_POSBL_AT": "🚍 대형 주차 가능",
    "FRE_PARKNG_AT": "🆓 무료 주차",
    "ENTRN_PRICE_AT": "💵 입장료 있음"
}

selected_filters = st.multiselect(
    "🧩 적용할 조건을 모두 선택하세요:",
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

# 지도 생성
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

