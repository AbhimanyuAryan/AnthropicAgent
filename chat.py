"""
Chat implementation with tool support for building agents from scratch.
Enables Claude to automatically execute tools in a conversation loop.
"""

import anthropic
import json
import inspect
from typing import Callable, List, Optional, Any, Dict
from dotenv import load_dotenv
from logger import APILogger
from http_logger import create_logging_client

# Load environment variables from .env file
load_dotenv()


def generate_tool_schema(func: Callable) -> Dict:
    """
    Generate JSON schema for a tool from its type hints and docstring.

    Args:
        func: Function to convert to tool schema

    Returns:
        Tool schema dictionary for Claude API
    """
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or ""

    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue

        param_type = param.annotation
        properties[param_name] = {
            "type": "string"  # Default to string, can be enhanced
        }

        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    return {
        "name": func.__name__,
        "description": doc.split('\n')[0] if doc else f"Execute {func.__name__}",
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required
        }
    }


def mk_toolres(tool_call_id: str, content: Any) -> Dict:
    """Create a tool result message for Claude."""
    return {
        "type": "tool_result",
        "tool_use_id": tool_call_id,
        "content": str(content)
    }


class Chat:
    """
    Chat class that maintains conversation history and supports tool execution.
    """

    def __init__(self, model: str = "claude-sonnet-4-5-20250929", tools: Optional[List[Callable]] = None, enable_logging: bool = True, enable_http_logging: bool = True):
        """
        Initialize Chat instance.

        Args:
            model: Claude model to use
            tools: List of tool functions to make available
            enable_logging: Enable comprehensive API logging
            enable_http_logging: Enable HTTP-level request/response logging
        """
        self.logger = APILogger() if enable_logging else None

        # Create Anthropic client with optional HTTP logging
        if enable_logging and enable_http_logging:
            # Create custom HTTP client with logging
            http_client = create_logging_client(logger=self.logger)
            self.c = anthropic.Anthropic(http_client=http_client)
        else:
            self.c = anthropic.Anthropic()

        self.model = model
        self.h = []  # Conversation history
        self.tools = {}
        self.tool_schemas = []

        if tools:
            for tool in tools:
                self.register_tool(tool)

    def register_tool(self, func: Callable):
        """Register a tool function."""
        schema = generate_tool_schema(func)
        self.tools[func.__name__] = func
        self.tool_schemas.append(schema)

    def __call__(self, user_message: str, **kwargs) -> anthropic.types.Message:
        """
        Send a message and get a response.

        Args:
            user_message: User's message
            **kwargs: Additional arguments to pass to the API

        Returns:
            Claude's response message
        """
        self.h.append({"role": "user", "content": user_message})

        # Log the API request
        if self.logger:
            self.logger.log_api_request(
                model=self.model,
                messages=self.h,
                tools=self.tool_schemas if self.tool_schemas else None,
                **kwargs
            )

        response = self.c.messages.create(
            model=self.model,
            max_tokens=kwargs.get('max_tokens', 4096),
            messages=self.h,
            tools=self.tool_schemas if self.tool_schemas else anthropic.NOT_GIVEN
        )

        # Log the API response
        if self.logger:
            self.logger.log_api_response(response)

        self.h.append({
            "role": "assistant",
            "content": response.content
        })

        return response

    def toolloop(self, user_message: str, max_steps: int = 10, cont_func: Optional[Callable] = None):
        """
        Execute a tool loop: send message, execute tools, continue until done.

        Args:
            user_message: Initial user message
            max_steps: Maximum number of tool execution rounds
            cont_func: Optional function to determine if loop should continue

        Yields:
            Claude responses at each step
        """
        response = self(user_message)
        yield response

        for step in range(max_steps):
            # Check if we should continue
            if cont_func and not cont_func(response):
                break

            # Check if there are tool calls to execute
            tool_calls = [block for block in response.content if block.type == "tool_use"]
            if not tool_calls:
                break

            # Execute all tool calls
            tool_results = []
            for tool_call in tool_calls:
                tool_name = tool_call.name
                tool_input = tool_call.input

                if tool_name in self.tools:
                    try:
                        result = self.tools[tool_name](**tool_input)
                        tool_results.append(mk_toolres(tool_call.id, result))

                        # Log successful tool execution
                        if self.logger:
                            self.logger.log_tool_execution(tool_name, tool_input, result)
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        tool_results.append(mk_toolres(tool_call.id, error_msg))

                        # Log failed tool execution
                        if self.logger:
                            self.logger.log_tool_execution(tool_name, tool_input, None, error=str(e))
                else:
                    error_msg = f"Error: Unknown tool {tool_name}"
                    tool_results.append(mk_toolres(tool_call.id, error_msg))

                    # Log unknown tool
                    if self.logger:
                        self.logger.log_tool_execution(tool_name, tool_input, None, error=f"Unknown tool")

            # Add tool results to history
            self.h.append({
                "role": "user",
                "content": tool_results
            })

            # Log the next API request
            if self.logger:
                self.logger.log_api_request(
                    model=self.model,
                    messages=self.h,
                    tools=self.tool_schemas if self.tool_schemas else None,
                    max_tokens=4096
                )

            # Get next response
            response = self.c.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=self.h,
                tools=self.tool_schemas if self.tool_schemas else anthropic.NOT_GIVEN
            )

            # Log the API response
            if self.logger:
                self.logger.log_api_response(response)

            self.h.append({
                "role": "assistant",
                "content": response.content
            })

            yield response

    def get_text(self, response: anthropic.types.Message) -> str:
        """Extract text content from a response."""
        text_blocks = [block.text for block in response.content if hasattr(block, 'text')]
        return '\n'.join(text_blocks)
