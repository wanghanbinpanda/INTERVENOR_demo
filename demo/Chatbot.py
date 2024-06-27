from openai import OpenAI
import streamlit as st
from python_tool import PythonREPL
import json

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
with st.expander("Quick Start"):
    st.write('''
        🚀 Your code repair assistant!
    ''')
    # st.image("https://static.streamlit.io/examples/dice.jpg")


history = []

# 这段代码检查st.session_state中是否不存在键为"messages"的项目。如果不存在，它将使用包含一个字典的列表初始化st.session_state["messages"]
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hi, I am INTERVENOR, a code bug repair assistant developed by NEUIR. You can start by typing your code in the input box."}]
    history.append({"role": "system", "content": "You are INTERVENOR, a code bug repair assistant developed by NEUIR."})

# 将messages中的内容写入到聊界面
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write("```" + msg["content"] + "```")

def gpt_runner(api_key,base_url,messages):
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
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=2048,
        temperature=1,
        top_p=0.95,
        stop=[],
        n=1
    )
    responses = [response.choices[i].message.content for i in range(1)]
    return responses[0]

# 检查是否有用户在聊天输入框中输入了内容，如果有的话，将内容赋值给prompt。

if prompt := st.chat_input():
    # 检查是否已经设置了OpenAI API密钥。如果没有设置密钥，它会在应用程序界面上显示一条信息，提示用户添加OpenAI API密钥以继续。然后通过st.stop()停止应用程序的执行。
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    if not openai_base_url:
        base_url = "https://api.openai.com/v1"
    else:
        base_url = openai_base_url

    if len(st.session_state["messages"]) > 1:
        history = read_jsonl_file("history.jsonl")
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        history.append({"role": "user", "content": prompt})
        # st.write(history)
        response = gpt_runner(openai_api_key,base_url, history)

        #如果response里有代码，提取出来代码
        if "```python" in response and "```" in response:
            history.append({"role": "assistant", "content": response})
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)

            output = check_basic_code_success(response)
            test_results = """
                        Here is the test result:
                        {output}
                        """.format(output=output)
            st.session_state.messages.append({"role": "assistant", "content": test_results})
            st.chat_message("assistant").write(test_results)
            write_jsonl_file("history.jsonl", history)
        else:
            history.append({"role": "assistant", "content": response})
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)
            write_jsonl_file("history.jsonl", history)
        #停止
        st.stop()

    code = prompt
    prompt = f'''
```python
{code}
```
'''
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)


    st.write("### Test Cases Designer working...")
    new_prompt = "Here is the problem description and code(may contain bugs) user input:\n\n" + prompt + "\nPlease analyze the problem description and then design test cases to verify the code.(Note: When design test cases, you should ignore the code and only according to the probelm description. If there are test cases in the poblem description, just use then and do not provide other test cases)"

    history.append({"role": "user", "content": new_prompt})
    response = gpt_runner(openai_api_key,base_url, history)
    response = "Based on the problem description above, we design test cases to verify the code.\n" + response
    history.append({"role": "assistant", "content": response})
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)


    st.write("### Originazing the test code...")
    history.append({"role": "user", "content": "Based on the message above, wrap the user's code with the test cases(do not modify the user's code, just copy it), if the code do not pass the test cases, you should raise exception by using assert or others. You should put the code and test code in the same code block. e.g.,\n```python\n# user code\n# test code\n```"})
    response = gpt_runner(openai_api_key,base_url, history)
    response = "Based on the test cases above, we organize the test code.\n" + response
    history.append({"role": "assistant", "content": response})
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)


    st.write("### Testing...")
    output = check_basic_code_success(response)
    history.append({"role": "user", "content": "Here is the test result:\n" + output})

    test_results = """
    Here is the test result:
    {output}
    """.format(output=output)
    st.session_state.messages.append({"role": "assistant", "content": test_results})
    st.chat_message("assistant").write(test_results)



    # assistant根据test results判断
    st.write("### Repairing...")
    history.append({"role": "user", "content": "Based on the test results, If the test passed, claim the code is correct. If the test failed, please claim what's wrong with the code and give the repaired code."})
    response = gpt_runner(openai_api_key,base_url, history)
    response = "Based on the test results above, we repair the code.\n" + response
    history.append({"role": "assistant", "content": response})
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)


    #if response里有代码，提取出来代码,并进行测试
    if "```python" in response and "```" in response:
        st.write("### Testing...")
        output = check_basic_code_success(response)
        history.append({"role": "user", "content": "Here is the test result:\n" + output})

        test_results = """
            Here is the test result:
            {output}
            """.format(output=output)
        st.session_state.messages.append({"role": "assistant", "content": test_results})
        st.chat_message("assistant").write(test_results)

    st.write("### If you have any questions or my answer is not correct, please let me know. I will try my best to help you. Just type your question in the input box.")

    #把history写入/history.jsonl文件
    write_jsonl_file("history.jsonl",history)


    # while True:
    #     if prompt := st.chat_input(key="tmp"):
    #         st.session_state.messages.append({"role": "user", "content": prompt})
    #         st.chat_message("user").write(prompt)
    #         history.append({"role": "user", "content": prompt})
    #         response = gpt_runner(openai_api_key,base_url, history)
    #         history.append({"role": "assistant", "content": response})
    #         st.session_state.messages.append({"role": "assistant", "content": response})
    #         st.chat_message("assistant").write(response)





