#!/usr/bin/env python
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

from cpp import CppWriter

class ParserException(Exception):

    def __init__(self, msg, line=None):
        self.msg = msg
        self.line = line

    def __str__(self):
        if self.line == None:
            return self.msg
        else:
            return "[at line %i] %s" % (self.line, self.msg)

class XmlTag:

    def __init__(self, data, line=None):
        self.attrs = {}
        self.name = 'div'
        self.content = None
        self.line = line

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

    def parse_name_part(self):
        return self.consume_regex('\w+')

    def parse_name(self):
        while self.data and self.data[0] not in [' ', '(', '{']:
            type_c = self.data[0]
            self.data = self.data[1:]

            if type_c == '%':
                self.name = self.parse_name_part()
            elif type_c == '#':
                self.add_attr('id', '"%s"' % self.parse_name_part())
            elif type_c == '.':
                self.add_attr('class', '"%s"' % self.parse_name_part())
            else:
                raise ParserException("Couldn't parse tag name", self.line)

    def parse_attrs(self):
        if self.data and self.data[0] == '(':
            self.data = self.data[1:]

            while self.data[0] != ')':
                self.consume_regex("\s*")
                key = self.consume_regex("\w+")
                self.consume_regex("\s*=\s*")
                value = self.consume_regex("[^)\s]+")

                if value and key:
                    self.add_attr(key, value)
                else:
                    raise ParserException("Failed to parse the attributes", self.line)

            self.data = self.data[1:]
        elif self.data and self.data[0] == '{':
            self.data = self.data[1:]

            while self.data[0] != '}':
                self.consume_regex("\s*")
                key = self.consume_regex("\w+")
                self.consume_regex("\s*(?:=>)\s*")
                value = self.consume_regex('[^,}]+')
                self.consume_regex("\s*,?")

                if value and key:
                    self.add_attr(key, value)
                else:
                    print self.data
                    raise ParserException("Failed to parse the attribute", self.line)

            self.data = self.data[1:]

    def parse_content(self):
        self.content = self.data

class Parser:

    def __init__(self, inp, out_name):
        self.inp = inp
        self.out = CppWriter(out_name)

    def write_indent(self):
        self.out.write(" " * (self.indent * 2))

    def sync_stack(self, to):
        stack = self.stack
        while len(stack) > to:
            fun = stack.pop()
            if fun: fun()

    def count_indent(self, line):
        return len(re.match("^\s*", line).group()) / 2

    def backshift_display(self, line):
        self.indent -= 1
        self.indent_display(line)

    def indent_display(self, line, pre_indent=False):
        self.write_indent()
        self.display(line, pre_indent)
        self.out.write("\n")

    def display(self, line, pre_indent=False):
        if line.startswith('='):
            self.out.evaluate(line[1:].strip())
        else:
            self.out.write(line)

    def escape(self, line, pre_indent):
        self.out.write(line[1:])

    def execute(self, line, pre_indent):
        if pre_indent:
            self.out.block_exec(line[1:].strip())
            return self.out.close_block
        else:
            self.out.execute(line[1:].strip())

    def parse_tag(self, line, pre_indent):
        tag = XmlTag(line, self.line)

        self.write_indent()

        self.out.write("<%s" % tag.name)

        for key, values in tag.attrs.iteritems():
            self.out.write(' %s="' % key)
            for index, value in enumerate(values):
                if index > 0:
                    self.out.write(" ")

                self.out.evaluate(value)

            self.out.write('"')

        self.out.write(">")

        if pre_indent:
            if tag.content:
                raise ParserException("No content allowed for nested tags", self.line)

            self.indent += 1
            self.out.write("\n")
            return lambda: self.backshift_display("</%s>" % tag.name)
        else:
            self.display(tag.content)
            self.out.write("</%s>\n" % tag.name)

    def comment(self, line, pre_indent):
        self.write_indent()
        self.out.write('<!--')

        if pre_indent:
            self.indent += 1
            self.out.write("\n")
            return lambda: self.backshift_display("-->")
        else:
            self.out.write(" %s -->\n" % line[1:].strip())

    def line_split(self, inp):
        last = None
        self.line = 0

        for new in inp:
            if last and last.strip():
                yield (last, self.count_indent(new) > self.count_indent(last))

            last = new
            self.line += 1

        if last and last.strip():
            yield (last, False)

    def parse(self):
        out = self.out

        out.start()

        self.indent = 0
        self.stack = stack = []

        actions = {
                '#': self.parse_tag,
                '%': self.parse_tag,
                '.': self.parse_tag,
                '-': self.execute,
                '/': self.comment,
                '\\': self.escape,
                }

        for line, pre_indent in self.line_split(self.inp):
            self.out.comment('Haml line %i' % self.line)

            self.sync_stack(self.count_indent(line))

            content = line.strip()

            start = content[0]
            action = actions[start] if start in actions else self.indent_display

            pop_val = action(content, pre_indent)
            stack.append(pop_val)

        self.out.comment("End of Haml file")
        
        # clear the stack
        self.sync_stack(0)

        out.finish()

def main(argv):
    Parser(file(argv[0]), 'test').parse()

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])

