"""
Simple test to verify logging directory structure and formatting.
"""

from logger import APILogger
import json

def test_logging_structure():
    print("Testing logging structure...")

    # Create logger
    logger = APILogger(name="TestLogger", log_dir="logs")

    print("\n" + "="*80)
    print("Logger initialized successfully!")
    print("="*80)

    # Test API request logging
    logger.log_api_request(
        model="claude-3-5-sonnet-20241022",
        messages=[
            {"role": "user", "content": "What's the weather like?"}
        ],
        tools=[
            {
                "name": "get_weather",
                "description": "Get weather information for a location"
            }
        ],
        max_tokens=1024
    )

    # Test tool execution logging (success)
    logger.log_tool_execution(
        tool_name="get_weather",
        tool_input={"location": "Tokyo"},
        tool_output={"temperature": 22, "condition": "Sunny"}
    )

    # Test tool execution logging (error)
    logger.log_tool_execution(
        tool_name="calculate",
        tool_input={"operation": "divide", "a": 10, "b": 0},
        tool_output=None,
        error="Division by zero error"
    )

    # Log summary
    logger.log_summary()

    print("\n" + "="*80)
    print("Log files created in the 'logs/' directory:")
    print("  - logs/claude_complete.log")
    print("  - logs/api/api_calls.log")
    print("  - logs/tools/tool_executions.log")
    print("  - logs/errors/errors.log")
    print("  - logs/session_*.log")
    print("="*80)
    print("\nCheck the log files to see the hierarchical structure!")

if __name__ == "__main__":
    test_logging_structure()
