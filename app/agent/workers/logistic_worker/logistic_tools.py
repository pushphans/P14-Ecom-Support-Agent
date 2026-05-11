from langchain.tools import tool


@tool
def track_order(order_id: str) -> str:
    """Tracks the delivery status of a customer's order using its order ID."""
    print(f"\n[TOOL CALLED] Tracking order status for: {order_id}")

    # Mock logic: Hamesha out for delivery return karega
    return f"Order {order_id} is currently out for delivery and will reach you soon."


# List of tools to export
logistics_tools = [track_order]
