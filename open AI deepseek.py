from openai import OpenAI

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

client = OpenAI(
    api_key="sk-9408079017cf46ba95c085a4a00ab0d3",
    base_url="https://api.deepseek.com/v1",
)

def get_completion(_prompt, _model):
    messages = [{"role": "user", "content": _prompt}]
    response = client.chat.completions.create(
        model=_model,
        messages=messages,
        temperature=0,
    )
    print(response)
    return response.choices[0].message.content


customer_email = """
Arrr, I be fuming that me blender lid \
flew off and splattered me kitchen walls \
with smoothie! And to make matters worse,\
the warranty don't cover the cost of \
cleaning up me kitchen. I need yer help \
right now, matey!
"""

style = """American English \
in a calm and respectful tone
"""

prompt = f"""Translate the text \
that is delimited by triple backticks 
into a style that is {style}.
text: ```{customer_email}```
"""

response = get_completion(prompt, "deepseek-chat")

print(response)