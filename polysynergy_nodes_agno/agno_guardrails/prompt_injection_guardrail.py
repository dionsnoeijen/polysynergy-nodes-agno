from agno.guardrails import PromptInjectionGuardrail

from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="Prompt Injection Guardrail",
    category="agno_guardrails",
    has_enabled_switch=False,
    icon="agno.svg",
    version=1.0
)
class PromptInjectionGuardrailNode(ServiceNode):
    """
    Detect and prevent prompt injection attempts in agent inputs.

    Default patterns detected:
    - "ignore previous instructions"
    - "ignore your instructions"
    - "you are now a"
    - "forget everything above"
    - "developer mode"
    - "override safety"
    - "disregard guidelines"
    - "system prompt"
    - "jailbreak"
    - "act as if"
    - "pretend you are"
    - "roleplay as"
    - "simulate being"
    - "bypass restrictions"
    - "ignore safeguards"
    - "admin override"
    - "root access"
    """

    injection_patterns: list[str] | None = NodeVariableSettings(
        label="Injection Patterns",
        dock=True,
        has_in=True,
        default=None,
        info="Custom list of injection patterns to detect (overrides default patterns)"
    )

    instance: PromptInjectionGuardrail = NodeVariableSettings(
        label="Guardrail",
        info="Prompt Injection Guardrail instance for use with agents",
        has_out=True,
        type="agno.guardrails.PromptInjectionGuardrail"
    )

    async def provide_instance(self) -> PromptInjectionGuardrail:
        """Create and return the PromptInjectionGuardrail instance."""
        kwargs = {}

        if self.injection_patterns:
            kwargs["injection_patterns"] = self.injection_patterns

        self.instance = PromptInjectionGuardrail(**kwargs)
        return self.instance
