import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic
import random

st.set_page_config(page_title="♿ 배리어프리 관광경로 추천", layout="wide")
st.title("♿ 배리어프리 관광경로 추천 앱 (샘플 20개 버전)")

# 사용자 위치
user_lat = st.number_input("📍 현재 위치 위도", value=37.5665)
user_lon = st.number_input("📍 현재 위치 경도", value=126.9780)
radius_km = st.slider("📏 추천 반경 (km)", 1, 50, 10)
user_location = (user_lat, user_lon)

# 샘플 데이터 생성
places = [
    "서울역사박물관", "국립중앙박물관", "세종문화회관", "예술의전당", "국립현대미술관",
    "DDP", "롯데월드타워", "63빌딩", "광화문광장", "서울식물원",
    "한강시민공원", "코엑스", "남산타워", "창덕궁", "경복궁",
    "청계천", "북서울꿈의숲", "서울대공원", "어린이대공원", "서대문자연사박물관"
]

sample_data = []
for i, name in enumerate(places):
    sample_data.append({
        "관광지": name,
        "위도": round(37.45 + random.random() * 0.15, 6),
        "경도": round(126.9 + random.random() * 0.1, 6),
        "WCHAIR_HOLD_AT": random.choice(["Y", "N"]),
        "DSPSN_TOILET_AT": random.choice(["Y", "N"]),
        "DSPSN_PRKPLCE_AT": random.choice(["Y", "N"]),
        "GUID_DOG_ACP_POSBL_AT": random.choice(["Y", "N"]),
        "BRLL_GUID_AT": random.choice(["Y", "N"]),
        "KLANG_VIC_GUID_AT": random.choice(["Y", "N"]),
        "DSPSN_TOILET_ATMC_DOOR_AT": random.choice(["Y", "N"]),
        "LRGE_PARKNG_POSBL_AT": random.choice(["Y", "N"]),
        "FRE_PARKNG_AT": random.choice(["Y", "N"]),
        "ENTRN_PRICE_AT": random.choice(["Y", "N"])
    })
df = pd.DataFrame(sample_data)

# 필터 목록
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

# 필터 적용
for f in selected_filters:
    df = df[df[f] == "Y"]

# 거리 계산
df["거리"] = df.apply(lambda row: geodesic(user_location, (row["위도"], row["경도"])).km, axis=1)
result_df = df[df["거리"] <= radius_km].sort_values("거리")

st.success(f"✅ 추천 관광지 수: {len(result_df)}개")

# 지도 생성
m = folium.Map(location=user_location, zoom_start=12)
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


