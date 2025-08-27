from langchain_ollama import ChatOllama

llm = ChatOllama(
    # model = "gpt-oss:20b",
    model = "qwen2:latest",
    base_url="http://localhost:11434",
    validate_model_on_init = True,
    temperature = 0.8,
    num_predict = 256,
    # other params ...
)

messages = [
    ("system", "You are a helpful translator. Translate the user sentence to Chinese."),
    ("human", "I love programming."),
]
llm.invoke(messages)


for chunk in llm.stream("Return the words Hello World!"):
    print(chunk.text(), end="")
    
stream = llm.stream(messages)

full = next(stream)
for chunk in stream:
    full += chunk
full

# await llm.ainvoke("Hello how are you!")

# async for chunk in llm.astream("Say hello world!"):
#     print(chunk.content)
    
# messages = [
#     ("human", "Say hello world!"),
#     ("human","Say goodbye world!")
# ]
# await llm.abatch(messages)

llm = ChatOllama(
    # model = "deepseek-r1:8b",
    model = "qwen2:latest", # glm4:latest
    validate_model_on_init = True,
    reasoning= True,
)

# or, on an invocation basis:
try:
    llm.invoke("how many r in the word strawberry?")
except Exception as e:
    print(e)

try:
    llm.invoke("how many r in the word strawberry?", reasoning=True)
except Exception as e:
    print(e)


'''
(langgraph) shhaofu@shhaofudeMacBook-Pro p-llm-agent-langgraph % python simple_ollama.py
Hello World!Traceback (most recent call last):
  File "/Users/shhaofu/Code/cursor-projects/p-llm-agent-langgraph/simple_ollama.py", line 47, in <module>
    llm.invoke("how many r in the word strawberry?")
  File "/opt/anaconda3/envs/langgraph/lib/python3.11/site-packages/langchain_core/language_models/chat_models.py", line 383, in invoke
    self.generate_prompt(
  File "/opt/anaconda3/envs/langgraph/lib/python3.11/site-packages/langchain_core/language_models/chat_models.py", line 1006, in generate_prompt
    return self.generate(prompt_messages, stop=stop, callbacks=callbacks, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/langgraph/lib/python3.11/site-packages/langchain_core/language_models/chat_models.py", line 825, in generate
    self._generate_with_cache(
  File "/opt/anaconda3/envs/langgraph/lib/python3.11/site-packages/langchain_core/language_models/chat_models.py", line 1072, in _generate_with_cache
    result = self._generate(
             ^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/langgraph/lib/python3.11/site-packages/langchain_ollama/chat_models.py", line 822, in _generate
    final_chunk = self._chat_stream_with_aggregation(
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/langgraph/lib/python3.11/site-packages/langchain_ollama/chat_models.py", line 757, in _chat_stream_with_aggregation
    for chunk in self._iterate_over_stream(messages, stop, **kwargs):
  File "/opt/anaconda3/envs/langgraph/lib/python3.11/site-packages/langchain_ollama/chat_models.py", line 844, in _iterate_over_stream
    for stream_resp in self._create_chat_stream(messages, stop, **kwargs):
  File "/opt/anaconda3/envs/langgraph/lib/python3.11/site-packages/langchain_ollama/chat_models.py", line 743, in _create_chat_stream
    yield from self._client.chat(**chat_params)
  File "/opt/anaconda3/envs/langgraph/lib/python3.11/site-packages/ollama/_client.py", line 170, in inner
    raise ResponseError(e.response.text, e.response.status_code) from None
ollama._types.ResponseError: registry.ollama.ai/library/qwen2:latest does not support thinking (status code: 400)
'''

# or llm.stream("how many r in the word strawberry?", reasoning=True)

# If not provided, the invocation will default to the ChatOllama reasoning
# param provided (None by default).

llm = ChatOllama(
    # model = "deepseek-r1:8b",
    # model = "granite3.2:2b",
    # model="llama3:8b",
    # model = "gemma3:1b",
    model = "qwen3:1.7b",
    validate_model_on_init = True,
    reasoning= True,
)

# or, on an invocation basis:
try:
    m = llm.invoke("how many r in the word strawberry?")
    print(m.content)
except Exception as e:
    print(e)

try:
    m = llm.invoke("how many r in the word strawberry?", reasoning=True)
    print(m.content)
except Exception as e:
    print(e)