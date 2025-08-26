import os
import sqlite3
from typing import Literal
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama

def init_db():
    """初始化数据库信息"""
    if not os.path.exists('test.db'):
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute('''create table users
                 (id int primary key not null,
                 name varchar not null,
                 mail varchar not null);''')
        c.execute("insert into users (id, name, mail) " +
                  "values (1, 'John', 'john@test.com')")
        c.execute("insert into users (id, name, mail) " +
                  "values (2, 'Tom', 'tom@test.com')")
        conn.commit()
        conn.close()


def query_from_db(sql: str):
    """使用SQL语句从数据库查询信息"""
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute(sql)
    rows = c.fetchall()
    conn.close()
    return rows


@tool
def search(query: str):
    """从数据库查询用户信息"""
    return str(query_from_db(query))


tools = [search]
tool_node = ToolNode(tools)
model = ChatOllama(
    model="qwen2:latest",
    base_url="http://localhost:11434",
    temperature=0
)

# 为Ollama模型配置工具调用功能
model = model.bind_tools(tools)


def should_continue(state: MessagesState) -> Literal["tools", END]:
    '''定义继续条件'''
    messages = state['messages']
    last_message = messages[-1]
    # 如果LLM命中了tool call, 则路由到tools节点
    if last_message.tool_calls:
        return "tools"
    # 否则以LLM的返回回复用户，结束对话
    return END


def call_model(state: MessagesState):
    '''Agent调用LLM的方法'''
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}


def init_workflow():
    # 创建状态图以管理消息状态和流程控制
    workflow = StateGraph(MessagesState)
    # 定义将循环运行的两个节点
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    # 定义工作流的入口点为agent节点
    workflow.set_entry_point("agent")
    # 添加条件边，当agent被调用时判断是否继续流转
    workflow.add_conditional_edges(
        "agent",
        should_continue,
    )
    # 添加两个普通边，tools被调用完后，继续调用agent
    workflow.add_edge("tools", 'agent')
    # 初始化内存以在状态图运行过程中保持状态
    checkpointer = InMemorySaver()
    # 将工作流编译成一个可执行的App
    app = workflow.compile(checkpointer=checkpointer)
    return app


if __name__ == "__main__":
    init_db()
    app = init_workflow()
    inputs = {"messages": [HumanMessage(
        content="从数据库查询一下id=1的用户信息，数据库的schema信息为：id int primary key not null, name varchar not null, mail varchar not null，表名：users，数据库是sqlite3，输出是完整的查询sql语句")]} # 补充数据库的schema信息
    i = 0
    for output in app.stream(
            inputs,
            config={"configurable": {"thread_id": 42}}):
        for key, value in output.items():
            i = i + 1
            print(f"\n===========\n{i}、从'{key}'输出:")
            print(value)

'''
(langgraph) shhaofu@shhaofudeMacBook-Pro p-llm-agent-langgraph % python langgraph-sample.py 

===========
1、从'agent'输出:
{'messages': [AIMessage(content='', additional_kwargs={}, response_metadata={'model': 'qwen2:latest', 'created_at': '2025-08-26T08:09:38.812215Z', 'done': True, 'done_reason': 'stop', 'total_duration': 2920104125, 'load_duration': 83042375, 'prompt_eval_count': 147, 'prompt_eval_duration': 2077102292, 'eval_count': 26, 'eval_duration': 757836583, 'model_name': 'qwen2:latest'}, id='run--8f378568-0cfc-424e-b32b-d609448a51b9-0', tool_calls=[{'name': 'search', 'args': {'query': 'id=1'}, 'id': '09c60939-2556-4bbd-ad3b-0e2d7d1a7228', 'type': 'tool_call'}], usage_metadata={'input_tokens': 147, 'output_tokens': 26, 'total_tokens': 173})]}

===========
2、从'tools'输出:
{'messages': [ToolMessage(content='Error: OperationalError(\'near "id": syntax error\')\n Please fix your mistakes.', name='search', id='7f39a7ef-c620-4b9e-b912-6fb6ce8eabf8', tool_call_id='09c60939-2556-4bbd-ad3b-0e2d7d1a7228', status='error')]}

===========
3、从'agent'输出:
{'messages': [AIMessage(content='查询ID为1的用户信息时遇到了错误，错误信息为：在"id"附近时语法错误。请检查您的输入或数据库结构是否正确。', additional_kwargs={}, response_metadata={'model': 'qwen2:latest', 'created_at': '2025-08-26T08:09:40.053453Z', 'done': True, 'done_reason': 'stop', 'total_duration': 1234919959, 'load_duration': 49931750, 'prompt_eval_count': 206, 'prompt_eval_duration': 232134208, 'eval_count': 34, 'eval_duration': 949750208, 'model_name': 'qwen2:latest'}, id='run--aeebd1cb-272e-491c-9b1b-eaa2874ba5b1-0', usage_metadata={'input_tokens': 206, 'output_tokens': 34, 'total_tokens': 240})]}
(langgraph) shhaofu@shhaofudeMacBook-Pro p-llm-agent-langgraph % python langgraph-sample.py

===========
1、从'agent'输出:
{'messages': [AIMessage(content='', additional_kwargs={}, response_metadata={'model': 'qwen2:latest', 'created_at': '2025-08-26T09:43:05.117956Z', 'done': True, 'done_reason': 'stop', 'total_duration': 7455082208, 'load_duration': 872663500, 'prompt_eval_count': 187, 'prompt_eval_duration': 5687830167, 'eval_count': 32, 'eval_duration': 880947083, 'model_name': 'qwen2:latest'}, id='run--265868fa-b766-4281-96b5-32d2b3d80aed-0', tool_calls=[{'name': 'search', 'args': {'query': 'SELECT * FROM users WHERE id = 1'}, 'id': 'ebc293b0-7d38-49a7-9138-095a27d15a7b', 'type': 'tool_call'}], usage_metadata={'input_tokens': 187, 'output_tokens': 32, 'total_tokens': 219})]}

===========
2、从'tools'输出:
{'messages': [ToolMessage(content="[(1, 'John', 'john@test.com')]", name='search', id='09518afc-34f8-44d3-b90c-d58349883b4d', tool_call_id='ebc293b0-7d38-49a7-9138-095a27d15a7b')]}

===========
3、从'agent'输出:
{'messages': [AIMessage(content='查询结果如下：\n\n- id: 1\n- name: John\n- mail: john@test.com', additional_kwargs={}, response_metadata={'model': 'qwen2:latest', 'created_at': '2025-08-26T09:43:06.00703Z', 'done': True, 'done_reason': 'stop', 'total_duration': 878735125, 'load_duration': 47101542, 'prompt_eval_count': 246, 'prompt_eval_duration': 228300791, 'eval_count': 22, 'eval_duration': 600743084, 'model_name': 'qwen2:latest'}, id='run--1e96e244-ad8f-4687-939a-10fcb549074f-0', usage_metadata={'input_tokens': 246, 'output_tokens': 22, 'total_tokens': 268})]}
'''


