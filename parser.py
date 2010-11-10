###############################################################################
##
##  hardcode_haml - Haml for hardcore coders
##  Copyright (C) 2010  Thammi
## 
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU Affero General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
## 
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU Affero General Public License for more details.
## 
##  You should have received a copy of the GNU Affero General Public License
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
###############################################################################

import re

def is_escaped(value, index):
    cur = index - 1

    if cur < 0:
        return False

    # loop while on a backshlash
    while value[cur] == '\\':
        cur -= 1

        # the end is neigh, let's stop
        if cur < 0:
            break

    # uneven number of backslashs?
    return (index - cur - 1) % 2

def find_unescaped(haystack, needle, start=0):
    last = start

    while True:
        index = haystack.find(needle, last)

        # nothing found
        if index == -1:
            break

        if is_escaped(haystack, index):
            # the needle escaped, let's go on
            last = index + 1
        else:
            # we found the needle
            return index

    return -1

class ParserException(Exception):

    def __init__(self, msg, line=None):
        self.msg = msg
        self.line = line

    def __str__(self):
        if self.line == None:
            return self.msg
        else:
            return "[at line %i] %s" % (self.line, self.msg)

class HamlElement:

    def __init__(self, data, opts, line=None):
        self.opts = opts
        self.line = line
        self.childs = []

        self.parse(data)

    def fail(self, msg):
        raise ParserException(msg, self.line)

    def add_child(self, child):
        self.childs.append(child)

    def option(self, key):
        opts = self.opts

        if key in opts:
            return opts[key]
        else:
            return None

    def write_indent(self, indent, out):
        if self.option('indent'):
            out.write(" " * (indent * 2))

    def exec_childs(self, out, indent):
        for child in self.childs:
            if self.option('debug') and child.line != None:
                out.comment(">> haml line %i started" % child.line)

            child.execute(out, indent)

            if self.option('debug') and child.line != None:
                out.comment("<< haml line %i ended" % child.line)

    def parse(self, data):
        raise NotImplementedError

    def execute(self, out, indent):
        raise NotImplementedError

class ChildlessElement(HamlElement):

    def add_child(self, child):
        self.fail("This element can't contain sub-blocks")

def split_lines(inp):
    for line in inp:
        if line.split():
            yield line

class HamlFile(HamlElement):

    def count_indent(self, line):
        if self.indent_str == None:
            indent = re.match("^\s*", line).group()

            if indent:
                self.indent_str = indent
            else:
                return 0

        count = 0
        cur = line
        indent_len = len(self.indent_str)
        while cur.startswith(self.indent_str):
            count += 1
            cur = cur[indent_len:]

        if cur[0].isspace():
            return -1

        return count

    def parse(self, inp):
        self.manual_declare = False
        stack = [self]

        self.indent_str = None if self.option('auto_indent') else "  "

        actions = {
                '#': XmlTag,
                '%': XmlTag,
                '.': XmlTag,
                '-': Execution,
                '/': Comment,
                '\\': Escape,
                '?': Declaration,
                }

        for line, data in enumerate(split_lines(inp), 1):
            indent = self.count_indent(data)

            if indent == -1:
                raise ParserException("Could not parse indent", line)

            if indent >= len(stack):
                raise ParserException("More than one indent added", line)

            stack = stack[:indent+1]

            content = data.strip()

            start = content[0]
            if start in actions:
                action = actions[start]
            else:
                action = DirectDisplay

            # TODO: still kind of hacky
            if start == '?':
                if self.manual_declare:
                    self.fail("Multiple declarations")
                elif len(stack) > 1:
                    self.fail("Declaration inide a block")
                else:
                    self.manual_declare = True

            element = action(content, self.opts, line)

            stack[-1].add_child(element)
            stack.append(element)

    def execute(self, out, indent=0):
        out.start()

        if not self.manual_declare:
            out.comment("Declaring automatically, no '?' found")
            out.declare([])

        self.exec_childs(out, indent)

        out.finish()

class Declaration(ChildlessElement):

    def parse(self, data):
        if data.strip():
            self.paras = [para.strip() for para in data[1:].split(',')]
        else:
            self.paras = []

    def execute(self, out, indent):
        out.declare(self.paras)

class Comment(HamlElement):

    def parse(self, data):
        self.comment = data[1:].strip()

    def execute(self, out, indent):
        self.write_indent(indent, out)
        out.write("<!--")

        if self.childs:
            if self.content:
                self.fail("No content allowed for nested comments")

            out.write("\n")

            self.exec_childs(out, indent + 1)

            self.write_indent(indent, out)
        else:
            out.write(" ")
            out.write(self.comment)
            out.write(" ")

        out.write("-->\n")

class Execution(HamlElement):

    def parse(self, data):
        self.command = data[1:].strip()

    def execute(self, out, indent):
        if self.childs:
            out.block_exec(self.command)

            self.exec_childs(out, indent)

            out.close_block()
        else:
            self.out.execute(self.command)

class XmlTag(HamlElement):

    def parse(self, data):
        self.attrs = {}
        self.name = 'div'
        self.content = None

        self.data = data

        self.parse_name()
        self.parse_attrs()
        self.parse_content()

    def add_attr(self, key, value):
        attrs = self.attrs

        if key in attrs:
            attrs[key].append(value)
        else:
            attrs[key] = [value]

    def consume_regex(self, regex):
        match = re.match(regex, self.data)

        if match:
            res = match.group()
            self.data = self.data[len(res):]
            return res
        else:
            return ""

    def consume_value(self, stoppers):
        data = self.data
        index = 0

        bracket_depth = 0

        while True:
            if data[index] in stoppers:
                if bracket_depth == 0:
                    break

            if data[index] == '"':
                index = find_unescaped(data, '"', index + 1) + 1
            elif data[index] == "'":
                index = find_unescaped(data, "'", index + 1) + 1
            elif data[index] == '(':
                bracket_depth += 1
                index += 1
            elif data[index] == ')':
                bracket_depth -= 1
                index += 1
            else:
                index += 1

            if bracket_depth < 0:
                self.fail("Unmatched closing bracket")

            if not 0 <= index < len(data):
                self.fail("Error parsing value")

        self.data = data[index:]
        return data[:index]

    def parse_name_part(self):
        return self.consume_regex('\w+')

    def parse_name(self):
        while self.data and self.data[0] not in [' ', '(', '{']:
            type_c = self.data[0]
            self.data = self.data[1:]

            if type_c == '%':
                self.name = self.parse_name_part()
            elif type_c == '#':
                self.add_attr('"id"', '"%s"' % self.parse_name_part())
            elif type_c == '.':
                self.add_attr('"class"', '"%s"' % self.parse_name_part())
            else:
                self.fail("Couldn't parse tag name")

    def parse_attrs(self):
        while self.data and self.data[0] in ['(', '{']:
            if self.data and self.data[0] == '(':
                self.data = self.data[1:]

                while self.data[0] != ')':
                    self.consume_regex("\s*")
                    key = '"%s"' % self.consume_regex("\w+")
                    self.consume_regex("\s*=\s*")
                    value = self.consume_value([' ', ')'])

                    if value and key:
                        self.add_attr(key, value)
                    else:
                        self.fail("Failed to parse the attributes")

                self.data = self.data[1:]

            elif self.data and self.data[0] == '{':
                self.data = self.data[1:]

                while self.data[0] != '}':
                    self.consume_regex("\s*")
                    key = self.consume_value(['='])
                    self.consume_regex("\s*=>\s*")
                    value = self.consume_value([',', '}'])
                    self.consume_regex("\s*,?")

                    if value and key:
                        self.add_attr(key, value)
                    else:
                        self.fail("Failed to parse the attribute")

                self.data = self.data[1:]

    def parse_content(self):
        if self.data.strip():
            self.content = Display(self.data)

    def execute(self, out, indent):
        self.write_indent(indent, out)

        out.write("<%s" % self.name)

        for key, values in self.attrs.iteritems():
            out.write(' ')
            out.evaluate(key)
            out.write('="')
            for index, value in enumerate(values):
                if index > 0:
                    out.write(" ")

                out.evaluate(value)

            out.write('"')

        out.write(">")

        if self.childs:
            if self.content:
                self.fail("No content allowed for nested tags")

            out.write("\n")

            self.exec_childs(out, indent + 1)

            self.write_indent(indent, out)
        else:
            if self.content:
                self.content.execute(out)

        out.write("</%s>\n" % self.name)


class DirectDisplay(ChildlessElement):

    def parse(self, data):
        self.display = Display(data)

    def execute(self, out, indent):
        self.write_indent(indent, out)
        self.display.execute(out)
        out.write("\n")

class Escape(DirectDisplay):

    def parse(self, data):
        self.display = Display(data[1:].rstrip())

class Display:

    def __init__(self, data):
        if data.startswith('='):
            self.evaluate = True

            self.data = data[1:].rstrip()
        else:
            self.evaluate = False
            self.data = data

    def execute(self, out):
        data = self.data

        if self.evaluate:
            self.out.evaluate(self.data)
        else:
            last = 0

            # find evaluation expressions
            while True:
                index = data.find('#{', last)

                if index == -1:
                    break

                end_index = data.find('}', index)

                if end_index == -1:
                    self.fail("Evaluation subexpression not closed.")

                # print everything before the expression
                out.write(data[last:index])

                # process the actual evaluation
                out.evaluate(data[index+2:end_index])

                last = end_index + 1

            # print the end
            out.write(data[last:])

