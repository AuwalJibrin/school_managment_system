import os
import re

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def find_missing_templates():
    missing = []
    # Find all templates directories
    template_dirs = [BASE_DIR / 'templates']
    for root, dirs, files in os.walk(BASE_DIR):
        if 'templates' in dirs:
            template_dirs.append(Path(root) / 'templates')

    # Find all views.py
    for root, dirs, files in os.walk(BASE_DIR):
        if 'venv' in root or '.venv' in root or 'env' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Find render(..., 'template.html', ...)
                    # Also find TemplateResponse(..., 'template.html', ...)
                    matches = re.findall(r"render\s*\(\s*[^,]+,\s*['\"]([^'\"]+)['\"]", content)
                    matches += re.findall(r"get_template\s*\(\s*['\"]([^'\"]+)['\"]", content)
                    
                    for match in set(matches):
                        # check if match exists in any template_dir
                        exists = False
                        for td in template_dirs:
                            if (td / match).exists():
                                exists = True
                                break
                        if not exists:
                            missing.append((file_path.relative_to(BASE_DIR), match))
                            
    for f, m in missing:
        print(f"Missing template: {m} (referenced in {f})")

if __name__ == '__main__':
    find_missing_templates()
