
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import re
from wordcloud import WordCloud

st.set_page_config(page_title="키워드 분석", layout="wide")
st.title("📊 SUNI 키워드 분석 대시보드")

uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요 (.xlsx)", type="xlsx")
analysis_type = st.radio("분석 유형을 선택하세요", ["전사", "직무별"])

FONT_PATH = "NanumGothic.ttf"

stopwords = set([
    '위해', '관련', '강화', '기반', '및', '수준', '필요', '제안', '방안', '활용',
    '참석', '교육', '진행', '역량', '내용', '이해', '제고', '확보', '대한', '있습니다',
    '있도록', '위한', '하고', '싶습니다', '합니다', '통해', '한번', '하는', '같은', '보여', '된다', '수행'
])

def extract_keywords(texts):
    text = ' '.join(texts)
    text = re.sub(r"[^가-힣\s]", "", text)
    words = text.split()
    filtered = [w for w in words if w not in stopwords and len(w) > 1]
    return Counter(filtered)

def draw_charts(title, freq_dict):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"📊 {title} - 막대그래프")
        fig, ax = plt.subplots()
        ax.bar(freq_dict.keys(), freq_dict.values(), color='skyblue')
        plt.xticks(rotation=45)
        st.pyplot(fig)

    with col2:
        st.subheader(f"🧁 {title} - 파이차트")
        fig, ax = plt.subplots()
        ax.pie(freq_dict.values(), labels=freq_dict.keys(), autopct='%1.1f%%', startangle=140)
        st.pyplot(fig)

    st.subheader(f"☁️ {title} - 워드클라우드")
    wc = WordCloud(font_path=FONT_PATH, background_color='white', width=800, height=400)
    wc.generate_from_frequencies(freq_dict)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df_focus = df.copy()

    if '직무' not in df_focus.columns or '(2) 성장/역량/커리어-구성원 의견' not in df_focus.columns:
        st.error("엑셀 파일에 '직무' 및 '(2) 성장/역량/커리어-구성원 의견' 컬럼이 있어야 합니다.")
    else:
        if analysis_type == "전사":
            texts = df_focus['(2) 성장/역량/커리어-구성원 의견'].dropna().tolist()
            counter = extract_keywords(texts)
            top50 = dict(counter.most_common(50))
            draw_charts("전사 키워드", top50)
        else:
            results = []
            for job, group in df_focus.groupby("직무"):
                texts = group['(2) 성장/역량/커리어-구성원 의견'].dropna().tolist()
                counter = extract_keywords(texts)
                top10 = dict(counter.most_common(10))
                results.append((job, top10))

            for job, freq_dict in results:
                st.markdown(f"### 🔍 직무: {job}")
                draw_charts(job, freq_dict)
