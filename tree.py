from pathlib import Path

EXCLUDED = {
    "venv",
    ".venv",
    "__pycache__",
}

def print_tree(path: Path, prefix=""):
    entries = sorted(
        [p for p in path.iterdir() if p.name not in EXCLUDED],
        key=lambda p: (p.is_file(), p.name.lower())
    )

    for i, entry in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "

        print(prefix + connector + entry.name)

        if entry.is_dir():
            extension = "    " if i == len(entries) - 1 else "│   "
            print_tree(entry, prefix + extension)


print_tree(Path("."))