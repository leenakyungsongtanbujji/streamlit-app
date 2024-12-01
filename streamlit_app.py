import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# GitHub에 업로드한 CSV 파일의 URL
file_url = "https://raw.githubusercontent.com/leenakyungsongtanbujji/streamlit-app/main/top_5_detailed_products.csv"

# CSV 파일 읽기
data = pd.read_csv(file_url, encoding="cp949") 

# 'EXAMIN_MRKT_NM' 열을 '판매처'로 사용
data["판매처"] = data["EXAMIN_MRKT_NM"]

# Streamlit 제목
st.title("판매 품목 데이터 분석")

# 사용자가 선택할 품목 목록
product_options = data["PRDLST_NM"].unique()
selected_product = st.selectbox("분석할 품목을 선택하세요:", product_options)

# 선택된 품목 데이터 필터링
filtered_data = data[data["PRDLST_NM"] == selected_product]

# 날짜 필터링 추가
st.subheader("날짜 필터링")
start_date = st.date_input("시작 날짜", value=pd.to_datetime(filtered_data["EXAMIN_DE"].min()))
end_date = st.date_input("종료 날짜", value=pd.to_datetime(filtered_data["EXAMIN_DE"].max()))

# 날짜 필터링 적용
filtered_data["EXAMIN_DE"] = pd.to_datetime(filtered_data["EXAMIN_DE"])
filtered_data = filtered_data[
    (filtered_data["EXAMIN_DE"] >= pd.Timestamp(start_date)) &
    (filtered_data["EXAMIN_DE"] <= pd.Timestamp(end_date))
]

# 평균, 최대, 최소 가격 계산
average_price = filtered_data["EXAMIN_AMT"].mean()
max_price = filtered_data["EXAMIN_AMT"].max()
min_price = filtered_data["EXAMIN_AMT"].min()

# 최저가 판매처 및 지역 확인
cheapest_row = filtered_data.loc[filtered_data["EXAMIN_AMT"].idxmin()]
cheapest_store = cheapest_row["판매처"]
cheapest_region = cheapest_row["EXAMIN_AREA_NM"]

# 결과 출력
st.subheader(f"{selected_product} 분석 결과")
st.write(f"평균 가격: {average_price:.0f}원")
st.write(f"최대 가격: {max_price:.0f}원")
st.write(f"최소 가격: {min_price:.0f}원")
st.write(f"가장 저렴하게 판매하는 곳: {cheapest_store} (지역: {cheapest_region})")

# 가격 변동 그래프
st.subheader(f"{selected_product} 가격 변동")
daily_prices = filtered_data.groupby("EXAMIN_DE")["EXAMIN_AMT"].mean()

fig, ax = plt.subplots()
ax.plot(daily_prices.index, daily_prices.values, marker='o', label=selected_product, color='blue')
ax.set_title(f"{selected_product}의 일별 평균 가격 변화")
ax.set_xlabel("날짜")
ax.set_ylabel("평균 가격 (원)")
ax.legend()
plt.xticks(rotation=45)
st.pyplot(fig)

# 시장 vs 마트 가격 비교
st.subheader(f"{selected_product} 시장 vs 마트 가격 비교")
filtered_data["판매처 유형"] = filtered_data["판매처"].apply(lambda x: "시장" if "시장" in x or "도매" in x else "마트")
avg_prices = filtered_data.groupby("판매처 유형")["EXAMIN_AMT"].mean()

fig, ax = plt.subplots()
avg_prices.plot(kind='bar', ax=ax, color=['skyblue', 'salmon'], alpha=0.7)
for i, v in enumerate(avg_prices):
    ax.text(i, v + 10, f"{v:.0f}원", ha='center', fontsize=10)
ax.set_title(f"{selected_product} 시장 vs 마트 평균 가격 비교")
ax.set_ylabel("평균 가격 (원)")
st.pyplot(fig)