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

from os.path import join

class PythonWriter:

    def __init__(self, name, directory):
        file_name = join(directory, name + ".py")
        self.out = open(file_name, 'w')
        self.write_buf = []
        self.name = name

    def start(self):
        self.indent = 0

    def finish(self):
        self.flush()

    def declare(self, paras):
        para_str = ', '.join(['out'] + paras)
        fstr = "\ndef {name}({para}):\n"
        self.out.write(fstr.format(name=self.name, para=para_str))
        self.indent += 1

    def evaluate(self, cmd):
        self.execute("out.write(str({cmd}))".format(cmd=cmd))

    def execute(self, cmd):
        self.flush()
        self.out.write("    " * self.indent + cmd + "\n")

    def write(self, data):
        # escape!
        self.write_buf.append(data)

    def flush(self):
        if self.write_buf:
            data = ''.join(self.write_buf)
            self.write_buf = []
            self.execute('out.write({data})'.format(data=repr(data)))

    def conditional_block(self, expression):
        self.block_exec("if {expr}".format(expr=expression))

    def block_exec(self, cmd):
        self.execute(cmd + ":")
        self.indent += 1

    def close_block(self):
        self.flush()
        self.indent -= 1

    def comment(self, data):
        self.flush()
        self.out.write("    " * self.indent + "# " + data + "\n")

