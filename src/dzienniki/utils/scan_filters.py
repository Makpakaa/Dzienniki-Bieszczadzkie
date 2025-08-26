from __future__ import annotations
from pathlib import Path
import json

_DEFAULT = {
    "ignore_contains": ["trawa", "grass", "grass_short"],
    "ignore_names": [],
    "allow_names": [],
    "max_distance": None,
}

def _settings_dir() -> Path:
    # .../src/dzienniki/utils/scan_filters.py -> parents[1] == .../src/dzienniki
    return Path(__file__).resolve().parents[1] / "settings"

def load_scan_filters() -> dict:
    """Ładuje konfigurację filtrów skanowania. Jeśli plik nie istnieje, zwraca domyślną."""
    cfg = dict(_DEFAULT)
    path = _settings_dir() / "scan_filters.json"
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        for k in ("ignore_contains", "ignore_names", "allow_names", "max_distance"):
            if k in data and data[k] is not None:
                cfg[k] = data[k]
    except FileNotFoundError:
        # Brak pliku = użyj domyślnej konfiguracji
        pass

    # Normalizacja do lower-case
    cfg["ignore_contains"] = [str(s).lower() for s in cfg.get("ignore_contains", [])]
    cfg["ignore_names"] = [str(s).lower() for s in cfg.get("ignore_names", [])]
    cfg["allow_names"] = [str(s).lower() for s in cfg.get("allow_names", [])]
    return cfg

def should_ignore(name: str, cfg: dict) -> bool:
    """Zwraca True, jeśli element powinien zostać odfiltrowany."""
    ln = str(name or "").lower().strip()
    allow = cfg.get("allow_names") or []
    if allow:
        # Jeśli zdefiniowano białą listę — przepuszczamy tylko te nazwy
        return ln not in allow
    if ln in (cfg.get("ignore_names") or []):
        return True
    for sub in (cfg.get("ignore_contains") or []):
        if sub and sub in ln:
            return True
    return False
