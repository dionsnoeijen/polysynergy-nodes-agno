from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings


class IdentityMixin:
    # IDENTITY SETTINGS

    name: str | None = NodeVariableSettings(
        group="identity",
        dock=True,
        info="De naam van de agent die zichtbaar is in de chat."
    )

    agent_id: str | None = NodeVariableSettings(
        group="identity",
        dock=True,
        info="Uniek ID voor deze agent. Wordt automatisch gegenereerd als je het leeg laat."
    )

    user_id: str | None = NodeVariableSettings(
        group="identity",
        dock=True,
        info="Standaard user_id die gebruikt wordt bij runs. Nuttig als je de agent altijd voor dezelfde gebruiker inzet."
    )

    session_id: str | None = NodeVariableSettings(
        group="identity",
        dock=True,
        info="Uniek sessie-ID om de context of chatgeschiedenis te groeperen. Leeg laten voor een nieuwe sessie per run."
    )

    session_name: str | None = NodeVariableSettings(
        group="identity",
        dock=True,
        info="Naam van de sessie voor debugging of opslag. Alleen voor menselijk gebruik."
    )

    introduction: str | None = NodeVariableSettings(
        group="identity",
        dock=True,
        info="Introductie die aan de start van een sessie wordt toegevoegd aan de message history."
    )