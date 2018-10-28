# -*- coding: utf-8 -*-
import re
# result = re.match(".*?\((.*?)\)","R003(201000)")
result = re.match("(.*?)\(","R003(201000)")
print(result.group(1))
print(type(result))