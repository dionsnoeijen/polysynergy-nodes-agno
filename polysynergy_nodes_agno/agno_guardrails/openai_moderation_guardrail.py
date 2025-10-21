from agno.guardrails import OpenAIModerationGuardrail

from polysynergy_node_runner.setup_context.dock_property import dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="OpenAI Moderation Guardrail",
    category="agno_guardrails",
    has_enabled_switch=False,
    icon="agno.svg",
    version=1.0
)
class OpenAIModerationGuardrailNode(ServiceNode):
    """
    Detect content that violates OpenAI's content policy.

    Uses OpenAI's Moderation API to check for:
    - Violence
    - Hate
    - Harassment
    - Self-harm
    - Sexual content
    - And other policy violations

    Can be used with any AI provider while still enforcing OpenAI's guidelines.
    """

    moderation_model: str = NodeVariableSettings(
        label="Moderation Model",
        dock=dock_property(
            select_values={
                "omni-moderation-latest": "Omni Moderation (Latest)",
                "text-moderation-latest": "Text Moderation (Latest)",
                "text-moderation-stable": "Text Moderation (Stable)",
            }
        ),
        default="omni-moderation-latest",
        has_in=True,
        info="OpenAI moderation model to use"
    )

    raise_for_categories: list[str] | None = NodeVariableSettings(
        label="Categories",
        dock=True,
        has_in=True,
        default=None,
        info="List of categories to check (e.g., ['violence', 'hate']). Empty = all categories"
    )

    instance: OpenAIModerationGuardrail = NodeVariableSettings(
        label="Guardrail",
        info="OpenAI Moderation Guardrail instance for use with agents",
        has_out=True,
        type="agno.guardrails.OpenAIModerationGuardrail"
    )

    async def provide_instance(self) -> OpenAIModerationGuardrail:
        """Create and return the OpenAIModerationGuardrail instance."""
        kwargs = {
            "moderation_model": self.moderation_model,
        }

        if self.raise_for_categories:
            kwargs["raise_for_categories"] = self.raise_for_categories

        self.instance = OpenAIModerationGuardrail(**kwargs)
        return self.instance
