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

from parser import find_unescaped

def number(value):
    if re.match("[0-9]+(?:\.[0-9]*)$", value):
        return value
    else:
        return None

def string(value):
    if value.startswith('"') and value.endswith('"'):
        raw_str = value[1:-1]
        if find_unescaped(raw_str, '"') == -1:
            return raw_str
        else:
            return None
    else:
        return None

defaults = [number, string]

def find_primitive(value, primitives=defaults):
    for primitive in primitives:
        res = primitive(value)

        if res:
            return res

