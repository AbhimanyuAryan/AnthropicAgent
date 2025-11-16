"""
Demo showing the Chat class with tools and comprehensive logging.

This demo demonstrates:
1. Simple tool usage
2. Multiple tool calls in a loop
3. Complete request-response cycle logging with HTTP details and tool executions
4. Order management system
"""

from chat import Chat
from tools import get_weather, get_order, get_customer, list_orders, calculate


def simple_demo():
    """Simple demo with a weather tool."""
    print("=" * 80)
    print("SIMPLE WEATHER DEMO")
    print("=" * 80)
    print()

    chat = Chat(tools=[get_weather])
    response = chat("What's the weather in Paris?")

    print(f"User: What's the weather in Paris?")
    print(f"Assistant: {chat.get_text(response)}\n")


def toolloop_demo():
    """Demo using the toolloop for automatic tool execution."""
    print("=" * 80)
    print("TOOL LOOP DEMO")
    print("=" * 80)
    print()

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
    print("=" * 80)
    print("ORDERS MANAGEMENT DEMO")
    print("=" * 80)
    print()

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


def logging_info():
    """Print information about the logging system."""
    print("\n" + "=" * 80)
    print("ABOUT THE LOGGING SYSTEM")
    print("=" * 80)
    print("\nThis demo includes comprehensive logging of all API interactions.")
    print("\nLogs Directory Structure:")
    print("  logs/")
    print("    - claude_complete.log          (All logs with detailed view)")
    print("    - session_YYYYMMDD_HHMMSS.log  (Current session only)")
    print("    - cycles/")
    print("        - complete_cycles.log      (Complete request-response cycles)")
    print("    - tools/")
    print("        - tool_executions.log      (Tool calls & results)")
    print("    - errors/")
    print("        - errors.log               (Errors only)")
    print("\nEach cycle includes:")
    print("  - HTTP Request (method, URL, headers, body)")
    print("  - API Request (model, messages, tools)")
    print("  - HTTP Response (status, duration, body)")
    print("  - API Response (content blocks, token usage)")
    print("  - Tools Executed (inputs, outputs, errors)")
    print("  - Total cycle duration")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print("CHAT TOOL DEMO WITH COMPREHENSIVE LOGGING")
    print("=" * 80)
    print("\nThis demo requires an ANTHROPIC_API_KEY environment variable.\n")

    try:
        # Print logging info first
        logging_info()

        # Run demos
        simple_demo()
        toolloop_demo()
        orders_demo()

        print("\n" + "=" * 80)
        print("DEMO COMPLETE")
        print("=" * 80)
        print("\nCheck the 'logs/' directory for detailed logs:")
        print("  - logs/claude_complete.log (everything, detailed)")
        print("  - logs/cycles/complete_cycles.log (complete request-response cycles)")
        print("  - logs/tools/tool_executions.log (tool executions)")
        print("=" * 80)
        print()

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have set your ANTHROPIC_API_KEY environment variable.")
        print("You can set it in a .env file:")
        print("  ANTHROPIC_API_KEY=your-api-key-here")
