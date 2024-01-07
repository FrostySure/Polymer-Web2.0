from re import A, S
import os
silicon = 0
graphene = 0
# self.data = '43_50_un'
# with open('in.inp', 'r') as infile:
#     for line in infile:
#         parts = line.strip().split('=')
#         if len(parts) != 2:
#             continue
#         key, value = parts[0].strip(), parts[1].strip()
#         if key == 'ncore':
#             ncore = int(value)
#         elif key == 'outfilename':
#             outfilename = value
#         elif key == 'filename':
#             filename = list(map(str, value.split()))
#         elif key == 'npoly':
#             npoly = list(map(str, value.split()))
#         elif key == 'linkatom':
#             linkatom = value.split()  # Split by space to create a list
#         elif key == 'order_nchain':
#             order_nchain = list(map(str, value.split()))
#         elif key == 'disorder_nchain':
#             disorder_nchain = list(map(str, value.split()))
#         elif key == 'lbox':
#             lbox = list(map(str, value.split()))  # Split by space and convert to str
#         elif key == 'step':
#             step = list(map(str, value.split()))  # Split by space and convert to str
#         elif key == 'annealing':
#             annealing = value
#         elif key == 'rise_step':
#             rise_step = str(value)
#         elif key == 'rise_equil_step':
#             rise_equil_step = str(value)
#         elif key == 'down_step':
#             down_step = str(value)
#         elif key == 'down_equil_step':
#             down_equil_step = str(value)
#         elif key == 'anneal_tmp_start':
#             anneal_tmp_start = str(value)
#         elif key == 'anneal_tmp_down':
#             anneal_tmp_down = str(value)
#         elif key == 'silicon':
#             silicon = str(value)
#         elif key == 'graphene':
#             graphene = str(value)
# class Data2pdb():
#     def __init__(self, data):
#         self.data = data

#     def get_atom(self, line):
#         cnt = 0
#         for i in line:
#             if 'Atoms' in i:
#                 break
#             cnt += 1
#         return cnt

#     def data2pdb(self):
#         fr = open(self.data+".data", 'r')
#         line = fr.readlines()
#         fr.close()
#         cnt = self.get_atom(line)+2
#         fw = open(self.data+".pdb", "w")
#         Atoms = []
#         fr = open(self.data+".data", 'r')

#         for line in fr.readlines()[cnt:]:
#             if line == "\n":
#                 break
#             atom = []
#             line = line.split(' ')
#             for string in line:
#                 if string:
#                     atom.append(string)
#             Atoms.append(atom)
#         for atom in Atoms:
#             atom_id = int(atom[0])
#             mol_id = 'MOL'  # Modify as needed
#             atom_type = atom[2]
#             atom_x = round(float(atom[4]), 3)
#             atom_y = round(float(atom[5]), 3)
#             atom_z = round(float(atom[6]), 3)
#             data = f"ATOM  {atom_id:5} {atom_type:<4}{mol_id:<4}A{atom_id:4}{atom_x:12.3f}{atom_y:8.3f}{atom_z:8.3f}  1.00  0.00"
#             fw.write(data+'\n')
#         fr.close()
#         fw.close()
from re import A, S
# self.data = '43_50_un'
element_data = {
    1: "Ag",
    2: "Al",
    3: "Al",
    4: "Al",
    5: "Au",
    6: "Cr",
    7: "Cu",
    8: "Cu",
    9: "Fe",
    10: "Fe",
    11: "Li",
    12: "Li",
    13: "Li",
    14: "Na",
    15: "Na",
    16: "Na",
    17: "K",
    18: "K",
    19: "K",
    20: "Mo",
    21: "Ni",
    22: "Pb",
    23: "Pd",
    24: "Pt",
    25: "Sn",
    26: "Sn",
    27: "W",
    28: "Ar",
    29: "Br",
    30: "Br",
    31: "C",
    32: "C",
    33: "C",
    34: "C",
    35: "C",
    36: "C",
    37: "C",
    38: "C",
    39: "C",
    40: "C",
    41: "C",
    42: "C",
    43: "C",
    44: "C",
    45: "C",
    46: "C",
    47: "C",
    48: "C",
    49: "C",
    50: "C",
    51: "C",
    52: "C",
    53: "C",
    54: "C",
    55: "C",
    56: "C",
    57: "C",
    58: "Ca",
    59: "Ca",
    60: "Cl",
    61: "Cl",
    62: "Cl",
    63: "Cl",
    64: "Cl",
    65: "Cl",
    66: "Cs",
    67: "D",
    68: "D",
    69: "D",
    70: "D",
    71: "D",
    72: "D",
    73: "F",
    74: "F",
    75: "F",
    76: "F",
    77: "F",
    78: "F",
    79: "H",
    80: "H",
    81: "H",
    82: "H",
    83: "H",
    84: "H",
    85: "He",
    86: "I",
    87: "I",
    88: "Kr",
    89: "Mg",
    90: "Mg",
    91: "N",
    92: "N",
    93: "N",
    94: "N",
    95: "N",
    96: "N",
    97: "N",
    98: "N",
    99: "N",
    100: "N",
    101: "N",
    102: "N",
    103: "N",
    104: "N",
    105: "N",
    106: "N",
    107: "N",
    108: "N",
    109: "N",
    110: "N",
    111: "N",
    112: "N",
    113: "Ne",
    114: "O",
    115: "O",
    116: "O",
    117: "O",
    118: "O",
    119: "O",
    120: "O",
    121: "O",
    122: "O",
    123: "O",
    124: "O",
    125: "O",
    126: "O",
    127: "O",
    128: "O",
    129: "O",
    130: "O",
    131: "O",
    132: "O",
    133: "O",
    134: "O",
    135: "O",
    136: "O",
    137: "O",
    138: "O",
    139: "P",
    140: "P",
    141: "Rb",
    142: "S",
    143: "S",
    144: "S",
    145: "S",
    146: "S",
    147: "S",
    148: "S",
    149: "S",
    150: "S",
    151: "S",
    152: "S",
    153: "Si",
    154: "Si",
    155: "Si",
    156: "Si",
    157: "Xe",
    158: "Zn",
    159: "Sr",
    160: "Ba",
    161: "Be",
    162: "Si",
    163: "O",
    164: "O",
    165: "O",
    166: "O",
    167: "O",
    168: "O",
    169: "O",
    170: "O",
    171: "O",
    172: "O",
    173: "O",
    174: "X",
    175: "Sc",
    176: "Y",
    177: "La",
    178: "Ce",
    179: "Nd",
    180: "Eu",
    181: "Eu",
    182: "Gd",
    183: "Tb",
    184: "Ho",
    185: "Yb",
    186: "Lu",
    187: "Th",
    188: "U",
    189: "O",
    190: "O",
    191: "O",
    192: "O",
    193: "O",
    194: "O",
    195: "O",
    196: "O",
    197: "O",
    198: "O",
    199: "O",
    200: "O",
    201: "Ti",
    202: "Ti",
    203: "Ti",
    204: "V",
    205: "V",
    206: "O",
    207: "Cr",
    208: "O",
    209: "Mn",
    210: "Mn",
    211: "O",
    212: "Fe",
    213: "Fe",
    214: "O",
    215: "Co",
    216: "Ni",
    217: "Zn",
    218: "Cu",
    219: "Cu",
    220: "Ge",
    221: "Rb",
    222: "O",
    223: "Zr",
    224: "O",
    225: "Ag",
    226: "O",
    227: "Cd",
    228: "Te",
    229: "O"
}
from re import A, S
# self.data = '43_50_un'
with open('in.inp', 'r') as infile:
    for line in infile:
        parts = line.strip().split('=')
        if len(parts) != 2:
            continue
        key, value = parts[0].strip(), parts[1].strip()
        if key == 'ncore':
            ncore = int(value)
        elif key == 'outfilename':
            outfilename = value
        elif key == 'filename':
            filename = list(map(str, value.split()))
        elif key == 'npoly':
            npoly = list(map(str, value.split()))
        elif key == 'linkatom':
            linkatom = value.split()  # Split by space to create a list
        elif key == 'order_nchain':
            order_nchain = list(map(str, value.split()))
        elif key == 'disorder_nchain':
            disorder_nchain = list(map(str, value.split()))
        elif key == 'lbox':
            lbox = list(map(str, value.split()))  # Split by space and convert to str
        elif key == 'step':
            step = list(map(str, value.split()))  # Split by space and convert to str
        elif key == 'annealing':
            annealing = value
        elif key == 'rise_step':
            rise_step = str(value)
        elif key == 'rise_equil_step':
            rise_equil_step = str(value)
        elif key == 'down_step':
            down_step = str(value)
        elif key == 'down_equil_step':
            down_equil_step = str(value)
        elif key == 'anneal_tmp_start':
            anneal_tmp_start = str(value)
        elif key == 'anneal_tmp_down':
            anneal_tmp_down = str(value)
class Data2pdb():
    def __init__(self, data):
        self.data = data

    def get_atom(self, line):
        cnt = 0
        for i in line:
            if 'Atoms'in i:
                break
            cnt += 1
        return cnt
    def get_box(self,line):
        xnt=0
        for i in line:
            if "xlo xhi" in i:
                break
            xnt += 1
        return xnt
    def data2pdb(self):
        fr = open(self.data+".data", 'r')
        line = fr.readlines()
        fr.close()
        fr = open(self.data+".data", 'r')
        xnt=self.get_box(line)
        cnt=self.get_atom(line)+2
        fr.close()
        fr = open(self.data+".data", 'r')
        # for line in fr.readlines()[xnt:xnt+3]:
        #     if line=='\n':
        #        break
        #     if 'xlo' in line:
               
        #        line=line.split(' ')
        #        x_1=line[0]
        #        x_2=line[1]
        #        #print(line)
        #        x=float(x_2)-float(x_1)
        #     if 'ylo' in line:
        #        line=line.split(' ')
        #        y_1=line[0]
        #        y_2=line[1]
        #        y=float(y_2)-float(y_1)
        #     if 'zlo' in line:
        #        line=line.split(' ')
        #        z_1=line[0]
        #        z_2=line[1]
        #        z=float(z_2)-float(z_1)
        #print(x,y,z)   
        fr.close()
        #cnt = self.get_atom(line)+2
        #print(cnt,xnt)
        fw = open(self.data+".pdb", "w")
        Atoms = []
        # fw.write('CRYST1  '+str(x)+' '+str(y)+' '+str(z)+'  90.00  90.00  90.00 P 1           1\n')
        fr = open(self.data+".data", 'r')

        for line in fr.readlines()[cnt:]:
            if line == "\n":
                break
            atom = []
            line = line.split(' ')
            for string in line:
                if string:
                    atom.append(string)
            Atoms.append(atom)
        Atoms = sorted(Atoms, key=lambda x: int(x[0]))
        for atom in Atoms[:]:
            #print(atom[2]+'yes')
            atom[2]=str(element_data.get(int(atom[2])))
            # if atom[2]=='42' or atom[2]=='47':        
            #    atom[2]='C'
            # elif atom[2]=='61':
            #    atom[2]='Cl'
            # elif atom[2]=='80':
            #    atom[2]='H'
       
            atom_id = "{:>7}".format(atom[0])
            mol_id = "{:>3}".format(atom[1])
            atom_type = "{:<5}".format(atom[2])
            atom_charge = "{:<5}".format(atom[3])
            atom_x = "{:>7}".format(str(round(float(atom[4]), 3)))
            atom_y = "{:>7}".format(str(round(float(atom[5]), 3)))
            atom_z = "{:>7}".format(str(round(float(atom[6]), 3)))
            #atom_name = "{:<5}".format((atom[8].strip("\n")).upper())
            # data = 'ATOM' + atom_id + ' ' + atom_type + 'POL A ' + \
            #     mol_id + '     ' + atom_x + ' ' + atom_y + \
            #     ' '+atom_z + ' ' + " 1.00  0.00  ES"
            #fw.write(data+'\n')
            fw.write("{:6s}{:5d} {:4s} {:3s} {:1s}{:4d}    {:8.3f}{:8.3f}{:8.3f}{:6.2f}{:6.2f}          {:>2s}\n".format(
                "ATOM", int(atom_id), "MOL", "A", " ", 1, float(atom_x), float(atom_y), float(atom_z), 0, 0, atom_type))

        fr.close()
        fw.close()
if os.path.exists('order_system.data'):
    demo = Data2pdb('order_system')
    demo.data2pdb()
if silicon:
    demo = Data2pdb('sio2_single_system_outside')
    demo.data2pdb()
if graphene:
    demo = Data2pdb('graphene_all')
    demo.data2pdb()