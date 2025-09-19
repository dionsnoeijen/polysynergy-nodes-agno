from agno.models.base import Model
from agno.models.openai import OpenAIChat
from polysynergy_node_runner.setup_context.dock_property import dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="OpenAI Model",
    category="agno_models",
    icon="openai_logo.svg",
)
class ModelOpenAi(ServiceNode):

    api_key: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        has_in=True,
        info="Your OpenAI API key for authenticating requests."
    )

    organization: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        info="Your OpenAI organization ID, if applicable."
    )

    base_url: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        info="Override the base URL for API requests (e.g. for proxy or Azure)."
    )

    timeout: float | None = NodeVariableSettings(
        group="auth",
        dock=True,
        info="Timeout for the API request in seconds."
    )

    max_retries: int | None = NodeVariableSettings(
        group="auth",
        dock=True,
        info="Number of times to retry the request on failure."
    )

    model: str | None = NodeVariableSettings(
        label="Model",
        default="gpt-4o",
        group="model",
        dock=dock_property(select_values={
            "gpt-4.1": "gpt-4.1 (10.000 TPM)",
            "gpt-4.1-mini": "gpt-4.1-mini (60.000 TPM)",
            "gpt-4.1-nano": "gpt-4.1-nano (60.000 TPM)",
            "o3": "o3 (100.000 TPM)",
            "o4-mini": "o4-mini (100.000 TPM)",
            "gpt-4o": "gpt-4o (10.000 TPM)",
            "gpt-4o-mini": "gpt-4o-mini (60.000 TPM)",
        }),
        info="Select which OpenAI model to use for the chat completion."
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

    frequency_penalty: float | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="Penalizes repetition. Higher values reduce repeated phrases."
    )

    presence_penalty: float | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="Incentivizes introducing new topics. Higher = more novel."
    )

    stop: list[str] | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="List of stop sequences that will end the completion."
    )

    seed: int | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="Optional seed for deterministic outputs (useful in testing)."
    )

    logit_bias: dict | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="Map of token IDs to bias values. Adjusts likelihood of specific tokens."
    )

    store: bool | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Store the request and response for later inspection or logging."
    )

    reasoning_effort: str | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Set how much reasoning effort the model should apply (if supported)."
    )

    model_metadata: dict | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Optional metadata to attach to the request for tracking or logging."
    )

    logprobs: bool | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Return log-probabilities of top tokens (useful for debugging or analysis)."
    )

    top_logprobs: int | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Number of top tokens to include when returning logprobs."
    )

    role_map: dict | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Override role mapping (e.g. map 'system' to 'developer')."
    )

    user: str | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="A user ID to help OpenAI monitor and detect abuse."
    )

    modalities: list | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Enable specific input/output modalities like 'text' or 'audio'."
    )

    audio: dict | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Audio configuration for the response (e.g. voice, format)."
    )

    extra_headers: dict | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Extra HTTP headers to include with the request."
    )

    extra_query: dict | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Extra query parameters to append to the request URL."
    )

    instance: Model | None = NodeVariableSettings(
        label="Instance",
        has_out=True,
    )

    async def provide_instance(self) -> Model:
        print("DEBUG: Inside ModelOpenAi.provide_instance() - ASYNC VERSION")
        self.instance = OpenAIChat(
            api_key=self.api_key,
            organization=self.organization,
            base_url=self.base_url if self.base_url else None,
            timeout=self.timeout,
            max_retries=self.max_retries,
            id=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stop=self.stop,
            seed=self.seed,
            logit_bias=self.logit_bias,
            store=self.store,
            reasoning_effort=self.reasoning_effort,
            metadata=self.model_metadata,
            logprobs=self.logprobs,
            top_logprobs=self.top_logprobs,
            role_map=self.role_map,
            user=self.user,
            modalities=self.modalities,
            audio=self.audio,
            extra_headers=self.extra_headers,
            extra_query=self.extra_query
        )
        return self.instance