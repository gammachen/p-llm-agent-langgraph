from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

# 1. 定义状态 State
class OrderState(TypedDict):
    order_id: str
    product_id: str
    quantity: int
    is_valid: bool
    inventory_sufficient: bool
    payment_success: bool
    logistics_assigned: bool
    message: str

# 2. 定义各个节点函数 (Node Functions)
def receive_order(state: OrderState) -> OrderState:
    """节点1: 接收订单"""
    print(f"正在接收订单 {state['order_id']}...")
    # 简单的验证逻辑
    if state['quantity'] > 0:
        state['is_valid'] = True
        state['message'] = f"订单 {state['order_id']} 验证通过。"
    else:
        state['is_valid'] = False
        state['message'] = "订单数量无效。"
    return state

def check_inventory(state: OrderState) -> OrderState:
    """节点2: 检查库存"""
    if state['is_valid']:
        print(f"正在为订单 {state['order_id']} 检查商品 {state['product_id']} 的库存...")
        # 模拟库存检查：假设商品 "item_001" 有 10 个库存
        if state['product_id'] == "item_001" and state['quantity'] <= 10:
            state['inventory_sufficient'] = True
            state['message'] = "库存充足。"
        else:
            state['inventory_sufficient'] = False
            state['message'] = "库存不足。"
    else:
        state['message'] = "订单无效，跳过库存检查。"
        state['inventory_sufficient'] = False
    return state

def process_payment(state: OrderState) -> OrderState:
    """节点3: 处理支付"""
    if state['inventory_sufficient']:
        print(f"正在为订单 {state['order_id']} 处理支付...")
        # 模拟支付处理：假设数量为偶数时支付成功
        if state['quantity'] % 2 == 0:
            state['payment_success'] = True
            state['message'] = "支付成功。"
        else:
            state['payment_success'] = False
            state['message'] = "支付失败。"
    else:
        state['message'] = "库存不足，跳过支付处理。"
    return state

def assign_logistics(state: OrderState) -> OrderState:
    """节点4: 分配物流"""
    if state['payment_success']:
        print(f"正在为订单 {state['order_id']} 分配物流...")
        state['logistics_assigned'] = True
        state['message'] = "已分配物流。"
    else:
        state['message'] = "支付未成功，无法分配物流。"
    return state

def inventory_alert(state: OrderState) -> OrderState:
    """节点5: 库存预警"""
    print(f"警报：订单 {state['order_id']} 所需商品 {state['product_id']} 库存不足！")
    state['message'] = "已触发库存预警。"
    return state

def handle_payment_failure(state: OrderState) -> OrderState:
    """节点6: 处理支付失败"""
    print(f"订单 {state['order_id']} 支付失败，需要人工介入或提醒用户。")
    state['message'] = "支付失败已处理。"
    return state

# 3. 定义条件边所需的路径函数 (Path Functions)
def route_after_inventory_check(state: OrderState) -> Literal["sufficient", "insufficient"]:
    """在检查库存后决定路径"""
    if state['inventory_sufficient']:
        return "sufficient" # 库存充足
    else:
        return "insufficient" # 库存不足

def route_after_payment(state: OrderState) -> Literal["success", "failure"]:
    """在支付处理后决定路径"""
    if state['payment_success']:
        return "success" # 支付成功
    else:
        return "failure" # 支付失败

# 4. 构建图
builder = StateGraph(OrderState) # 创建图构建器，指定状态类型

# 添加节点 (Add Nodes)
builder.add_node("receive_order", receive_order)
builder.add_node("check_inventory", check_inventory)
builder.add_node("process_payment", process_payment)
builder.add_node("assign_logistics", assign_logistics)
builder.add_node("inventory_alert", inventory_alert)
builder.add_node("handle_payment_failure", handle_payment_failure)

# 设置入口节点 (Set Entry Point)
builder.set_entry_point("receive_order")

# 添加边 (Add Edges)
# 从 receive_order 连接到 check_inventory
builder.add_edge("receive_order", "check_inventory")

# 添加条件边：从 check_inventory 根据路由函数分流
builder.add_conditional_edges(
    "check_inventory",
    route_after_inventory_check, # 路径判断函数
    {
        "sufficient": "process_payment", # 库存充足 -> 支付处理
        "insufficient": "inventory_alert" # 库存不足 -> 库存预警
    }
)

# 添加条件边：从 process_payment 根据路由函数分流
builder.add_conditional_edges(
    "process_payment",
    route_after_payment, # 路径判断函数
    {
        "success": "assign_logistics", # 支付成功 -> 分配物流
        "failure": "handle_payment_failure" # 支付失败 -> 支付失败处理
    }
)

# 为“分配物流”、“库存预警”、“支付失败处理”这三个节点添加通向 END 的普通边
builder.add_edge("assign_logistics", END)
builder.add_edge("inventory_alert", END)
builder.add_edge("handle_payment_failure", END)

# 5. 编译图
graph = builder.compile()

# 6. 执行图
# 模拟一个订单
initial_state = {
    "order_id": "order_12345",
    "product_id": "item_001",
    "quantity": 2, # 尝试修改数量为 11（库存不足）或 3（支付失败）来看不同分支效果
    "is_valid": False, # 初始值，会被节点覆盖
    "inventory_sufficient": False,
    "payment_success": False,
    "logistics_assigned": False,
    "message": "",
}
final_state = graph.invoke(initial_state)
print("\n最终状态信息:", final_state['message'])
print("完整最终状态:", final_state)

try:
    # 尝试绘制流程图
    graph.get_graph().draw_png(output_file_path="order_flow.png")
    print("流程图已成功保存为 order_flow.png")
except Exception as e:
    # 如果绘制失败（例如缺少pygraphviz依赖），打印友好的错误信息
    print(f"绘制流程图时出错: {str(e)}")
    print("提示: 如需绘制流程图，请先安装系统级Graphviz库，然后重新安装pygraphviz")
    print("MacOS用户可以使用: brew install graphviz")
    print("Ubuntu用户可以使用: sudo apt-get install graphviz graphviz-dev")
