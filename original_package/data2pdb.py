from re import A, S
# self.data = '43_50_un'


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
        for line in fr.readlines()[xnt:xnt+3]:
            if line=='\n':
               break
            if 'xlo' in line:
               
               line=line.split(' ')
               x_1=line[0]
               x_2=line[1]
               #print(line)
               x=float(x_2)-float(x_1)
            if 'ylo' in line:
               line=line.split(' ')
               y_1=line[0]
               y_2=line[1]
               y=float(y_2)-float(y_1)
            if 'zlo' in line:
               line=line.split(' ')
               z_1=line[0]
               z_2=line[1]
               z=float(z_2)-float(z_1)
        #print(x,y,z)   
        fr.close()
        #cnt = self.get_atom(line)+2
        #print(cnt,xnt)
        fw = open(self.data+".pdb", "w")
        Atoms = []
        fw.write('CRYST1  '+str(x)+' '+str(y)+' '+str(z)+'  90.00  90.00  90.00 P 1           1\n')
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
        for atom in Atoms[:]:
            #print(atom[2]+'yes')
            
            if atom[2]=='42' or atom[2]=='47':        
               atom[2]='C'
            elif atom[2]=='61':
               atom[2]='Cl'
            elif atom[2]=='80':
               atom[2]='H'
       
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


#demo = Data2pdb('graphene_system_single_outside')
#demo=Data2pdb('tes_un')
#demo.data2pdb()
