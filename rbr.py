#!/usr/bin/env python3
import os
import sys
import argparse

import re
import pathlib

def get_paths(start_dir: pathlib.Path, recursive: bool):
    return (
        start_dir.rglob("*")
        if recursive
        else start_dir.glob("*")
    )

def main():
    parser = argparse.ArgumentParser(prog="rbr", description="bulk rename files using Python regex patterns")
    parser.add_argument("-r", "--recursive", action="store_true", help="search recursively")
    parser.add_argument("-s", "--start_dir", default="./")
    parser.add_argument("pattern")
    parser.add_argument("replace")
    args = parser.parse_args()

    pattern_str = args.pattern
    pattern = re.compile(pattern_str)
    start_dir = pathlib.Path(args.start_dir)
    replace = args.replace
    recursive = args.recursive

    posix_start_dir = start_dir.as_posix()
    if pattern_str.startswith(posix_start_dir):
        print(f"warning: start directory used in pattern, consider removing {posix_start_dir}/")

    if "\\" in pattern_str:
        print(f"warning: backslashes are not matched as path separators")

    paths = get_paths(start_dir, recursive)

    for path in paths:
        path_matched = path.relative_to(start_dir)

        path_str = path_matched.as_posix()
        if pattern.fullmatch(path_str):
            if path_matched.is_dir():
                print(f"warning: skipping path {path_str}, is a directory")
                continue

            print(path_str)
            new = pathlib.Path(pattern.sub(replace, path_str))

            try:
                abs_src = start_dir.joinpath(path_matched)
                abs_dst = start_dir.joinpath(new)
                abs_src.rename(abs_dst)
            except FileExistsError:
                print(f"error: path {new.as_posix()} already exists")

if __name__ == "__main__":
    exit(main())
