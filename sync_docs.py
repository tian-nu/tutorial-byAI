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
    "C语言精通教程": "c",
    "数据库精通教程": "database",
    "Docker精通教程": "docker",
    "Git到GitHub教程": "git",
    "高中数学人教版教程": "math",
    "AIcoding从零到精通": "ai-coding",
    "初创互联网团队": "startup",
}

# 需要排除的文件名模式
EXCLUDE_PATTERNS = {"mkdocs.yml", "site", ".gitignore", "build_log.txt", "changelog.md",
                     "detailed_outline.md", "outline.md", "README.md"}


def sync_tutorial(src_dir: Path, dest_dir: Path):
    """将 src_dir 下的 .md 和 .pages 文件复制到 dest_dir/"""
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    # 先尝试当前目录的 .md 文件
    md_files = list(src_dir.glob("*.md"))
    # 统计递归找到的总 md 数，判断是否用扁平化复制
    all_md = list(src_dir.rglob("*.md"))
    # 如果子目录中有 .md 文件（说明文件分散在子目录中），用扁平化复制
    has_sub_md = any(f.parent != src_dir for f in all_md)
    if has_sub_md:
        for f in all_md:
            if f.parent != src_dir:
                dest_path = dest_dir / f.name
                if not dest_path.exists():
                    shutil.copy2(f, dest_path)
                    count += 1
        for f in md_files:
            if f.name not in EXCLUDE_PATTERNS:
                shutil.copy2(f, dest_dir / f.name)
                count += 1
    else:
        for f in md_files:
            if f.name in EXCLUDE_PATTERNS:
                continue
            shutil.copy2(f, dest_dir / f.name)
            count += 1

    # 复制 .pages 文件（导航排序配置）
    pages_file = src_dir / ".pages"
    if pages_file.exists():
        shutil.copy2(pages_file, dest_dir / ".pages")
        print(f"    + .pages")

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

    # 确保 docs/stylesheets/ 和 docs/javascripts/ 存在
    (DOCS / "stylesheets").mkdir(parents=True, exist_ok=True)
    (DOCS / "javascripts").mkdir(parents=True, exist_ok=True)

    # 复制根目录的 index.md 和 stylesheets/extra.css
    root_index = ROOT / "index.md"
    if root_index.exists():
        shutil.copy2(root_index, DOCS / "index.md")

    # 复制 paths.md
    root_paths = ROOT / "paths.md"
    if root_paths.exists():
        shutil.copy2(root_paths, DOCS / "paths.md")

    # 复制 overrides 目录
    overrides_src = ROOT / "overrides"
    if overrides_src.exists():
        overrides_dest = DOCS / "overrides"
        # 不需要复制到 docs，MkDocs 直接从根目录 overrides/ 读取
        pass

    root_css = ROOT / "stylesheets" / "extra.css"
    if root_css.exists():
        shutil.copy2(root_css, DOCS / "stylesheets" / "extra.css")

    # 复制 javascripts/ 目录（MathJax 配置等）
    js_src = ROOT / "javascripts"
    if js_src.exists():
        js_dest = DOCS / "javascripts"
        for f in js_src.iterdir():
            shutil.copy2(f, js_dest / f.name)

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
