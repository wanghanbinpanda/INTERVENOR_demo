import backoff
import openai
from openai import OpenAI
@backoff.on_exception(backoff.expo, openai.RateLimitError)
def gpt_agent(messages, n):
    import openai

    openai.api_key = 'sk-b55cccba08844a7f94a801c088b6553a'  # 令牌处创建，获得
    openai.api_base = 'https://api.deepseek.com/v1'

    openai.default_headers = {"x-foo": "true"}

    from openai import OpenAI

    client = OpenAI(
        api_key='sk-b55cccba08844a7f94a801c088b6553a',
        base_url='https://api.deepseek.com/v1'
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        max_tokens=2048,
        temperature=1,
        top_p=1,
        stop=[],
        n=n
    )
    responses = [response.choices[i].message.content for i in range(n)]
    return responses, response.usage, response.model


messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "who are you?"},
    {"role": "user", "content": "who are you?"}
]
n = 1
responses, usage, model = gpt_agent(messages, n)
print(responses, usage, model)