"""
Demo showing comprehensive API logging.
This demonstrates how every request, response, and tool call is logged.
"""

from chat import Chat
from tools import get_weather, calculate

def main():
    print("=" * 80)
    print("COMPREHENSIVE API LOGGING DEMO")
    print("=" * 80)
    print("\nThis demo will show you:")
    print("  1. Every API request sent to Claude (messages, tools, parameters)")
    print("  2. Every API response from Claude (content blocks, tool calls, usage)")
    print("  3. Every tool execution (inputs, outputs, errors)")
    print("  4. Full conversation flow")
    print("\nLogs Directory Structure:")
    print("  logs/")
    print("  ├── claude_complete.log          (All logs combined)")
    print("  ├── session_YYYYMMDD_HHMMSS.log  (Current session only)")
    print("  ├── api/")
    print("  │   └── api_calls.log            (API requests & responses)")
    print("  ├── tools/")
    print("  │   └── tool_executions.log      (Tool calls & results)")
    print("  └── errors/")
    print("      └── errors.log               (Errors only)")
    print("\n" + "=" * 80 + "\n")

    # Create chat with logging enabled (default)
    chat = Chat(tools=[get_weather, calculate])

    # Example 1: Simple tool use
    print("\n### Example 1: Simple tool use ###\n")
    user_msg = "What's the weather in Tokyo?"
    print(f"User: {user_msg}\n")

    for i, response in enumerate(chat.toolloop(user_msg)):
        text = chat.get_text(response)
        if text:
            print(f"Assistant: {text}\n")

    # Example 2: Multiple tool calls
    print("\n### Example 2: Multiple tool calls ###\n")
    user_msg = "Calculate 25 * 17, then tell me the weather in Paris"
    print(f"User: {user_msg}\n")

    for i, response in enumerate(chat.toolloop(user_msg)):
        text = chat.get_text(response)
        if text:
            print(f"Assistant: {text}\n")

    # Print summary
    if chat.logger:
        chat.logger.log_summary()

    print("\n" + "=" * 80)
    print("Demo complete! Check the 'logs/' directory for detailed logs:")
    print("  - logs/claude_complete.log (everything)")
    print("  - logs/api/api_calls.log (API interactions)")
    print("  - logs/tools/tool_executions.log (tool calls)")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have set your ANTHROPIC_API_KEY environment variable.")
