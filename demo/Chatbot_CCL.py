from openai import OpenAI
import streamlit as st
from python_tool import PythonREPL
import json
st.set_page_config(layout="wide")
def check_basic_code_success(code):
    shell = PythonREPL(
        user_ns={"hello": lambda: print("hello world")},
        timeout=5,
    )
    try:
        code = code.split("```python")[1].split("```")[0]
    except:
        code = "print('no code')"

    output = shell(code)
    return output

def read_jsonl_file(file_path):
    results = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            results.append(json.loads(line.strip()))
    return results


def write_jsonl_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in data:
            f.write(json.dumps(line, ensure_ascii=False) + '\n')

st.session_state["api_key"] = None
st.session_state["base_url"] = None
st.session_state["model"] = None

with st.sidebar:
    # logo = "demo/figures/logo.png"
    # st.sidebar.image(logo,width=200)
    st.sidebar.title(" 🎈 About INTERVENOR 🎈 ")

    markdown = """
INTERVENOR conducts an interactive code-repair process, facilitating the collaboration among agents and the code compiler. It is developed by [NEUIR](https://neuir.github.io/), a research group at Northeastern University.
- 📜 [Paper](https://arxiv.org/abs/2311.09868)
- [![Open in GitHub](https://github.com/codespaces/badge.svg)](https://github.com/NEUIR/INTERVENOR)
"""
    st.sidebar.info(markdown)

    # 分割线
    st.sidebar.markdown("---")
    if st.button("Clear Chat History", key="clear_button", help="Click to clear chat history", type="primary"):
        # 清空聊天记录
        st.session_state["messages"] = []
        history = []

    if st.button("Refresh Page", key="refresh_button", help="Click to refresh the page"):
        # 如果按钮被点击，使用JavaScript实现页面刷新
        st.markdown("<meta http-equiv='refresh' content='0'>", unsafe_allow_html=True)

    #分割线
    st.sidebar.markdown("---")

    st.sidebar.subheader(" 🎈 OpenAI API Key 🎈 ")
    openai_api_key = st.text_input("OpenAI API Key 🌐 [Get an OpenAI API key](https://platform.openai.com/account/api-keys)", key="chatbot_api_key", type="password")
    # "🌐 [Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    st.sidebar.subheader(" 🎈 Base Url 🎈 ")
    openai_base_url = st.text_input("Base Url (default: https://api.openai.com/v1)", key="chatbot_base_url")

    st.sidebar.subheader(" 🎈 Model 🎈 ")
    openai_model_name = st.text_input("Model Name", key="chatbot_model_name")

    # 分割线
    st.sidebar.markdown("---")

    st.sidebar.subheader(" 💻 Interpreter 💻 ")
    # 获取用户输入
    user_input = st.sidebar.text_area("请输入代码：")

    st.write("运行结果：")
    # 检测用户是否按下回车键
    if user_input:
        shell = PythonREPL(
            user_ns={"hello": lambda: print("hello world")},
            timeout=5,
        )
        # 输出用户输入的内容
        output = shell(user_input)
        st.sidebar.code(output,language="python", line_numbers=False)
        # st.sidebar.write("运行结果：", output)






st.title(":sunglasses: INTERVENOR :sunglasses:")
with st.expander("🚀 你好！我是INTERVENOR，一个由NEUIR开发的代码错误修复助手! 点击查看使用攻略！"):
    st.write('''
        1.首先，你需要输入简单的问题描述和你觉得可能存在问题的代码。
        
        2.随后，你可以通过按钮选择测试用例生成，代码测试，代码修复链生成以及代码修复。
    ''')
    # st.image("https://static.streamlit.io/examples/dice.jpg")



def gpt_runner(api_key,base_url,model,messages):
    import openai

    openai.api_key = api_key  # 令牌处创建，获得
    openai.api_base = base_url

    openai.default_headers = {"x-foo": "true"}

    from openai import OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=2048,
        temperature=1,
        top_p=0.95,
        stop=[],
        n=1
    )
    responses = [response.choices[i].message.content for i in range(1)]
    return responses[0]

col1, col2 = st.columns(2)
problem = ""
with col1:
   # st.header("编程问题描述")
   problem = st.text_area(
       label = ":blue[编程问题描述]",
       placeholder = "请输入简单的编程问题描述或者函数功能介绍。",
       height=300,
   )

code = ""
with col2:
   # st.header("代码")
   code = st.text_area(
       label=":red[代码]",
       placeholder = "请输入可能存在问题的代码",
        height = 300,
   )


st.session_state["messages"] =[]
st.session_state.messages.append({"role": "assistant", "content": "Hi"})
st.session_state.messages.append({"role": "user", "content": "Hi"})
st.session_state.messages.append({"role": "assistant", "content": "Hi"})
st.session_state.messages.append({"role": "user", "content": "Hi"})
# 将messages中的内容写入到聊界面
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write("```" + msg["content"] + "```")

# 初始化 session_state 中的按钮状态
if 'button_test_case' not in st.session_state:
    st.session_state.button_test_case = False
if 'button_test' not in st.session_state:
    st.session_state.button_test = False
if 'button_code_fix' not in st.session_state:
    st.session_state.button_code_fix = False

# 初始化 session_state 中的按钮状态
if 'button_test_case1' not in st.session_state:
    st.session_state.button_test_case1 = False
if 'button_test1' not in st.session_state:
    st.session_state.button_test1 = False
if 'button_code_fix1' not in st.session_state:
    st.session_state.button_code_fix1 = False


# 初始化 session_state 中的按钮状态
if 'button_test_case2' not in st.session_state:
    st.session_state.button_test_case2 = False
if 'button_test2' not in st.session_state:
    st.session_state.button_test2 = False
if 'button_code_fix2' not in st.session_state:
    st.session_state.button_code_fix2 = False

# 初始化 session_state 中的按钮状态
if 'button_test_case3' not in st.session_state:
    st.session_state.button_test_case3 = False
if 'button_test3' not in st.session_state:
    st.session_state.button_test3 = False
if 'button_code_fix3' not in st.session_state:
    st.session_state.button_code_fix3 = False

# 初始化 session_state 中的按钮状态
if 'button_test_case4' not in st.session_state:
    st.session_state.button_test_case4 = False
if 'button_test4' not in st.session_state:
    st.session_state.button_test4 = False
if 'button_code_fix4' not in st.session_state:
    st.session_state.button_code_fix4 = False

# 按钮点击事件处理
def on_click_test_case():
    st.session_state.button_test_case = True

def on_click_test():
    st.session_state.button_test = True

def on_click_code_fix():
    st.session_state.button_code_fix = True

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("测试用例生成", key="test_case_button", type="primary", use_container_width=True, on_click=on_click_test_case):
        pass

with col2:
    if st.button("测试", key="test_button", type="primary", use_container_width=True, on_click=on_click_test):
        pass

with col3:
    if st.button("代码修复", key="code_fix_button", type="primary", use_container_width=True, on_click=on_click_code_fix):
        pass

# 根据按钮状态显示消息
if st.session_state.button_test_case:
    with st.chat_message("user"):
        st.write("👋 测试用例生成...（第一轮）")

if st.session_state.button_test:
    with st.chat_message("user"):
        st.write("💻 测试...（第一轮）")

if st.session_state.button_code_fix:
    with st.chat_message("user"):
        st.write("🔨 修复...（第一轮）")


if st.session_state.button_test_case and st.session_state.button_test and st.session_state.button_code_fix:



    # 按钮点击事件处理
    def on_click_test_case1():
        st.session_state.button_test_case1 = True


    def on_click_test1():
        st.session_state.button_test1 = True


    def on_click_code_fix1():
        st.session_state.button_code_fix1 = True


    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("测试用例生成", key="test_case_button1", type="primary", use_container_width=True,
                     on_click=on_click_test_case1):
            pass

    with col2:
        if st.button("测试", key="test_button1", type="primary", use_container_width=True, on_click=on_click_test1):
            pass

    with col3:
        if st.button("代码修复", key="code_fix_button1", type="primary", use_container_width=True,
                     on_click=on_click_code_fix1):
            pass

    # 根据按钮状态显示消息
    if st.session_state.button_test_case1:
        with st.chat_message("user"):
            st.write("👋 测试用例生成...（第二轮）")

    if st.session_state.button_test1:
        with st.chat_message("user"):
            st.write("💻 测试...（第二轮）")

    if st.session_state.button_code_fix1:
        with st.chat_message("user"):
            st.write("🔨 修复...（第二轮）")



if st.session_state.button_test_case1 and st.session_state.button_test1 and st.session_state.button_code_fix1:



    # 按钮点击事件处理
    def on_click_test_case2():
        st.session_state.button_test_case2 = True


    def on_click_test2():
        st.session_state.button_test2 = True


    def on_click_code_fix2():
        st.session_state.button_code_fix2 = True


    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("测试用例生成", key="test_case_button2", type="primary", use_container_width=True,
                     on_click=on_click_test_case2):
            pass

    with col2:
        if st.button("测试", key="test_button2", type="primary", use_container_width=True, on_click=on_click_test2):
            pass

    with col3:
        if st.button("代码修复", key="code_fix_button2", type="primary", use_container_width=True,
                     on_click=on_click_code_fix2):
            pass

    # 根据按钮状态显示消息
    if st.session_state.button_test_case2:
        with st.chat_message("user"):
            st.write("👋 测试用例生成...（第三轮）")

    if st.session_state.button_test2:
        with st.chat_message("user"):
            st.write("💻 测试...（第三轮）")

    if st.session_state.button_code_fix2:
        with st.chat_message("user"):
            st.write("🔨 修复...（第三轮）")


if st.session_state.button_test_case2 and st.session_state.button_test2 and st.session_state.button_code_fix2:
    # 按钮点击事件处理
    def on_click_test_case3():
        st.session_state.button_test_case3 = True


    def on_click_test3():
        st.session_state.button_test3 = True


    def on_click_code_fix3():
        st.session_state.button_code_fix3 = True


    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("测试用例生成", key="test_case_button3", type="primary", use_container_width=True,
                     on_click=on_click_test_case3):
            pass

    with col2:
        if st.button("测试", key="test_button3", type="primary", use_container_width=True, on_click=on_click_test3):
            pass

    with col3:
        if st.button("代码修复", key="code_fix_button3", type="primary", use_container_width=True,
                     on_click=on_click_code_fix3):
            pass

    # 根据按钮状态显示消息
    if st.session_state.button_test_case3:
        with st.chat_message("user"):
            st.write("👋 测试用例生成...（第四轮）")

    if st.session_state.button_test3:
        with st.chat_message("user"):
            st.write("💻 测试...（第四轮）")

    if st.session_state.button_code_fix3:
        with st.chat_message("user"):
            st.write("🔨 修复...（第四轮）")


if st.session_state.button_test_case3 and st.session_state.button_test3 and st.session_state.button_code_fix3:
    # 按钮点击事件处理
    def on_click_test_case4():
        st.session_state.button_test_case4 = True


    def on_click_test4():
        st.session_state.button_test4 = True


    def on_click_code_fix4():
        st.session_state.button_code_fix4 = True


    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("测试用例生成", key="test_case_button4", type="primary", use_container_width=True,
                     on_click=on_click_test_case4):
            pass

    with col2:
        if st.button("测试", key="test_button4", type="primary", use_container_width=True, on_click=on_click_test4):
            pass

    with col3:
        if st.button("代码修复", key="code_fix_button4", type="primary", use_container_width=True,
                     on_click=on_click_code_fix4):
            pass

    # 根据按钮状态显示消息
    if st.session_state.button_test_case4:
        with st.chat_message("user"):
            st.write("👋 测试用例生成...（第五轮）")

    if st.session_state.button_test4:
        with st.chat_message("user"):
            st.write("💻 测试...（第五轮）")

    if st.session_state.button_code_fix4:
        with st.chat_message("user"):
            st.write("🔨 修复...（第五轮）")


