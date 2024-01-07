from asyncore import write
from operator import index
import random
import numpy as np
import os

class Car2lt():
    def __init__(self, pc_list, npoly, tes_chain, box_size_list, lbox_size_list, mix_style, tes=1, linkatom=['C8', 'C7'], output_file='tes', chain_style='order',cube_size=100):
        self.pc_list = pc_list
        self.npoly = npoly
        self.tes = tes
        self.tes_chain = tes_chain
        self.x = '{: >5}'.format(box_size_list[0])
        self.y = '{: >5}'.format(box_size_list[1])
        # str(box_size_list[2])
        self.z = '{: >5}'.format(box_size_list[2])
        # str(lbox_size_list[0])
        self.lx = '{: >5}'.format(str(lbox_size_list[0]))
        # str(lbox_size_list[1])
        self.ly = '{: >5}'.format(str(lbox_size_list[1]))
        # str(lbox_size_list[2])
        self.lz = '{: >5}'.format(str(lbox_size_list[2]))
        self.linkatom = linkatom
        self.mix_style = mix_style
        self.output_file = output_file
        self.chain_style = chain_style
        self.chain_order_move = 6
        self.cube_size=cube_size

 

    def rand_wk(self, num_steps, num_chains, cube_size, step_size):
        def is_within_cube(position, monomers, cube_size):
            for monomer in monomers:
                if np.all(np.abs(position - monomer) <= cube_size):
                    return True
            return False

        chains = []
        # for _ in range(num_chains):
        chain = np.zeros((num_steps + 1, 3))  # 存储每个单体的坐标
        chain[0] = np.random.uniform(low=-cube_size, high=cube_size, size=3)  # 随机选择初始位置

        for i in range(1, num_steps):
            valid_step = False
            while not valid_step:
                step = np.random.uniform(0, step_size)  # 随机生成步长
                angles = np.random.uniform(0, np.pi/2, 3)  # 随机生成三个角度
                direction = np.array([np.sin(angles[0])*np.cos(angles[1]),
                                    np.sin(angles[0])*np.sin(angles[1]),
                                    np.cos(angles[0])])  # 生成随机方向
                displacement = step * direction  # 计算位移向量
                new_position = chain[i-1] + displacement  # 计算新位置
                # valid_step = True
                # chain[i] = new_position

                # if np.all(np.abs(new_position) <= cube_size):  # 检查新位置是否在立方体内
                within_space = True
                for j in range(i):
                    cube_position = chain[j]  # 之前位置的1立方单位的位置
                    distance = np.linalg.norm(new_position - cube_position)  # 计算新位置与之前位置的距离
                    if distance < 3:  # 判断距离是否小于3个单位
                        within_space = False
                        break
                if within_space:
                    # 检查新位置与其他链的单体的距离
                    for other_chain in chains:
                        for other_position in other_chain:
                            distance = np.linalg.norm(new_position - other_position)
                            if distance < 3:  # 判断距离是否小于3个单位
                                within_space = False
                                break
                        if not within_space:
                            break
                if within_space:
                    valid_step = True
                    chain[i] = new_position

        chains.append(chain)
        return chains







    def write_lts(self):  # write pc_h pc pn pc_t
        # print(self.pc_list)
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
                for string in new_line[12:]:

                    if string and '/' in string:
                        end_id = string.index('/')
                        string = string[:end_id]
                        line_bond.append(string)
                    else:
                        line_bond.append(string)
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
            fw.write("    }\n write('Data Bond List') {\n")
            i = 1
            for bond in new_bonds:
                # $bond:b1  $atom:C1     $atom:C2

                fw.write('     $bond:b'+str(i)+'  $atom:' +
                         bond[0]+'  $atom:'+bond[1]+'\n')
                i += 1
            fw.write('}\n}')
            fw.close()

    # write mix_npoly.lt

    def write_mix_npoly_lt(self):  # get (pc + pn).lt
        npoly_id = 0
        # print('he')

        for poly in self.mix_style:
            lt_file = 'poly'+self.npoly[npoly_id]+'.lt'
            fw = open(lt_file, 'w')
            for mon in self.pc_list:
                lt_id = self.pc_list.index(mon)+1
                fw.write('import "poly_'+str(lt_id)+'.lt"\n')
            fw.write('\n\nPoly_'+self.npoly[npoly_id]+' inherits COMPASS {\n')
# 链首
            fw.write(' push(move(0,0,0))\npop()\n')
            mon_id = 1
            rot_id = 102.7797
            single_id = 1
            rotvv = ''
            move = ''
            rotvv_3 = 1
            for i in range(2):
                rotvv_n = random.uniform(-rotvv_3, rotvv_3)
                rotvv = rotvv+str(rotvv_n)+','
                rotvv_3 = rotvv_3-rotvv_n**2
            rotvv_3 = str(rotvv_3**0.5)
            rotvv = rotvv+rotvv_3
#                rotvv = rotvv+str(random.random())+','
            for i in range(3):
               # move = move + str(random.random())+','
                move = move+str(random.uniform(-1, 1))+','
            # fw.write(' push(rotvv(1,0,0,0,0,1))\n')
            fw.write(' push(rotvv(1,0,0,'+rotvv+'))\n')
            fw.write(' push(move('+move[:-1]+'))\n')
            fw.write(' mon[0] = new '+self.pc_list[0] +
                     '.scale(1,0.8,0.8).rot(0.0,1.0,0.0,0.0)\n')
            #  '.scale(1,0.8,0.8).rot('+str((mon_id*102.7797))+',1.0,0.0,0.0)\n')
# 链中
            for single_num in poly:  # ['9','10']
                # print(single_num)
                for mon in range(int(single_num)):
                    move = ''
                    rotvv_t = ''
                    rotvv_3 = 1
                    for i in range(2):
                        rotvv_n = random.uniform(-rotvv_3, rotvv_3)
                        rotvv_t = rotvv_t+str(rotvv_n)+','
                        rotvv_3 = rotvv_3-rotvv_n**2
                    rotvv_3 = str(rotvv_3**0.5)
                    rotvv_t = rotvv_t+rotvv_3
                    for i in range(3):
                        move = move + str(random.uniform(-1, 1))+','
                       # move = move+str(random.uniform(-1, 0))+','
                    fw.write(' push(rotvv('+rotvv+','+rotvv_t+'))\n')
                    fw.write(' push(move('+move[:-1]+'))\n')
                    fw.write(' mon['+str(mon_id)+'] = new '+self.pc_list[single_id] +
                             '.scale(1,0.8,0.8).rot('+str(mon_id*102.7797)+',1.0,0.0,0.0)\n')

                    rotvv = rotvv_t
                    mon_id += 1
                    rot_id += 102.7797
                single_id += 1
            # 最后一个单体

            move = ''
            rotvv_t = ''

            rotvv_3 = 1
            for i in range(2):
                rotvv_n = random.uniform(-rotvv_3, rotvv_3)
                rotvv_t = rotvv_t+str(rotvv_n)+','
                rotvv_3 = rotvv_3-rotvv_n**2
            rotvv_3 = str(rotvv_3**0.5)
            rotvv_t = rotvv_t+rotvv_3
#                rotvv_t = rotvv_t+str(random.random())+','
            for i in range(3):
                move = move + str(3*random.random())+','
             # move = move+str(random.uniform(, 0))+','
            # print(rotvv+rotvv_t[:-1])
            fw.write(' push(rotvv('+rotvv+','+rotvv_t+'))\n')
            fw.write(' push(move('+move[:-1]+'))\n')
            fw.write(' mon['+str(mon_id)+'] = new '+self.pc_list[-1] +
                     '.scale(1,0.8,0.8).rot('+str(mon_id*rot_id)+',1.0,0.0,0.0)\n')
            for i in range(int(self.npoly[0])):
                fw.write(' pop()\n')
            fw.write("\nwrite('Data Bond List') {\n")

            i = 1
            lt_id = 1
            for i in range(int(self.npoly[npoly_id])-1):
                fw.write('         $bond:b'+str(i+1)+'  $atom:mon['+str(
                    i)+']/'+self.linkatom[0]+'  $atom:mon['+str(i+1)+']/'+self.linkatom[1]+'\n')

            fw.write('}\n}\n')
            fw.close()
            npoly_id += 1
        for poly in self.npoly:
            poly_n_file = 'tes'+str(poly)+'.lt'
            # tes_file = self.output_file+poly+'.lt'
            # print(poly_n_file)
            fw = open(poly_n_file, 'w')
            fw.write('   import "poly'+str(poly)+'.lt"\n   polymer = new Poly_'+str(poly) +
                     '\n   write_once("Data Boundary") {\n     0.0000000  '+self.x+'  xlo xhi\n     0.0000000  '+self.y+'  ylo yhi\n     0.0000000  '+self.z+'  zlo zhi\n }\n')
            fw.close()
            npoly_id += 1

    def write_order_mix_npoly_lt(self):  # get (pc + pn).lt
        npoly_id = 0
        # print('he')

        for poly in self.mix_style:
            lt_file = 'poly'+self.npoly[npoly_id]+'.lt'
            fw = open(lt_file, 'w')
            for mon in self.pc_list:
                lt_id = self.pc_list.index(mon)+1
                fw.write('import "poly_'+str(lt_id)+'.lt"\n')
            fw.write('\n\nPoly_'+self.npoly[npoly_id]+' inherits COMPASS {\n')

            mon_id = 1
            single_id = 1
            fw.write(' mon[0] = new '+self.pc_list[0] + '\n')
            # print(len(poly), poly)
            if len(poly) > 1:

                for single_num in poly:  # ['9','10']
                    fw.write(' mon['+str(mon_id)+'] = new '+self.pc_list[single_id] +
                             '.rot('+str(180*mon_id)+',1.0,0.0,0.0).move('+str(float(self.chain_order_move)*mon_id)+',0,0)\n')
                    for mon in range(int(single_num)):
                        # fw.write(' mon['+str(mon_id)+'] = new '+self.pc_list[single_id] +
                        #          '.rot('+str(180*mon_id)+',1.0,0.0,0.0).move('+str(float(self.chain_order_move)*mon_id)+',0,0)\n')

                        mon_id += 1
                    single_id += 1
            # 最后一个单体
            fw.write(' mon['+str(mon_id)+'] = new '+self.pc_list[-1] +
                     '.rot('+str(180*mon_id)+',1.0,0.0,0.0).move('+str(float(self.chain_order_move)*mon_id)+',0,0)\n')

            fw.write("\nwrite('Data Bond List') {\n")

            i = 1
            lt_id = 1
            # atom_id = 0
            for i in range(int(self.npoly[npoly_id])-1):
                # $bond:b1  $atom:mon[0]/C7  $atom:mon[1]/C8
                fw.write('         $bond:b'+str(i+1)+'  $atom:mon['+str(
                    i)+']/'+self.linkatom[0]+'  $atom:mon['+str(i+1)+']/'+self.linkatom[1]+'\n')

            fw.write('}\n}\n')
            fw.close()
            npoly_id += 1
        for poly in self.npoly:
            poly_n_file = 'tes'+str(poly)+'.lt'
            # tes_file = self.output_file+poly+'.lt'
            # print(poly_n_file)
            fw = open(poly_n_file, 'w')
            fw.write('   import "poly'+str(poly)+'.lt"\n   polymer = new Poly_'+str(poly) +
                     '\n   write_once("Data Boundary") {\n     0.0000000  '+self.x+'  xlo xhi\n     0.0000000  '+self.y+'  ylo yhi\n     0.0000000  '+self.z+'  zlo zhi\n }\n')
            fw.close()
            npoly_id += 1

    def write_npoly_lt(self):
        for poly in self.npoly:  # ['40', '50'] #poly40.lt poly50.lt 聚合度为n的单链前体
            # print(poly)
            npoly_file = 'poly'+str(poly)+'.lt'
            fw = open(npoly_file, 'w')
            # fw.write()
            for mon in self.pc_list:
                lt_id = self.pc_list.index(mon)+1
                fw.write('import "poly_'+str(lt_id)+'.lt"\n')
            fw.write('\n\n\nPoly_'+str(poly)+' inherits COMPASS {\n')
            # mon[0]
            fw.write(' push(move(0,0,0))\npop()\n')
            mon_id = 1
            rot_id = 102.7797
            rotvv = ''
            move = ''
            for i in range(6):
                rotvv = rotvv+str(random.random())+','
            for i in range(3):
                move = move+str(random.random())+','
            fw.write(' push(rotvv('+rotvv[:-1]+'))\n')
            fw.write(' push(move('+move[:-1]+'))\n')
            fw.write(' mon[0] = new '+self.pc_list[0] +
                     '.scale(1,0.8,0.8).rot(0.0,1.0,0.0,0.0)\n')
            # mon[1:-1]
            for m in range(int(poly)-2):
                rotvv = ''
                move = ''
                for i in range(6):
                    rotvv = rotvv+str(0.1*random.random())+','
                for i in range(3):
                    move = move+str(random.random())+','
                fw.write(' push(rotvv('+rotvv[:-1]+'))\n')
                fw.write(' push(move('+move[:-1]+'))\n')
                fw.write(' mon['+str(mon_id)+'] = new '+self.pc_list[1] +
                         '.scale(1,0.8,0.8).rot('+str(rot_id)+',1.0,0.0,0.0)\n')
                mon_id += 1
                rot_id += 102.7797

            # mon[-1]
            rotvv = ''
            move = ''
            for i in range(6):
                rotvv = rotvv+str(random.random())+','
            for i in range(3):
                move = move+str(random.random())+','
            fw.write(' push(rotvv('+rotvv[:-1]+'))\n')
            fw.write(' push(move('+move[:-1]+'))\n')
            fw.write(' mon['+str(mon_id)+'] = new '+self.pc_list[-1] +
                     '.scale(1,0.8,0.8).rot('+str(rot_id)+',1.0,0.0,0.0)\n')
            # for i in range(int(poly)):
            #    fw.write(' pop()\n')
            fw.write("write('Data Bond List') {\n")
            for i in range(int(poly)-1):
                #                $bond:b1  $atom:monomers[0]/C8 $atom:monomers[1]/C7
                fw.write('         $bond:b'+str(i+1)+'  $atom:mon['+str(
                    i)+']/'+self.linkatom[0]+' $atom:mon['+str(i+1)+']/'+self.linkatom[1]+'\n')
            fw.write('}\n}\n')
            fw.close()

        # write tes.lt
            tes_file = self.output_file+str(poly)+'.lt'
            fw = open(tes_file, 'w')
            fw.write('   import "poly'+poly+'.lt"\n   polymer = new Poly_'+str(poly) +
                     '\n   write_once("Data Boundary") {\n     0.0000000  '+self.x+'  xlo xhi\n     0.0000000  '+self.y+'  ylo yhi\n     0.0000000  '+self.z+'  zlo zhi\n }\n')
            fw.close()

    def write_order_npoly_lt(self):
            if len(self.npoly)>1:
                poly=str(sum([int(x)  for x in self.npoly])+2)
            else:
                poly=str(sum([int(x)  for x in self.npoly]))
            
        # for poly in self.npoly:  # ['40', '50'] #poly40.lt poly50.lt 聚合度为n的单链前体
            chains=self.rand_wk(num_steps=int(poly),num_chains=1,cube_size=self.cube_size,step_size=self.chain_order_move)#    def rand_wk(self,num_steps, num_chains, cube_size,step_size):
            
            # chains=self.rand_wk(num_steps=int(self.npoly[0]),num_chains=1,cube_size=self.cube_size,step_size=self.chain_order_move)#    def rand_wk(self,num_steps, num_chains, cube_size,step_size):
            # print(self.npoly[0],self.tes_chain[0])
            # print(poly)
            # chains=self.rand_wk(num_steps=int(self.npoly[0]),num_chains=self.tes_chain[0],cube_size=self.cube_size,step_size=self.chain_order_move)#    def rand_wk(self,num_steps, num_chains, cube_size,step_size):
            # chain=chains[0]#1.51#,gap=3
            # chains=self.rand_wk(num_steps=int(self.npoly[0]),num_chains=self.tes_chain[0],square_size=self.cube_size,step_size=self.chain_order_move)#    def rand_wk(self,num_steps, num_chains, cube_size,step_size):
            #num_steps, num_chains, square_size, step_size
            # print(self.cube_size)
            npoly_file = 'poly'+str(poly)+'.lt'
            fw = open(npoly_file, 'w')
            for mon in self.pc_list:
                lt_id = self.pc_list.index(mon)+1
                fw.write('import "poly_'+str(lt_id)+'.lt"\n')
            fw.write('\n\n\nPoly_'+str(poly)+' inherits COMPASS {\n')
            # mon[0]
            fw.write(' push(move(0,0,0))\npop()\n')
            mon_id = 0
            chain=0
            # 直链
            # print(chains[0])
            # while mon_id<int(int(poly)-1):
            chain_id=mon_id
            position = [str(coord) for coord in chains[0][chain_id]]
            # 获取当前单体的坐标
            location = ','.join(position)  # 将坐标转换为字符串形式

            fw.write(f" mon[0] = new {self.pc_list[0]}.move({location})\n")
            # mon_id = 1
            for poly_id in range(len(self.npoly)):
                    # all_poly=0
                    # if len(self.npoly)>1:
                    #     for poly in self.npoly:
                    #         if poly != ' ':
                    #             all_poly+=int(poly)
                    # if all_poly!=self.npoly:
                    if len(self.npoly)>1:
                        # print(int(self.npoly[poly_id]))
                        for poly_ in range(int(self.npoly[poly_id])):
                            mon_id+=1
                            # print(poly_)
                            chain_id=mon_id
                            position = [str(coord) for coord in chains[0][chain_id]]
                            # 获取当前单体的坐标
                            location = ','.join(position)  # 将坐标转换为字符串形式
                            fw.write(f" mon[{chain * int(self.npoly[0]) + chain_id}] = new {self.pc_list[poly_id+1]}.move({location})\n") 
                            # if mon_id == 0 :
                            #     fw.write(f" mon[0] = new {self.pc_list[0]}.move({location})\n") 
                            # if mon_id ==int(poly)-1:
                            #     fw.write(f" mon[{chain * int(self.npoly[0]) + chain_id}] = new {self.pc_list[-1]}.move({location})\n") 
                            # elif mon_id ==int(self.npoly[poly_id])+1:
                            #     pass
                            # else:
                            #     # print(f" mon[{chain * int(self.npoly[0]) + chain_id}] = new {self.pc_list[poly_id+1]}.move({location})\n")
                            #     fw.write(f" mon[{chain * int(self.npoly[0]) + chain_id}] = new {self.pc_list[poly_id+1]}.move({location})\n") 
                            if mon_id ==int(poly)-2:
                                chain_id=mon_id+1
                                position = [str(coord) for coord in chains[0][chain_id]]
                                # 获取当前单体的坐标
                                location = ','.join(position)  # 将坐标转换为字符串形式
                                fw.write(f" mon[{chain * int(self.npoly[0]) + chain_id}] = new {self.pc_list[-1]}.move({location})\n")
                    else:

                        for poly_ in range(int(self.npoly[poly_id])):
                            chain_id=mon_id
                            position = [str(coord) for coord in chains[0][chain_id]]
                            # 获取当前单体的坐标
                            location = ','.join(position)  # 将坐标转换为字符串形式
                            if mon_id == 0 :
                                # fw.write(f" mon[0] = new {self.pc_list[0]}.move({location})\n") 
                                pass
                            elif mon_id ==int(poly)-1:
                                fw.write(f" mon[{chain * int(self.npoly[0]) + chain_id}] = new {self.pc_list[-1]}.move({location})\n") 
                            else:
                                fw.write(f" mon[{chain * int(self.npoly[0]) + chain_id}] = new {self.pc_list[poly_id+1]}.move({location})\n") 

                            mon_id+=1
            # for chain in range(int(1)):
            #     for i in range(int(poly)):
            #     # for i in range(int(self.npoly[0])):
            #         # chain_id=mon_id%int(self.npoly[0])
            #         chain_id=1
            #         # print(chain_id)
            #         position = [str(coord) for coord in chains[chain][chain_id]]  # 获取当前单体的坐标
            #         location = ','.join(position)  # 将坐标转换为字符串形式
            #         chain_id=i
                    
            #         # print(len(self.npoly))
            #         if len(self.npoly)>1:
            #             if mon_id == 0 :
            #                 fw.write(f" mon[{chain * int(self.npoly[0]) + chain_id}] = new {self.pc_list[0]}.move({location})\n")
            #                 mon_id += 1
            #             else:
            #                 for polymer in range(len(self.npoly)):
            #                     print(mon_id)
            #                     if polymer==0:
            #                         if 0<mon_id < int(self.npoly[polymer]):
            #                             fw.write(f" mon[{chain * int(self.npoly[0]) + chain_id}] = new {self.pc_list[1]}.move({location})\n")
            #                             mon_id += 1
            #                     else:
            #                         if int(self.npoly[polymer-1]) <mon_id < int(self.npoly[polymer]):
            #                             fw.write(f" mon[{chain * int(self.npoly[0]) + chain_id}] = new {self.pc_list[polymer+1]}.move({location})\n")
            #                             mon_id += 1

            #                         elif mon_id == int(poly):
            #                             fw.write(f" mon[{chain * int(self.npoly[0]) + chain_id}] = new {self.pc_list[-1]}.move({location})\n")
            #                             mon_id += 1
                            
            #         else:
            #             if mon_id == 0 or mon_id == chain*int(self.npoly[0]):
            #                 fw.write(f" mon[{chain * int(self.npoly[0]) + chain_id}] = new {self.pc_list[0]}.move({location})\n")

            #             elif mon_id %(int(self.npoly[0])-1+chain*int(self.npoly[0])) == 0:
            #                 fw.write(f" mon[{chain * int(self.npoly[0]) + chain_id}] = new {self.pc_list[-1]}.move({location})\n")
            #             else:
            #                 fw.write(f" mon[{chain * int(self.npoly[0]) + chain_id}] = new {self.pc_list[1]}.move({location})\n")

            #             mon_id += 1
                
            fw.write("write('Data Bond List') {\n")
            # for chain in chains:
            bond_id=0
            # for chain_ in range(int(self.tes_chain[0])):
            for chain_ in range(int(1)):
                for i in range(int(poly)-1):
                    if i % int(poly) == int(poly) - 1:
                        atom_line = '$atom:mon[' + str(int(chain_)*int(poly)+i + 1) + ']/' + self.linkatom[0] + ' $atom:mon[' + str(int(chain_)*int(poly)+i + 2) + ']/' + self.linkatom[1] + '\n'
                        fw.write('         $bond:b' + str(bond_id + 1) + '  ' + atom_line)
                    else:
                        # print(int(chain_)*int(poly))

                        atom_line = '$atom:mon[' + str(int(chain_)*int(poly)+i) + ']/' + self.linkatom[0] + ' $atom:mon[' + str(int(chain_)*int(poly)+i + 1) + ']/' + self.linkatom[1] + '\n'
                        fw.write('         $bond:b' + str(bond_id + 1) + '  ' + atom_line)

                    bond_id+=1
            fw.write('}\n}\n')
            fw.close()

        # write tes.lt
            tes_file = self.output_file+str(poly)+'.lt'
            fw = open(tes_file, 'w')
            fw.write('   import "poly'+poly+'.lt"\n   polymer = new Poly_'+str(poly) +
                     '\n   write_once("Data Boundary") {\n     0.0000000  '+self.x+'  xlo xhi\n     0.0000000  '+self.y+'  ylo yhi\n     0.0000000  '+self.z+'  zlo zhi\n }\n')
            fw.close()

    def write_system_lt(self):
        xlo = 0
        xhi = 0
        ylo = 0
        yhi = 0
        zlo = 0
        zhi = 0
        if os.path.exists('order_system.data'):
        # Read the 'order_system.data' file and extract the values
            with open('order_system.data', 'r') as data_file:
                for line in data_file:
                    if 'xlo' in line:
                        xlo, xhi = map(str, line.split()[:2])
                    elif 'ylo' in line:
                        ylo, yhi = map(str, line.split()[:2])
                    elif 'zlo' in line:
                        zlo, zhi = map(str, line.split()[:2])
        elif os.path.exists('sio2_single_system_outside.data') and os.path.exists('graphene_all.data'):
            with open('sio2_single_system_outside.data', 'r') as data_file:
                for line in data_file:
                    if 'xlo' in line:
                        sio2_xlo, sio2_xhi = map(str, line.split()[:2])
                    elif 'ylo' in line:
                        sio2_ylo, sio2_yhi = map(str, line.split()[:2])
                    elif 'zlo' in line:
                        sio2_zlo, sio2_zhi = map(str, line.split()[:2])
            with open('graphene_all.data', 'r') as data_file:
                for line in data_file:
                    if 'xlo' in line:
                        gra_xlo, gra_xhi = map(str, line.split()[:2])
                    elif 'ylo' in line:
                        gra_ylo, gra_yhi = map(str, line.split()[:2])
                    elif 'zlo' in line:
                        gra_zlo, gra_zhi = map(str, line.split()[:2])
            xlo=str(max(float(sio2_xlo),float(gra_xlo)))
            xhi=str(max(float(sio2_xhi),float(gra_xhi)))
            ylo=str(max(float(sio2_ylo),float(gra_ylo)))
            yhi=str(max(float(sio2_yhi),float(gra_yhi)))
            zlo=str(max(float(sio2_zlo),float(gra_zlo)))
            zhi=str(max(float(sio2_zhi),float(gra_zhi)))          
            # print(zlo)
        elif os.path.exists('sio2_single_system_outside.data'):
            with open('sio2_single_system_outside.data', 'r') as data_file:
                for line in data_file:
                    if 'xlo' in line:
                        xlo, xhi = map(str, line.split()[:2])
                    elif 'ylo' in line:
                        ylo, yhi = map(str, line.split()[:2])
                    elif 'zlo' in line:
                        zlo, zhi = map(str, line.split()[:2])
                    # print(zlo)
        elif os.path.exists('graphene_all.data'):
            with open('graphene_all.data', 'r') as data_file:
                for line in data_file:
                    if 'xlo' in line:
                        xlo, xhi = map(str, line.split()[:2])
                    elif 'ylo' in line:
                        ylo, yhi = map(str, line.split()[:2])  
                    elif 'zlo' in line:
                        zlo, zhi = map(str, line.split()[:2])
        fw = open('system.lt', 'w')
        all_poly=0
        if len(self.npoly)>1:
            for poly in self.npoly:
                if poly != ' ':
                    all_poly+=int(poly)
            all_poly+=2    
            npoly=all_poly
            fw.write(' import poly'+str(npoly)+'.lt\n')
            polymer_id = 1
            poly_id = 0
            for chains in self.tes_chain:
                fw.write('polymer'+str(polymer_id)+' = new Poly_' +
                        str(npoly)+'['+str(chains)+']\n')
                polymer_id += 1
                poly_id += 1
        else:
            for poly in self.npoly:
                poly=str(poly)

                fw.write(' import poly'+poly+'.lt\n')
            polymer_id = 1
            poly_id = 0
            for chains in self.tes_chain:
                fw.write('polymer'+str(polymer_id)+' = new Poly_' +
                        str(self.npoly[poly_id])+'['+str(chains)+']\n')
                polymer_id += 1
                poly_id += 1
        fw.write('\n write_once("Data Boundary") {\n')
        #      0  100.000000  xlo xhi
        # fw.write('     0  '+str(self.lx)+'  xlo xhi\n')
        # fw.write('     0  '+str(self.ly)+'  ylo yhi\n')
        # fw.write('     0  '+str(self.lz)+'  zlo zhi\n')
        zhi='1000'
        fw.write('     '+str(xlo)+'  '+str(xhi)+'  xlo xhi\n')
        fw.write('     '+str(ylo)+'  '+str(yhi)+'  ylo yhi\n')
        fw.write('     '+str(zlo)+'  '+str(zhi)+'  zlo zhi\n')
        fw.write('  }\n')
        fw.close()

    def main(self):
        # if 'random' in self.mix_style:
        #     pass
        Car2lt.write_lts(self)
        Car2lt.write_order_npoly_lt(self)
        Car2lt.write_system_lt(self)

