from collections.abc import Callable

from polysynergy_node_runner.setup_context.dock_property import dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="Agent Tools Settings",
    category="agno_settings",
    has_enabled_switch=False,
    icon="agno.svg",
)
class AgentSettingsTools(ServiceNode):

    # Settings that can be used by the agent on runtime.
    settings: list = [
        'tools',
        'tool_calls',
        'show_tool_calls',
        'tool_call_limit',
        'tool_choice',
        'tool_hooks',
        'read_chat_history',
        'search_knowledge',
        'update_knowledge',
        'read_tool_call_history',
    ]

    show_tool_calls: bool = NodeVariableSettings(
        dock=True,
        info="Whether tool calls are included in the agent's output response.",
        node=False
    )

    tool_call_limit: int | None = NodeVariableSettings(
        dock=True,
        info="Maximum number of tool calls allowed per run.",
        node=False
    )

    tool_choice: str | dict | None = NodeVariableSettings(
        dock=dock_property(select_values={"none": "none", "auto": "auto"}),
        default="auto",
        has_in=True,
        info=(
            "Controls how tools are used: "
            "'none' disables tools, 'auto' lets the model choose, or specify a tool dict to enforce a specific call."
        )
    )

    tool_hooks: list[Callable] | None = NodeVariableSettings(
        group="tools",
        dock=True,
        has_out=True,
        info="List of middleware functions that are called around tool executions (e.g. for logging or filtering)."
    )

    read_chat_history: bool = NodeVariableSettings(
        dock=True,
        info="Adds a tool that allows the model to read the chat history.",
    )

    search_knowledge: bool = NodeVariableSettings(
        dock=True,
        info="Adds a tool that allows the model to search the knowledge base. Only enabled if knowledge is provided.",
    )

    update_knowledge: bool = NodeVariableSettings(
        dock=True,
        info="Adds a tool that allows the model to update the knowledge base.",
    )

    read_tool_call_history: bool = NodeVariableSettings(
        dock=True,
        info="Adds a tool that allows the model to read the history of previous tool calls.",
    )

    instance: "AgentSettingsTools" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.agent_settings_tools.AgentSettingsTools"
    )

    def provide_instance(self) -> "AgentSettingsTools":
        return self