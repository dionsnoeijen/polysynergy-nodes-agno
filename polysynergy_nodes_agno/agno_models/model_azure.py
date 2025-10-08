from agno.models.base import Model
from agno.models.azure import AzureOpenAI
from polysynergy_node_runner.setup_context.dock_property import dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Azure OpenAI",
    category="agno_models",
    icon="azure_logo.svg",
)
class ModelAzure(ServiceNode):

    api_key: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        has_in=True,
        info="Your Azure OpenAI API key for authenticating requests."
    )

    azure_endpoint: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        has_in=True,
        info="Your Azure OpenAI endpoint URL (e.g., https://your-resource.openai.azure.com/)."
    )

    azure_deployment: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        has_in=True,
        info="The deployment name of your Azure OpenAI model."
    )

    api_version: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        default="2024-10-21",
        info="The API version to use for requests."
    )

    azure_ad_token: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        info="Azure AD token for authentication (alternative to API key)."
    )

    base_url: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        info="Override the base URL for API requests."
    )

    model: str | None = NodeVariableSettings(
        label="Model",
        default="gpt-4o",
        group="model",
        dock=dock_property(select_values={
            "gpt-4.1": "GPT-4.1",
            "gpt-4.1-mini": "GPT-4.1 Mini",
            "gpt-4o": "GPT-4o",
            "gpt-4o-mini": "GPT-4o Mini",
            "gpt-4": "GPT-4",
            "gpt-4-32k": "GPT-4 32k",
            "gpt-35-turbo": "GPT-3.5 Turbo",
            "gpt-35-turbo-16k": "GPT-3.5 Turbo 16k",
        }),
        info="Select which Azure OpenAI model deployment to use."
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

    user: str | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="A user ID to help Azure OpenAI monitor and detect abuse."
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

    azure_ad_token_provider: object | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Azure AD token provider for dynamic token refresh."
    )

    instance: Model | None = NodeVariableSettings(
        label="Instance",
        has_out=True,
    )

    async def provide_instance(self) -> Model:
        self.instance = AzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.azure_endpoint,
            azure_deployment=self.azure_deployment,
            api_version=self.api_version,
            azure_ad_token=self.azure_ad_token,
            base_url=self.base_url,
            id=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stop=self.stop,
            seed=self.seed,
            logit_bias=self.logit_bias,
            logprobs=self.logprobs,
            top_logprobs=self.top_logprobs,
            user=self.user,
            default_headers=self.default_headers,
            default_query=self.default_query,
            azure_ad_token_provider=self.azure_ad_token_provider,
        )
        return self.instance