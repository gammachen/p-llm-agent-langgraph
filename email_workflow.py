import os
import sqlite3
import logging
import datetime
from typing import Literal, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from dotenv import load_dotenv
import random

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

def init_db():
    """初始化用户数据库信息"""
    if not os.path.exists('user.db'):
        conn = sqlite3.connect('user.db')
        c = conn.cursor()
        c.execute('''create table users
                 (id int primary key not null,
                 name varchar not null,
                 mail varchar not null);''')
        c.execute("insert into users (id, name, mail) " +
                  "values (1, 'John', 'alphachenx@sina.com')")
        c.execute("insert into users (id, name, mail) " +
                  "values (2, 'Tom', 'alphachenx@sina.com')")
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成，创建了测试用户数据")
    else:
        logger.info("数据库已存在，跳过初始化")


@tool
def query_all_users():
    """查询数据库中所有的用户信息，返回用户的id、姓名和邮箱地址"""
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("SELECT id, name, mail FROM users")
    rows = c.fetchall()
    conn.close()
    logger.info(f"查询到{len(rows)}个用户")
    return str(rows)

@tool
def query_user_by_name(name: str):
    """查询数据库中所有的用户信息，返回用户的id、姓名和邮箱地址"""
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("SELECT id, name, mail FROM users WHERE name = ?", (name,))
    rows = c.fetchall()
    if len(rows) == 0:
        return "没有查询到用户"
    else:
        conn.close()
        logger.info(f"查询到{len(rows)}个用户")
        return str(rows)
def init_recomment_db():
    """初始化推荐数据库信息"""
    if not os.path.exists('recommend.db'):
        conn = sqlite3.connect('recommend.db')
        c = conn.cursor()
        c.execute('''create table recommend
                 (id int primary key not null,
                 name varchar not null,
                 content varchar not null);''')
        c.execute("insert into recommend (id, name, content) " +
                  "values (1, '推荐你去尝试一下这个项目xxxx', '推荐你去尝试一下这个项目xxxxxxxxx')")
        c.execute("insert into recommend (id, name, content) " +
                  "values (2, '推荐你去尝试一下这个项目yyyy', '推荐你去尝试一下这个项目yyyyyyyyy')")
        c.execute("insert into recommend (id, name, content) " +
                  "values (3, '推荐你去尝试一下这个项目zzzz', '推荐你去尝试一下这个项目zzzzzzzzz')")
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成，创建了测试推荐数据")
    else:
        logger.info("数据库已存在，跳过初始化")

@tool
def query_all_recommend():
    """查询数据库中所有的推荐信息，返回推荐的id、姓名和内容"""
    conn = sqlite3.connect('recommend.db')
    c = conn.cursor()
    c.execute("SELECT id, name, content FROM recommend")
    rows = c.fetchall()
    conn.close()
    logger.info(f"查询到{len(rows)}条推荐信息")
    return str(rows)

@tool
def get_current_weekday():
    """获取当前是星期几"""
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    current_day = datetime.datetime.now().weekday()
    logger.info(f"当前是{weekdays[current_day]}")
    return weekdays[current_day]


def _send_welcome_email_impl(mail: str, name: str):
    """邮件发送的核心实现逻辑"""
    # 配置邮件服务器
    smtp_server = "smtp.sina.com"
    smtp_port = 587
    
    # 从环境变量中获取邮件发送者信息
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        error_msg = "未配置邮件发送者信息，请检查.env文件"
        logger.error(error_msg)
        return error_msg
    
    # 创建邮件对象
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = mail
    msg['Subject'] = "欢迎加入我们的平台"
    
    # 添加邮件正文
    body = f"亲爱的{name}：\n\n欢迎加入我们的平台！我们很高兴能有您这样的用户。\n\n如有任何问题，请随时联系我们。\n\n祝好！\n我们的团队"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # 连接到SMTP服务器并发送邮件
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # server.starttls()  # 如果需要SSL/TLS加密连接，可以取消注释此行
            server.login(sender_email, sender_password)
            server.send_message(msg)
            logger.info(f"欢迎邮件已发送至 {mail}（{name}）")
            return f"成功发送欢迎邮件至{name}（{mail}）"
    except Exception as e:
        error_msg = f"发送邮件时出错：{str(e)}"
        logger.error(error_msg)
        return error_msg


@tool
def send_welcome_email(mail: str, name: str):
    """给指定用户发送欢迎邮件"""
    return _send_welcome_email_impl(mail, name)

@tool
def get_random_number():
    """返回一个随机数，范围是0 到 100 """
    return random.randint(0, 100)


# 定义工具列表
tools = [query_all_users, query_user_by_name,send_welcome_email, get_current_weekday, query_all_recommend, get_random_number]
tool_node = ToolNode(tools)

# 初始化Ollama模型
model = ChatOllama(
    model="qwen2:latest",
    base_url="http://localhost:11434",
    temperature=0
)

# 为Ollama模型配置工具调用功能
model = model.bind_tools(tools)

def check_weekday_and_random_number(state: MessagesState) -> Literal["tools", "process_random_number", END]:
    '''根据工具调用请求或工具返回结果决定路由'''
    messages = state['messages']
    last_message = messages[-1]
    
    # 检查是否有工具调用请求
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    # 检查是否是工具返回的结果
    if hasattr(last_message, 'name'):
        # 如果已经获取了星期几和随机数，处理随机数
        weekday_found = False
        random_number_found = False
        for msg in messages:
            if hasattr(msg, 'name'):
                if msg.name == 'get_current_weekday':
                    weekday_found = True
                elif msg.name == 'get_random_number':
                    random_number_found = True
        
        if weekday_found and random_number_found:
            return "process_random_number"
        
        # 如果还需要获取其他工具的结果，继续使用工具
        return "tools"
    
    # 其他情况结束对话
    return END


def process_random_number(state: MessagesState) -> Dict[str, Any]:
    '''根据随机数处理邮件发送任务'''
    # 从消息中提取星期几和随机数
    weekday = None
    random_number = None
    
    for msg in state['messages']:
        if hasattr(msg, 'name'):
            if msg.name == 'get_current_weekday':
                weekday = msg.content
            elif msg.name == 'get_random_number':
                # 尝试将内容转换为整数
                try:
                    random_number = int(msg.content)
                except ValueError:
                    # 如果转换失败，检查内容中是否包含数字
                    import re
                    numbers = re.findall(r'\d+', msg.content)
                    if numbers:
                        random_number = int(numbers[0])
                    else:
                        random_number = 0
    
    logger.info(f"获取到当前是{weekday}，随机数是{random_number}")
    
    # 根据随机数大小执行不同操作
    if random_number > 50:
        # 随机数大于50，获取John的邮箱并发送包含随机数和推荐信息的邮件
        conn = sqlite3.connect('user.db')
        c = conn.cursor()
        c.execute("SELECT id, name, mail FROM users WHERE name = ?", ("John",))
        john_user = c.fetchone()
        conn.close()
        
        if john_user:
            _, name, mail = john_user
            # 获取推荐信息
            recommend_conn = sqlite3.connect('recommend.db')
            recommend_c = recommend_conn.cursor()
            recommend_c.execute("SELECT id, name, content FROM recommend")
            recommend_data = recommend_c.fetchall()
            recommend_conn.close()
            
            # 构建邮件内容
            email_content = f"亲爱的{name}：\n\n您好！这是一封包含随机数和推荐信息的邮件。\n\n随机数：{random_number}\n\n推荐信息：\n"
            for item in recommend_data:
                email_content += f"- {item[1]}: {item[2]}\n"
            email_content += "\n如有任何问题，请随时联系我们。\n\n祝好！\n我们的团队"
            
            # 发送邮件
            result = send_custom_email(mail, name, email_content, "随机数与推荐信息")
            return {"messages": [AIMessage(content=f"任务已完成：随机数{random_number}大于50，已向John发送包含随机数和推荐信息的邮件\n{result}")]}
        else:
            return {"messages": [AIMessage(content="任务执行失败：未找到名为John的用户")]}
    else:
        # 随机数小于等于50，获取Tom的邮箱并发送包含随机数和推荐信息的邮件
        conn = sqlite3.connect('user.db')
        c = conn.cursor()
        c.execute("SELECT id, name, mail FROM users WHERE name = ?", ("Tom",))
        tom_user = c.fetchone()
        conn.close()
        
        if tom_user:
            _, name, mail = tom_user
            # 获取推荐信息
            recommend_conn = sqlite3.connect('recommend.db')
            recommend_c = recommend_conn.cursor()
            recommend_c.execute("SELECT id, name, content FROM recommend")
            recommend_data = recommend_c.fetchall()
            recommend_conn.close()
            
            # 构建邮件内容
            email_content = f"亲爱的{name}：\n\n您好！这是一封包含随机数和推荐信息的邮件。\n\n随机数：{random_number}\n\n推荐信息：\n"
            for item in recommend_data:
                email_content += f"- {item[1]}: {item[2]}\n"
            email_content += "\n如有任何问题，请随时联系我们。\n\n祝好！\n我们的团队"
            
            # 发送邮件
            result = send_custom_email(mail, name, email_content, "随机数与推荐信息")
            return {"messages": [AIMessage(content=f"任务已完成：随机数{random_number}小于等于50，已向Tom发送包含随机数和推荐信息的邮件\n{result}")]}
        else:
            return {"messages": [AIMessage(content="任务执行失败：未找到名为Tom的用户")]}


def send_custom_email(mail: str, name: str, content: str, subject: str = "自定义邮件"):
    '''发送自定义内容的邮件'''
    # 配置邮件服务器
    smtp_server = "smtp.sina.com"
    smtp_port = 587
    
    # 从环境变量中获取邮件发送者信息
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        error_msg = "未配置邮件发送者信息，请检查.env文件"
        logger.error(error_msg)
        return error_msg
    
    # 创建邮件对象
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = mail
    msg['Subject'] = subject
    
    # 添加邮件正文
    msg.attach(MIMEText(content, 'plain'))
    
    try:
        # 连接到SMTP服务器并发送邮件
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # server.starttls()  # 如果需要SSL/TLS加密连接，可以取消注释此行
            server.login(sender_email, sender_password)
            server.send_message(msg)
            logger.info(f"邮件已发送至 {mail}（{name}），主题：{subject}")
            return f"成功发送邮件至{name}（{mail}）"
    except Exception as e:
        error_msg = f"发送邮件时出错：{str(e)}"
        logger.error(error_msg)
        return error_msg


def call_model(state: MessagesState):
    '''Agent调用LLM的方法'''    
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}


def init_workflow():
    """初始化工作流"""
    # 创建状态图以管理消息状态和流程控制
    workflow = StateGraph(MessagesState)
    
    # 定义节点
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.add_node("process_random_number", process_random_number)
    
    # 定义工作流的入口点为agent节点
    workflow.set_entry_point("agent")
    
    # 添加条件边，根据工具调用请求或工具返回结果决定路由
    workflow.add_conditional_edges(
        "agent",
        check_weekday_and_random_number,
    )
    
    # 添加工具调用完成后的边
    workflow.add_edge("tools", 'agent')
    
    # 添加处理随机数的边
    workflow.add_edge("process_random_number", END)
    
    # 初始化内存以在状态图运行过程中保持状态
    checkpointer = InMemorySaver()
    
    # 将工作流编译成一个可执行的App
    app = workflow.compile(checkpointer=checkpointer)
    return app


if __name__ == "__main__":
    # 初始化数据库
    init_db()
    
    init_recomment_db()
    
    # 初始化工作流
    app = init_workflow()
    
    # 定义任务指令：同时获取当前星期几和随机数
    task_instruction = """请同时调用get_current_weekday工具获取当前是星期几，以及调用get_random_number工具获取一个随机数。"""
    
    # 执行工作流
    inputs = {"messages": [HumanMessage(content=task_instruction)]}
    
    logger.info("开始执行工作流：查询所有用户并发送欢迎邮件")
    
    # 流式输出结果
    i = 0
    for output in app.stream(
            inputs,
            config={"configurable": {"thread_id": 42}}):
        for key, value in output.items():
            i += 1
            print(f"\n==========={i}、从'{key}'输出:\n{value}")
    
    logger.info("工作流执行完成")