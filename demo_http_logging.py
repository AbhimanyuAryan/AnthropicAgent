"""
Demo: Complete HTTP Request/Response Cycle Logging

This demo showcases the full HTTP-level logging capabilities including:
- Raw HTTP request details (method, URL, headers, body)
- Raw HTTP response details (status code, headers, body, timing)
- Complete request/response cycle with formatting
- Multiple request handling (tool loop)

The logs show the complete picture:
1. HTTP Request (raw network-level details)
2. API Request (logical message structure)
3. API Response (logical response structure)
4. HTTP Response (raw network-level details)
"""

from chat import Chat
from tools import get_weather, calculate


def simple_http_cycle_demo():
    """
    Demo: Simple request/response showing complete HTTP cycle.
    """
    print("\n" + "=" * 100)
    print("DEMO 1: Simple HTTP Request/Response Cycle")
    print("=" * 100)
    print("\nThis demo shows:")
    print("  1. HTTP Request  - Raw network request (method, URL, headers, body)")
    print("  2. API Request   - Logical message structure")
    print("  3. API Response  - Logical response structure")
    print("  4. HTTP Response - Raw network response (status, headers, body, timing)")
    print("\nCheck the logs for complete details!\n")

    # Create chat with HTTP logging enabled (default)
    chat = Chat(model="claude-3-5-sonnet-20240620", enable_logging=True, enable_http_logging=True)

    # Simple request
    response = chat("What is the capital of France? Give me a very brief answer.")

    # Extract text
    text = chat.get_text(response)
    print(f"\nClaude's response: {text}")


def tool_loop_http_cycle_demo():
    """
    Demo: Tool loop showing multiple HTTP request/response cycles.
    """
    print("\n" + "=" * 100)
    print("DEMO 2: Tool Loop with Multiple HTTP Cycles")
    print("=" * 100)
    print("\nThis demo shows:")
    print("  - Multiple HTTP request/response cycles")
    print("  - Tool execution between cycles")
    print("  - Complete round-trip for each interaction")
    print("\nCheck the logs for complete details!\n")

    # Create chat with tools and HTTP logging
    chat = Chat(
        model="claude-3-5-sonnet-20240620",
        tools=[get_weather, calculate],
        enable_logging=True,
        enable_http_logging=True
    )

    # Run tool loop - this will generate multiple HTTP cycles
    print("\nRunning tool loop...")
    for i, response in enumerate(chat.toolloop("What's the weather in San Francisco? Then calculate 15 * 24."), 1):
        print(f"\n--- Response {i} ---")
        text = chat.get_text(response)
        if text:
            print(f"Claude: {text}")

        # Check for tool calls
        tool_calls = [block for block in response.content if block.type == "tool_use"]
        if tool_calls:
            for tool_call in tool_calls:
                print(f"Tool call: {tool_call.name}({tool_call.input})")


def compare_logging_modes():
    """
    Demo: Compare with and without HTTP logging.
    """
    print("\n" + "=" * 100)
    print("DEMO 3: Comparing Logging Modes")
    print("=" * 100)

    print("\n--- Mode 1: HTTP Logging ENABLED (default) ---")
    print("Logs show: HTTP Request → API Request → API Response → HTTP Response")
    chat_with_http = Chat(
        model="claude-3-5-sonnet-20240620",
        enable_logging=True,
        enable_http_logging=True  # Full HTTP details
    )
    response1 = chat_with_http("Say 'HTTP logging enabled' briefly")
    print(f"Response: {chat_with_http.get_text(response1)}")

    print("\n--- Mode 2: HTTP Logging DISABLED ---")
    print("Logs show: API Request → API Response (no HTTP details)")
    chat_without_http = Chat(
        model="claude-3-5-sonnet-20240620",
        enable_logging=True,
        enable_http_logging=False  # No HTTP details
    )
    response2 = chat_without_http("Say 'HTTP logging disabled' briefly")
    print(f"Response: {chat_without_http.get_text(response2)}")

    print("\n--- Mode 3: All Logging DISABLED ---")
    print("Logs show: (nothing)")
    chat_no_logging = Chat(
        model="claude-3-5-sonnet-20240620",
        enable_logging=False  # No logging at all
    )
    response3 = chat_no_logging("Say 'No logging' briefly")
    print(f"Response: {chat_no_logging.get_text(response3)}")


def main():
    """Run all HTTP logging demos."""
    print("\n" + "#" * 100)
    print("# HTTP REQUEST/RESPONSE CYCLE LOGGING DEMO")
    print("#" * 100)
    print("\nThis demo showcases complete HTTP-level logging of Claude API interactions.")
    print("\nKey features:")
    print("  • Raw HTTP request details (method, URL, headers, body)")
    print("  • Raw HTTP response details (status code, headers, body)")
    print("  • Request/response timing (latency)")
    print("  • Complete cycle formatting")
    print("  • Header masking for sensitive data")
    print("  • JSON pretty-printing")
    print("\nLogs are written to:")
    print("  - Console (stdout)")
    print("  - logs/claude_complete.log (all logs)")
    print("  - logs/api/api_calls.log (API-specific)")
    print("  - logs/session_YYYYMMDD_HHMMSS.log (this session)")
    print("\n" + "=" * 100)

    # Run demos
    simple_http_cycle_demo()

    input("\nPress Enter to continue to Demo 2...")
    tool_loop_http_cycle_demo()

    input("\nPress Enter to continue to Demo 3...")
    compare_logging_modes()

    print("\n" + "=" * 100)
    print("DEMO COMPLETE!")
    print("=" * 100)
    print("\nCheck the log files for complete HTTP request/response details:")
    print("  - logs/claude_complete.log")
    print("  - logs/api/api_calls.log")
    print("  - logs/session_YYYYMMDD_HHMMSS.log")
    print("\nEach request shows:")
    print("  1. HTTP Request  → Raw network request with headers and body")
    print("  2. API Request   → Logical message structure")
    print("  3. API Response  → Logical response content")
    print("  4. HTTP Response → Raw network response with status, headers, timing")


if __name__ == "__main__":
    main()
