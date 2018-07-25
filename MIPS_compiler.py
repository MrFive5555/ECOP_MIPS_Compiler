import re

def immeStr(imme):
  Iformat = ''
  if imme >= 0:
    Iformat = '{:0>16b}'
  else:
    Iformat = '{:1>16b}'
  imme = (2**16 + imme) % 2**16
  return Iformat.format(imme)

regFormat = '{:0>5b}'
# R
# <op> rd rs rt
def R(instruction):
  m = re.search(r'^([^ ]*) +\$(\d+), *\$(\d+), *\$(\d+)', instruction)
  rd = int(m.group(2))
  rs = int(m.group(3))
  rt = int(m.group(4))
  return regFormat.format(rs) \
    + regFormat.format(rt) \
    + regFormat.format(rd) \
    + '00000000000'

# <op> rs rt immediate
def I(instuction):
  m = re.search(r'^([^ ]*) +\$(\d+), *\$(\d+), *(-?\d+)', instruction)
  rt = int(m.group(2))
  rs = int(m.group(3))
  imme = int(m.group(4))
  return regFormat.format(rs) \
    + regFormat.format(rt) \
    + immeStr(imme)

# <op> address
def J(instruction):
  m = re.search(r'^([^ ]*) +(?:0x)?(\w+)', instruction)
  addr = int(m.group(2), 16)
  return '{:0>26b}'.format(addr >> 2)

# <op> rd rt sa
def sll(instruction):
  m = re.search(r'^([^ ]*) +\$(\d+), *\$(\d+), *(\d+)', instruction)
  rt = int(m.group(2))
  rd = int(m.group(3))
  sa = int(m.group(4))
  return '00000' + regFormat.format(rt) \
    + regFormat.format(rd) + regFormat.format(sa) + '000000'

# <op> rt immediate(rs)
def sw_lw(instruction):
  m = re.search(r'^([^ ]*) +\$(\d+), *(\w+)*\(\$(\d+)\)', instruction)
  rt = int(m.group(2))
  imme = int(m.group(3))
  rs = int(m.group(4))
  return regFormat.format(rs) + regFormat.format(rt) + immeStr(imme)

# <op> rs immediate
def bltz(instuction):
  m = re.search(r'^([^ ]*) +\$(\d+), *(-?\d+)', instruction)
  rs = int(m.group(2))
  imme = int(m.group(3))
  return regFormat.format(rs) + '00000' + immeStr(imme)

# <op> rs
def jr(instruction):
  m = re.search(r'^([^ ]*) +\$(\d+)', instruction)
  rs = int(m.group(2))
  return regFormat.format(rs) + '000000000000000000000'

getType = {
  "add": R,
  "addi": I,
  "sub": R,
  "or": R,
  "ori": I,
  "and": R,
  "sll": sll,
  "slt": R,
  "sltiu": I,
  "sw": sw_lw,
  "lw": sw_lw,
  "beq": I,
  "bltz": bltz,
  "j": J,
  "jr": jr,
  "jal": J,
  "halt": lambda x: '00000000000000000000000000'
}

getFunct = {
  "add"  : '000000',
  "addi" : '000001',
  "sub"  : '000010',
  "or"   : '010010',
  "ori"  : '010000',
  "and"  : '010001',
  "sll"  : '011000',
  "slt"  : '011011',
  "sltiu": '011100',
  "sw"   : '100110',
  "lw"   : '100111',
  "beq"  : '110000',
  "bltz" : '110110',
  "j"    : '111000',
  "jr"   : '111001',
  "jal"  : '111010',
  "halt" : '111111'
}

def compile(instruction):
  ins = re.match(r'^([^ ]*)', instruction).group()
  code = getFunct[ins] + getType[ins](instruction)
  return code[0:8] + ' ' + code[8:16] + ' ' + code[16:24] + ' ' + code[24:32] + '\n'

import sys

if len(sys.argv) != 3:
  print('[Failed]command format: python MIPS_compiler.py <input> <output>')
  exit()

try:
  inputFile = open(sys.argv[1], 'r')
except FileNotFoundError:
  print('the given file "{0}" can\'t be found'.format(sys.argv[1]))
else:
  outputFile = open(sys.argv[2], 'w')
  for instruction in inputFile:
    outputFile.write(compile(instruction))
