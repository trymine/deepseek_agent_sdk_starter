from agents.decorators import tool

# Demo data only. Replace this dictionary with a properly authenticated ERP/API call.
ORDERS = {
    "A100": {"status": "已发货", "tracking_number": "SF123456"},
    "A101": {"status": "待处理", "tracking_number": None},
}


@tool(strict_mode=False)
def get_order_status(order_id: str) -> str:
    """根据订单编号查询订单状态和物流单号。

    Args:
        order_id: 需要查询的订单编号，例如 A100。
    """
    order = ORDERS.get(order_id)
    if order is None:
        return f"未找到订单：{order_id}"

    tracking = order["tracking_number"] or "暂无物流单号"
    return (
        f"订单编号：{order_id}；"
        f"订单状态：{order['status']}；"
        f"物流单号：{tracking}"
    )
