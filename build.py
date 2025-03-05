import os
import argparse
import sys


def generate_directory_index(root_dir, output_file, exclude):
    root_dir = os.path.abspath(root_dir)
    script_path = os.path.abspath(sys.argv[0])
    directories = {}

    # 收集目录结构信息
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 过滤隐藏目录和排除目录
        dirnames[:] = [d for d in dirnames
                       if not d.startswith('.') and d not in exclude]

        # 过滤文件
        valid_files = []
        for f in filenames:
            file_abs = os.path.join(dirpath, f)
            if (f == 'index.md' or
                    file_abs == script_path or
                    f.startswith('.') or
                    f in exclude):
                continue
            valid_files.append(f)

        # 获取相对路径信息
        rel_path = os.path.relpath(dirpath, root_dir)
        depth = rel_path.count(os.sep) if rel_path != "." else 0
        path_parts = rel_path.split(os.sep) if rel_path != "." else []

        # 保存目录信息
        directories[rel_path] = {
            "files": sorted(valid_files),
            "subdirs": sorted(dirnames),
            "depth": depth,
            "path_parts": path_parts
        }

    # 生成目录索引文件
    for rel_path, data in directories.items():
        content = ['# [小树的网盘](https://xiaoshu312.github.io/Files/)\n\n']
        depth = data["depth"]
        current_dir = os.path.join(root_dir, rel_path)

        # 生成面包屑导航（非根目录）
        if rel_path != ".":
            breadcrumb = []
            for i, part in enumerate(data["path_parts"]):
                target_dir = os.path.join(root_dir, *data["path_parts"][:i + 1])
                relative_path = os.path.relpath(
                    target_dir,
                    current_dir
                ).replace(os.sep, '/')
                breadcrumb.append(f"[{part}](<{relative_path}>)")

            heading = "#" * (depth + 2)
            content.append(f"{heading} {' / '.join(breadcrumb)}\n\n")

        # 添加文件列表（隐藏.html扩展名）
        for file in data["files"]:
            # 处理显示名称
            display_name = file.rsplit('.html', 1)[0] if file.endswith('.html') else file
            # 保持原始文件链接
            file_link = file.replace(os.sep, '/')
            content.append(f"- [{display_name}](<{file_link}>)\n")

        # 添加子目录列表（带斜杠）
        for subdir in data["subdirs"]:
            subdir_link = os.path.relpath(
                os.path.join(current_dir, subdir),
                current_dir
            ).replace(os.sep, '/')
            content.append(f"- [{subdir}/](<{subdir_link}>)\n")

        # 确定写入路径
        write_path = os.path.join(root_dir, output_file) if rel_path == "." \
            else os.path.join(current_dir, "index.md")

        # 写入文件
        with open(write_path, "w", encoding="utf-8") as f:
            f.writelines(content)
            print(f"Generated: {write_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="生成隐藏HTML扩展名的目录索引")
    parser.add_argument("--root_dir", default=".",
                        help="根目录路径（默认：当前目录）")
    parser.add_argument("--output", default="index.md",
                        help="根目录索引文件名（默认：index.md）")
    parser.add_argument("--exclude", nargs="*", default=[],
                        help="要排除的文件/目录列表")
    args = parser.parse_args()

    generate_directory_index(
        args.root_dir,
        args.output,
        args.exclude
    )