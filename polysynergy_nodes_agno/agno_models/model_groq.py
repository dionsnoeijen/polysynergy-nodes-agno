from agno.models.base import Model
from agno.models.groq import Groq
from polysynergy_node_runner.setup_context.dock_property import dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Groq",
    category="agno_models",
    icon="groq_logo.svg",
)
class ModelGroq(ServiceNode):

    api_key: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        has_in=True,
        info="Your Groq API key for authenticating requests."
    )

    base_url: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        info="Override the base URL for API requests."
    )

    timeout: int | None = NodeVariableSettings(
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
        default="llama-3.3-70b-versatile",
        group="model",
        dock=dock_property(select_values={
            "llama-3.3-70b-versatile": "Llama 3.3 70B Versatile",
            "llama-3.1-70b-versatile": "Llama 3.1 70B Versatile",
            "llama-3.1-8b-instant": "Llama 3.1 8B Instant",
            "llama3-70b-8192": "Llama 3 70B",
            "llama3-8b-8192": "Llama 3 8B",
            "mixtral-8x7b-32768": "Mixtral 8x7B",
            "gemma2-9b-it": "Gemma 2 9B",
            "gemma-7b-it": "Gemma 7B",
        }),
        info="Select which Groq model to use for the chat completion."
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

    stop: list[str] | str | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="Stop sequence(s) that will end the completion."
    )

    seed: int | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="Optional seed for deterministic outputs (useful in testing)."
    )

    logprobs: bool | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Return log-probabilities of top tokens (useful for debugging)."
    )

    top_logprobs: int | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Number of top tokens to include when returning logprobs."
    )

    logit_bias: dict | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Map of token IDs to bias values. Adjusts likelihood of specific tokens."
    )

    user: str | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="A user ID to help Groq monitor and detect abuse."
    )

    default_headers: dict | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Default headers to include with all requests."
    )

    default_query: dict | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Default query parameters for all requests."
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

    client_params: dict | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Additional parameters to configure the Groq client."
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
        self.instance = Groq(
            api_key=self.api_key,
            base_url=self.base_url,
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
            logprobs=self.logprobs,
            top_logprobs=self.top_logprobs,
            logit_bias=self.logit_bias,
            user=self.user,
            default_headers=self.default_headers,
            default_query=self.default_query,
            extra_headers=self.extra_headers,
            extra_query=self.extra_query,
            client_params=self.client_params,
            request_params=self.request_params,
        )
        return self.instance