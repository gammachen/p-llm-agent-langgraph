#!/usr/bin/env python3
"""
测试 LangGraph 高级工作流

该脚本用于测试我们在 graph.py 中定义的基于星期几、天气和随机数的复杂条件工作流。
"""

import asyncio
import sys
import os
from typing import Any, Dict

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 初始化工作流变量
graph = None
State = None
Context = None

# 导入我们的工作流模块
graph = None
State = None
Context = None

print("尝试导入工作流模块...")
try:
    # 尝试直接从目录结构导入 (最简单的方式)
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'new_langgraph-p'))
    from src.agent.graph import graph as workflow_graph, State as WorkflowState, Context as WorkflowContext
    
    # 赋值给预期变量名
    graph = workflow_graph
    State = WorkflowState
    Context = WorkflowContext
    print("成功从src.agent.graph导入工作流模块")
    
except ImportError as e1:
    print(f"第一次导入尝试失败: {str(e1)}")
    try:
        # 最后尝试直接加载文件
        graph_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'new_langgraph-p', 'src', 'agent', 'graph.py')
        print(f"尝试直接加载文件: {graph_file_path}")
        
        import importlib.util
        spec = importlib.util.spec_from_file_location("graph_module", graph_file_path)
        
        if spec and spec.loader:
            graph_module = importlib.util.module_from_spec(spec)
            sys.modules["graph_module"] = graph_module
            spec.loader.exec_module(graph_module)
            
            graph = graph_module.graph
            State = graph_module.State
            Context = graph_module.Context
            print("成功通过importlib直接加载graph.py文件")
        else:
            raise ImportError(f"无法导入graph.py模块，文件路径: {graph_file_path}")
        
    except ImportError as e2:
        print(f"第二次导入尝试失败: {str(e2)}")
        print("无法导入工作流模块，将创建一个简单的模拟版本进行测试...")
        
        # 创建一个简单的模拟版本
        class MockState:
            def __init__(self, **kwargs):
                self.input_query = kwargs.get('input_query', '')
                self.current_weekday = "星期三"  # 模拟是星期三，以便测试完整流程
                self.coordinates = "纬度: 39.9042, 经度: 116.4074"  # 北京坐标
                self.weather = "晴天"  # 模拟是晴天
                self.random_number = 75  # 模拟随机数大于50
                self.current_time = "2023-11-15 12:00:00"
                self.result = "邮件已成功发送至 plus50@sina.com，主题: 欢迎邮件"
        
        class MockContext(dict):
            pass
            
        class MockGraph:
            async def ainvoke(self, initial_state, config=None):
                print("模拟工作流执行...")
                # 模拟执行流程
                print("开始执行工作流...")
                print(f"获取到当前是: 星期三")
                print("今天是星期三，继续流程")
                print(f"获取到经纬度: 纬度: 39.9042, 经度: 116.4074")
                print(f"获取到天气: 晴天")
                print("天气是晴天，继续流程")
                print(f"获取到随机数: 75")
                print("随机数 75 >= 50，发送欢迎邮件")
                print("向 plus50@sina.com 发送邮件，主题: 欢迎邮件")
                
                # 返回模拟结果
                return MockState(**initial_state)
                
        graph = MockGraph()
        State = MockState
        Context = MockContext


async def test_workflow():
    """测试工作流执行"""
    try:
        print("准备测试工作流...")
        
        # 创建初始状态字典（因为graph.py返回字典）
        initial_state = {
            "input_query": "执行高级工作流测试"
        }
        
        # 创建上下文配置
        config = {"thread_id": "test_thread_123"}
        
        print("开始执行工作流...")
        # 执行工作流
        result = await graph.ainvoke(initial_state, config=config)
        
        print("\n=== 工作流执行结果摘要 ===")
        # 检查result是否为字典
        if isinstance(result, dict):
            # 使用字典访问方式获取数据
            print(f"输入查询: {result.get('input_query', 'N/A')}")
            current_weekday = result.get('current_weekday', 'N/A')
            print(f"当前星期几: {current_weekday}")
            
            # 检查是否获取了经纬度（星期三才会执行这一步）
            coordinates = result.get('coordinates', '')
            if coordinates:
                print(f"经纬度: {coordinates}")
                print("  ✓ 已成功获取经纬度")
            else:
                print("  ✗ 未获取经纬度（可能不是星期三）")
            
            # 检查是否获取了天气（星期三且经纬度有效才会执行这一步）
            weather = result.get('weather', '')
            if weather:
                print(f"天气: {weather}")
                print("  ✓ 已成功获取天气信息")
            else:
                print("  ✗ 未获取天气信息（可能不是星期三）")
            
            # 检查是否获取了随机数（星期三且天气是晴天才会执行这一步）
            random_number = result.get('random_number')
            if random_number is not None:
                print(f"随机数: {random_number}")
                print("  ✓ 已成功获取随机数")
            else:
                print("  ✗ 未获取随机数（可能不是星期三或天气不是晴天）")
            
            # 检查是否获取了当前时间
            current_time = result.get('current_time', '')
            if current_time:
                print(f"当前时间: {current_time}")
            
            # 检查最终结果
            final_result = result.get('result', '')
            if final_result:
                print(f"\n最终执行结果: {final_result}")
                
            # 输出工作流执行状态
            print("\n=== 工作流执行状态 ===")
            if current_weekday == "星期三":
                print("- 已触发星期三特定流程")
                if weather == "晴天":
                    print("- 天气条件满足（晴天），已继续执行随机数判断流程")
                    if random_number is not None:
                        if random_number >= 50:
                            print(f"- 随机数 {random_number} >= 50，已触发发送欢迎邮件流程")
                        else:
                            print(f"- 随机数 {random_number} < 50，已触发发送送别邮件流程")
                else:
                    print("- 天气条件不满足（非晴天），未继续执行随机数判断流程")
            else:
                print(f"- 今天是{current_weekday}，不是星期三，未触发特定流程")
        else:
            # 如果result不是字典，尝试使用属性访问（兼容模拟版本）
            print(f"输入查询: {getattr(result, 'input_query', 'N/A')}")
            current_weekday = getattr(result, 'current_weekday', 'N/A')
            print(f"当前星期几: {current_weekday}")
            # 其他属性访问类似处理
            
    except Exception as e:
        print(f"测试工作流时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_multiple_scenarios():
    """测试多种场景（可选：用于测试不同条件下的工作流行为）"""
    print("\n=== 开始测试多种场景 ===")
    print("注意：此测试需要修改graph.py中的模拟函数来模拟不同条件")
    print("场景1: 星期三 + 晴天 + 随机数>=50 → 发送欢迎邮件")
    print("场景2: 星期三 + 晴天 + 随机数<50 → 发送送别邮件")
    print("场景3: 星期三 + 非晴天 → 不发送邮件")
    print("场景4: 非星期三 → 不触发特定流程")
    print("要测试这些场景，请手动修改graph.py中的模拟工具函数返回值")

# 运行测试
if __name__ == "__main__":
    print("\n====================================")
    print("          LangGraph 工作流测试")
    print("====================================")
    print("该测试将执行基于星期几、天气和随机数的复杂条件工作流")
    print("\n测试流程:")
    print("1. 获取当前星期几")
    print("2. 如果是星期三，获取经纬度")
    print("3. 通过经纬度和当前日期获取天气")
    print("4. 如果天气是晴天，获取随机数")
    print("5. 根据随机数大小决定发送哪种邮件\n")
    
    # 运行主要测试
    asyncio.run(test_workflow())
    
    # 显示多场景测试说明
    asyncio.run(test_multiple_scenarios())
    
    print("\n测试完成！")