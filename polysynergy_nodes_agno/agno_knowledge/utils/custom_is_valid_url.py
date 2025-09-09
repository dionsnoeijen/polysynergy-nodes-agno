from typing import Callable

def make_url_validator(filetypes: list[str]) -> Callable[[str], bool]:
    lower_types = [ft.lower().lstrip(".") for ft in filetypes]

    def _validator(url: str) -> bool:
        u = url.lower()
        for ft in lower_types:
            if f".{ft}" in u:
                return True
        return False

    return _validator