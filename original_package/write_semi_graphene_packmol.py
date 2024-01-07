import os
if os.path.exists('in.inp'):
    nchain=0
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
            elif key == 'nchain':
                nchain = list(map(str, value.split()))
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
def write_packmol(disorder_nchain):
    xlo = None
    xhi = None
    ylo = None
    yhi = None
    if os.path.exists('order_system.data'):
    # Read the 'order_system.data' file and extract the values
        with open('order_system.data', 'r') as data_file:
            for line in data_file:
                if 'xlo' in line:
                    xlo, xhi = map(str, line.split()[:2])
                elif 'ylo' in line:
                    ylo, yhi = map(str, line.split()[:2])
    elif os.path.exists('sio2_single_system_outside.data') and os.path.exists('graphene_all.data'):
        with open('sio2_single_system_outside.data', 'r') as data_file:
            for line in data_file:
                if 'xlo' in line:
                    sio2_xlo, sio2_xhi = map(str, line.split()[:2])
                elif 'ylo' in line:
                    sio2_ylo, sio2_yhi = map(str, line.split()[:2])

        with open('graphene_all.data', 'r') as data_file:
            for line in data_file:
                if 'xlo' in line:
                    gra_xlo, gra_xhi = map(str, line.split()[:2])
                elif 'ylo' in line:
                    gra_ylo, gra_yhi = map(str, line.split()[:2])
        xlo=str(max(float(sio2_xlo),float(gra_xlo)))
        xhi=str(max(float(sio2_xhi),float(gra_xhi)))
        ylo=str(max(float(sio2_ylo),float(gra_ylo)))
        yhi=str(max(float(sio2_yhi),float(gra_yhi)))

    elif os.path.exists('sio2_single_system_outside.data'):
        with open('sio2_single_system_outside.data', 'r') as data_file:
            for line in data_file:
                if 'xlo' in line:
                    xlo, xhi = map(str, line.split()[:2])
                elif 'ylo' in line:
                    ylo, yhi = map(str, line.split()[:2])
    elif os.path.exists('graphene_all.data'):
        with open('graphene_all.data', 'r') as data_file:
            for line in data_file:
                if 'xlo' in line:
                    xlo, xhi = map(str, line.split()[:2])
                elif 'ylo' in line:
                    ylo, yhi = map(str, line.split()[:2])  

    fw = open('packmol.in', 'w')
    fw.write('tolerance 2.0\nfiletype pdb\noutput system.pdb\n\n')
    fw.write('filetype pdb\nstructure ' +
                'tes_un.pdb\n  number '+str(disorder_nchain[0])+'\n\n')
    fw.write('  inside box '+xlo+' '+ylo+' 0. ' +
                xhi+' '+yhi+' '+'1000\nend structure\n')     
if not nchain:    
    demo=write_packmol(disorder_nchain=disorder_nchain)
if nchain:
    demo=write_packmol(disorder_nchain=nchain)



from re import A, S
# self.data = '43_50_un'


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
