
"""Аналізатор конфігурації Django-проєкту."""

import ast
import os
import sys


def read_settings(settings_path: str) -> dict:
    """Зчитує налаштування Django за допомогою AST."""
    with open(settings_path, "r", encoding="utf-8") as file:
        source = file.read()

    tree = ast.parse(source, filename=settings_path)
    settings = {}

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    settings[target.id] = node.value

    return settings


def get_literal(node, default=None):
    """Отримує значення простого Python-виразу."""
    if node is None:
        return default

    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError, MemoryError):
        return default


def analyze_settings(settings_path: str) -> dict:
    """Аналізує основні параметри settings.py."""
    settings = read_settings(settings_path)

    debug = get_literal(settings.get("DEBUG"), "Динамічне значення")
    apps = get_literal(settings.get("INSTALLED_APPS"), [])
    language = get_literal(settings.get("LANGUAGE_CODE"), "Невідомо")
    timezone = get_literal(settings.get("TIME_ZONE"), "Невідомо")

    database_engine = "Не визначено"
    databases_node = settings.get("DATABASES")

    if isinstance(databases_node, ast.Dict):
        for key, value in zip(databases_node.keys, databases_node.values):
            if get_literal(key) == "default" and isinstance(value, ast.Dict):
                for db_key, db_value in zip(value.keys, value.values):
                    if get_literal(db_key) == "ENGINE":
                        database_engine = get_literal(
                            db_value, "Динамічне значення"
                        )

    return {
        "DEBUG": debug,
        "INSTALLED_APPS": apps,
        "DATABASES": database_engine,
        "LANGUAGE_CODE": language,
        "TIME_ZONE": timezone,
    }


def check_security(settings_path: str) -> list[str]:
    """Перевіряє три базові правила безпеки."""
    settings = read_settings(settings_path)
    warnings = []

    debug = get_literal(settings.get("DEBUG"))

    if debug is True:
        warnings.append(
            "DEBUG = True: режим налагодження не можна "
            "використовувати у production."
        )

    secret_node = settings.get("SECRET_KEY")

    if isinstance(secret_node, ast.Constant) and isinstance(
        secret_node.value, str
    ):
        warnings.append(
            "SECRET_KEY записаний безпосередньо у settings.py. "
            "Для production потрібно використовувати змінні оточення."
        )
    elif secret_node is None:
        warnings.append("SECRET_KEY не знайдено.")

    allowed_hosts = get_literal(settings.get("ALLOWED_HOSTS"))

    if allowed_hosts == []:
        warnings.append(
            "ALLOWED_HOSTS порожній. Для production потрібно "
            "вказати дозволені хости."
        )

    return warnings


def main():
    settings_path = os.path.join(
        "mysite", "mysite", "settings.py"
    )

    if not os.path.isfile(settings_path):
        print(f"Файл {settings_path} не знайдено.")
        sys.exit(1)

    config = analyze_settings(settings_path)

    print("=== Аналіз конфігурації Django ===")

    for key, value in config.items():
        print(f"{key}: {value}")

    print("\n=== Перевірка безпеки ===")

    warnings = check_security(settings_path)

    if warnings:
        for index, warning in enumerate(warnings, start=1):
            print(f"{index}. {warning}")
    else:
        print("Попереджень не знайдено.")

    print(f"\nКількість попереджень: {len(warnings)}")


if __name__ == "__main__":
    main()
