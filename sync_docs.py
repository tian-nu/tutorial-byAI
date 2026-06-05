#!/usr/bin/env python3
"""将各教程源目录的 md 文件同步到 docs/ 下对应子目录，供 MkDocs 构建。"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

# 教程映射：源目录名 → docs/ 子目录名
TUTORIALS = {
    "GO从零到后端教程": "go",
    "Python速成后端教程": "python",
    "java从零到spring boot后端教程": "java",
    "Vue速成前端教程": "vue",
    "数据库精通教程": "database",
    "Docker教程": "docker",
    "Git到GitHub教程": "git",
    "AIcoding从零到精通": "ai-coding",
    "初创互联网团队": "startup",
}

# 需要排除的文件名模式
EXCLUDE_PATTERNS = {"mkdocs.yml", "site", ".gitignore", "build_log.txt", "changelog.md",
                     "detailed_outline.md", "outline.md", "README.md"}


def sync_tutorial(src_dir: Path, dest_dir: Path):
    """将 src_dir 下的 .md 文件复制到 dest_dir/"""
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for f in sorted(src_dir.glob("*.md")):
        if f.name in EXCLUDE_PATTERNS:
            continue
        shutil.copy2(f, dest_dir / f.name)
        count += 1

    # 复制 stylesheets 子目录（如果存在）
    styles_src = src_dir / "stylesheets"
    if styles_src.exists():
        styles_dest = dest_dir / "stylesheets"
        if styles_dest.exists():
            shutil.rmtree(styles_dest)
        shutil.copytree(styles_src, styles_dest)

    print(f"  {src_dir.name} → docs/{dest_dir.name}/ ({count} files)")


def main():
    # 确保 docs/ 存在
    DOCS.mkdir(parents=True, exist_ok=True)

    # 确保 docs/stylesheets/ 存在
    (DOCS / "stylesheets").mkdir(parents=True, exist_ok=True)

    # 复制根目录的 index.md 和 stylesheets/extra.css
    root_index = ROOT / "index.md"
    if root_index.exists():
        shutil.copy2(root_index, DOCS / "index.md")

    root_css = ROOT / "stylesheets" / "extra.css"
    if root_css.exists():
        shutil.copy2(root_css, DOCS / "stylesheets" / "extra.css")

    print("Syncing tutorials:")
    for src_name, dest_name in TUTORIALS.items():
        src_dir = ROOT / src_name
        if not src_dir.exists():
            print(f"  ⚠ {src_name} not found, skipping")
            continue
        sync_tutorial(src_dir, DOCS / dest_name)

    print("Done!")


if __name__ == "__main__":
    main()
