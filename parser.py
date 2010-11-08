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
                raise ParserException("Unmatched closing bracket", self.line)

            if not 0 <= index < len(data):
                raise ParserException("Error parsing value", self.line)

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
                raise ParserException("Couldn't parse tag name", self.line)

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
                        raise ParserException("Failed to parse the attributes", self.line)

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
                        raise ParserException("Failed to parse the attribute", self.line)

                self.data = self.data[1:]

    def parse_content(self):
        self.content = self.data

class Parser:

    def __init__(self, inp, out, readable=True):
        self.inp = inp
        self.out = out
        self.readable = readable

    def write_indent(self):
        if self.readable:
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
            last = 0

            # find evaluation expressions
            while True:
                index = line.find('#{', last)

                if index == -1:
                    break

                end_index = line.find('}', index)

                if end_index == -1:
                    raise ParserException("Evaluation subexpression not closed.", self.line)

                # print everything before the expression
                self.out.write(line[last:index])

                # process the actual evaluation
                self.out.evaluate(line[index+2:end_index])

                last = end_index + 1

            # print the end
            self.out.write(line[last:])

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
            self.out.write(' ')
            self.out.evaluate(key)
            self.out.write('="')
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
            self.display(tag.content.strip())
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

    def declare(self, line="", pre_indent=False):
        if self.declared:
            raise ParserException("The template was already declared", self.line)
        if pre_indent:
            raise ParserException("Declaration can't include sub-blocks", self.line)

        if self.stack:
            raise ParserException("Can't declare inside a block", self.line)

        if line.strip():
            paras = [para.strip() for para in line.split(',')]
        else:
            paras = []

        self.out.declare(paras)
        self.declared = True

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
        readable = self.readable

        out.start()

        self.indent = 0
        self.stack = stack = []
        self.declared = False

        actions = {
                '#': self.parse_tag,
                '%': self.parse_tag,
                '.': self.parse_tag,
                '-': self.execute,
                '/': self.comment,
                '\\': self.escape,
                }

        for line, pre_indent in self.line_split(self.inp):
            if readable:
                out.comment('syncing the stack')

            self.sync_stack(self.count_indent(line))

            if readable:
                out.comment('Haml line %i' % self.line)

            content = line.strip()

            start = content[0]
            action = actions[start] if start in actions else self.indent_display

            # dirty hack to assure declaration without declaration line
            # TODO: find a better way
            if not self.declared and self.declared not in ['-', '?']:
                self.declare()

            pop_val = action(content, pre_indent)
            stack.append(pop_val)

        if readable:
            out.comment("end of Haml file, clearing stack")
        
        # clear the stack
        self.sync_stack(0)

        # we have to declare, no matter what!
        if not self.declared:
            self.declare()

        out.finish()

