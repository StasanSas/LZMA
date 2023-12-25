from coder import Coder
from decoder import DeCoder


a = \
"""
aaaaaaaaaaaaaaaaaaaaaaaaa
bbbbbbbbbbbbbbbbbbbbbbbbb
aaaaaaaaaaaaaaaaaaaaaaaaa
ccccccccccccccccccccccccc
edededededededededededede
"""
coder = Coder(a)
result = coder.run()
print(len(result))

in_str_2 = ''.join(format(byte, '08b') for byte in result)
decoder = DeCoder(result)
decoded_text = decoder.run()
print(len(decoded_text))
print(decoded_text)