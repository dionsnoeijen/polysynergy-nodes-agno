# Agno Agent Human-in-the-Loop (HITL) Integration

## Overview

The Agno Agent node now supports **Human-in-the-Loop (HITL)** patterns, allowing agents to pause flow execution and request user input before continuing. This integrates Agno's native pause/resume mechanism with PolySynergy's flow pause architecture.

## How It Works

### Flow Pattern

```
User → AgnoAgent runs → Agent pauses → response.is_paused = True
→ Store pause state, don't set paths → Flow pauses → Save to DynamoDB
→ User provides input via API → Flow resumes with user_input_data
→ AgnoAgent.execute() calls continue_run() → Gets final response
→ Sets true_path → Flow continues
```

### Key Mechanism

When an Agno agent pauses:
1. The node **does NOT set `true_path` or `false_path`**
2. This causes connections to become "killers" (like `confirm_reject.py`)
3. Flow execution stops and state is saved to DynamoDB
4. Lambda exits normally
5. User provides input via API, which updates `user_input_data`
6. Flow resumes, node detects pause state, calls `agent.acontinue_run()`
7. Final response is processed and `true_path` is set

## Supported HITL Patterns

The integration supports all 4 Agno HITL patterns:

### 1. Tool Confirmation (`requires_confirmation=True`)

Agent requests approval before executing tools.

**Example Agent Setup:**
```python
agent = Agent(
    model=model,
    tools=[sensitive_tool],
    requires_confirmation=True
)
```

**Pause Detection:**
- `response.is_paused = True`
- `response.tools_requiring_confirmation` contains list of tools

**User Input Format:**
```json
{
  "user_input_data": true  // or false to reject
}
```

**What Happens:**
- Node sets `tool.confirmed = True/False` on all tools
- Calls `agent.acontinue_run(run_response=response)`
- Agent continues with confirmation applied

### 2. User Input Request (`requires_user_input=True`)

Agent requests structured input from user.

**Example Agent Setup:**
```python
agent = Agent(
    model=model,
    requires_user_input=True
)
```

**Pause Detection:**
- `response.is_paused = True`
- `response.user_input_schema` contains list of `UserInputField` objects

**User Input Format:**
```json
{
  "user_input_data": {
    "field_name_1": "value1",
    "field_name_2": "value2"
  }
}
```

**What Happens:**
- Node calls `agent.acontinue_run(run_response=response, user_input=user_input_data)`
- Agent receives user input and continues

### 3. Dynamic User Input (via `UserControlFlowTools()`)

Agent dynamically requests input using control flow tools.

**Example Agent Setup:**
```python
from agno.tools.user_control_flow import UserControlFlowTools

agent = Agent(
    model=model,
    tools=[UserControlFlowTools()]
)
```

**What Agent Can Do:**
```python
# In agent's execution
tool.request_user_input(
    message="What is your email?",
    fields=[
        {"name": "email", "type": "string", "required": True}
    ]
)
```

**Same handling as pattern #2** - `user_input_schema` is populated.

### 4. External Tool Execution (`external_execution=True`)

Tools marked for external execution pause the agent.

**Example Tool Setup:**
```python
@tool(external_execution=True)
def execute_payment(amount: float):
    """Execute payment - requires external confirmation"""
    pass

agent = Agent(
    model=model,
    tools=[execute_payment]
)
```

**Pause Detection:**
- `response.is_paused = True`
- `response.tools_awaiting_external_execution` contains list of tools

**User Input Format:**
```json
{
  "user_input_data": {
    "execute_payment": {
      "success": true,
      "transaction_id": "txn_123"
    }
  }
}
```

**What Happens:**
- Node sets `tool.result = user_input_data[tool_name]` for each tool
- Calls `agent.acontinue_run(run_response=response)`
- Agent receives tool results and continues

## Node Variables

### Input Variables

**`user_input_data`** (dict | bool | None)
- User's input to resume paused execution
- `bool` for confirmation (pattern #1)
- `dict` for user input (patterns #2, #3, #4)
- Provided via API when resuming flow

### Output Variables

**`pause_reason`** (str | None)
- Why execution paused
- Values: `"confirmation"`, `"user_input"`, `"external_tool"`, `"unknown"`

**`pause_info`** (dict | None)
- Details about the pause for UI display
- Always includes:
  - `paused`: `true`
  - `type`: Same as `pause_reason`
  - `message`: Human-readable message
  - `run_id`: Agno run ID
- Pattern-specific fields:
  - **Confirmation**: `tools` array with `tool_name` and `tool_args`
  - **User Input**: `schema` array with field definitions
  - **External Tools**: `tools` array with tool info

**Example `pause_info` for User Input:**
```json
{
  "paused": true,
  "type": "user_input",
  "run_id": "run_abc123",
  "message": "Agent needs user input",
  "schema": [
    {
      "name": "email",
      "description": "User's email address",
      "type": "string",
      "required": true
    },
    {
      "name": "phone",
      "description": "Phone number (optional)",
      "type": "string",
      "required": false
    }
  ]
}
```

## Flow Setup Example

### 1. Simple Confirmation Flow

```
[Agno Agent with requires_confirmation=True]
  ↓ (true_path)
[Process Result]
```

**Agent pauses:**
- UI displays tools awaiting confirmation
- User approves/rejects
- API resumes flow with `user_input_data: true/false`
- Flow continues to "Process Result"

### 2. Dynamic Form Generation Flow

```
[Agno Agent with UserControlFlowTools]
  ↓ (true_path)
[Send Email with form data]
```

**Agent pauses:**
- Agent calls `request_user_input()` to ask for email/name
- UI displays form based on `pause_info.schema`
- User fills form
- API resumes flow with `user_input_data: {email: "...", name: "..."}`
- Agent processes input and continues
- Flow sends email with collected data

### 3. External Payment Flow

```
[Agno Agent with external payment tool]
  ↓ (true_path)
[Record Transaction]
```

**Agent pauses:**
- Agent wants to execute payment tool
- System pauses for external execution
- Payment processor executes payment externally
- API resumes flow with `user_input_data: {execute_payment: {success: true, txn_id: "..."}}`
- Agent receives payment result
- Flow records transaction

## API Integration

### Detecting Paused State

When flow execution completes, check the AgnoAgent node's state:

```python
# After flow execution
node = state.get_node_by_id(agent_node_id)

if node.pause_info and node.pause_info.get("paused"):
    # Flow is paused, present UI to user
    pause_type = node.pause_info["type"]

    if pause_type == "confirmation":
        # Show approval dialog
        tools = node.pause_info["tools"]

    elif pause_type == "user_input":
        # Show form based on schema
        schema = node.pause_info["schema"]

    elif pause_type == "external_tool":
        # Execute tools externally
        tools = node.pause_info["tools"]
```

### Resuming Flow

```python
# User provided input
user_input = collect_user_input()  # Your UI logic

# Resume flow via API
response = await continue_run(
    flow_id=flow_id,
    run_id=run_id,
    node_updates={
        agent_node_id: {
            "user_input_data": user_input
        }
    }
)
```

## Best Practices

### 1. Always Check `pause_info`

After AgnoAgent execution, always check for pause state:

```python
if agent_node.pause_info and agent_node.pause_info.get("paused"):
    # Handle pause
    pass
```

### 2. Provide Clear Schemas

When using dynamic user input, provide clear field descriptions:

```python
tool.request_user_input(
    message="We need some information to create your account",
    fields=[
        {
            "name": "email",
            "type": "string",
            "description": "Your email address for login",
            "required": True
        },
        {
            "name": "company",
            "type": "string",
            "description": "Company name (optional)",
            "required": False
        }
    ]
)
```

### 3. Handle Timeout/Expiry

Paused flows should have timeout policies:
- Store pause timestamp
- Expire after N hours/days
- Clean up stale paused flows

### 4. Validate User Input

Before resuming, validate user input matches the schema:

```python
schema = node.pause_info["schema"]
user_input = collect_user_input()

# Validate all required fields present
for field in schema:
    if field["required"] and field["name"] not in user_input:
        raise ValueError(f"Missing required field: {field['name']}")
```

## Debugging

Enable debug logging to track HITL flow:

```python
agent = Agent(
    model=model,
    debug_mode=True,
    debug_level=2
)
```

Look for these log messages:
- `[HITL] Agent execution paused - awaiting user input`
- `[HITL] Waiting for confirmation on N tool(s)`
- `[HITL] Waiting for user input: N field(s)`
- `[HITL] Resuming paused agent execution with user input`
- `[HITL] Calling acontinue_run...`
- `[HITL] Resume completed, processing response`

## Limitations

1. **Streaming Not Supported During Resume**: The `acontinue_run()` response is processed as a complete response, not streamed
2. **Single Pause Per Execution**: Agent can only pause once per execution; nested pauses not supported
3. **State Storage**: Paused `RunResponse` object is stored in node state - ensure it's serializable
4. **Team Agents**: HITL only works for standalone agents, not team members

## Related Nodes

- **Confirm/Reject Node** (`/human_in_loop/confirm_reject.py`) - Simple boolean confirmation
- **User Control Flow Tools** (Agno built-in) - Dynamic form generation
- **AgnoAgent Node** - Main agent execution

## Technical Notes

### Why Not Set Paths?

The key to pause mechanism is **not setting `true_path` or `false_path`**:

```python
# In _handle_pause():
# DO NOT set true_path or false_path
# This causes connections to become killers and flow stops
```

This leverages PolySynergy's flow engine behavior in `flow_execution_mixin.py` (lines 127-137):
- If paths are not set (remain `None`), connections don't become killers
- Flow saves state and exits normally
- On resume, node re-executes with `user_input_data` populated

### Serialization

The `paused_run_response` is stored as-is. Ensure Agno's `RunResponse` object is serializable to DynamoDB. If issues arise, consider storing only necessary fields:

```python
# Potential optimization
self.paused_run_response = {
    "run_id": run_response.run_id,
    "session_id": run_response.session_id,
    # ... other serializable fields
}
```

Then reconstruct on resume using `run_id`.
