import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import rc, font_manager
import os

# NanumGothic 폰트 다운로드 및 설정
font_url = "https://raw.githubusercontent.com/leenakyungsongtanbujji/streamlit-app/main/NanumGothic.ttf"
font_path = "NanumGothic.ttf"

if not os.path.exists(font_path):
    os.system(f"curl -o {font_path} {font_url}")

# Matplotlib에 폰트 적용
font_prop = font_manager.FontProperties(fname=font_path)
plt.rc('font', family=font_prop.get_name())
plt.rcParams['axes.unicode_minus'] = False

# GitHub에 업로드한 CSV 파일의 URL
file_url = "https://raw.githubusercontent.com/leenakyungsongtanbujji/streamlit-app/main/top_5_detailed_products.csv"

# CSV 파일 읽기
data = pd.read_csv(file_url, encoding="cp949")

# 'EXAMIN_MRKT_NM' 열을 '판매처'로, 'EXAMIN_AREA_NM' 열을 '지역명'으로 사용
data["판매처"] = data["EXAMIN_MRKT_NM"]
data["지역명"] = data["EXAMIN_AREA_NM"]

# Streamlit 제목
st.title("판매 품목 데이터 분석")

# 사용자가 선택할 품목 목록
product_options = data["PRDLST_NM"].unique()
selected_product = st.selectbox("분석할 품목을 선택하세요:", product_options)

# 선택된 품목 데이터 필터링
filtered_data = data[data["PRDLST_NM"] == selected_product]

# 날짜 필터링 추가
st.subheader("날짜 필터링")  # 새로 추가된 부분
filtered_data["EXAMIN_DE"] = pd.to_datetime(filtered_data["EXAMIN_DE"])
start_date = st.date_input("시작 날짜", value=filtered_data["EXAMIN_DE"].min())
end_date = st.date_input("종료 날짜", value=filtered_data["EXAMIN_DE"].max())

# 날짜 범위 필터링
filtered_data = filtered_data[
    (filtered_data["EXAMIN_DE"] >= pd.Timestamp(start_date)) &
    (filtered_data["EXAMIN_DE"] <= pd.Timestamp(end_date))
]

# 평균, 최대, 최소 가격 계산
average_price = filtered_data["EXAMIN_AMT"].mean()
max_price = filtered_data["EXAMIN_AMT"].max()
min_price = filtered_data["EXAMIN_AMT"].min()

# 최저가 판매처 확인
cheapest_store = filtered_data.loc[filtered_data["EXAMIN_AMT"].idxmin(), "판매처"]
cheapest_region = filtered_data.loc[filtered_data["EXAMIN_AMT"].idxmin(), "지역명"]

# 결과 출력
st.subheader(f"{selected_product} 분석 결과")
st.write(f"평균 가격: {average_price:.0f}원")
st.write(f"최대 가격: {max_price:.0f}원")
st.write(f"최소 가격: {min_price:.0f}원")
st.write(f"가장 저렴하게 판매하는 곳: {cheapest_store} (지역: {cheapest_region})")

# 가격 변동 그래프
st.subheader(f"{selected_product} 가격 변동")
daily_prices = filtered_data.groupby("EXAMIN_DE")["EXAMIN_AMT"].mean()

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(daily_prices.index, daily_prices.values, marker='o', label=selected_product, color='blue')
ax.set_title(f"{selected_product}의 일별 평균 가격 변화", fontproperties=font_prop)
ax.set_xlabel("날짜", fontproperties=font_prop)
ax.set_ylabel("평균 가격 (원)", fontproperties=font_prop)
ax.legend(prop=font_prop)
plt.xticks(fontproperties=font_prop)
plt.yticks(fontproperties=font_prop)
st.pyplot(fig)

# 시장 vs 마트 가격 비교
st.subheader(f"{selected_product} 시장 vs 마트 가격 비교")
filtered_data["판매처 유형"] = filtered_data["판매처"].apply(lambda x: "시장" if "시장" in x or "도매" in x else "마트")
market_vs_mart = filtered_data.groupby("판매처 유형")["EXAMIN_AMT"].mean()

fig2, ax2 = plt.subplots(figsize=(10, 5))
market_vs_mart.plot(kind="bar", color=["salmon", "skyblue"], ax=ax2)
ax2.set_title(f"{selected_product} 시장 vs 마트 평균 가격 비교", fontproperties=font_prop)
ax2.set_ylabel("평균 가격 (원)", fontproperties=font_prop)
ax2.set_xlabel("판매처 유형", fontproperties=font_prop)
plt.xticks(rotation=0, fontproperties=font_prop)  # X축 글자 회전 제거
plt.yticks(fontproperties=font_prop)
for i, v in enumerate(market_vs_mart):
    ax2.text(i, v + 10, f"{int(v)}원", ha="center", fontsize=10, fontproperties=font_prop)
st.pyplot(fig2)