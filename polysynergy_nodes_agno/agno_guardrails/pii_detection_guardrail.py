from agno.guardrails import PIIDetectionGuardrail

from polysynergy_node_runner.setup_context.dock_property import dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="PII Detection Guardrail",
    category="agno_guardrails",
    has_enabled_switch=False,
    icon="agno.svg",
    version=1.0
)
class PIIDetectionGuardrailNode(ServiceNode):
    """
    Detect PII (Personally Identifiable Information) in agent inputs.

    Detects:
    - Social Security Numbers (SSNs)
    - Credit Card Numbers
    - Email Addresses
    - Phone Numbers
    - Custom PII patterns
    """

    enable_ssn_check: bool = NodeVariableSettings(
        label="Check SSN",
        dock=dock_property(switch=True),
        default=True,
        info="Enable detection of Social Security Numbers"
    )

    enable_credit_card_check: bool = NodeVariableSettings(
        label="Check Credit Cards",
        dock=dock_property(switch=True),
        default=True,
        info="Enable detection of Credit Card Numbers"
    )

    enable_email_check: bool = NodeVariableSettings(
        label="Check Emails",
        dock=dock_property(switch=True),
        default=True,
        info="Enable detection of Email Addresses"
    )

    enable_phone_check: bool = NodeVariableSettings(
        label="Check Phone Numbers",
        dock=dock_property(switch=True),
        default=True,
        info="Enable detection of Phone Numbers"
    )

    mask_pii: bool = NodeVariableSettings(
        label="Mask PII",
        dock=dock_property(switch=True),
        default=False,
        info="Mask detected PII with asterisks instead of raising error"
    )

    custom_patterns: dict | None = NodeVariableSettings(
        label="Custom Patterns",
        dock=True,
        has_in=True,
        default=None,
        info="Dict of custom PII patterns to detect (e.g., {'bank_account': r'\\b\\d{10}\\b'})"
    )

    instance: PIIDetectionGuardrail = NodeVariableSettings(
        label="Guardrail",
        info="PII Detection Guardrail instance for use with agents",
        has_out=True,
        type="agno.guardrails.PIIDetectionGuardrail"
    )

    async def provide_instance(self) -> PIIDetectionGuardrail:
        """Create and return the PIIDetectionGuardrail instance."""
        kwargs = {
            "enable_ssn_check": self.enable_ssn_check,
            "enable_credit_card_check": self.enable_credit_card_check,
            "enable_email_check": self.enable_email_check,
            "enable_phone_check": self.enable_phone_check,
            "mask_pii": self.mask_pii,
        }

        if self.custom_patterns:
            kwargs["custom_patterns"] = self.custom_patterns

        self.instance = PIIDetectionGuardrail(**kwargs)
        return self.instance
