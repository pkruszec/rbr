#!/usr/bin/env python3
#
# Regex Bulk Rename
# Bulk rename files using Python regex patterns.
#
# Having these files in your working directory:
# - Day-20240613.adoc
# - Day-20240614.adoc
# - Day-20240615.adoc
# 
# If you execute the program like that:
#   ./rbr.py "Day-([0-9]{4})([0-9]{2})([0-9]{2}).adoc" "Day-\1-\2-\3.adoc"
# 
# You get these files:
# - Day-2024-06-13.adoc
# - Day-2024-06-14.adoc
# - Day-2024-06-15.adoc
#
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
