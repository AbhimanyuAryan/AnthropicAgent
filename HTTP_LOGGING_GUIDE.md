# HTTP Request/Response Cycle Logging Guide

This guide explains the complete HTTP-level logging system for Claude API interactions, showing you how to observe the **entire request/response cycle** with all network-level details.

## Overview

The HTTP logging system captures **raw network-level details** of every API interaction:

| Level | What It Logs | Details |
|-------|-------------|---------|
| **HTTP Request** | Raw network request | Method, URL, headers, body, timestamp |
| **API Request** | Logical message structure | Model, messages, tools, parameters |
| **API Response** | Logical response structure | Content blocks, metadata, tokens |
| **HTTP Response** | Raw network response | Status code, headers, body, timing |

### Complete Request/Response Cycle

Each API call generates **four log entries** showing the complete cycle:

```
1. HTTP REQUEST #1     ← Raw outgoing HTTP request
2. API REQUEST #1      ← Logical message sent
3. API RESPONSE #1     ← Logical response received
4. HTTP RESPONSE #1    ← Raw incoming HTTP response
```

## Quick Start

### Enable HTTP Logging (Default)

```python
from chat import Chat

# HTTP logging is enabled by default
chat = Chat(
    model="claude-3-5-sonnet-20241022",
    enable_logging=True,        # Enable API logging
    enable_http_logging=True    # Enable HTTP logging (default)
)

response = chat("Hello, Claude!")
```

### Disable HTTP Logging

```python
# Only log logical API requests/responses (no HTTP details)
chat = Chat(
    model="claude-3-5-sonnet-20241022",
    enable_logging=True,
    enable_http_logging=False   # Skip HTTP details
)
```

### Disable All Logging

```python
# No logging at all
chat = Chat(
    model="claude-3-5-sonnet-20241022",
    enable_logging=False
)
```

## HTTP Request Logging

### What's Logged

The **HTTP Request** log captures the raw network request as it's sent to the API:

```
====================================================================================================
HTTP REQUEST #1
====================================================================================================

┌─ HTTP Request Line
│  POST https://api.anthropic.com/v1/messages
│  Timestamp: 2025-11-16T10:30:45.123456

├─ Request Headers (12 headers)
│  host: api.anthropic.com
│  user-agent: anthropic-python/0.40.0
│  accept: application/json
│  accept-encoding: gzip, deflate
│  connection: keep-alive
│  content-type: application/json
│  content-length: 1234
│  x-api-key: ********...xyz  ← Sensitive headers masked
│  anthropic-version: 2023-06-01
│  ...

└─ Request Body (1234 bytes)
   {
     "model": "claude-3-5-sonnet-20241022",
     "max_tokens": 1024,
     "messages": [
       {
         "role": "user",
         "content": "Hello, Claude!"
       }
     ]
   }
```

### Key Features

- **Header Masking**: Sensitive headers (`authorization`, `x-api-key`, `cookie`) are automatically masked
- **JSON Pretty-Printing**: Request body is formatted for readability
- **Timestamp**: Exact time the request was sent
- **Content Length**: Size of the request body

## HTTP Response Logging

### What's Logged

The **HTTP Response** log captures the raw network response as it's received:

```
====================================================================================================
HTTP RESPONSE #1
====================================================================================================

┌─ HTTP Status Line
│  Status Code: 200
│  Timestamp: 2025-11-16T10:30:46.789012
│  Elapsed Time: 1.666s (1666ms)  ← Request latency

├─ Response Headers (15 headers)
│  content-type: application/json
│  date: Sat, 16 Nov 2025 10:30:46 GMT
│  x-request-id: req_abc123xyz
│  anthropic-ratelimit-requests-limit: 1000
│  anthropic-ratelimit-requests-remaining: 999
│  anthropic-ratelimit-requests-reset: 2025-11-16T11:00:00Z
│  anthropic-ratelimit-tokens-limit: 100000
│  anthropic-ratelimit-tokens-remaining: 98765
│  anthropic-ratelimit-tokens-reset: 2025-11-16T11:00:00Z
│  cache-control: no-cache
│  ...

└─ Response Body (2345 bytes)
   {
     "id": "msg_abc123xyz",
     "type": "message",
     "role": "assistant",
     "model": "claude-3-5-sonnet-20241022",
     "content": [
       {
         "type": "text",
         "text": "Hello! How can I help you today?"
       }
     ],
     "stop_reason": "end_turn",
     "stop_sequence": null,
     "usage": {
       "input_tokens": 10,
       "output_tokens": 12
     }
   }
```

### Key Features

- **Status Code**: HTTP status (200, 400, 429, 500, etc.)
- **Timing**: Exact elapsed time in seconds and milliseconds
- **Rate Limit Headers**: See your current rate limits and remaining quota
- **Caching Headers**: Observe cache behavior
- **JSON Pretty-Printing**: Response body formatted for readability

## Complete Cycle Example

Here's what you see for a single API call with HTTP logging enabled:

```
# 1. HTTP REQUEST - Raw outgoing request
====================================================================================================
HTTP REQUEST #1
====================================================================================================
POST https://api.anthropic.com/v1/messages
Headers: {...}
Body: {"model": "...", "messages": [...]}

# 2. API REQUEST - Logical message structure
================================================================================
API REQUEST #1
================================================================================
┌─ Request Metadata
│  {"request_number": 1, "model": "...", "num_messages": 1, ...}
└─ Conversation Messages (1)
   └─ Message 1/1 [user]
      {"role": "user", "content": "Hello!"}

# 3. API RESPONSE - Logical response structure
================================================================================
API RESPONSE #1
================================================================================
┌─ Response Metadata
│  {"id": "msg_...", "stop_reason": "end_turn", ...}
└─ Response Content (1 blocks)
   └─ Block 1/1 [text]
      Hello! How can I help you today?

# 4. HTTP RESPONSE - Raw incoming response
====================================================================================================
HTTP RESPONSE #1
====================================================================================================
Status Code: 200
Elapsed Time: 1.666s (1666ms)
Headers: {...}
Body: {"id": "msg_...", "content": [...], "usage": {...}}
```

## Use Cases

### 1. Debugging API Issues

See exactly what's being sent and received:
- Is the request body formatted correctly?
- What's the exact error response?
- Are headers set correctly?

### 2. Monitoring Rate Limits

Track your API usage from response headers:
```
anthropic-ratelimit-requests-remaining: 999
anthropic-ratelimit-tokens-remaining: 98765
```

### 3. Analyzing Performance

Monitor API latency:
```
Elapsed Time: 1.666s (1666ms)
```

### 4. Understanding Caching

Observe prompt caching behavior:
```json
"usage": {
  "input_tokens": 100,
  "cache_creation_input_tokens": 50,
  "cache_read_input_tokens": 200
}
```

### 5. Security Auditing

Verify sensitive data is masked:
```
x-api-key: ********...xyz
```

## Tool Loop Logging

When using tools, the HTTP logging captures **every request/response cycle** in the loop:

```python
chat = Chat(tools=[get_weather, calculate], enable_http_logging=True)

for response in chat.toolloop("What's the weather in SF?"):
    # Each iteration logs:
    # - HTTP Request
    # - API Request
    # - API Response
    # - HTTP Response
    # - Tool Execution (if tools are called)
    pass
```

### Example Tool Loop Cycle

```
Iteration 1:
  HTTP REQUEST #1 → API REQUEST #1 → API RESPONSE #1 → HTTP RESPONSE #1
  Tool Execution: get_weather(location="San Francisco")

Iteration 2:
  HTTP REQUEST #2 → API REQUEST #2 → API RESPONSE #2 → HTTP RESPONSE #2
  Final response with weather info
```

## Log File Organization

HTTP logs are written to multiple locations:

```
logs/
├── claude_complete.log              # All logs (HTTP + API + tools)
├── api/
│   └── api_calls.log               # API + HTTP logs only
├── tools/
│   └── tool_executions.log         # Tool execution logs
├── errors/
│   └── errors.log                  # Error logs
└── session_20251116_103045.log     # This session's logs
```

### Log Rotation

- Each log file has a maximum size (5-10MB)
- Old logs are automatically rotated (keeps 5 backups)
- No manual cleanup needed

## Advanced Configuration

### Custom HTTP Client

If you need more control over the HTTP client:

```python
from http_logger import create_logging_client
from logger import APILogger
import anthropic

# Create logger
logger = APILogger()

# Create custom HTTP client with logging
http_client = create_logging_client(
    logger=logger,
    timeout=30.0,  # Custom timeout
    # ... other httpx.Client parameters
)

# Create Anthropic client with custom HTTP client
client = anthropic.Anthropic(http_client=http_client)
```

### Filtering Logs

You can configure Python's logging to filter specific log types:

```python
import logging

# Only show ERROR and above
logging.getLogger("ClaudeAPI").setLevel(logging.ERROR)

# Show all logs
logging.getLogger("ClaudeAPI").setLevel(logging.DEBUG)
```

## Performance Considerations

### Overhead

HTTP logging adds minimal overhead:
- **Latency**: < 1ms per request (negligible)
- **Memory**: ~10KB per request/response pair
- **Disk**: Logs are rotated automatically

### When to Disable

Consider disabling HTTP logging when:
- Running in production with high throughput
- You only need logical API structure
- Disk space is constrained
- You're making thousands of requests

```python
# Production: Disable HTTP logging
chat = Chat(
    enable_logging=True,         # Keep API logging
    enable_http_logging=False    # Disable HTTP details
)
```

## Troubleshooting

### Issue: Logs Not Appearing

**Solution**: Check that logging is enabled:
```python
chat = Chat(enable_logging=True, enable_http_logging=True)
```

### Issue: API Key Visible in Logs

**Solution**: API keys are automatically masked. If you see an unmasked key, please report this as a security issue.

### Issue: Log Files Too Large

**Solution**: Log rotation is automatic. If files grow too large, reduce `maxBytes` in `logger.py`:
```python
# In logger.py
RotatingFileHandler(
    api_log,
    maxBytes=5*1024*1024,  # Reduce from 10MB to 5MB
    backupCount=3          # Keep fewer backups
)
```

### Issue: HTTP Logging Not Working

**Solution**: Make sure you're using the Chat class, not the raw Anthropic client:
```python
# ✅ Correct - HTTP logging works
from chat import Chat
chat = Chat(enable_http_logging=True)

# ❌ Wrong - HTTP logging doesn't work
import anthropic
client = anthropic.Anthropic()
```

## Example Output

Run the demo to see complete HTTP logging:

```bash
python demo_http_logging.py
```

This will generate logs showing:
1. Simple request/response cycle
2. Tool loop with multiple cycles
3. Comparison of different logging modes

Check the log files for complete details!

## Summary

The HTTP logging system provides **complete visibility** into Claude API interactions at the network level:

| Feature | Benefit |
|---------|---------|
| **Raw HTTP Details** | See exactly what's sent/received |
| **Request/Response Timing** | Monitor API latency |
| **Header Inspection** | Track rate limits, caching |
| **Security** | Sensitive headers automatically masked |
| **Performance** | Minimal overhead, automatic rotation |
| **Organization** | Separate logs for different purposes |

Enable HTTP logging to get the **full picture** of your Claude API interactions!
