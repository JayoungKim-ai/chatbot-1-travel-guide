import openai
import streamlit as st
from openai import OpenAI
import os
from html import escape

st.title("여행 안내 챗봇")
st.sidebar.title("설정")

# -----
# OpenAI API Key 입력
# -----
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.sidebar.warning("openai API Key를 입력해주세요.")
    st.stop()

# -----
# OpenAI 클라이언트 초기화
# -----
client = OpenAI(api_key=openai_api_key) 
try:
    client.models.list()
    st.sidebar.success("OpenAI 클라이언트가 성공적으로 초기화되었습니다.")
except Exception as e:
    st.sidebar.error(f'잘못된 API Key입니다.')
    st.stop()

# -----
# OpenAI 모델과의 대화
# -----
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "system",
            "content": """당신은 여행에 관한 질문에 답하는 챗봇입니다.
            여행지 추천, 준비물, 문화, 음식 등 다양한 주제에 대해 친절하고 유익하게 답변해 주세요.
            여행에 관한 질문이 아니면 "저는 여행에 관한 질문에만 답변할 수 있어요!"라고 답변해 주세요.
            모르는 질문이면 "모르는 질문입니다."라고 답변해 주세요.
            """
        }
    ]

user_input = st.text_area("질문을 입력하세요:", height=50, placeholder="여기에 질문을 입력하세요...", key="user_input")
if st.button("전송"):     
    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state["messages"]
        )
        reply = response.choices[0].message.content
        st.session_state["messages"].append({"role": "assistant", "content": reply})

        # ------
        # 대화내용 표시 (사용자 메시지는 연보라색 배경)
        #------
        # CSS 한 번 삽입
        st.markdown(
            """
            <style>
            .user-msg { background: #efe6ff; padding:10px 14px; border-radius:10px; margin:6px 0; }
            .assistant-msg { background: #f1f1f1; padding:10px 14px; border-radius:10px; margin:6px 0; }
            .meta { font-size:12px; color:#666; margin-bottom:4px; }
            </style>
            """,
            unsafe_allow_html=True,
        )
        for message in st.session_state["messages"]:
            content = escape(message["content"]).replace('\n', '<br/>')
            if message["role"] == "user":
                st.markdown(f"<div class=\"user-msg\"><div class=\"meta\">👤 사용자</div>{content}</div>", unsafe_allow_html=True)
            elif message["role"] == "assistant":
                st.markdown(f"<div class=\"assistant-msg\"><div class=\"meta\">🤖 챗봇</div>{content}</div>", unsafe_allow_html=True)

            
            
    
        
        
    
