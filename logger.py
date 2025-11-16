"""
Comprehensive logging utility for Claude API interactions.
Logs all requests, responses, tool calls, and conversation flow.
"""

import logging
import json
from typing import Any, Dict, List
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
import anthropic


class APILogger:
    """Logger for tracing Claude API interactions with organized file structure."""

    def __init__(self, name: str = "ClaudeAPI", level: int = logging.DEBUG, log_dir: str = "logs"):
        """
        Initialize the API logger with organized file structure.

        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, etc.)
            log_dir: Directory to store log files
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Remove existing handlers to avoid duplicates
        if self.logger.handlers:
            self.logger.handlers.clear()

        # Create logs directory structure
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Subdirectories for organized logs
        (self.log_dir / "api").mkdir(exist_ok=True)
        (self.log_dir / "tools").mkdir(exist_ok=True)
        (self.log_dir / "errors").mkdir(exist_ok=True)

        # Console handler with detailed formatting
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # Custom formatter with hierarchy
        console_formatter = logging.Formatter(
            '\n%(asctime)s - %(name)s - %(levelname)s\n%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Detailed file formatter with better hierarchy
        file_formatter = logging.Formatter(
            '\n{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s"}\n%(message)s\n' + '=' * 100,
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Main log file - all logs with rotation (max 10MB per file, keep 5 backups)
        main_log = self.log_dir / "claude_complete.log"
        main_handler = RotatingFileHandler(
            main_log,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_handler.setLevel(level)
        main_handler.setFormatter(file_formatter)
        self.logger.addHandler(main_handler)

        # API-specific log file (requests/responses)
        api_log = self.log_dir / "api" / "api_calls.log"
        self.api_handler = RotatingFileHandler(
            api_log,
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        self.api_handler.setLevel(logging.INFO)
        self.api_handler.setFormatter(file_formatter)

        # Tool execution log file
        tools_log = self.log_dir / "tools" / "tool_executions.log"
        self.tools_handler = RotatingFileHandler(
            tools_log,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        self.tools_handler.setLevel(logging.INFO)
        self.tools_handler.setFormatter(file_formatter)

        # Error log file
        error_log = self.log_dir / "errors" / "errors.log"
        self.error_handler = RotatingFileHandler(
            error_log,
            maxBytes=5*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        self.error_handler.setLevel(logging.ERROR)
        self.error_handler.setFormatter(file_formatter)
        self.logger.addHandler(self.error_handler)

        # Session-specific log file with timestamp
        session_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        session_log = self.log_dir / f"session_{session_timestamp}.log"
        self.session_handler = logging.FileHandler(session_log, mode='w', encoding='utf-8')
        self.session_handler.setLevel(level)
        self.session_handler.setFormatter(file_formatter)
        self.logger.addHandler(self.session_handler)

        self.request_count = 0

        # Log initialization
        self.logger.info(f"{'='*100}")
        self.logger.info(f"API Logger initialized - Session started")
        self.logger.info(f"{'='*100}")
        self.logger.info(f"Log directory: {self.log_dir.absolute()}")
        self.logger.info(f"  - Main log: claude_complete.log")
        self.logger.info(f"  - API calls: api/api_calls.log")
        self.logger.info(f"  - Tool executions: tools/tool_executions.log")
        self.logger.info(f"  - Errors: errors/errors.log")
        self.logger.info(f"  - Session log: session_{session_timestamp}.log")

    def _format_json(self, data: Any) -> str:
        """Format data as pretty JSON."""
        if isinstance(data, (dict, list)):
            return json.dumps(data, indent=2, default=str)
        return str(data)

    def _serialize_message(self, msg: Dict) -> Dict:
        """Serialize a message for logging (handles Anthropic types)."""
        if not isinstance(msg, dict):
            return {"error": "Not a dict", "value": str(msg)}

        serialized = {"role": msg.get("role")}

        content = msg.get("content")
        if isinstance(content, str):
            serialized["content"] = content
        elif isinstance(content, list):
            serialized["content"] = []
            for item in content:
                if hasattr(item, 'type'):
                    # Anthropic content block
                    if item.type == "text":
                        serialized["content"].append({
                            "type": "text",
                            "text": item.text
                        })
                    elif item.type == "tool_use":
                        serialized["content"].append({
                            "type": "tool_use",
                            "id": item.id,
                            "name": item.name,
                            "input": item.input
                        })
                    elif item.type == "tool_result":
                        serialized["content"].append({
                            "type": "tool_result",
                            "tool_use_id": item.tool_use_id if hasattr(item, 'tool_use_id') else "unknown",
                            "content": str(item.content) if hasattr(item, 'content') else str(item)
                        })
                elif isinstance(item, dict):
                    serialized["content"].append(item)
                else:
                    serialized["content"].append(str(item))
        else:
            serialized["content"] = str(content)

        return serialized

    def log_api_request(self, model: str, messages: List[Dict], tools: List[Dict] = None, **kwargs):
        """
        Log an API request to Claude.

        Args:
            model: Model name
            messages: Conversation messages
            tools: Tool schemas
            **kwargs: Additional parameters
        """
        self.request_count += 1

        log_data = {
            "request_number": self.request_count,
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "max_tokens": kwargs.get('max_tokens', 4096),
            "num_messages": len(messages),
            "num_tools": len(tools) if tools else 0
        }

        separator = "=" * 80
        header = f"{separator}\nAPI REQUEST #{self.request_count}\n{separator}"

        # Build hierarchical log message
        log_message = [header]
        log_message.append(f"\n┌─ Request Metadata")
        log_message.append(f"│  {self._format_json(log_data).replace(chr(10), chr(10) + '│  ')}")

        # Log tool schemas (if any)
        if tools:
            log_message.append(f"\n├─ Tools Available ({len(tools)})")
            for tool in tools:
                log_message.append(f"│  ├─ {tool['name']}")
                log_message.append(f"│  │  └─ {tool['description']}")

        # Log full conversation history
        log_message.append(f"\n└─ Conversation Messages ({len(messages)})")
        for i, msg in enumerate(messages, 1):
            serialized = self._serialize_message(msg)
            prefix = "   ├─" if i < len(messages) else "   └─"
            log_message.append(f"{prefix} Message {i}/{len(messages)} [{serialized.get('role', 'unknown')}]")
            formatted_content = self._format_json(serialized)
            indented_content = "   │  " + formatted_content.replace("\n", "\n   │  ")
            if i == len(messages):
                indented_content = "      " + formatted_content.replace("\n", "\n      ")
            log_message.append(indented_content)

        full_log = "\n".join(log_message)

        # Log to main logger (goes to all handlers)
        self.logger.info(full_log)

        # Also log to API-specific handler
        api_logger = logging.getLogger(f"{self.logger.name}.api")
        api_logger.addHandler(self.api_handler)
        api_logger.setLevel(logging.INFO)
        api_logger.propagate = False
        api_logger.info(full_log)

    def log_api_response(self, response: anthropic.types.Message):
        """
        Log an API response from Claude.

        Args:
            response: Claude API response
        """
        separator = "=" * 80
        header = f"\n{separator}\nAPI RESPONSE #{self.request_count}\n{separator}"

        # Response metadata
        response_data = {
            "id": response.id,
            "model": response.model,
            "role": response.role,
            "stop_reason": response.stop_reason,
            "stop_sequence": response.stop_sequence,
            "type": response.type,
        }

        # Usage statistics
        if hasattr(response, 'usage') and response.usage:
            response_data["usage"] = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "cache_creation_input_tokens": getattr(response.usage, 'cache_creation_input_tokens', None),
                "cache_read_input_tokens": getattr(response.usage, 'cache_read_input_tokens', None)
            }

        # Build hierarchical log message
        log_message = [header]
        log_message.append(f"\n┌─ Response Metadata")
        log_message.append(f"│  {self._format_json(response_data).replace(chr(10), chr(10) + '│  ')}")

        # Content blocks
        log_message.append(f"\n└─ Response Content ({len(response.content)} blocks)")
        for i, block in enumerate(response.content, 1):
            prefix = "   ├─" if i < len(response.content) else "   └─"

            if block.type == "text":
                log_message.append(f"{prefix} Block {i}/{len(response.content)} [text]")
                text_lines = block.text.split('\n')
                indent = "   │  " if i < len(response.content) else "      "
                for line in text_lines:
                    log_message.append(f"{indent}{line}")

            elif block.type == "tool_use":
                log_message.append(f"{prefix} Block {i}/{len(response.content)} [tool_use]")
                tool_data = {
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                }
                formatted_tool = self._format_json(tool_data)
                indent = "   │  " if i < len(response.content) else "      "
                indented_tool = indent + formatted_tool.replace("\n", f"\n{indent}")
                log_message.append(indented_tool)

        full_log = "\n".join(log_message)

        # Log to main logger
        self.logger.info(full_log)

        # Also log to API-specific handler
        api_logger = logging.getLogger(f"{self.logger.name}.api")
        if self.api_handler not in api_logger.handlers:
            api_logger.addHandler(self.api_handler)
        api_logger.setLevel(logging.INFO)
        api_logger.propagate = False
        api_logger.info(full_log)

    def log_tool_execution(self, tool_name: str, tool_input: Dict, tool_output: Any, error: str = None):
        """
        Log tool execution details.

        Args:
            tool_name: Name of the tool
            tool_input: Input parameters
            tool_output: Tool result
            error: Error message if execution failed
        """
        separator = "-" * 80
        status = "ERROR" if error else "SUCCESS"
        header = f"\n{separator}\nTOOL EXECUTION: {tool_name} [{status}]\n{separator}"

        execution_data = {
            "tool": tool_name,
            "input": tool_input,
            "timestamp": datetime.now().isoformat(),
            "status": "error" if error else "success"
        }

        # Build hierarchical log message
        log_message = [header]
        log_message.append(f"\n┌─ Execution Details")
        log_message.append(f"│  ├─ Tool: {tool_name}")
        log_message.append(f"│  ├─ Timestamp: {execution_data['timestamp']}")
        log_message.append(f"│  └─ Status: {execution_data['status'].upper()}")

        log_message.append(f"\n├─ Input Parameters")
        formatted_input = self._format_json(tool_input)
        log_message.append(f"│  {formatted_input.replace(chr(10), chr(10) + '│  ')}")

        if error:
            log_message.append(f"\n└─ Error Details")
            log_message.append(f"   {error}")
            full_log = "\n".join(log_message)
            self.logger.error(full_log)
        else:
            log_message.append(f"\n└─ Output")
            formatted_output = str(tool_output)
            log_message.append(f"   {formatted_output.replace(chr(10), chr(10) + '   ')}")
            full_log = "\n".join(log_message)
            self.logger.info(full_log)

        # Also log to tools-specific handler
        tools_logger = logging.getLogger(f"{self.logger.name}.tools")
        if self.tools_handler not in tools_logger.handlers:
            tools_logger.addHandler(self.tools_handler)
        tools_logger.setLevel(logging.INFO)
        tools_logger.propagate = False
        if error:
            tools_logger.error(full_log)
        else:
            tools_logger.info(full_log)

    def log_conversation_state(self, history: List[Dict]):
        """
        Log current conversation state.

        Args:
            history: Conversation history
        """
        separator = "=" * 80
        self.logger.debug(f"\n{separator}")
        self.logger.debug(f"CONVERSATION STATE")
        self.logger.debug(f"{separator}")
        self.logger.debug(f"Total messages in history: {len(history)}")

        for i, msg in enumerate(history, 1):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            if isinstance(content, list):
                content_summary = f"{len(content)} content blocks"
            elif isinstance(content, str):
                content_summary = content[:100] + "..." if len(content) > 100 else content
            else:
                content_summary = str(content)[:100]

            self.logger.debug(f"  {i}. [{role}] {content_summary}")

    def log_summary(self):
        """Log session summary."""
        separator = "=" * 80
        self.logger.info(f"\n{separator}")
        self.logger.info(f"SESSION SUMMARY")
        self.logger.info(f"{separator}")
        self.logger.info(f"Total API requests: {self.request_count}")

    def log_http_request(self, request_id: int, method: str, url: str, headers: dict, body: str = None):
        """
        Log raw HTTP request details.

        Args:
            request_id: Unique request identifier
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            body: Request body (if any)
        """
        separator = "=" * 100
        header = f"\n{separator}\nHTTP REQUEST #{request_id}\n{separator}"

        log_message = [header]
        log_message.append(f"\n┌─ HTTP Request Line")
        log_message.append(f"│  {method} {url}")
        log_message.append(f"│  Timestamp: {datetime.now().isoformat()}")

        # Log request headers
        log_message.append(f"\n├─ Request Headers ({len(headers)} headers)")
        for key, value in headers.items():
            # Mask sensitive headers
            if key.lower() in ['authorization', 'x-api-key', 'cookie']:
                value = f"{'*' * 8}...{value[-4:]}" if len(value) > 4 else "***"
            log_message.append(f"│  {key}: {value}")

        # Log request body
        if body:
            log_message.append(f"\n└─ Request Body ({len(body)} bytes)")
            try:
                # Try to parse and pretty-print JSON
                body_json = json.loads(body)
                formatted_body = json.dumps(body_json, indent=2)
                for line in formatted_body.split('\n'):
                    log_message.append(f"   {line}")
            except json.JSONDecodeError:
                # If not JSON, log as-is (truncate if too long)
                if len(body) > 5000:
                    log_message.append(f"   {body[:5000]}...")
                    log_message.append(f"   ... (truncated, total {len(body)} bytes)")
                else:
                    for line in body.split('\n'):
                        log_message.append(f"   {line}")
        else:
            log_message.append(f"\n└─ Request Body")
            log_message.append(f"   (empty)")

        full_log = "\n".join(log_message)
        self.logger.info(full_log)

        # Also log to API-specific handler
        api_logger = logging.getLogger(f"{self.logger.name}.api")
        if self.api_handler not in api_logger.handlers:
            api_logger.addHandler(self.api_handler)
        api_logger.setLevel(logging.INFO)
        api_logger.propagate = False
        api_logger.info(full_log)

    def log_http_response(self, request_id: int, status_code: int, headers: dict, body: str = None, elapsed_time: float = None):
        """
        Log raw HTTP response details.

        Args:
            request_id: Unique request identifier (matches request)
            status_code: HTTP status code
            headers: Response headers
            body: Response body (if any)
            elapsed_time: Request duration in seconds
        """
        separator = "=" * 100
        header = f"\n{separator}\nHTTP RESPONSE #{request_id}\n{separator}"

        log_message = [header]
        log_message.append(f"\n┌─ HTTP Status Line")
        log_message.append(f"│  Status Code: {status_code}")
        log_message.append(f"│  Timestamp: {datetime.now().isoformat()}")
        if elapsed_time is not None:
            log_message.append(f"│  Elapsed Time: {elapsed_time:.3f}s ({elapsed_time*1000:.0f}ms)")

        # Log response headers
        log_message.append(f"\n├─ Response Headers ({len(headers)} headers)")
        for key, value in headers.items():
            log_message.append(f"│  {key}: {value}")

        # Log response body
        if body:
            log_message.append(f"\n└─ Response Body ({len(body)} bytes)")
            try:
                # Try to parse and pretty-print JSON
                body_json = json.loads(body)
                formatted_body = json.dumps(body_json, indent=2)
                for line in formatted_body.split('\n'):
                    log_message.append(f"   {line}")
            except json.JSONDecodeError:
                # If not JSON, log as-is (truncate if too long)
                if len(body) > 5000:
                    log_message.append(f"   {body[:5000]}...")
                    log_message.append(f"   ... (truncated, total {len(body)} bytes)")
                else:
                    for line in body.split('\n'):
                        log_message.append(f"   {line}")
        else:
            log_message.append(f"\n└─ Response Body")
            log_message.append(f"   (empty)")

        full_log = "\n".join(log_message)
        self.logger.info(full_log)

        # Also log to API-specific handler
        api_logger = logging.getLogger(f"{self.logger.name}.api")
        if self.api_handler not in api_logger.handlers:
            api_logger.addHandler(self.api_handler)
        api_logger.setLevel(logging.INFO)
        api_logger.propagate = False
        api_logger.info(full_log)

    def log_http_error(self, request_id: int, error: str, elapsed_time: float = None):
        """
        Log HTTP request error.

        Args:
            request_id: Unique request identifier
            error: Error message
            elapsed_time: Time elapsed before error
        """
        separator = "=" * 100
        header = f"\n{separator}\nHTTP ERROR #{request_id}\n{separator}"

        log_message = [header]
        log_message.append(f"\n┌─ Error Details")
        log_message.append(f"│  Timestamp: {datetime.now().isoformat()}")
        if elapsed_time is not None:
            log_message.append(f"│  Elapsed Time: {elapsed_time:.3f}s")
        log_message.append(f"\n└─ Error Message")
        log_message.append(f"   {error}")

        full_log = "\n".join(log_message)
        self.logger.error(full_log)
