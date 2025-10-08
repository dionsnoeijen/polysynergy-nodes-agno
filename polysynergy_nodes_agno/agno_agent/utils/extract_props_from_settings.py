def extract_props_from_settings(settings: dict) -> dict:
    props = {}
    for key, instance in settings.items():
        print(f"DEBUG extract_props: Processing settings instance '{key}': {type(instance)}")
        if not hasattr(instance, "settings"):
            print(f"DEBUG extract_props: Instance '{key}' has no 'settings' attribute")
            continue  # Skip instances without declared settings

        print(f"DEBUG extract_props: Instance '{key}' settings list: {instance.settings}")
        for name in instance.settings:
            if name.startswith("_"):
                continue
            try:
                value = getattr(instance, name)
                print(f"DEBUG extract_props: Instance '{key}', setting '{name}' = {value} (type: {type(value)})")

                # Skip callables EXCEPT for classes (like Pydantic models)
                # Classes are technically callable but are valid values for response_model
                if callable(value) and not isinstance(value, type):
                    print(f"DEBUG extract_props: Skipping '{name}' (callable function/method)")
                    continue

                if value is not None:
                    props[name] = value
                    print(f"DEBUG extract_props: Added '{name}' to props")
                else:
                    print(f"DEBUG extract_props: Skipping '{name}' (None)")
            except AttributeError:
                print(f"DEBUG extract_props: AttributeError for '{name}'")
                continue
    print(f"DEBUG extract_props: Final props: {list(props.keys())}")
    return props