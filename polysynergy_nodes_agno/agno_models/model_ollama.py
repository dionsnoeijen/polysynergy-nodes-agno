from agno.models.base import Model
from agno.models.ollama import Ollama
from polysynergy_node_runner.setup_context.dock_property import dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Ollama",
    category="agno_models",
    icon="ollama_logo.svg",
    metadata={"deployment": "local"},
)
class ModelOllama(ServiceNode):
    """
    Ollama model provider for running local LLMs.

    NOTE: This node requires a locally running Ollama server (default: localhost:11434),
    making it unsuitable for serverless/cloud deployments. For production cloud
    environments, use cloud-based model providers like OpenAI, Anthropic, or Google.
    """

    host: str | None = NodeVariableSettings(
        group="connection",
        dock=True,
        default="http://localhost:11434",
        info="Ollama server host URL (e.g., http://localhost:11434)."
    )

    api_key: str | None = NodeVariableSettings(
        group="connection",
        dock=True,
        has_in=True,
        info="Optional API key for Ollama server authentication."
    )

    timeout: float | None = NodeVariableSettings(
        group="connection",
        dock=True,
        info="Timeout for the API request in seconds."
    )

    model: str | None = NodeVariableSettings(
        label="Model",
        default="llama3.1",
        group="model",
        dock=dock_property(select_values={
            "llama3.1": "Llama 3.1",
            "llama3.2": "Llama 3.2",
            "llama3": "Llama 3",
            "llama2": "Llama 2",
            "codellama": "Code Llama",
            "mistral": "Mistral",
            "mixtral": "Mixtral",
            "qwen": "Qwen",
            "gemma": "Gemma",
            "deepseek-coder": "DeepSeek Coder",
            "phi3": "Phi-3",
            "nomic-embed-text": "Nomic Embed Text",
            "dolphin-mistral": "Dolphin Mistral",
        }),
        info="Select which Ollama model to use. Make sure the model is installed locally."
    )

    format: dict | str | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="Response format specification (e.g., 'json' or custom format schema)."
    )

    options: dict | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="Model-specific options (temperature, top_k, top_p, etc.)."
    )

    keep_alive: float | str | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="How long to keep the model loaded in memory (e.g., '5m', '1h', or seconds)."
    )

    client_params: dict | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Additional parameters to configure the Ollama client."
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
        self.instance = Ollama(
            host=self.host,
            api_key=self.api_key,
            timeout=self.timeout,
            id=self.model,
            format=self.format,
            options=self.options,
            keep_alive=self.keep_alive,
            client_params=self.client_params,
            request_params=self.request_params,
        )
        return self.instance