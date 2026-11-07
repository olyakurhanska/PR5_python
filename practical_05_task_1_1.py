
"""Скрипт перевірки середовища розробки."""

import sys
import importlib
from importlib.metadata import version, PackageNotFoundError


def check_python_version():
    """Перевіряє версію Python (потрібна >= 3.10)."""
    current = sys.version_info

    print(f"Python {current.major}.{current.minor}.{current.micro}")

    if current >= (3, 10):
        print("Версія Python відповідає вимогам.")
        return True

    print("УВАГА: потрібна версія Python 3.10 або новіша.")
    return False


def check_package(package_name: str) -> bool:
    """Перевіряє встановлення пакета та виводить його версію."""
    try:
        importlib.import_module(package_name)

        package_version = version(package_name)

        print(f"  {package_name}: {package_version} - встановлено")
        return True

    except (ImportError, PackageNotFoundError):
        print(f"  {package_name}: НЕ ВСТАНОВЛЕНО")
        return False


def main():
    python_ok = check_python_version()

    print("\nВстановлені пакети:")

    packages = ["django", "flask"]
    results = {
        package: check_package(package)
        for package in packages
    }

    installed = sum(results.values())
    missing = len(packages) - installed

    print("\nПідсумок перевірки:")
    print(f"Встановлено пакетів: {installed}")
    print(f"Відсутні пакети: {missing}")

    if missing:
        missing_names = [
            package
            for package, is_installed in results.items()
            if not is_installed
        ]
        print(
            "Для встановлення виконайте: "
            f"python -m pip install {' '.join(missing_names)}"
        )
    else:
        print("Усі необхідні фреймворки встановлено.")

    print(f"\nІнтерпретатор Python: {sys.executable}")
    print(f"Середовище venv активне: {sys.prefix != sys.base_prefix}")

    if not python_ok:
        print("Версія Python не відповідає вимогам.")


if __name__ == "__main__":
    main()
