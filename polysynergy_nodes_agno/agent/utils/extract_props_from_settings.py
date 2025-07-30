def extract_props_from_settings(settings: dict) -> dict:
    props = {}
    for instance in settings.values():
        if not hasattr(instance, "settings"):
            continue  # Skip instances without declared settings

        for name in instance.settings:
            if name.startswith("_"):
                continue
            try:
                value = getattr(instance, name)
                if callable(value):
                    continue
                if value is not None:
                    props[name] = value
            except AttributeError:
                continue
    return props