from agno.models.base import Model
from agno.models.huggingface import HuggingFace
from polysynergy_node_runner.setup_context.dock_property import dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="HuggingFace",
    category="agno_models",
    icon="huggingface_logo.svg",
)
class ModelHuggingFace(ServiceNode):

    api_key: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        has_in=True,
        info="Your HuggingFace API token for authenticating requests."
    )

    base_url: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        info="Override the base URL for HuggingFace API requests."
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
        default="meta-llama/Meta-Llama-3-8B-Instruct",
        group="model",
        dock=dock_property(select_values={
            "meta-llama/Meta-Llama-3-8B-Instruct": "Llama 3 8B Instruct",
            "meta-llama/Meta-Llama-3-70B-Instruct": "Llama 3 70B Instruct",
            "meta-llama/Llama-2-7b-chat-hf": "Llama 2 7B Chat",
            "meta-llama/Llama-2-13b-chat-hf": "Llama 2 13B Chat",
            "meta-llama/Llama-2-70b-chat-hf": "Llama 2 70B Chat",
            "microsoft/DialoGPT-medium": "DialoGPT Medium",
            "microsoft/DialoGPT-large": "DialoGPT Large",
            "mistralai/Mistral-7B-Instruct-v0.1": "Mistral 7B Instruct",
            "mistralai/Mixtral-8x7B-Instruct-v0.1": "Mixtral 8x7B Instruct",
            "bigscience/bloom-560m": "BLOOM 560M",
            "google/flan-t5-large": "Flan-T5 Large",
            "HuggingFaceH4/zephyr-7b-beta": "Zephyr 7B Beta",
        }),
        info="Select which HuggingFace model to use. Make sure the model supports chat/instruct format."
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

    store: bool | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Store the request and response for later inspection or logging."
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

    client_params: dict | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Additional parameters to configure the HuggingFace client."
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
        self.instance = HuggingFace(
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
            store=self.store,
            logprobs=self.logprobs,
            top_logprobs=self.top_logprobs,
            logit_bias=self.logit_bias,
            default_headers=self.default_headers,
            default_query=self.default_query,
            client_params=self.client_params,
            request_params=self.request_params,
        )
        return self.instance