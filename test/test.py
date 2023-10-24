import sys
import random
import string


size = random.randint(0,2^31 - 1)
bytes = [None] * size
for index in range(size):
    rnd = random.randint(32,1114111)
    n = min(size-index,4)
    while(n > 0):
        rnd >>= 1
        n = n - 1 # Integer.size/Byte.size
    # print(chr(rnd))
    bytes[index] = chr(rnd)

# x = 20
# x >>= 1
# x >>=1
# print(chr(488)) 1114111
# x = str(round(tmp,len(str(tmp))-10)) + 'F'
line = ["Version: 1.0"]
version = ["sfddf",'fsddds']
version=version + line
print(version)