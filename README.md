# 🤖 AI Agent Framework Built on Claude API

A custom **AI agent framework** implementation using Anthropic's Claude API. This enables Claude to automatically execute tools (functions) in a conversation loop, creating truly autonomous agents.

---

## 📋 Table of Contents

- [What Are Tools?](#-what-are-tools)
- [Architecture Overview](#-architecture-overview)
- [Understanding `toolloop`](#-understanding-toolloop)
- [How Tools Are Called](#-how-tools-are-called)
- [Complete Flow Example](#-complete-flow-example)
- [Setup & Usage](#-setup--usage)
- [Project Structure](#-project-structure)

---

## 🔧 What Are Tools?

**Tools are Python functions** that Claude can call to perform actions. For example:

```python
def get_order(order_id: str):
    """Get order details by order ID"""
    return orders.get(order_id, "Order not found")
```

This function becomes a "tool" that Claude can invoke during conversations.

---

## 🏗️ Architecture Overview

### Main Components

#### 1. `Chat` Class (`chat.py:64-185`)
- Manages conversations with Claude
- Maintains conversation history (`self.h`)
- Registers and executes tools (functions that Claude can call)
- Handles the back-and-forth between user, Claude, and tool execution

#### 2. `orders.py`
- Sample data for demos (customers and orders)
- Used to demonstrate tool capabilities

---

## 🔄 Understanding `toolloop`

**`toolloop` (`chat.py:120-179`)** is the core method that implements an **agentic loop**:

```
User sends message
     ↓
Claude responds (may request tool calls)
     ↓
Tools are executed automatically
     ↓
Results sent back to Claude
     ↓
Claude responds with results (may request more tools)
     ↓
Loop continues until Claude is done or max_steps reached
```

### How `toolloop` Works:

1. **Initial message** (line 132): Sends your message to Claude
2. **Loop execution** (line 135): Runs up to `max_steps` times
3. **Check for tool calls** (line 141): Extracts any `tool_use` blocks from Claude's response
4. **Execute tools** (lines 146-158): Runs each requested tool with the provided parameters
5. **Send results back** (lines 161-164): Adds tool results to conversation history
6. **Get next response** (lines 167-172): Claude receives results and continues reasoning
7. **Yield responses** (line 179): Returns each response to the caller

---

## 🔨 How Tools Are Called

### Step 1: Function → Schema Registration

**Tool Schema Generation (`chat.py:16-52`)**

```python
generate_tool_schema(func)  # Converts Python function to JSON schema
```

This inspects the function and creates a schema like:

```json
{
  "name": "get_order",
  "description": "Get order details by order ID",
  "input_schema": {
    "type": "object",
    "properties": {"order_id": {"type": "string"}},
    "required": ["order_id"]
  }
}
```

**Registration (`chat.py:87-91`)**

```python
self.tools[func.__name__] = func  # Store the actual function
self.tool_schemas.append(schema)   # Store the schema for API
```

### Step 2: Message Flow to API

**Simple Call (`chat.py:93-118`)**

```python
chat("What's the weather?")
```

**Internally:**

1. **Add to history** (line 104):
   ```python
   self.h.append({"role": "user", "content": user_message})
   ```

2. **API call** (lines 106-111):
   ```python
   response = self.c.messages.create(
       model=self.model,
       max_tokens=4096,
       messages=self.h,              # Full conversation history
       tools=self.tool_schemas        # Available tools schemas
   )
   ```

3. **Save response** (lines 113-116): Add Claude's response to history

### Step 3: API Response Structure

Claude's response contains **content blocks**:

```python
response.content = [
    TextBlock(text="Let me check that order..."),
    ToolUseBlock(
        id="toolu_123",
        name="get_order",
        input={"order_id": "O1"}
    )
]
```

### Step 4: Tool Execution (The Magic!)

**In `toolloop` (`chat.py:141-158`):**

#### Extract Tool Calls (line 141)
```python
tool_calls = [block for block in response.content if block.type == "tool_use"]
# Finds all ToolUseBlock objects
```

#### Execute Each Tool (lines 147-158)
```python
for tool_call in tool_calls:
    tool_name = tool_call.name          # "get_order"
    tool_input = tool_call.input        # {"order_id": "O1"}

    if tool_name in self.tools:
        result = self.tools[tool_name](**tool_input)  # Actual function call!
        # This is like calling: get_order(order_id="O1")

        tool_results.append(mk_toolres(tool_call.id, result))
```

#### Send Results Back to Claude (lines 161-164)
```python
self.h.append({
    "role": "user",        # Results come back as "user" messages
    "content": tool_results  # List of tool_result objects
})
```

#### Claude Processes Results (lines 167-172)
```python
response = self.c.messages.create(...)  # Claude sees the results
# Claude can now respond with findings or call more tools
```

---

## 🎯 Complete Flow Example

### User Code:
```python
chat = Chat(tools=[get_order])
for response in chat.toolloop("What's in order O1?"):
    print(chat.get_text(response))
```

### What Happens:

#### 1️⃣ First API Call:
- **Sends:** `[{"role": "user", "content": "What's in order O1?"}]`
- **Claude thinks:** "I need to use get_order tool"
- **Returns:** `[TextBlock("Let me check..."), ToolUseBlock(name="get_order", input={"order_id": "O1"})]`

#### 2️⃣ Tool Execution (Your Code):
- **Python executes:** `get_order(order_id="O1")`
- **Returns:** `{"id": "O1", "product": "Laptop", "quantity": 1, "price": 1200, ...}`

#### 3️⃣ Second API Call:
- **Sends:** `[..previous messages.., {"role": "user", "content": [tool_result]}]`
- **Claude sees** the laptop data
- **Returns:** `[TextBlock("Order O1 is for a Laptop, quantity 1, price $1200...")]`

#### 4️⃣ Loop Ends
- No more `tool_use` blocks detected
- Final response displayed to user

---

## 🚀 Setup & Usage

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your Anthropic API key:**
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```

   Or create a `.env` file:
   ```
   ANTHROPIC_API_KEY=your-api-key-here
   ```

### Running the Demo with Comprehensive Logging

To run the demo with full logging of all API interactions:

```bash
./venv/Scripts/python demo.py
```

Or on Windows Command Prompt/PowerShell:
```cmd
venv\Scripts\python demo.py
```

This will:
- Run three demos: simple weather, tool loop, and orders management
- Generate complete cycle logs with full HTTP and API details
- Show tool executions with inputs/outputs
- Track timing for each request-response cycle

**Logs are saved to:**
```
logs/
  ├── claude_complete.log          (Everything with detailed view)
  ├── session_YYYYMMDD_HHMMSS.log  (Current session only)
  ├── cycles/
  │   └── complete_cycles.log      (Complete request-response cycles)
  ├── tools/
  │   └── tool_executions.log      (Tool executions only)
  └── errors/
      └── errors.log               (Errors only)
```

**Each cycle log includes:**
- HTTP Request (method, URL, headers, body)
- API Request (model, messages, tools, parameters)
- HTTP Response (status code, duration, body)
- API Response (content blocks, token usage)
- Tool Executions (inputs, outputs, errors)
- Total cycle duration

### Basic Usage

#### Simple Chat
```python
from chat import Chat

def get_weather(city: str):
    """Get the weather for a city"""
    return f"It's sunny in {city}!"

chat = Chat(tools=[get_weather])
response = chat("What's the weather in Paris?")
print(chat.get_text(response))
```

#### Using Tool Loop (Autonomous Agent)
```python
from chat import Chat

def get_order(order_id: str):
    """Get order details by order ID"""
    return orders.get(order_id, "Order not found")

def get_customer(customer_id: str):
    """Get customer details by customer ID"""
    return customers.get(customer_id, "Customer not found")

chat = Chat(tools=[get_order, get_customer])

# Claude will automatically call tools as needed
for response in chat.toolloop("Show me order O1 and its customer details"):
    print(chat.get_text(response))
```

#### Custom Tools
```python
def calculate(expression: str):
    """Evaluate a mathematical expression"""
    return eval(expression)

def search_database(query: str):
    """Search the database for records matching the query"""
    # Your implementation
    return results

chat = Chat(tools=[calculate, search_database])
```

### Advanced Features

#### Custom Stopping Logic
```python
def my_stop_condition(response):
    # Custom logic to determine if loop should continue
    text = chat.get_text(response)
    return "DONE" not in text

for response in chat.toolloop("message", cont_func=my_stop_condition):
    print(chat.get_text(response))
```

#### Max Steps Control
```python
# Limit tool execution rounds
for response in chat.toolloop("complex task", max_steps=5):
    print(chat.get_text(response))
```

---

## 📁 Project Structure

```
AnthropicAgent/
├── chat.py          # Main Chat class implementation
├── logger.py        # Comprehensive API logging system
├── demo.py          # Demo with three example scenarios
├── tools.py         # Example tool functions
├── orders.py        # Sample data for demos
├── requirements.txt # Python dependencies
├── .env            # API key (create this)
├── logs/            # Generated log files
│   ├── claude_complete.log
│   ├── session_*.log
│   ├── cycles/complete_cycles.log
│   ├── tools/tool_executions.log
│   └── errors/errors.log
└── README.md       # This file
```

---

## 💡 Key Insights

- **Tools aren't "sent" to Claude** - only their *schemas* are sent
- **Claude decides** which tools to call based on the schemas
- **Your code executes** the actual Python functions
- **Results go back** to Claude as special "user" messages
- This creates a **conversation loop** where Claude can reason → act → observe → reason again

**The beauty is that Claude orchestrates everything** - it decides when to use tools, what parameters to pass, and when it has enough information to give you a final answer!

---

## 📦 Requirements

- Python 3.7+
- anthropic >= 0.40.0
- python-dotenv

---

## 📄 License

MIT
