"""
Example tools that can be used with the Chat class.
"""

from orders import orders, customers


def get_weather(city: str) -> str:
    """Get the weather for a city"""
    return f"It's sunny in {city}!"


def get_order(order_id: str) -> str:
    """Get order details by order ID"""
    if order_id in orders:
        order = orders[order_id]
        return f"Order {order['id']}: {order['product']} (Qty: {order['quantity']}, Price: ${order['price']}, Status: {order['status']})"
    return f"Order {order_id} not found"


def get_customer(customer_id: str) -> str:
    """Get customer details by customer ID"""
    if customer_id in customers:
        customer = customers[customer_id]
        order_list = ", ".join([o['id'] for o in customer['orders']])
        return f"Customer {customer['name']} (Email: {customer['email']}, Phone: {customer['phone']}, Orders: {order_list})"
    return f"Customer {customer_id} not found"


def list_orders() -> str:
    """List all orders in the system"""
    order_list = []
    for order_id, order in orders.items():
        order_list.append(f"{order['id']}: {order['product']} - {order['status']}")
    return "\n".join(order_list)


def calculate(expression: str) -> str:
    """Evaluate a mathematical expression"""
    try:
        # Safe evaluation - only allows basic math operations
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error calculating: {str(e)}"
