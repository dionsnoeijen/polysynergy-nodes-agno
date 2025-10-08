from agno.models.base import Model
from agno.models.google import Gemini
from polysynergy_node_runner.setup_context.dock_property import dock_property
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode

@node(
    name="Google Gemini",
    category="agno_models",
    icon="google_logo.svg",
)
class ModelGoogle(ServiceNode):

    api_key: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        has_in=True,
        info="Your Google AI API key for authenticating requests."
    )

    vertexai: bool | None = NodeVariableSettings(
        group="auth",
        dock=True,
        info="Use Vertex AI instead of Google AI Studio API."
    )

    project_id: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        info="Google Cloud Project ID (required for Vertex AI)."
    )

    location: str | None = NodeVariableSettings(
        group="auth",
        dock=True,
        info="Google Cloud region for Vertex AI (e.g., 'us-central1')."
    )

    model: str | None = NodeVariableSettings(
        label="Model",
        default="gemini-2.0-flash-001",
        group="model",
        dock=dock_property(select_values={
            "gemini-2.0-flash-001": "Gemini 2.0 Flash (Latest)",
            "gemini-1.5-pro-002": "Gemini 1.5 Pro (Latest)",
            "gemini-1.5-flash-002": "Gemini 1.5 Flash (Latest)",
            "gemini-1.5-pro-001": "Gemini 1.5 Pro",
            "gemini-1.5-flash-001": "Gemini 1.5 Flash",
            "gemini-1.0-pro": "Gemini 1.0 Pro",
        }),
        info="Select which Gemini model to use for the chat completion."
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

    max_output_tokens: int | None = NodeVariableSettings(
        group="model",
        dock=True,
        info="Maximum number of tokens to generate in the response."
    )

    search: bool | None = NodeVariableSettings(
        group="features",
        dock=True,
        info="Enable Google Search integration for real-time information."
    )

    grounding: bool | None = NodeVariableSettings(
        group="features",
        dock=True,
        info="Enable grounding to provide more accurate and factual responses."
    )

    url_context: bool | None = NodeVariableSettings(
        group="features",
        dock=True,
        info="Enable URL context for processing web content."
    )

    vertexai_search: bool | None = NodeVariableSettings(
        group="features",
        dock=True,
        info="Enable Vertex AI Search integration."
    )

    vertexai_search_datastore: str | None = NodeVariableSettings(
        group="features",
        dock=True,
        info="Vertex AI Search datastore ID for custom search."
    )

    safety_settings: list | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Configure content safety filtering and blocking thresholds."
    )

    generation_config: dict | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Advanced generation configuration options."
    )

    function_declarations: list | None = NodeVariableSettings(
        group="advanced",
        dock=True,
        info="Function declarations for tool calling capabilities."
    )

    instance: Model | None = NodeVariableSettings(
        label="Instance",
        has_out=True,
    )

    async def provide_instance(self) -> Model:
        self.instance = Gemini(
            api_key=self.api_key,
            vertexai=self.vertexai,
            project_id=self.project_id,
            location=self.location,
            id=self.model,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            max_output_tokens=self.max_output_tokens,
            search=self.search,
            grounding=self.grounding,
            url_context=self.url_context,
            vertexai_search=self.vertexai_search,
            vertexai_search_datastore=self.vertexai_search_datastore,
            safety_settings=self.safety_settings,
            generation_config=self.generation_config,
            function_declarations=self.function_declarations,
        )
        return self.instance