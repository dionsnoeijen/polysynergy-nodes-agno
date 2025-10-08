from agno.models.base import Model
from agno.models.mistral import MistralChat
from polysynergy_node_runner.setup_context.dock_property import dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Mistral",
    category="agno_models",
    icon="mistral_logo.svg",
)
class ModelMistral(ServiceNode):

    api_key: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        has_in=True,
        info="Your Mistral API key for authenticating requests."
    )

    endpoint: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        info="Custom endpoint URL for Mistral API requests."
    )

    max_retries: int | None = NodeVariableSettings(
        group="auth",
        dock=True,
        info="Number of times to retry the request on failure."
    )

    timeout: int | None = NodeVariableSettings(
        group="auth",
        dock=True,
        info="Timeout for the API request in seconds."
    )

    model: str | None = NodeVariableSettings(
        label="Model",
        default="mistral-large-latest",
        group="model",
        dock=dock_property(select_values={
            "mistral-large-latest": "Mistral Large (Latest)",
            "mistral-medium-latest": "Mistral Medium (Latest)",
            "mistral-small-latest": "Mistral Small (Latest)",
            "mistral-tiny": "Mistral Tiny",
            "mistral-7b-instruct": "Mistral 7B Instruct",
            "mixtral-8x7b-instruct": "Mixtral 8x7B Instruct",
            "mixtral-8x22b-instruct": "Mixtral 8x22B Instruct",
            "codestral-latest": "Codestral (Latest)",
            "codestral-mamba-latest": "Codestral Mamba (Latest)",
        }),
        info="Select which Mistral model to use for the chat completion."
    )

    temperature: float | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="Controls randomness. Higher = more creative, lower = more focused."
    )

    max_tokens: int | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="Maximum number of tokens to generate in the response."
    )

    top_p: float | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="Controls diversity via nucleus sampling. 1.0 = no filtering."
    )

    random_seed: int | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="Optional seed for deterministic outputs (useful in testing)."
    )

    safe_mode: bool | None = NodeVariableSettings(
        group="safety",
        dock=True,
        default=False,
        info="Enable safe mode to filter harmful content."
    )

    safe_prompt: bool | None = NodeVariableSettings(
        group="safety",
        dock=True,
        default=False,
        info="Enable safe prompt to add safety instructions to the input."
    )

    client_params: dict | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Additional parameters to configure the Mistral client."
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
        self.instance = MistralChat(
            api_key=self.api_key,
            endpoint=self.endpoint,
            max_retries=self.max_retries,
            timeout=self.timeout,
            id=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            random_seed=self.random_seed,
            safe_mode=self.safe_mode,
            safe_prompt=self.safe_prompt,
            client_params=self.client_params,
            request_params=self.request_params,
        )
        return self.instance