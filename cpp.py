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

class CppWriter:

    def __init__(self, name):
        self.out = open("%s.cpp" % name, 'w')
        self.write_buf = []

        self.name = name

    def start(self):
        self.out.write("#include <iostream>\n\n")
        self.out.write("void %s(std::ostream &out) {\n" % self.name)

        self.indent = 1

    def finish(self):
        self.flush()
        self.out.write("}\n")
        self.out.write("int main() { %s(std::cout); return 0; }\n" % self.name)

    def evaluate(self, cmd):
        self.execute("out << %s" % cmd)

    def execute(self, cmd):
        self.flush()
        self.out.write("\t" * self.indent + cmd + ";\n")

    def write(self, data):
        # escape!
        replacements = [
                ('\\', '\\\\'),
                ('\n', '\\n'),
                ('"', '\\"'),
                ]
        
        for old, new in replacements:
            data = data.replace(old, new)

        self.write_buf.append(data)

    def flush(self):
        if self.write_buf:
            data = ''.join(self.write_buf)
            self.write_buf = []
            self.execute('out << "%s"' % data)

    def block_exec(self, cmd):
        self.flush()
        self.out.write("\t" * self.indent + cmd + " {\n")
        self.indent += 1

    def close_block(self):
        self.flush()
        self.indent -= 1
        self.out.write("\t" * self.indent + "}\n")

    def comment(self, data):
        self.flush()
        self.out.write("\t" * self.indent + "// " + data + "\n")

