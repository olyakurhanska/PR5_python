
"""Генератор requirements.txt з перевіркою залежностей."""

import json
import subprocess
import sys
from pathlib import Path
from importlib.metadata import distributions


def get_installed_packages() -> list[dict]:
    """Повертає список встановлених пакетів з версіями."""

    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    packages = json.loads(result.stdout)

    return [
        {"name": pkg["name"], "version": pkg["version"]}
        for pkg in packages
    ]


def generate_requirements(
    packages: list[dict],
    filename: str = "requirements.txt"
):
    """Записує пакети у файл requirements.txt."""

    excluded = {"pip", "setuptools", "wheel"}

    lines = []

    for package in packages:
        name = package["name"]
        version = package["version"]

        if name.lower() not in excluded:
            lines.append(f"{name}=={version}")

    lines.sort(key=str.lower)

    Path(filename).write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )


def verify_requirements(filename: str = "requirements.txt") -> bool:
    """Перевіряє наявність пакетів та збіг їхніх версій."""

    path = Path(filename)

    if not path.is_file():
        print(f"Помилка: файл '{filename}' не знайдено.")
        return False

    installed = {
        package.metadata["Name"].lower().replace("_", "-"): package.version
        for package in distributions()
    }

    all_ok = True

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if "==" not in line:
            print(f"Некоректний запис: {line}")
            all_ok = False
            continue

        name, required_version = line.split("==", 1)
        normalized_name = name.lower().replace("_", "-")
        current_version = installed.get(normalized_name)

        if current_version is None:
            print(f"[MISSING] {name} не встановлено")
            all_ok = False
        elif current_version != required_version:
            print(
                f"[MISMATCH] {name}: "
                f"потрібна {required_version}, "
                f"встановлена {current_version}"
            )
            all_ok = False
        else:
            print(f"[OK] {name}=={required_version}")

    return all_ok


def main():
    print("=== Встановлені пакети ===")

    packages = get_installed_packages()
    print(f"Знайдено {len(packages)} пакетів\n")

    for package in packages[:10]:
        print(f"  {package['name']}=={package['version']}")

    if len(packages) > 10:
        print(f"  ... та ще {len(packages) - 10}")

    print("\n=== Генерація requirements.txt ===")

    generate_requirements(packages)
    print("Файл requirements.txt створено.")

    print("\n=== Перевірка залежностей ===")

    ok = verify_requirements()

    print(
        "\nПеревірка залежностей: "
        + ("Усе OK" if ok else "Є розбіжності")
    )

    print("\n=== Перевірка відсутнього файлу ===")

    missing_file_ok = not verify_requirements(
        "missing_requirements.txt"
    )

    print(
        "Обробка відсутнього файлу: "
        + ("Успішно" if missing_file_ok else "Помилка")
    )


if __name__ == "__main__":
    main()
