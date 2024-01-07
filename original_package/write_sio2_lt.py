
class Write_sio2_lt():
    def __init__(self, layer, fr_list=[], auto_size_list=[]):
        self.fr_list = fr_list
        self.layer = layer
        self.auto_size_list = auto_size_list

    def get_bond_list(self, fr):
        # print('write_sio2_lt.py'+str(self.fr_list))
        fr_list = []
        # fr = open(f, 'r')
        atoms_Si = []
        atoms_O = []
        for line in fr.readlines()[2:]:
            line.strip('\n')
            line = line.split(' ')
            atom_Si = []
            atom_O = []
            if line[0] == 'Si':
                for string in line:
                    if string:
                        atom_Si.append(string)
                atom_Si[1] = float(atom_Si[1])  # x
                atom_Si[2] = float(atom_Si[2])  # y
                atom_Si[3] = float(atom_Si[3])  # z
                atoms_Si.append(atom_Si)
            elif line[0] == 'O':
                for string in line:
                    if string:
                        atom_O.append(string)
                atom_O[1] = float(atom_O[1])  # x
                atom_O[2] = float(atom_O[2])  # y
                atom_O[3] = float(atom_O[3])  # z
                atoms_O.append(atom_O)
        fr_list.append(atoms_Si)
        fr_list.append(atoms_O)

        #print(atoms_O, atoms_Si)

        bond_list = []
        Si_id = 1
        for atom_Si in atoms_Si:
            # other_atoms = atoms.pop(atom)
            atom_Si_x = atom_Si[1]
            atom_Si_y = atom_Si[2]
            atom_Si_z = atom_Si[3]
            bond = 0
            # while bond < 4:
            O_id = 1

            for atom_O in atoms_O:
                atom_O_x = atom_O[1]
                atom_O_y = atom_O[2]
                atom_O_z = atom_O[3]
                # 1.55019 bond_lenth
                distance_x = atom_Si_x-atom_O_x
                distance_y = atom_Si_y-atom_O_y
                distance_z = atom_Si_z-atom_O_z
                distance = (distance_x**2+distance_y**2+distance_z**2)**0.5
                #print(distance)
                if distance < 2:#1.56
                    bond += 1
                    bond_list.append([Si_id, O_id])
                O_id += 1
            Si_id += 1

        return atoms_Si, atoms_O, bond_list

    def write_sio2_inside_lt(self, fw_name_head):
        fr_id = 0
        for f in self.fr_list:
            fr = open(f, 'r')
            lists = Write_sio2_lt.get_bond_list(self, fr)
            atoms_Si = lists[0]
            atoms_O = lists[1]
            bond_list = lists[2]
            # atoms_Si = Write_sio2_lt.get_bond_list(self, fr)[0]
            # atoms_O = Write_sio2_lt.get_bond_list(self, fr)[1]
            # bond_list = Write_sio2_lt.get_bond_list(self, fr)[2]
            # fw_name = 'sio2_membrane_'+str(fr_id+1)+'.lt'
            fw_name = fw_name_head+str(fr_id+1)+'.lt'
            fw = open(fw_name, 'w')
            fw.write(
                'import "compass.lt"\nSiO2_'+str(fr_id+1)+' inherits COMPASS {\n   write("Data Atoms") {\n')
            Si_id = 1
            for Si in atoms_Si:
                atom_id = '{: <5}'.format(str(Si_id))
                Si[1] = '{: <20}'.format(str(Si[1]))
                Si[2] = '{: <20}'.format(str(Si[2]))
                Si[3] = '{: <20}'.format(str(Si[3]))

                Si_id += 1
                fw.write('     $atom:Si'+atom_id +
                         ' $mol:...  @atom:si4z      0.8900       '+str(Si[1])+' '+str(Si[2])+' '+str(Si[3])+'\n')
            O_id = 1
            for O in atoms_O:

                atom_id = '{: <5}'.format(str(O_id))
                O[1] = '{: <20}'.format(str(O[1]))
                O[2] = '{: <20}'.format(str(O[2]))
                O[3] = '{: <20}'.format(str(O[3]))
                O_id += 1
                fw.write('     $atom:O'+atom_id +
                         ' $mol:...  @atom:o2z      -0.4450       '+str(O[1])+' '+str(O[2])+' '+str(O[3])+'\n')
            fw.write("}\n write('Data Bond List') {\n")
            bond_id = 1
            data = ''
            for bond in bond_list:
                id = '{: <5}'.format(str(bond_id))
                bond[0] = '{: <5}'.format(str(bond[0]))
                bond[1] = '{: <5}'.format(str(bond[1]))
                data = '     $bond:b'+str(id)+'  $atom:Si' + \
                    bond[0]+'   $atom:O' + bond[1]+'\n'
                fw.write(data)
                bond_id += 1
            fw.write('}\n}\n')
            fw.close()
            fr_id += 1

    def write_sio2_outside_lt(self, fw_name_head):
        for f in self.fr_list:
            fr = open(f, 'r')
            lists = Write_sio2_lt.get_bond_list(self, fr)
            atoms_Si = lists[0]
            atoms_O = lists[1]
            bond_list = lists[2]
            # atoms_Si = Write_sio2_lt.get_bond_list(self, fr)[0]
            # atoms_O = Write_sio2_lt.get_bond_list(self, fr)[1]
            # bond_list = Write_sio2_lt.get_bond_list(self, fr)[2]
            # fw_name = 'sio2_membrane_'+str(fr_id+1)+'.lt'
            fw_name = fw_name_head+'.lt'
            fw = open(fw_name, 'w')
            fw.write(
                'import "compass.lt"\nSiO2 inherits COMPASS {\n   write("Data Atoms") {\n')
            Si_id = 1
            for Si in atoms_Si:
                atom_id = '{: <5}'.format(str(Si_id))
                Si[1] = '{: <20}'.format(str(Si[1]))
                Si[2] = '{: <20}'.format(str(Si[2]))
                Si[3] = '{: <20}'.format(str(Si[3]))

                Si_id += 1
                fw.write('     $atom:Si'+atom_id +
                         ' $mol:...  @atom:si4z      0.8900       '+str(Si[1])+' '+str(Si[2])+' '+str(Si[3])+'\n')
            O_id = 1
            for O in atoms_O:

                atom_id = '{: <5}'.format(str(O_id))
                O[1] = '{: <20}'.format(str(O[1]))
                O[2] = '{: <20}'.format(str(O[2]))
                O[3] = '{: <20}'.format(str(O[3]))
                O_id += 1
                fw.write('     $atom:O'+atom_id +
                         ' $mol:...  @atom:o2z      -0.4450       '+str(O[1])+' '+str(O[2])+' '+str(O[3])+'\n')
            fw.write("}\n write('Data Bond List') {\n")
            bond_id = 1
            data = ''
            for bond in bond_list:
                id = '{: <5}'.format(str(bond_id))
                bond[0] = '{: <5}'.format(str(bond[0]))
                bond[1] = '{: <5}'.format(str(bond[1]))
                data = '     $bond:b'+str(id)+'  $atom:Si' + \
                    bond[0]+'   $atom:O' + bond[1]+'\n'
                fw.write(data)
                bond_id += 1
            fw.write('}\n}\n')
            fw.close()

    def write_sio2_system_inside_lt(self, system_name):
        fr_id = 0
        sio2_system_inside_list = []
        for f in self.fr_list:
            fw_name = system_name+'_'+str(fr_id+1)+'.lt'
            fw = open(fw_name, 'w')
            # print(f)
            sio2_system_inside_list.append(fw_name)
            # fw.write(
            #     'import "'+f[:-4]+'.lt"\nmembrane_sio2 = new SiO2['+str(self.layer[fr_id])+']\n')
            fw.write(
                'import "sio2_supers_inside_'+str(fr_id+1)+'.lt"\nmembrane_sio2 = new SiO2_'+str(fr_id+1)+' ['+str(self.layer[fr_id])+']\n')

            fw.write('write_once("Data Boundary")')
            data = """{
    -2.98333333     68.61666667 xlo xhi
    -2.98333333     68.61666667 ylo yhi
    -0.298333333     6.861666667 zlo zhi
 }
"""
            fw.write(data)
            fw.close()
            fr_id += 1        #
        # print(sio2_system_inside_list)
        return sio2_system_inside_list

    def write_sio2_system_outside_lt(self, system_name):
        sio2_system_outside_list = []
        for f in self.fr_list:
            fw_name = system_name+'.lt'
            # print(f)
            sio2_system_outside_list.append(fw_name)
            fw = open(fw_name, 'w')
            fw.write(
                'import "'+f[:-4]+'.lt"\nmembrane_sio2 = new SiO2\n')

            fw.write('write_once("Data Boundary")')
            data = '{\n     '+str(self.auto_size_list[0][0])+'     '+str(
                self.auto_size_list[0][1])+' xlo xhi\n     '+str(self.auto_size_list[1][0]+'     '+str(
                    self.auto_size_list[1][1])+' ylo yhi\n     -0.298333333     6.861666667 zlo zhi}\n')
#             data = """{
#     -2.98333333     68.61666667 xlo xhi
#     -2.98333333     68.61666667 ylo yhi
#     -0.298333333     6.861666667 zlo zhi
#  }
# """
            fw.write(data)
            fw.close()
        # print(sio2_system_outside_list)
        return sio2_system_outside_list
        # demo = Write_sio2_lt(['sio2_superss.xyz', 'sio2_super.xyz'])
        # demo.write_sio2_lt()
        # #

    def write_sio2_single_system_inside_lt(self, system_name):
        sio2_single_system_inside_list = []
        fr_id = 0
        for f in self.fr_list:
            fw_name = system_name+'_'+str(fr_id+1)+'.lt'
            fw = open(fw_name, 'w')
            sio2_single_system_inside_list.append(fw_name)
            fw.write(
                'import "sio2_single_inside_'+str(fr_id+1)+'.lt"\nmembrane_sio2 = new SiO2_'+str(fr_id+1)+'\n')

            fw.write('write_once("Data Boundary")')
            data = """{
    -2.98333333     68.61666667 xlo xhi
    -2.98333333     68.61666667 ylo yhi
    -0.298333333     6.861666667 zlo zhi
 }
"""
            fw.write(data)
            fw.close()
            fr_id += 1
        # print(sio2_single_system_inside_list)

        return sio2_single_system_inside_list

    def write_sio2_single_system_outside_lt(self, system_name):
        sio2_single_system_outside_list = []
        for f in self.fr_list:
            fw_name = system_name+'.lt'
            fw = open(fw_name, 'w')
            # print(fw_name)
            sio2_single_system_outside_list.append(fw_name)

            fw.write(
                'import "'+f[:-4]+'.lt"\nmembrane_sio2 = new SiO2\n')

            fw.write('write_once("Data Boundary")')
            data = """{
    -2.98333333     68.61666667 xlo xhi
    -2.98333333     68.61666667 ylo yhi
    -0.298333333     6.861666667 zlo zhi
 }
"""
            fw.write(data)
            fw.close()
        # print(sio2_single_system_outside_list)
        return sio2_single_system_outside_list
