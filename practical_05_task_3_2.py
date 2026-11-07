
"""Порівняльний аналіз структури Django та Flask проєктів."""

import os


# Службові файли та каталоги не включаємо до аналізу.
IGNORED_DIRS = {
    "__pycache__",
    "venv",
    "venv2",
    ".git",
    ".idea",
    ".vscode",
}

IGNORED_FILES = {
    "db.sqlite3",
    ".DS_Store",
}


def should_ignore(name: str, is_directory: bool = False) -> bool:
    """Перевіряє, чи потрібно пропустити елемент."""

    if is_directory:
        return name in IGNORED_DIRS

    return name in IGNORED_FILES or name.endswith(".pyc")


def scan_directory(path: str, prefix: str = "") -> list[str]:
    """Рекурсивно сканує каталог і повертає дерево файлів."""

    tree = []

    if not os.path.isdir(path):
        return tree

    entries = []

    for name in os.listdir(path):
        full_path = os.path.join(path, name)
        is_directory = os.path.isdir(full_path)

        if not should_ignore(name, is_directory):
            entries.append((name, full_path, is_directory))

    # Спочатку каталоги, потім файли.
    entries.sort(key=lambda item: (not item[2], item[0].lower()))

    for index, (name, full_path, is_directory) in enumerate(entries):
        is_last = index == len(entries) - 1
        connector = "└── " if is_last else "├── "

        if is_directory:
            tree.append(f"{prefix}{connector}{name}/")

            next_prefix = prefix + ("    " if is_last else "│   ")
            tree.extend(scan_directory(full_path, next_prefix))
        else:
            tree.append(f"{prefix}{connector}{name}")

    return tree


def analyze_project(path: str) -> dict:
    """Збирає статистику файлів і каталогів проєкту."""

    stats = {
        "py_files": 0,
        "html_files": 0,
        "css_files": 0,
        "total_size": 0,
        "directories": [],
    }

    for root, dirs, files in os.walk(path):
        dirs[:] = sorted(
            directory
            for directory in dirs
            if not should_ignore(directory, True)
        )

        for directory in dirs:
            directory_path = os.path.relpath(
                os.path.join(root, directory), path
            )
            stats["directories"].append(directory_path)

        for filename in files:
            if should_ignore(filename):
                continue

            full_path = os.path.join(root, filename)
            extension = os.path.splitext(filename)[1].lower()

            if extension == ".py":
                stats["py_files"] += 1
            elif extension == ".html":
                stats["html_files"] += 1
            elif extension == ".css":
                stats["css_files"] += 1

            stats["total_size"] += os.path.getsize(full_path)

    stats["directories"].sort()

    return stats


def compare_projects(django_path: str, flask_path: str):
    """Порівнює структури Django та Flask і виводить таблицю."""

    print("=" * 60)
    print("ПОРІВНЯННЯ СТРУКТУРИ ПРОЄКТІВ")
    print("=" * 60)

    print(f"\n--- Django ({django_path}) ---")

    django_tree = scan_directory(django_path)

    print(f"{django_path}/")
    for line in django_tree:
        print(line)

    django_stats = analyze_project(django_path)

    print(f"\n--- Flask ({flask_path}) ---")

    flask_tree = scan_directory(flask_path)

    print(f"{flask_path}/")
    for line in flask_tree:
        print(line)

    flask_stats = analyze_project(flask_path)

    print("\n" + "=" * 60)
    print("ПОРІВНЯЛЬНА ТАБЛИЦЯ")
    print("=" * 60)

    rows = [
        ("Файли .py", django_stats["py_files"],
         flask_stats["py_files"]),
        ("Файли .html", django_stats["html_files"],
         flask_stats["html_files"]),
        ("Файли .css", django_stats["css_files"],
         flask_stats["css_files"]),
        ("Каталоги", len(django_stats["directories"]),
         len(flask_stats["directories"])),
        ("Розмір (байт)", django_stats["total_size"],
         flask_stats["total_size"]),
    ]

    print(f"{'Характеристика':<22} {'Django':>12} {'Flask':>12}")
    print("-" * 48)

    for name, django_value, flask_value in rows:
        print(f"{name:<22} {django_value:>12} {flask_value:>12}")

    print("\n=== Основні відмінності ===")

    print(
        "Django має стандартну структуру з файлами "
        "settings.py, urls.py, manage.py та окремими додатками."
    )

    print(
        "Flask використовує гнучку структуру, яку розробник "
        "організовує самостійно."
    )

    print(
        "Django містить більше вбудованих компонентів, "
        "а Flask починається з мінімального набору файлів."
    )

    print("\nАналіз завершено успішно.")


def main():
    django_path = "mysite"
    flask_path = "myflaskapp"

    for path in [django_path, flask_path]:
        if not os.path.isdir(path):
            print(
                f"Каталог '{path}' не знайдено. "
                "Спершу виконайте попередні завдання."
            )
            return

    compare_projects(django_path, flask_path)


if __name__ == "__main__":
    main()
