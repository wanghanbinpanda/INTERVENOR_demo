from openai import OpenAI
import streamlit as st
from python_tool import PythonREPL
import json
import time

import functools
from concurrent import futures

executor = futures.ThreadPoolExecutor(1)

def timeout(seconds):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            future = executor.submit(func, *args, **kw)
            return future.result(timeout=seconds)
        return wrapper
    return decorator


st.set_page_config(layout="wide")

@timeout(5)
def check_basic_code_success(code):
    shell = PythonREPL(
        user_ns={"hello": lambda: print("hello world")},
        timeout=5,
    )
    if "<test>" in code and "</test>" in code:
        code = code.split("<test>")[1].split("</test>")[0]
    elif "```python" in code and "```" in code:
        code = code.split("```python")[1].split("```")[0]
    elif "<repair_code>" in code and "</repair_code>" in code:
        code = code.split("<repair_code>")[1].split("</repair_code>")[0]
    else:
        code = "未找到代码。"

    output = shell(code)
    return output

def extract_code(code):
    if "<test>" in code and "</test>" in code:
        code = code.split("<test>")[1].split("</test>")[0]
    elif "```python" in code and "```" in code:
        code = code.split("```python")[1].split("```")[0]
    elif "<repair_code>" in code and "</repair_code>" in code:
        code = code.split("<repair_code>")[1].split("</repair_code>")[0]
    else:
        code = "未找到代码。"
    return code
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


# path = "./prompts/test_cases_generate.txt"
# with open(path,encoding="utf-8") as f:
#     test_cases_generate_prompt = f.read()
test_cases_generate_prompt = """
You are a test case design assistant, and your task is to design test cases based on the given problem description and code, and then use these test cases to test whether the code is correct or not.Please analyze the problem description and then design test cases to verify the code.(Note: When design test cases, you should ignore the code and only according to the probelm description. If there are test cases in the poblem description, just use then and do not provide other test cases)
you should originaze the code and the tese cases you designed, for example, you can use assert statements or other format to check the output of the code.
you should put the test code between <test> and </test> to make it a valid code block that can be executed by Python interpreter.

Problem:
Calculate the sum of two integers.

Code(may contain bugs):
def sum(a,b):
    sum = a ++ b
    return sum

Test Code:
Ignoring the code and focusing only on the problem description, here are some test cases to verify the functionality of a correct "sum of two integers" function:

Test case for positive integers:
Input: a = 5, b = 3
Expected Output: 8
Test case for negative integers:
Input: a = -5, b = -3
Expected Output: -8
Test case for a positive and a negative integer:
Input: a = 5, b = -3
Expected Output: 2
Test case for zero and a non-zero integer:
Input: a = 0, b = 7
Expected Output: 7
Test case for large integers (to ensure there's no overflow):
Input: a = 1000000, b = 999999
Expected Output: 1999999

Based on the test cases, we can design the following test code(do not modify the code user provided):
<test>
def sum(a,b):
    sum = a ++ b
    return sum

assert sum(5, 3) == 8, "Test case for positive integers failed: Expected 8, got different result"
assert sum(-5, -3) == -8, "Test case for negative integers failed: Expected -8, got different result"
assert sum(5, -3) == 2, "Test case for a positive and a negative integer failed: Expected 2, got different result"
assert sum(0, 7) == 7, "Test case for zero and a non-zero integer failed: Expected 7, got different result"
assert sum(1000000, 999999) == 1999999, "Test case for large integers failed: Expected 1999999, got different result"
</test>

Problem:
%%%problem%%%

Code(may contain bugs):
%%%code%%%

Test Code:
"""
# path = "./prompts/code_repair.txt"
# with open(path,encoding="utf-8") as f:
#     code_repair_prompt = f.read()
code_repair_prompt = """
You are an intelligent code fix assistant, and your job is to fix the errors in the code.

You have two tasks:
Task 1: Generate a chain of code repairs based on the compiler's error messages. The chain of code repairs should analyze the code errors and provide detailed suggestions for fixes. The chain of code repairs should be enclosed within <chain_of_repair> and </chain_of_repair>.
Task 2: Fix the code according to the chain of code repairs. The fixed code should be enclosed within <repair_code> and </repair_code>.

Problem:
Calculate the sum of two integers.

Code(may contain bugs):
def sum(a,b):
    sum = a plus b
    return sum

Error Messages:
Cell In[1], line 2
    sum = a plus b
            ^
SyntaxError: invalid syntax

Repaired Code：
<chain_of_repair>
The issue with the code is that the use of the word "plus" is incorrect in Python. In Python, to add two integers, you need to use the "+" operator instead of "plus".
Additionally, using the variable name "sum" as a function name can cause confusion as there is a built-in function called sum() in Python. Although it is not an error in this case, it is good practice to avoid using built-in function names as variable names.
Here is the chain of repairs for the code:

Replace "plus" with "+" to perform the addition correctly.
Consider renaming the function to something other than "sum" to avoid potential confusion.
</chain_of_repair>

<repair_code>
def add_two_numbers(a, b):
    result = a + b
    return result
</repair_code>


Problem:
%%%problem%%%

Code(may contain bugs):
%%%buggy_code%%%

Error Messages:
%%%error_messages%%%

Repaired Code：
"""
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
    # st.sidebar.markdown("---")
    # if st.button("Clear Chat History", key="clear_button", help="Click to clear chat history", type="primary"):
    #     # 清空聊天记录
    #     st.session_state["messages"] = []
    #     history = []

    # if st.button("Refresh Page", key="refresh_button", help="Click to refresh the page"):
    #     # 如果按钮被点击，使用JavaScript实现页面刷新
    #     st.markdown("<meta http-equiv='refresh' content='0'>", unsafe_allow_html=True)

    #分割线
    st.sidebar.markdown("---")

    st.sidebar.subheader(" 🎈 OpenAI API Key 🎈 ")
    openai_api_key = st.text_input("OpenAI API Key 🌐 [Get an OpenAI API key](https://platform.openai.com/account/api-keys)", key="chatbot_api_key", type="password")
    # "🌐 [Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    st.session_state["api_key"] = openai_api_key

    st.sidebar.subheader(" 🎈 Base Url 🎈 ")
    openai_base_url = st.text_input("Base Url (default: https://api.openai.com/v1)", key="chatbot_base_url")
    st.session_state["base_url"] = openai_base_url

    st.sidebar.subheader(" 🎈 Model 🎈 ")
    openai_model_name = st.text_input("Model Name", key="chatbot_model_name")
    st.session_state["model"] = openai_model_name

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




def agent(api_key,base_url,model,messages):
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

# st.session_state["messages"] =[]
# st.session_state.messages.append({"role": "assistant", "content": "Hi"})
# st.session_state.messages.append({"role": "user", "content": "Hi"})
# st.session_state.messages.append({"role": "assistant", "content": "Hi"})
# st.session_state.messages.append({"role": "user", "content": "Hi"})


# 初始化 session state
if "messages" not in st.session_state:
    st.session_state.messages = []
# 将messages中的内容写入到聊界面
if "history" not in st.session_state:
    st.session_state.history = []

if "buggy_code" not in st.session_state:
    st.session_state.buggy_code = ""

if "error_message" not in st.session_state:
    st.session_state.error_message = ""

if "success" not in st.session_state:
    st.session_state.success = False

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write("```" + msg["content"] + "```")

if st.session_state.success:
    st.success("Successfully fix the code!")


if len(st.session_state["api_key"]) == 0 or len(st.session_state["base_url"]) == 0 or len(st.session_state["model"]) == 0:
    # st.toast('请输入api_key,base_url以及model！', icon='😍')
    # st.warning('请在侧边栏输入api_key,base_url以及model！', icon="⚠️")
    st.error('请在侧边栏输入api_key,base_url以及model！', icon="⚠️")
else:
    col1, col2, col3,col4 = st.columns(4)
    with col1:
        if st.button("测试用例生成", key="test_case_button", type="primary", use_container_width=True):
            prompt = test_cases_generate_prompt.replace("%%%problem%%%",problem).replace("%%%code%%%",code)
            # prompt = problem +"\n" +  code
            st.session_state.history.append({"role": "user", "content": prompt})
            response = agent(api_key=st.session_state["api_key"], base_url=st.session_state["base_url"], model=st.session_state["model"], messages=st.session_state.history)
            st.session_state.history.append({"role": "assistant", "content": response})
            response = "生成测试用例...\n\n" + response
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.success = False
            st.experimental_rerun()  # 立即刷新页面
    with col2:
        if st.button("测试", key="test_button", type="primary", use_container_width=True):
            # st.session_state.messages的最后一个回复的content里抽取出code，测试代码。如果没有抽取出code，则显示没用可供测试的代码。
            tmp_content =st.session_state.messages[-1]["content"]
            print(tmp_content)
            try:
                test_result = check_basic_code_success(tmp_content)
            except Exception as e:
                test_result = "Timeout Exception!"
            if "[Executed Successfully with No Output]" in test_result:
                st.session_state.success = True
            else:
                st.session_state.success = False
            st.session_state.buggy_code = extract_code(tmp_content)
            st.session_state.error_message = test_result
            st.session_state.history.append({"role": "user", "content": "Test results:" + test_result})
            st.session_state.messages.append({"role": "user", "content": test_result})
            st.experimental_rerun()  # 立即刷新页面
    with col3:
        if st.button("代码修复", key="code_fix_button", type="primary", use_container_width=True):
            prompt = code_repair_prompt.replace("%%%problem%%%",problem).replace("%%%buggy_code%%%",st.session_state.buggy_code).replace("%%%error_messages%%%",st.session_state.error_message)
            st.session_state.history.append({"role": "user", "content": prompt})
            response = agent(api_key=st.session_state["api_key"], base_url=st.session_state["base_url"],
                             model=st.session_state["model"], messages=st.session_state.history)
            if "<chain_of_repair>" not in response:
                response = "<chain_of_repair>\n" + response
            st.session_state.history.append({"role": "assistant", "content": response})
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.experimental_rerun()  # 立即刷新页面
    with col4:
        if st.button("清空聊天", key="clear_button", type="primary", use_container_width=True):
            # st.session_state.messages.append({"role": "assistant", "content": "代码修复"})
            # st.experimental_rerun()  # 立即刷新页面
            st.session_state["messages"] = []
            st.session_state.success = False
            st.experimental_rerun()  # 立即刷新页面
