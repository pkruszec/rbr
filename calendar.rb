#!/usr/bin/env ruby
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

require "pathname"
require "date"

Doc = Struct.new(:text, :revdate)
Revdate = ":revdate: "

def process_file(path, docs)
  comment_block = false
  comment_section = false
  comment_section_block = false

  doc = Doc.new("", DateTime.new)

  File.open(path, "r:bom|utf-8") do |input|
    input.each_line.with_index do |raw_line, index|
      line = raw_line.strip
      if line == "////"
        comment_block = !comment_block
      elsif line == "[comment]"
        comment_section = true
      elsif comment_section
        if line == "--"
          if !comment_section_block
            comment_section_block = true
          else
            comment_section_block = false
            comment_section = false
          end
        elsif line == ""
          if !comment_section_block
            comment_section = false
          end
        end
      end

      comment = comment_block || comment_section
      should_append = true

      if !comment
        if line.start_with?("include::")
          return
        end

        if line.start_with?(Revdate)
          str = line[Revdate.length..]
          begin
            doc.revdate = DateTime.parse(str)
          rescue Date::Error
            puts "warning: could not parse date \"#{str}\""
          end
        end
      end

      if should_append
        doc.text << line
        doc.text << "\n"
      end
    end
  end

  docs << doc
end

def traverse(path, docs)
  path.children.collect do |child|
    if child.file? and child.extname == ".adoc"
      process_file(child, docs)
    elsif child.directory?
      traverse(child, docs)
    end
  end
end

def usage
  puts "usage: calendar [-h|--help] [-o <path>] [--header <path>] <src_path>"
  puts "  -h, --help    print this and exit"
  puts "  -o            output path"
  puts "  --header      header path (the text will be inserted at the beginning of the file)"
end

args = ARGV

src_path = nil
out_path = "calendar.adoc"
header_path = nil
footer_path = nil

while args.count > 0
  arg, *args = args
  if arg == "-h" || arg == "--help"
    usage
    exit
  elsif arg == "-o"
    if args.count <= 0
      puts "error: expected path after -o"
      exit
    end
    out_path, *args = args
  elsif arg == "--header"
    if args.count <= 0
      puts "error: expected path after --header"
      exit
    end
    header_path, *args = args
  elsif arg == "--footer"
    if args.count <= 0
      puts "error: expected path after --footer"
      exit
    end
    footer_path, *args = args
  else
    src_path = arg
  end
end

if src_path.nil?
  puts "error: source path not provided"
  usage
  exit
end

header = "= Calendar\n\n"
if !header_path.nil?
  header = File.read(header_path)
end

footer = ""
if !footer_path.nil?
  footer = File.read(footer_path)
end

docs = []
traverse(Pathname.new(src_path), docs)
docs.sort_by! {|doc| doc.revdate}

File.open(out_path, "w") do |f|
  f.write(header)
  f.write("\n\n:leveloffset: +1\n\n")

  docs.reverse_each do |doc|
    f.write(doc.text)
    f.write("\n\n")
  end

  f.write("\n\n:leveloffset: -1\n\n")
  f.write(footer)
end
