class Write_all_system_lt():
    def __init__(self, npoly, tes_chain, inside_sio2_layer=[], inside_graphene_layer=[],  fr_sio2_list=[], fr_graphene_list=[], outside_sio2_layer=[], outside_graphene_layer=[], inside='inside_all.lt', outside='outside_all.lt', mix='mix_all.lt'):
        self.inside = inside
        self.outside = outside
        self.mix = mix
        self.npoly = npoly
        self.inside_sio2_layer = inside_sio2_layer
        self.inside_graphene_layer = inside_graphene_layer
        self.outside_sio2_layer = outside_sio2_layer
        self.outside_graphene_layer = outside_graphene_layer
        self.fr_sio2_list = fr_sio2_list
        self.fr_graphene_list = fr_graphene_list
        self.tes_chain = tes_chain

    def write_all_inside_system_lt(self):
        fw = open(self.inside, 'w')
        for poly in self.npoly:
            poly=str(poly)
            fw.write(' import "poly'+poly+'.lt"\n')
        polymer_id = 1
        poly_id = 0
        fr_id = 0
        for f in self.fr_sio2_list:
            fw.write(
                'import "sio2_single_inside_'+str(fr_id+1)+'.lt"\n')
            # print(self.inside_sio2_layer[fr_id])
            fr_id += 1
        fr_id = 0
        for f in self.fr_graphene_list:
            fw.write('import "graphene_walls_inside_'+str(fr_id+1) + '.lt"\n')
            # print(self.inside_graphene_layer[fr_id])
            fr_id += 1
        for chains in self.tes_chain:

            # for chain in chains:
            # print(chains)
            # polymer1 = new Poly_40[6]
            fw.write('polymer'+str(polymer_id)+' = new Poly_' +
                     str(self.npoly[poly_id])+'['+str(chains)+']\n')
            polymer_id += 1
            poly_id += 1
        fr_id = 0
        for f in self.fr_sio2_list:
            fw.write(
                'membrane_sio2_'+str(fr_id+1)+' = new SiO2_'+str(fr_id+1)+' ['+str(self.inside_sio2_layer[fr_id])+']\n')
            # print(self.inside_sio2_layer[fr_id])
            fr_id += 1
        fr_id = 0
        for f in self.fr_graphene_list:
            fw.write('wall_'+str(fr_id+1)+' = new Wall_'+str(fr_id+1)+' [1]\n                [' +
                     str(self.inside_graphene_layer[fr_id])+'].move(0,0,3.34)\n')
            # print(self.inside_graphene_layer[fr_id])
            fr_id += 1
        fw.write('\n write_once("Data Boundary") {\n')
        #      0  100.000000  xlo xhi
        fw.write('     0  100  xlo xhi\n')
        fw.write('     0  100  ylo yhi\n')
        fw.write('     0  100  zlo zhi\n')
        fw.write('  }\n')
        fw.close()

    def write_all_outside_system_lt(self):
        fw = open(self.outside, 'w')
        for poly in self.npoly:
            fw.write(' import "poly'+poly+'.lt"\n')
        polymer_id = 1
        poly_id = 0
        fw.write('import "sio2_single_outside.lt"\n')
        fw.write('import "graphene_walls_outside.lt"\n')
        for chains in self.tes_chain:
            fw.write('polymer'+str(polymer_id)+' = new Poly_' +
                     self.npoly[poly_id]+'['+str(chains)+']\n')
            polymer_id += 1
            poly_id += 1
        fw.write(
            'outside_membrane_sio2 = new SiO2 ['+str(self.outside_sio2_layer)+']\n')
        fw.write('outside_wall = new Wall [1]\n                ['+str(
            self.outside_graphene_layer)+'].move(0,0,3.34)\n')

        fw.write('\n write_once("Data Boundary") {\n')
        #      0  100.000000  xlo xhi
        fw.write('     0  100  xlo xhi\n')
        fw.write('     0  100  ylo yhi\n')
        fw.write('     0  100  zlo zhi\n')
        fw.write('  }\n')
        fw.close()

    def write_all_mix_system_lt(self):
        fw = open(self.mix, 'w')
        for poly in self.npoly:
            fw.write(' import "poly'+poly+'.lt"\n')
        polymer_id = 1
        poly_id = 0
        fr_id = 0
        fw.write('import "sio2_single_outside.lt"\n')
        fw.write('import "graphene_walls_outside.lt"\n')

        for f in self.fr_sio2_list:
            fw.write(
                'import "sio2_single_inside_'+str(fr_id+1)+'.lt"\n')
            # print(self.inside_sio2_layer[fr_id])
            fr_id += 1
        fr_id = 0
        for f in self.fr_graphene_list:
            fw.write('import "graphene_walls_inside_'+str(fr_id+1) + '.lt"\n')
            # print(self.inside_graphene_layer[fr_id])
            fr_id += 1
        for chains in self.tes_chain:

            # for chain in chains:
            print(chains)
            # polymer1 = new Poly_40[6]
            fw.write('polymer'+str(polymer_id)+' = new Poly_' +
                     self.npoly[poly_id]+'['+str(chains)+']\n')
            polymer_id += 1
            poly_id += 1
        fr_id = 0
        for f in self.fr_sio2_list:
            fw.write(
                'membrane_sio2_'+str(fr_id+1)+' = new SiO2_'+str(fr_id+1)+' ['+str(self.inside_sio2_layer[fr_id])+']\n')
            # print(self.inside_sio2_layer[fr_id])
            fr_id += 1
        fr_id = 0
        for f in self.fr_graphene_list:
            fw.write('wall_'+str(fr_id+1)+' = new Wall_'+str(fr_id+1)+' [1]\n                [' +
                     str(self.inside_graphene_layer[fr_id])+'].move(0,0,3.34)\n')
            # print(self.inside_graphene_layer[fr_id])
            fr_id += 1

        fw.write(
            'outside_membrane_sio2 = new SiO2 ['+str(self.outside_sio2_layer)+']\n')
        fw.write('outside_wall = new Wall [1]\n                ['+str(
            self.outside_graphene_layer)+'].move(0,0,3.34)\n')

        fw.write('\n write_once("Data Boundary") {\n')
        #      0  100.000000  xlo xhi
        fw.write('     0  100  xlo xhi\n')
        fw.write('     0  100  ylo yhi\n')
        fw.write('     0  100  zlo zhi\n')
        fw.write('  }\n')
        fw.close()


import get_all_list
import os
from workflow_composite_inside import Workflow_composite_inside
from write_system_lt import Write_all_system_lt
# from write_moltemplate import Write_moltemplate
from workflow_semi import Workflow_semi

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



with open('order_system.data', 'r') as data_file:
    for line in data_file:
        if 'xlo' in line:
            xlo, xhi = map(str, line.split()[:2])
        elif 'ylo' in line:
            ylo, yhi = map(str, line.split()[:2])

fw = open('system.lt', 'w')
for poly in npoly:
    fw.write(' import poly'+poly+'.lt\n')
    for chain in disorder_nchain:
        fw.write('polymer = new Poly_' +str(poly)+'['+str(chain)+']\n')
                

fw.write('\n write_once("Data Boundary") {\n')
fw.write('     '+xlo+'  '+xhi+'  xlo xhi\n')
fw.write('     '+ylo+'  '+yhi+'  ylo yhi\n')
fw.write('     0 1000  zlo zhi\n')
fw.write('  }\n')
fw.close()

