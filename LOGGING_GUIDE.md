# Comprehensive API Logging Guide

This guide explains the logging system for tracing Claude API interactions.

## Overview

The logging system captures **every aspect** of your Claude API flow:

1. **API Requests** - What's sent to Claude
2. **API Responses** - What Claude returns
3. **Tool Executions** - Function calls and results
4. **Conversation State** - Full message history

## Quick Start

### Enable Logging (Default)

```python
from chat import Chat
from tools import get_weather

# Logging is enabled by default
chat = Chat(tools=[get_weather])

# All API calls will be logged
response = chat("What's the weather in Paris?")
```

### Disable Logging

```python
# If you don't want logging
chat = Chat(tools=[get_weather], enable_logging=False)
```

## What Gets Logged

### 1. API Requests

Every request to Claude includes:

```
API REQUEST #1
================================================================================
Request Metadata:
{
  "request_number": 1,
  "timestamp": "2025-11-16T10:30:45.123456",
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 4096,
  "num_messages": 1,
  "num_tools": 2
}

Tools Available (2):
  - get_weather: Get the weather for a city
  - calculate: Evaluate a mathematical expression

Conversation Messages (1):
  Message 1/1:
  {
    "role": "user",
    "content": "What's the weather in Paris?"
  }
```

### 2. API Responses

Every response from Claude includes:

```
API RESPONSE #1
================================================================================
Response Metadata:
{
  "id": "msg_01ABC123",
  "model": "claude-sonnet-4-5-20250929",
  "role": "assistant",
  "stop_reason": "tool_use",
  "stop_sequence": null,
  "type": "message",
  "usage": {
    "input_tokens": 450,
    "output_tokens": 85,
    "cache_creation_input_tokens": null,
    "cache_read_input_tokens": null
  }
}

Response Content (2 blocks):
  Block 1/2:
    Type: text
    Text: I'll check the weather in Paris for you.

  Block 2/2:
  {
    "type": "tool_use",
    "id": "toolu_01XYZ789",
    "name": "get_weather",
    "input": {
      "city": "Paris"
    }
  }
```

### 3. Tool Executions

Every tool call includes:

```
--------------------------------------------------------------------------------
TOOL EXECUTION: get_weather
--------------------------------------------------------------------------------
Execution Data:
{
  "tool": "get_weather",
  "input": {
    "city": "Paris"
  },
  "timestamp": "2025-11-16T10:30:45.789012",
  "status": "success",
  "output": "It's sunny in Paris!"
}
```

## Output Locations

### Console Output
All logs are printed to the console with timestamps and clear formatting.

### Log File
All logs are also saved to: **`claude_api_flow.log`**

The file persists across sessions and includes the complete history of all API interactions.

## Understanding the Flow

Here's what happens in a typical conversation:

```
1. API REQUEST #1
   ↓ User message sent
2. API RESPONSE #1
   ↓ Claude wants to use a tool
3. TOOL EXECUTION: get_weather
   ↓ Your Python function runs
4. API REQUEST #2
   ↓ Tool result sent back to Claude
5. API RESPONSE #2
   ↓ Claude responds with final answer
```

## Log Levels

The logger uses Python's standard logging levels:

- **INFO** - API requests, responses, tool executions
- **DEBUG** - Conversation state details
- **ERROR** - Tool execution failures

## Running the Demo

```bash
# Run the logging demo
python demo_logging.py
```

This will:
1. Make several API calls with tool usage
2. Show all logs in the console
3. Save complete logs to `claude_api_flow.log`

## Key Features

### Token Usage Tracking

See exactly how many tokens each request uses:
```json
"usage": {
  "input_tokens": 450,
  "output_tokens": 85
}
```

### Tool Call Details

See the exact parameters Claude passes to your tools:
```json
{
  "name": "calculate",
  "input": {
    "expression": "25 * 17"
  }
}
```

### Error Tracking

When tool execution fails, you see:
```json
{
  "status": "error",
  "error": "division by zero"
}
```

### Complete Message History

Every message in the conversation is logged with full content, including:
- User messages
- Assistant text responses
- Tool use blocks
- Tool result blocks

## Customization

### Change Log Level

```python
from logger import APILogger
import logging

# Create logger with different level
logger = APILogger(level=logging.INFO)  # Less verbose
```

### Programmatic Access

```python
chat = Chat(tools=[get_weather])

# Access the logger
if chat.logger:
    chat.logger.log_summary()
```

## Best Practices

1. **Development**: Keep logging enabled to debug tool behavior
2. **Production**: Disable logging for performance and privacy
3. **Debugging**: Check `claude_api_flow.log` for full request/response history
4. **Token Monitoring**: Watch usage stats to optimize costs

## Example Output

See `demo_logging.py` for a complete working example that demonstrates:
- Simple tool calls
- Multiple tool executions
- Complete request/response cycles
- Token usage tracking

## Troubleshooting

### Logs not appearing?

Check that logging is enabled:
```python
chat = Chat(tools=[...], enable_logging=True)
```

### Log file too large?

Clear the log file:
```bash
# Windows
del claude_api_flow.log

# Unix/Mac
rm claude_api_flow.log
```

### Want more detail?

The logger captures everything. Check the log file for complete JSON-formatted data.
