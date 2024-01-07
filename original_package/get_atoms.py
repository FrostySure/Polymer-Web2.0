fr = open('atoms.txt', 'r')
fw = open('atoms.data', 'w')
#  @atom:ag_m  Ag  "silver, metal"  (ver=2.1, ref=1)
atoms = []

for line in fr:
    line = line.split(' ')
    atom = []
    for string in line:
        if string:
            atom.append(string)
    atoms.append(atom[2])
for atom in atoms:
    fw.write(atom+' ')
fw.write('\n')
# for i in range(229):
#     fw.write('C ')
print(len((atoms)))
fr.close()

fr = open('suppot.data', 'r')
support = []
for line in fr:
    if line != '\n':
        # line = line.strip('\n')
        atom = ''
        for string in line:
            if string and string != '\n':
                # print(string)
                atom += string
        support.append(atom)
for atom in support:
    fw.write(atom+' ')
fw.close()
# print(support)
for atom in atoms:
    if atom not in support:
        print(atom, end=' ')
print('\n')
for atom in atoms:
    if atom in support:
        print(atom, end=' ')
