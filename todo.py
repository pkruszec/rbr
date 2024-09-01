#!/usr/bin/env python3
#
# Simple TODO grepper.
#
# It prints a file and a line number on one of those cases:
# - the line contains "TODO:" in it (even in strings),
# - the line contains one of AsciiDoc/Markdown style empty checkboxes (like "* [ ]", ". [ ]", "- [ ]").
#
# Copyright (c) 2024 Paweł Kruszec
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import sys
import pathlib
import glob

output = sys.stdout

def usage(program_name):
    print(f"Usage: {program_name} [option] ... [path] ...")
    print(f"  Arguments:")
    print(f"    path          Target file or directory")
    print(f"  Options:")
    print(f"    -h, --help    Print this message and exit")
    print(f"    -o <file>     Output to <file>")
    print(f"    -n, --no-rec  No recursive search")

def has_todo(path: pathlib.Path, line: str) -> bool:
    line = line.lstrip()

    # Markdown/AsciiDoc checkmarks
    if (
        line.startswith("* [ ]") or
        line.startswith(". [ ]") or
        line.startswith("- [ ]")
    ):
        return True
    
    if "TODO:" in line:
        return True

    return False

def print_todo(path: pathlib.Path, line: str, i: int):
    print(f"{path}:{i+1}: {line}", file=output)

def process_file(path: pathlib.Path):
    with open(path, "r", encoding="utf-8-sig") as f:
        try:
            lines = f.readlines()
        except UnicodeDecodeError as e:
            return

    for i, line in enumerate(lines):
        if has_todo(path, line):
            print_todo(path, line.strip(), i)

def traverse(root_path: pathlib.Path, recursive: bool):
    if str(root_path.name).startswith("."):
        return

    for subpath in root_path.iterdir():
        if subpath.is_dir():
            if recursive:
                traverse(subpath, recursive)
        elif subpath.is_file():
            process_file(subpath)

def main():
    program_name, *args = sys.argv

    recursive = True
    paths = [pathlib.Path("./")]
    outfile = None

    options = True
    while args:
        arg, *args = args
        if options:
            if arg == "-h" or arg == "--help":
                usage(program_name)
                exit(0)
                continue
            elif arg == "-n" or arg == "--no-rec":
                recursive = False
                continue
            elif arg == "-o":
                if not args:
                    print("error: expected path, got nothing", file=sys.stderr)
                    exit(1)

                outfile, *args = args
                continue
            else:
                paths.clear()
                options = False

        paths.append(pathlib.Path(arg))

    cwd = pathlib.Path.cwd()
    old_paths = paths
    new_paths = []
    for path in old_paths:
        # this is bad
        globs = [
            pathlib.Path(p)
            for p in
            glob.glob(str(path))
        ]

        new_paths.extend(globs)
    paths = new_paths

    global output

    if outfile is not None:
        output = open(outfile, "w", encoding="utf-8")

    for path in paths:
        if not path.exists():
            print(f"error: path {path} does not exist", file=sys.stderr)

        if path.is_dir():
            traverse(path, recursive)
        elif path.is_file():
            process_file(path)

    output.close()

if __name__ == "__main__":
    main()
