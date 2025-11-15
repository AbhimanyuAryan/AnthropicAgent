"""
Demo showing how to use the Chat class with tools.
"""

from chat import Chat
from tools import get_weather, get_order, get_customer, list_orders, calculate


def simple_demo():
    """Simple demo with a weather tool."""
    print("=== Simple Weather Demo ===\n")

    chat = Chat(tools=[get_weather])
    response = chat("What's the weather in Paris?")

    print(f"User: What's the weather in Paris?")
    print(f"Assistant: {chat.get_text(response)}\n")


def toolloop_demo():
    """Demo using the toolloop for automatic tool execution."""
    print("=== Tool Loop Demo ===\n")

    chat = Chat(tools=[get_weather, calculate])

    user_message = "What's the weather in Tokyo? Also, calculate 15 * 23 for me."
    print(f"User: {user_message}\n")

    for i, response in enumerate(chat.toolloop(user_message)):
        print(f"Step {i + 1}:")

        # Show tool uses
        for block in response.content:
            if block.type == "tool_use":
                print(f"  Tool: {block.name}({block.input})")

        # Show text response
        text = chat.get_text(response)
        if text:
            print(f"  Response: {text}")

        print()


def orders_demo():
    """Demo using order management tools."""
    print("=== Orders Management Demo ===\n")

    chat = Chat(tools=[list_orders, get_order, get_customer])

    user_message = "List all orders and tell me about customer C1"
    print(f"User: {user_message}\n")

    for i, response in enumerate(chat.toolloop(user_message)):
        print(f"Step {i + 1}:")

        # Show tool uses
        for block in response.content:
            if block.type == "tool_use":
                print(f"  Tool: {block.name}({block.input})")

        # Show text response
        text = chat.get_text(response)
        if text:
            print(f"  Response: {text}")

        print()


if __name__ == "__main__":
    print("Chat Tool Demo\n")
    print("This demo requires an ANTHROPIC_API_KEY environment variable.\n")

    try:
        # Run demos
        simple_demo()
        toolloop_demo()
        orders_demo()

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have set your ANTHROPIC_API_KEY environment variable.")
