import streamlit as st
import requests
import os

st.image("yiyan_logo.png")

st.markdown("<font color='red'>**注意：本站未配置数据库，只有临时缓存！重新打开（或刷新）网页都会导致缓存丢失！**</font>", unsafe_allow_html=True)

# 对话记录和对话缓存
if "messages" not in st.session_state:
    st.session_state.messages = []
if "cache" not in st.session_state:
    st.session_state.cache = []

# 侧边栏
with st.sidebar:
    # 各种参数
    system = st.text_area("System Prompt", value="You are a helpful assistant.")
    max_output_tokens = st.slider("Max Output Tokens", 2, 2048, 1024, step=1)
    temperature = st.slider("Temperature", 0.01, 1.00, 0.80, step=0.01)
    top_p = st.slider("Top P", 0.00, 1.00, 0.80, step=0.01)
    penalty_score = st.slider("Penalty Score", 1.00, 2.00, 1.00, step=0.01, help="通过对已生成的token增加惩罚，减少重复生成的现象。值越大表示惩罚越大。")
    disable_search = st.toggle("Web Search", key="websearch", value=1)

    # 历史对话选择器
    conversation_history = st.selectbox("Conversation History", [cache_list[0]["content"][:10] for cache_list in st.session_state.cache], index=None, help="开始新对话会自动将旧对话进行缓存，点击重置会清除全部记录。重新打开网页也会丢失缓存！")
    # 历史对话选择提交按钮
    submit_button = st.button("Submit", key="submit", type="primary", help="点击召回历史对话")

    # 按钮分区
    col1, col2 = st.columns(2)
    with col1:
        # 新对话按钮
        new_chat_button = st.button("New Chat", key="newchat", help="点击开始新的对话，当前对话会被缓存")
    with col2:
        # 重置按钮
        reset_button = st.button("Reset", key="reset", help="点击进行重置，会清除全部缓存")

api_key = os.environ.get("ERNIE_BOT_API")
host = api_key

data = {
    "system": system,
    "messages": [],
    "temperature": temperature,
    "top_p": top_p,
    "max_output_tokens": max_output_tokens,
    "penalty_score": penalty_score,
    "disable_search": disable_search
}

user_input = st.chat_input("Say something...")

if user_input:
    data["messages"].append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "user", "content": user_input})
    response = requests.post(host, json=data, verify=False)
    result = response.json()["data"]
    data["messages"].append({"role": "assistant", "content": result})
    st.session_state.messages.append({"role": "assistant", "content": result})

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)

# 新对话按钮，添加对话记录，清空当前对话缓存
if new_chat_button:
    st.session_state.cache.append(st.session_state.messages)
    data["messages"] = []
    st.session_state.messages = []
    st.rerun()

# 重置按钮，清空所有记录和缓存
if reset_button:
    data["messages"] = []
    st.session_state.cache = []
    st.session_state.messages = []
    st.rerun()

# 查看历史对话，并继续进行对话
if conversation_history and submit_button:
    selected_index = [cache_list[0]["content"][:10] for cache_list in st.session_state.cache].index(conversation_history)
    conversation_content = st.session_state.cache[selected_index]
    data["messages"] = []
    data["messages"].append(conversation_content)
    st.session_state.messages = []
    st.session_state.messages.append(conversation_content)
    for chatlog in conversation_content:
        with st.chat_message(chatlog["role"]):
            st.markdown(chatlog["content"])
