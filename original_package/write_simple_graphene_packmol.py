import os
if os.path.exists('in.inp'):
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







from re import A, S
# self.data = '43_50_un'
import MDAnalysis


class Dcd2data():
    def __init__(self, data_list):
        self.data_list = data_list

    def dcd2data(self):
        for data_id in self.data_list:
            u = MDAnalysis.Universe(
                data_id+".data", data_id+".dcd", format="LAMMPS")
            # data_id+".data", data_id+".dcd", format="LAMMPS")
            for ts in u.trajectory[-1:]:
                # if take_this_frame == True:
                with MDAnalysis.Writer(data_id+'_un.data') as W:
                    W.write(u.atoms)


class Data2pdb():
    def __init__(self, data):
        self.data = data

    def get_atom(self, line):
        cnt = 0
        for i in line:
            if 'Atoms' in i:
                break
            cnt += 1
        return cnt

    def data2pdb(self):
        fr = open(self.data+".data", 'r')
        line = fr.readlines()
        fr.close()
        cnt = self.get_atom(line)+2
        fw = open(self.data+".pdb", "w")
        Atoms = []
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
        for atom in Atoms:
            atom_id = "{:>7}".format(atom[0])
            mol_id = "{:>3}".format(atom[1])
            atom_type = "{:<5}".format(atom[2])
            atom_charge = "{:<5}".format(atom[3])
            atom_x = "{:>7}".format(str(round(float(atom[4]), 3)))
            atom_y = "{:>7}".format(str(round(float(atom[5]), 3)))
            atom_z = "{:>7}".format(str(round(float(atom[6]), 3)))
            #atom_name = "{:<5}".format((atom[8].strip("\n")).upper())
            data = 'ATOM' + atom_id + ' ' + atom_type + 'POL A ' + \
                mol_id + '     ' + atom_x + ' ' + atom_y + \
                ' '+atom_z + ' ' + " 1.00  0.00  ES"
            fw.write(data+'\n')
        fr.close()
        fw.close()



demo=Data2pdb('graphene_all')
demo.data2pdb()

demo=Dcd2data('final_300K')
demo.dcd2data()

demo=Data2pdb('final_300K_un')
demo.data2pdb()



  

def write_graphene_packmol():
    xlo = None
    xhi = None
    ylo = None
    yhi = None

    # Read the 'final_300K.data' file and extract the values
    with open('final_300K.data', 'r') as data_file:
        for line in data_file:
            if 'xlo' in line:
                xlo, xhi = map(str, line.split()[:2])
            elif 'ylo' in line:
                ylo, yhi = map(str, line.split()[:2])
            elif 'zlo' in line:
                zlo, zhi = map(str, line.split()[:2])
               
    fw = open('simple_graphene_packmol.in', 'w')
    fw.write('tolerance 2.0\nfiletype pdb\noutput simple_graphene.pdb\n\n')
    fw.write('filetype pdb\nstructure ' +
                'graphene_all.pdb\n  number 1\n\n')
    fw.write('  fixed 0.0 0.0 '+zlo+' 0. 0. 0. \nend structure\n')  

    data="""filetype pdb
structure final_300K_un.pdb
  number 1

  fixed 0. 0. 0 0 0 0
end structure
"""  
    fw.write(data)  
if os.path.exists('graphene_all.pdb'):
    demo=write_graphene_packmol()

