from agno.run.workflow import RunEvent
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="Agent Streaming Settings",
    category="agno_settings",
    has_enabled_switch=False,
    icon="agno.svg",
)
class AgentSettingsStreaming(ServiceNode):

    # Settings that can be used by the agent on runtime.
    settings: list = [
        'stream',
        'stream_intermediate_steps',
        'store_events',
        'events_to_skip',
    ]

    stream: bool | None = NodeVariableSettings(
        dock=True,
        info="If True, stream the final response from the agent as it is being generated."
    )

    stream_intermediate_steps: bool = NodeVariableSettings(
        dock=True,
        info="If True, stream intermediate reasoning steps or tool calls during execution."
    )

    store_events: bool = NodeVariableSettings(
        dock=True,
        info="If True, store detailed events during the agent run (e.g. tokens, tools, memory)."
    )

    events_to_skip: list[RunEvent] | None = NodeVariableSettings(
        dock=True,
        info="A list of RunEvent types to skip when storing events."
    )

    instance: "AgentSettingsStreaming" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.agent_settings_streaming.AgentSettingsStreaming"
    )

    def provide_instance(self) -> "AgentSettingsStreaming":
        return self