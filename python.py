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
        self.out = open(join(directory, "%s.py" % name), 'w')
        self.write_buf = []
        self.name = name

    def start(self):
        self.out.write("def %s(out):\n" % self.name)

        self.indent = 1

    def finish(self):
        self.flush()
        self.out.write("\nif __name__ == '__main__': import sys; %s(sys.stdout)\n" % self.name)

    def evaluate(self, cmd):
        self.execute("out.write(str(%s))" % cmd)

    def execute(self, cmd):
        self.flush()
        self.out.write("    " * self.indent + cmd + "\n")

    def write(self, data):
        # escape!
        self.write_buf.append(repr(data)[1:-1])

    def flush(self):
        if self.write_buf:
            data = ''.join(self.write_buf)
            self.write_buf = []
            self.execute("out.write('%s')" % data)

    def block_exec(self, cmd):
        self.execute(cmd + ":")
        self.indent += 1

    def close_block(self):
        self.flush()
        self.indent -= 1

    def comment(self, data):
        self.flush()
        self.out.write("    " * self.indent + "# " + data + "\n")

