from agno.models.base import Model
from agno.models.anthropic import Claude
from polysynergy_node_runner.setup_context.dock_property import dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Anthropic Claude",
    category="agno_models",
    icon="anthropic_logo.svg",
)
class ModelAnthropic(ServiceNode):

    api_key: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        has_in=True,
        info="Your Anthropic API key for authenticating requests."
    )

    model: str | None = NodeVariableSettings(
        label="Model",
        default="claude-3-5-sonnet-20241022",
        group="model",
        dock=dock_property(select_values={
            "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet (Latest)",
            "claude-3-5-sonnet-20240620": "Claude 3.5 Sonnet (June 2024)",
            "claude-3-5-haiku-20241022": "Claude 3.5 Haiku (Latest)",
            "claude-3-opus-20240229": "Claude 3 Opus",
            "claude-3-sonnet-20240229": "Claude 3 Sonnet",
            "claude-3-haiku-20240307": "Claude 3 Haiku",
        }),
        info="Select which Claude model to use for the chat completion."
    )

    max_tokens: int | None = NodeVariableSettings(
        default=4096,
        group="model",
        dock=True,
        info="Maximum number of tokens to generate in the response."
    )

    temperature: float | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="Controls randomness. Higher = more creative, lower = more focused."
    )

    top_p: float | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="Controls diversity via nucleus sampling. 1.0 = no filtering."
    )

    top_k: int | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="Controls diversity by limiting to top K most likely tokens."
    )

    stop_sequences: list[str] | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="List of stop sequences that will end the completion."
    )

    cache_system_prompt: bool | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Enable caching of system prompt to reduce costs for repeated requests."
    )

    extended_cache_time: bool | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Use extended cache time for better performance on repeated requests."
    )

    thinking: dict | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Configuration for Claude's thinking/reasoning process."
    )

    default_headers: dict | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Default headers to include with all requests to Anthropic API."
    )

    client_params: dict | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Additional parameters to configure the Anthropic client."
    )

    request_params: dict | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Additional parameters to include with each API request."
    )

    instance: Model | None = NodeVariableSettings(
        label="Instance",
        has_out=True,
    )

    async def provide_instance(self) -> Model:
        self.instance = Claude(
            api_key=self.api_key,
            id=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            stop_sequences=self.stop_sequences,
            cache_system_prompt=self.cache_system_prompt,
            extended_cache_time=self.extended_cache_time,
            thinking=self.thinking,
            default_headers=self.default_headers,
            client_params=self.client_params,
            request_params=self.request_params,
        )
        return self.instance