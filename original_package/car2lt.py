from asyncore import write
from operator import index


class Car2lt():
    def __init__(self, pc_list, npoly, tes_chain, box_size_list, lbox_size_list, tes=1, linkatom=['C7', 'C8'], mix_style=''):
        self.pc_list = pc_list
        self.npoly = npoly
        self.tes = tes
        self.tes_chain = tes_chain
        self.x = str(box_size_list[0])
        self.y = str(box_size_list[1])
        self.z = str(box_size_list[2])
        self.lx = str(lbox_size_list[0])
        self.ly = str(lbox_size_list[1])
        self.lz = str(lbox_size_list[2])
        self.linkatom = linkatom
        self.mix_style = mix_style

    def write_lts(self):  # write pc_h pc pn pc_t
        # if len(self.mix_style) == 1:
        # 三种单体的lt 文件,某中聚合度的lt文件，单链的lt文件，聚合物的lt文件
        for mon in self.pc_list:
            atoms = []
            bonds = []
            fr1 = open(mon+'.car', 'r')
            for line in fr1.readlines()[4:]:
                atom = []
                new_atom = []
                if 'end' in line:
                    break
                else:
                    line = line.strip('\n')
                    line = line.split(' ')
                    for string in line:
                        if string:
                            new_atom.append(string)
                    atom.append(new_atom[0])  # atom name
                    atom.append(new_atom[1])  # x
                    atom.append(new_atom[2])  # y
                    atom.append(new_atom[3])  # z
                    atom.append(new_atom[6])  # c3a
                    atom.append(new_atom[8])  # charge
                atoms.append(atom)
            fr1.close()
            fr2 = open(mon+'.mdf', 'r')
            for line in fr2.readlines()[21:]:  # 21

                line_bond = []
                line = line.strip('XXXX_1:')
                line = line.strip('\n')
                line = line.split(' ')
                line_bond.append(line[0])
                if line == '\n':
                    break
                new_line = []
                for string in line:
                    if string:
                        new_line.append(string)
                # print(new_line)
                for string in new_line[12:]:

                    if string and '/' in string:
                        end_id = string.index('/')
                        string = string[:end_id]
                        # print(string)
                        line_bond.append(string)
                    else:
                        line_bond.append(string)
                # if new_line:
                #     line_bond.append(new_line[-1])

                bonds.append(line_bond)
                fr2.close()

            new_bonds = []
            for bond in bonds:
                for atom in bond[1:]:
                    new_bond = [bond[0], atom]
                    new_bonds.append(new_bond)
            o_bonds = new_bonds
            for bond in new_bonds:
                atom1 = bond[0]
                atom2 = bond[1]
                bond_id = new_bonds.index(bond)
                for other_bond in new_bonds[bond_id:]:
                    if atom1 == other_bond[1] and atom2 == other_bond[0]:
                        new_bonds.remove(other_bond)
            lt_id = self.pc_list.index(mon)+1

            fw = open('poly_'+str(lt_id)+'.lt', 'w')
            fw.write('import "compass.lt"\n'+mon +
                     ' inherits COMPASS {\n     write("Data Atoms") {\n')
            for atom in atoms:
                # atom: 'C1', '-2.337804414', '2.350235301', '0.089504787', 'c3a', '0.000'
                #     $atom:C1     $mol:...  @atom:c3a        0.000000000       -2.337804317      2.350235224      0.089504786
                data1 = '$atom:'+atom[0]
                data1 = '{:<12}'.format(data1)
                data2 = '$mol:...'
                data3 = '@atom:'+atom[-2]  # 16
                data3 = '{:<16}'.format(data3)
                data4 = atom[-1]
                data4 = '{:>15}'.format(data4)
                data5 = atom[1]
                data5 = '{:>15}'.format(data5)
                data6 = atom[2]
                data6 = '{:>15}'.format(data6)
                data7 = atom[3]
                data7 = '{:>15}'.format(data7)
                fw.write('     '+data1+' '+data2+' '+data3+' ' +
                         data4+' '+data5+' '+data6+' '+data7+'\n')
                # fw.write('     $atom:'+atom[0]+'     $mol:...  @atom:'+atom[-2] +
                #          '        '+atom[1]+'        '+atom[2]+'        '+atom[3]+'\n')
            fw.write("    }\n write('Data Bond List') {\n")
            i = 1
            for bond in new_bonds:
                # $bond:b1  $atom:C1     $atom:C2

                fw.write('     $bond:b'+str(i)+'  $atom:' +
                         bond[0]+'  $atom:'+bond[1]+'\n')
                i += 1
            fw.write('}\n}')
            fw.close()

    # write npoly.lt and tes.lt
    def write_npoly_lt(self):
        for poly in self.npoly:
            npoly_file = 'poly'+str(poly)+'.lt'
            fw = open(npoly_file, 'w')
            for mon in self.pc_list:
                lt_id = self.pc_list.index(mon)+1
                fw.write('import "poly_'+str(lt_id)+'.lt"\n')
            fw.write('\n\n\nPoly'+str(poly)+' inherits COMPASS {\n')

        # 中间单体个数
        # nploy= 10
            fw.write('monomers = new ' +
                     self.pc_list[0]+' ['+str(poly)+'].rot(180,1,0,0).move(1.51,0,0)\n')
            fw.write('delete monomers[0]\ndelete monomers['+str(int(poly)-1)+']\nmonomers[0] = new ' +
                     self.pc_list[0]+'\nmonomers['+str(int(poly)-1)+'] = new '+self.pc_list[-1]+'\n\n')
            fw.write("write('Data Bond List') {\n")
            for i in range(int(poly)-1):
                #                $bond:b1  $atom:monomers[0]/C8 $atom:monomers[1]/C7
                fw.write('         $bond:b'+str(i+1)+'  $atom:monomers['+str(
                    i)+']/'+self.linkatom[1]+' $atom:monomers['+str(i+1)+']/'+self.linkatom[0]+'\n')
            fw.write('}\n}\n')
            fw.close()

        # write tes.lt
            tes_file = 'tes'+poly+'.lt'
            fw = open(tes_file, 'w')
            fw.write('   import "poly'+poly+'.lt"\n   polymer = new Poly_'+str(poly) +
                     '\n   write_once("Data Boundary") {\n     0.0000000  '+self.x+'  xlo xhi\n     0.0000000  '+self.y+'  ylo yhi\n     0.0000000  '+self.z+'  zlo zhi\n }\n')
            fw.close()
    # write mix_npoly.lt

    def write_mix_noly(self):  # get (pc + pn).lt
        fw = open('mix.lt', 'w')
        for mon in self.pc_list:
            lt_id = self.pc_list.index(mon)+1
            fw.write('import "poly_'+str(lt_id)+'.lt"\n')
        fw.write('\n\nPoly_'+self.npoly[0]+' inherits COMPASS {\n')
        fw.write('monomers_'+self.pc_list[0]+' = new '+self.pc_list[0]+'\n')
        for mon in self.pc_list[1:-1]:
            mix_id = self.pc_list.index(mon)-1
            fw.write('monomers_'+mon +
                     ' = new '+mon+' ['+self.mix_style[mix_id]+']\n')
        fw.write('monomers_'+self.pc_list[-1]+' = new '+self.pc_list[-1]+'\n')
        fw.write("\nwrite('Data Bond List') {\n")
        mix_list = []
        for intiger in self.mix_style:
            mix_list.append(int(intiger))
        i = 1
        lt_id = 1
        # atom_id = 0
        fw.write(
            '         $bond:b1  $atom:monomers_'+self.pc_list[0]+'/C8 $atom:monomers_'+self.pc_list[1]+'[0]/C7\n')
        for intiger in mix_list:

            for ii in range(intiger-1):
                fw.write('         $bond:b'+str(i+1) +
                         '  $atom:monomers_'+self.pc_list[lt_id]+'['+str(ii)+']/C8 $atom:monomers_'+self.pc_list[lt_id]+'['+str(ii+1)+']/C7\n')
                i += 1

            if mix_list.index(intiger) == mix_list.index(mix_list[-1]):
                print(mix_list.index(intiger))
                fw.write('         $bond:b'+str(i+1)+'  $atom:monomers_' +
                         self.pc_list[lt_id]+'[' + str(intiger-1)+']/C8 $atom:monomers_'+self.pc_list[lt_id+1]+'/C7\n')
            else:
                fw.write('         $bond:b'+str(i+1)+'  $atom:monomers_' +
                         self.pc_list[lt_id]+'[' + str(intiger-1)+']/C8 $atom:monomers_'+self.pc_list[lt_id+1]+'[0]/C7\n')
            i += 1
            lt_id += 1

        # fw.write('         $bond:b'+str(i+1)+'  $atom:monomers_' +
            # self.pc_list[-2]+'['+str(len(self.pc_list[-2]))+']/C8 $atom:monomers_tile/C7\n')
        fw.write('}\n}\n')
        fw.close()
        for poly in self.npoly:
            tes_file = 'tes'+poly+'.lt'
            fw = open(tes_file, 'w')
            fw.write('   import "mix.lt"\n   polymer = new Poly_'+str(poly) +
                     '\n   write_once("Data Boundary") {\n     0.0000000  '+self.x+'  xlo xhi\n     0.0000000  '+self.y+'  ylo yhi\n     0.0000000  '+self.z+'  zlo zhi\n }\n')
            fw.close()

    def write_npoly_lt(self):
        for poly in self.npoly:
            npoly_file = 'poly'+str(poly)+'.lt'
            fw = open(npoly_file, 'w')
            fw.write()
            for mon in self.pc_list:
                lt_id = self.pc_list.index(mon)+1
                fw.write('import "poly_'+str(lt_id)+'.lt"\n')
            fw.write('\n\n\nPoly'+str(poly)+' inherits COMPASS {\n')

        # 中间单体个数
        # nploy= 10
            fw.write('monomers = new ' +
                     self.pc_list[0]+' ['+str(poly)+'].rot(180,1,0,0).move(1.2533223,0,0)\n')
            fw.write('delete monomers[0]\ndelete monomers['+str(int(poly)-1)+']\nmonomers[0] = new ' +
                     self.pc_list[0]+'\nmonomers['+str(int(poly)-1)+'] = new '+self.pc_list[-1]+'\n\n')
            fw.write("write('Data Bond List') {\n")
            for i in range(int(poly)-1):
                #                $bond:b1  $atom:monomers[0]/C8 $atom:monomers[1]/C7
                fw.write('         $bond:b'+str(i+1)+'  $atom:monomers['+str(
                    i)+']/'+self.linkatom[1]+' $atom:monomers['+str(i+1)+']/'+self.linkatom[0]+'\n')
            fw.write('}\n}\n')
            fw.close()

        # write tes.lt
            tes_file = 'tes'+poly+'.lt'
            fw = open(tes_file, 'w')
            fw.write('   import "poly'+poly+'.lt"\n   polymer = new Poly_'+str(poly) +
                     '\n   write_once("Data Boundary") {\n     0.0000000  '+self.x+'  xlo xhi\n     0.0000000  '+self.y+'  ylo yhi\n     0.0000000  '+self.z+'  zlo zhi\n }\n')
            fw.close()

    def main(self):
        if 'random' in self.mix_style:
            pass
        elif len(self.mix_style) == 1:
            Car2lt.write_lts(self)
            Car2lt.write_npoly_lt(self)
            # print(self.mix_style)
            # Car2lt.write_tes_chain_lt(self)
        else:
            Car2lt.write_lts(self)
            Car2lt.write_mix_noly(self)
            # Car2lt.write_tes_chain_lt(self)

        # Car2lt.write_lts(self)
        # Car2lt.write_npoly_lt(self)
        # Car2lt.write_tes_chain_lt(self)

        # else:

        # demo = Car2lt(pc_list=['pc'], polyn=10, tes_chain=20, box_size_list=[
        #               10, 10, 10], lbox_size_list=[10, 10, 10])
        # # def __init__(self, pc_list, polyn, tes, tes_chain, box_size_list, lbox_size_list):
        # demo.write_lts()
