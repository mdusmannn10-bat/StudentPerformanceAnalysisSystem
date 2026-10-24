import os
import zipfile

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
ZIP_NAME = "StudentPerformanceAnalysisSystem_Submission.zip"
ZIP_PATH = os.path.join(PROJECT_DIR, ZIP_NAME)

# Paths/patterns to exclude from the distributable submission package
EXCLUDED_DIRS = {
    ".venv", "venv", "env", "__pycache__", ".pytest_cache",
    "_backup_pre_audit", ".git", ".idea", ".vscode"
}
EXCLUDED_FILES = {
    ".env", ZIP_NAME, "package_submission.py"
}
EXCLUDED_EXTS = {
    ".pyc", ".pyo", ".pyd", ".log", ".tmp"
}


def should_include(rel_path):
    parts = rel_path.replace("\\", "/").split("/")
    for p in parts:
        if p in EXCLUDED_DIRS:
            return False
    filename = parts[-1]
    if filename in EXCLUDED_FILES:
        return False
    _, ext = os.path.splitext(filename)
    if ext in EXCLUDED_EXTS:
        return False
    return True


def create_submission_zip():
    print(f"Creating clean submission package: {ZIP_NAME} ...")
    included_count = 0

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PROJECT_DIR):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, PROJECT_DIR)

                if should_include(rel_path):
                    zf.write(abs_path, arcname=os.path.join("StudentPerformanceAnalysisSystem", rel_path))
                    included_count += 1

    zip_size_kb = os.path.getsize(ZIP_PATH) / 1024
    print(f"Successfully packaged {included_count} files into {ZIP_NAME} ({zip_size_kb:.2f} KB).")


if __name__ == "__main__":
    create_submission_zip()
