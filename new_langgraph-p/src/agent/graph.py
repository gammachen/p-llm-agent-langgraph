"""LangGraph 高级工作流模板

实现了基于星期几、天气和随机数的复杂条件工作流，包括多个工具调用和条件路由。
"""

from __future__ import annotations

import datetime
import random
from dataclasses import dataclass
from typing import Any, Dict, Literal, TypedDict

from langgraph.graph import StateGraph, END
from langgraph.runtime import Runtime


class Context(TypedDict):
    """Context parameters for the agent.

    Set these when creating assistants OR when invoking the graph.
    See: https://langchain-ai.github.io/langgraph/cloud/how-tos/configuration_cloud/
    """

    my_configurable_param: str


@dataclass
class State:
    """Input state for the agent.

    Defines the initial structure of incoming data and intermediate states.
    """
    # 输入参数
    input_query: str = ""
    
    # 中间状态
    current_weekday: str = ""
    coordinates: str = ""
    weather: str = ""
    random_number: int = 0
    current_time: str = ""
    
    # 输出结果
    result: str = ""


# 模拟工具函数
async def get_weekday_tool(state: State) -> Dict[str, Any]:
    """获取当前时间所属的星期几"""
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    current_day = datetime.datetime.now().weekday()
    weekday = weekdays[current_day]
    print(f"获取到当前是: {weekday}")
    return {"current_weekday": weekday}


async def get_coordinates_tool(state: State) -> Dict[str, Any]:
    """获取随机经纬度"""
    # 模拟生成随机经纬度（北京附近）
    latitude = 39.9 + random.uniform(-0.1, 0.1)
    longitude = 116.4 + random.uniform(-0.1, 0.1)
    coordinates = f"纬度: {latitude:.6f}, 经度: {longitude:.6f}"
    print(f"获取到经纬度: {coordinates}")
    return {"coordinates": coordinates}


async def get_weather_tool(state: State) -> Dict[str, Any]:
    """根据经纬度与当前日期获取天气"""
    # 模拟天气数据，根据随机数决定天气
    weather_conditions = ["晴天", "多云", "阴天", "小雨", "中雨", "大雨"]
    weather = random.choice(weather_conditions)
    print(f"获取到天气: {weather}")
    return {"weather": weather}


async def get_random_number_tool(state: State) -> Dict[str, Any]:
    """获取0-100之间的随机数"""
    random_num = random.randint(0, 100)
    print(f"获取到随机数: {random_num}")
    return {"random_number": random_num}


async def get_current_time_tool(state: State) -> Dict[str, Any]:
    """获取当前时间"""
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"获取到当前时间: {current_time}")
    return {"current_time": current_time}


async def send_email_tool(state: State, email_type: str) -> Dict[str, Any]:
    """发送邮件"""
    if email_type == "welcome":
        recipient = "plus50@sina.com"
        subject = "欢迎邮件"
        content = "欢迎加入我们的平台！"
    else:
        recipient = "lowfat50@sina.com"
        subject = "送别邮件"
        content = "感谢您的使用，期待下次再见！"
    
    print(f"向 {recipient} 发送邮件，主题: {subject}")
    # 实际项目中这里会调用真实的邮件发送API
    result = f"邮件已成功发送至 {recipient}，主题: {subject}"
    return {"result": result}


# 条件路由函数
async def route_by_weekday(state: State) -> Literal["check_wednesday", END]:
    """根据星期几决定路由"""
    if state.current_weekday == "星期三":
        print("今天是星期三，继续流程")
        return "check_wednesday"
    else:
        print(f"今天是{state.current_weekday}，不是星期三，结束流程")
        return END


async def route_by_weather(state: State) -> Literal["get_random_number", END]:
    """根据天气决定路由"""
    if state.weather == "晴天":
        print("天气是晴天，继续流程")
        return "get_random_number"
    else:
        print(f"天气是{state.weather}，不是晴天，结束流程")
        return END


async def route_by_random_number(state: State) -> Literal["send_welcome_email", "send_goodbye_email", END]:
    """根据随机数决定路由"""
    if state.random_number >= 50:
        print(f"随机数 {state.random_number} >= 50，发送欢迎邮件")
        return "send_welcome_email"
    else:
        print(f"随机数 {state.random_number} < 50，发送送别邮件")
        return "send_goodbye_email"


# 节点函数
async def start_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """起始节点，初始化流程"""
    print("开始执行工作流...")
    return {}


async def check_wednesday_node(state: State) -> Dict[str, Any]:
    """星期三检查节点"""
    # 这里可以添加额外的星期三处理逻辑
    return {}


async def send_welcome_email_node(state: State) -> Dict[str, Any]:
    """发送欢迎邮件节点"""
    return await send_email_tool(state, "welcome")


async def send_goodbye_email_node(state: State) -> Dict[str, Any]:
    """发送送别邮件节点"""
    return await send_email_tool(state, "goodbye")


# 定义工作流图
graph = (
    StateGraph(State, context_schema=Context)
    # 添加节点
    .add_node("start", start_node)
    .add_node("get_weekday", get_weekday_tool)
    .add_node("check_wednesday", check_wednesday_node)
    .add_node("get_coordinates", get_coordinates_tool)
    .add_node("get_weather", get_weather_tool)
    .add_node("get_random_number", get_random_number_tool)
    .add_node("get_current_time", get_current_time_tool)
    .add_node("send_welcome_email", send_welcome_email_node)
    .add_node("send_goodbye_email", send_goodbye_email_node)
    
    # 设置起始点
    .add_edge("__start__", "start")
    .add_edge("start", "get_weekday")
    
    # 添加条件边
    .add_conditional_edges(
        "get_weekday",
        route_by_weekday,
        {
            "check_wednesday": "get_coordinates",
            END: END
        }
    )
    
    # 添加流程边
    .add_edge("check_wednesday", "get_coordinates")
    .add_edge("get_coordinates", "get_weather")
    
    # 添加天气条件边
    .add_conditional_edges(
        "get_weather",
        route_by_weather,
        {
            "get_random_number": "get_random_number",
            END: END
        }
    )
    
    # 添加随机数条件边
    .add_conditional_edges(
        "get_random_number",
        route_by_random_number,
        {
            "send_welcome_email": "send_welcome_email",
            "send_goodbye_email": "send_goodbye_email",
            END: END
        }
    )
    
    # 添加结束边
    .add_edge("send_welcome_email", END)
    .add_edge("send_goodbye_email", END)
    
    # 编译工作流
    .compile(name="高级天气邮件工作流")
)
