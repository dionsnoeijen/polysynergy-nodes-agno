from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="Agent Workflow Settings",
    category="agno_settings",
    has_enabled_switch=False,
    icon="agno.svg",
)
class AgentSettingsWorkflow(ServiceNode):

    # Settings that can be used by the agent on runtime.
    settings: list = [
        'workflow_id',
        'workflow_session_id',
        'workflow_session_state',
    ]

    workflow_id: str | None = NodeVariableSettings(
        dock=True,
        info="Optional workflow ID. Indicates this agent is part of a workflow."
    )

    workflow_session_id: str | None = NodeVariableSettings(
        dock=True,
        info="Session ID within the workflow this agent is part of."
    )

    workflow_session_state: dict | None = NodeVariableSettings(
        dock=True,
        info="Workflow session state passed down by the workflow controller."
    )

    instance: "AgentSettingsWorkflow" = NodeVariableSettings(
        label="Settings",
        info="Instance of this node for use in the agent.",
        has_out=True,
        type="polysynergy_nodes_agno.agent.agent_settings_workflow.AgentSettingsWorkflow"
    )

    def provide_instance(self) -> "AgentSettingsWorkflow":
        return self
