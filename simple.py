import getpass
import os

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

from langchain.chat_models import init_chat_model

model = init_chat_model(
    "gpt-4o-mini", 
    model_provider="openai", 
    temperature=0.7)

# 调用模型
response = model.invoke("你好")
print(response)
