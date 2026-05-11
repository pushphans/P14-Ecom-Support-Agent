from langchain.tools import tool


@tool
def check_stock(product_name: str) -> str:
    """Checks the inventory for a given product name to see if it is in stock."""
    print(f"\n[TOOL CALLED] Checking stock for: {product_name}")

    # Mock logic: Sirf laptop aur phone stock mein hain
    if product_name.lower() in ["laptop", "phone"]:
        return f"Yes, '{product_name}' is currently In Stock."
    else:
        return f"Sorry, '{product_name}' is Out of Stock."


# List of tools to export
inventory_tools = [check_stock]
