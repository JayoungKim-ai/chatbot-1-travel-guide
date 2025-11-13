# ----------------------------------------------------------------------
# API 숨기기
#  1. 해당 작업 폴더 내에 .streamlit 폴더 생성
#  2. .streamlit 폴더 내에 secrets.toml 파일 생성
#  3. secrets.toml 파일에 아래 내용 추가
#     openai_api_key="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# ----------------------------------------------------------------------

import streamlit as st
from openai import OpenAI
import os
from html import escape
from datetime import datetime

# ----------------------------------------------------------------------
# 1) 페이지 기본 설정 + CSS 스타일
# ----------------------------------------------------------------------
st.set_page_config(page_title="여행 안내 챗봇 🧳", layout="wide")

PAGE_CSS = """
<style>
body { background: linear-gradient(180deg, #f7fbff 0%, #fffef9 100%); }
.header { display:flex; align-items:center; gap:12px; margin-bottom: 10px; }
.logo { font-size:32px; }
.subtitle { color:#666; }

.chat-container { max-width:900px; margin:20px auto; }
.chat-wrapper:after { content: ""; display: table; clear: both; }

.user-msg, .assistant-msg {
    padding: 12px 16px;
    border-radius: 12px;
    margin: 10px 0;
    max-width: 75%;
    line-height: 1.5;
}

.user-msg {
    background: linear-gradient(90deg,#efe6ff,#f7eaff);
    float:right;
}

.assistant-msg {
    background: linear-gradient(90deg,#e8f6ff,#f4fbff);
    float:left;
}

.meta { font-size:12px; color:#666; margin-bottom:6px; }
.time { font-size:11px; color:#999; }
</style>
"""
st.markdown(PAGE_CSS, unsafe_allow_html=True)

# Header UI
st.markdown(
    """
<div class="header">
  <div class="logo">🧳✈️</div>
  <div>
    <h1 style="margin:0">여행 안내 챗봇</h1>
    <div class="subtitle">여행지 추천 · 준비물 · 현지 정보까지 친절하게 안내합니다.</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# 2) 사이드바 구성
# ----------------------------------------------------------------------
st.sidebar.title("⚙️ 설정")

# openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
openai_api_key = st.secrets.get("openai_api_key", "")

preferred_lang = st.sidebar.selectbox("응답 언어", ["한국어", "English"])
travel_style = st.sidebar.selectbox("여행 스타일", ["배낭여행", "휴양", "미식", "럭셔리"])
destination_hint = st.sidebar.text_input("관심 지역 (선택)", placeholder="예: 제주, 교토, 파리")

st.sidebar.markdown("---")
st.sidebar.markdown("💡 예시: **3박4일 제주 여행 코스 추천해줘**")

# API 키 체크
if not openai_api_key:
    st.sidebar.warning("OpenAI API Key를 입력해주세요.")
    st.stop()

client = OpenAI(api_key=openai_api_key)
try:
    client.models.list()
    st.sidebar.success("OpenAI 키 확인 완료")
except Exception:
    st.sidebar.error("잘못된 API Key입니다. 다시 확인해주세요.")
    st.stop()

# ----------------------------------------------------------------------
# 3) 세션 상태 초기화
# ----------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "당신은 여행에 대한 정보를 안내하는 챗봇입니다. "
                "여행지 추천, 준비물, 예산, 교통, 문화, 음식 등 모든 주제를 친절하게 설명합니다."
            ),
            "time": datetime.now().isoformat(),
        }
    ]

# ----------------------------------------------------------------------
# 4) 메시지 렌더링 함수
# ----------------------------------------------------------------------
def render_messages():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        content = escape(msg["content"]).replace("\n", "<br/>")
        time_label = ""

        if msg.get("time"):
            try:
                t = datetime.fromisoformat(msg["time"])
                time_label = t.strftime("%Y-%m-%d %H:%M")
            except:
                time_label = msg["time"]

        if msg["role"] == "user":
            st.markdown(
                f"""
                <div class="chat-wrapper">
                    <div class="user-msg">
                        <div class="meta">👤 사용자 <span class="time">{time_label}</span></div>
                        {content}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif msg["role"] == "assistant":
            st.markdown(
                f"""
                <div class="chat-wrapper">
                    <div class="assistant-msg">
                        <div class="meta">🤖 챗봇 <span class="time">{time_label}</span></div>
                        {content}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# 5) 입력창 + 전송 버튼
# ----------------------------------------------------------------------
user_text = st.text_area(
    "질문을 입력하세요:",
    height=120,
    placeholder="예: 3박4일 도쿄 여행 추천, 예산 100만원, 음식 위주",
)

send_btn = st.button("전송")

# ----------------------------------------------------------------------
# 6) 챗봇 응답 처리
# ----------------------------------------------------------------------
if send_btn and user_text:
    # 사용자 메시지 추가
    st.session_state.messages.append(
        {"role": "user", "content": user_text, "time": datetime.now().isoformat()}
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state.messages,
            max_tokens=700,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = "⚠️ 응답 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        st.sidebar.exception(e)

    st.session_state.messages.append(
        {"role": "assistant", "content": reply, "time": datetime.now().isoformat()}
    )

# ----------------------------------------------------------------------
# 7) 메시지 출력
# ----------------------------------------------------------------------
render_messages()
