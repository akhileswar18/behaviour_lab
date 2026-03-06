from pathlib import Path


REQUIRED = [
    "app/api/main.py",
    "app/dashboard/main.py",
    ".env.example",
]


def test_local_boot_files_exist() -> None:
    root = Path(__file__).resolve().parents[2]
    for rel in REQUIRED:
        assert (root / rel).exists(), f"missing {rel}"
