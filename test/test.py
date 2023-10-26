import sys
import random
import string
import platform

size = random.randint(0, 2 ^ 31 - 1)
bytes = [None] * size
for index in range(size):
    rnd = random.randint(32, 1114111)
    bytes[index] = str(chr(rnd))
string = ''.join(bytes)
print(string)


# list =['s','a','v']
# string = ''.join(list)
# print(type(list))


# print(chr(1114111)) 
# x = str(round(tmp,len(str(tmp))-10)) + 'F'
# line = "Version: 1.0"
# version = float(line[line.index("Version: ") + 9:])
# # version=version + line
# print(version)
# if version == 1.0:
#     print(sys.platform)