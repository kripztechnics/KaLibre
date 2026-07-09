from __future__ import annotations

import subprocess
import sys
from importlib import metadata
from pathlib import Path


def _normalize_requirement_name(requirement: str) -> str:
    """Convertit une ligne de requirements en nom de package utilisable par pip/metadata."""
    requirement = requirement.split(";", 1)[0].strip()
    requirement = requirement.split("#", 1)[0].strip()

    for separator in ("==", ">=", "<=", "~=", ">", "<"):
        if separator in requirement:
            requirement = requirement.split(separator, 1)[0]
            break

    return requirement.strip().lower().replace("_", "-")


def ensure_dependencies(requirements_path: str | None = None) -> None:
    """Vérifie les dépendances et les installe automatiquement si besoin."""
    if requirements_path is None:
        requirements_path = Path(__file__).resolve().parent.parent / "requirements.txt"
    else:
        requirements_path = Path(requirements_path)

    requirements = []
    if requirements_path.exists():
        for raw_line in requirements_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if line and not line.startswith("#"):
                requirements.append(line)

    missing = []
    for requirement in requirements:
        package_name = _normalize_requirement_name(requirement)
        try:
            metadata.version(package_name)
        except metadata.PackageNotFoundError:
            missing.append(requirement)

    if not missing:
        return

    print("Installation des dépendances Python manquantes...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "L'installation des dépendances a échoué. Vérifiez votre connexion internet ou exécutez 'pip install -r requirements.txt'."
        ) from exc

    print("Dépendances installées avec succès.")
