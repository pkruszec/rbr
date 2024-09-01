#!/usr/bin/env python3
#
# Combine AsciiDoc files in a directory as one file, sorted by :revdate:.
#
# SEGMENTS
#   There is a mode that uses :segment-mode: variables instead of :revdate:.
#   This allows you to make multiple entries in the generated summary with different dates, but from one source file.
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

import sys
import pathlib
from datetime import datetime
from dataclasses import dataclass

SEGMENT_DATE = ":segment-date: "
REVDATE = ":revdate: "
DATE_FORMAT = "%Y-%m-%d"
DEFAULT_OUTPUT_PATH = "kalendarium.adoc"

DEFAULT_HEADER = """= Kalendarium
:toc2:
:numbered:
"""

@dataclass
class Segment:
    path: pathlib.Path
    title: str | None
    date: datetime
    lines: list[str] | None

def usage(program):
    print(f"Usage: {program} [-r] [-d] [-o <path>] [--use-revdate] [-h <path>] <directories>", file=sys.stderr)
    print(f"    -r               Traverse directories recursively", file=sys.stderr)
    print(f"    -d               Sort the segments in descending order", file=sys.stderr)
    print(f"    -o <path>        Specify the output path", file=sys.stderr)
    print(f"    -h <path>        Specify the document header path (its contents will be appended before the generated text)", file=sys.stderr)
    print(f"    --use-revdate    Use {REVDATE}metadata instead of {SEGMENT_DATE}metadata", file=sys.stderr)

def traverse(files: set[pathlib.Path], directory: pathlib.Path, recursive: bool):
    for path in directory.iterdir():
        if path.is_file() and path.suffix == ".adoc":
            files.add(path)
        elif recursive and path.is_dir():
            traverse(files, path, recursive)

def put_segments(path, f, segments, prefix):
    lines = f.readlines()
    date = None
    content = []
    title = None

    tmp = []

    def commit():
        nonlocal date
        nonlocal content
        if date is not None:
            segment = Segment(path, title, date, content)
            tmp.append(segment)
            date = None
            content = []

    comment_block = False
    
    comment_section = False
    comment_section_block = False
    for i, line_raw in enumerate(lines):
        line = line_raw.strip()

        # Handle BOM if it appears on the first line
        if i == 0:
            line = line.strip(chr(0xFEFF))

        if line.startswith("////"):
            comment_block = not comment_block
        elif line.startswith("[comment]"):
            comment_section = True

        if comment_section:
            if comment_section_block:
                if line == "--":
                    comment_section_block = False
                    comment_section = False
                    
                    if date is not None:
                        content.append(line_raw)

                    continue
            else:
                if line == "--":
                    comment_section_block = True
                if not line:
                    comment_section = False

                    if date is not None:
                        content.append(line_raw)

                    continue
            
        if not (comment_block or comment_section):
            if line.startswith("= ") and title is None:
                title = line[len("= "):]
            
            if line.startswith("include::"):
                return

            if line.startswith(prefix):
                date_str = line[len(prefix):]
                try:
                    parsed = datetime.strptime(date_str, DATE_FORMAT)
                    commit()
                    date = parsed
                except ValueError:
                    print(f"{path}:{i+1}: invalid date format '{date_str}'", file=sys.stderr)
                    pass

        if date is not None:
            content.append(line_raw)

    commit()
    segments += tmp
    
def write_adoc(f, segments, header):
    now_iso = datetime.strftime(datetime.now(), DATE_FORMAT)
    f.write(header)
    f.write(f":revdate: {now_iso}\n\n")
    
    for segment in segments:
        date_fmt = datetime.strftime(segment.date, DATE_FORMAT)
        title_fmt = (
            segment.title
            if segment.title is not None else
            f"`{segment.path.name}`"
        )
        f.write(f"== {date_fmt}, {title_fmt}\n\n")
        f.write(":leveloffset: +1\n\n")
        f.writelines(segment.lines)
        f.write("\n\n")
        f.write(":leveloffset: -1\n\n")
    
def main():
    program, *argv = sys.argv
    if not argv:
        usage(program)
        exit(1)

    recursive = False
    descending = False
    output_path = pathlib.Path(DEFAULT_OUTPUT_PATH)
    header_path = None
    directories = []
    prefix = SEGMENT_DATE
    while argv:
        arg, *argv = argv
        if arg == "--use-revdate":
            prefix = REVDATE
        elif arg == "-r":
            recursive = True
        elif arg == "-d":
            descending = True
        elif arg == "-h":
            if not argv:
                print(f"Error: Expected header path after '-h', got nothing", file=sys.stderr)
                exit(1)
            path, *argv = argv
            header_path = pathlib.Path(path)
        elif arg == "-o":
            if not argv:
                print(f"Error: Expected output path after '-o', got nothing.", file=sys.stderr)
                exit(1)
            path, *argv = argv
            output_path = pathlib.Path(path)
        else:
            path = pathlib.Path(arg)
            if not path.is_dir():
                print(f"Error: '{arg}' is not a directory.", file=sys.stderr)
                exit(1)
            directories.append(path)

    header = DEFAULT_HEADER
    if header_path is not None:
        with open(header_path, "r", encoding="utf-8") as f:
            header = f.read()
            
    files = set()
    for directory in directories:
        traverse(files, directory, recursive)

    segments = []
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            put_segments(path, f, segments, prefix)

    segments.sort(key=lambda s: s.date, reverse=descending)
    with open(output_path, "w", encoding="utf-8") as f:
        write_adoc(f, segments, header)

if __name__ == "__main__":
    main()
