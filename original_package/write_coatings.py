import os
import get_graphene_single
import write_sio2_lt


class Write_coatings():
    def __init__(self, polymer='system', sio2='n', gra='n', sio2_num=1, gra_num=1):
        self.polymer = polymer
        self.sio2 = sio2
        self.gra = gra
        self.gra_num = int(gra_num)
        self.sio2_num = int(sio2_num)

    def write_coatings(self):
        item_id = 0
        sio2_id = 0
        graphene_id = 0
        sio2_x_n = 0
        sio2_y_n = 0
        fr_list = []
        # polymer_list = []
        polymer_name = self.polymer+'.data'

        # polymer_name = 'tes_chain_un.data'
        fr = open(polymer_name, 'r')
        for line in fr.readlines()[:30]:
            if 'xlo xhi' in line:
                line.strip('xlo xhi')
                line.strip('\n')
                line = line.split(' ')
                new_line = []
                for string in line:
                    if string:
                        new_line.append(string)
                x = float(new_line[1])-float(new_line[0])
                auto_x_list = [new_line[0], new_line[1]]
            if 'ylo yhi' in line:
                line.strip('ylo yhi')
                line.strip('\n')
                line = line.split(' ')
                new_line = []
                for string in line:
                    if string:
                        new_line.append(string)
                y = float(new_line[1])-float(new_line[0])
                auto_y_list = [new_line[0], new_line[1]]

        auto_x = x
        auto_y = y
        auto_size_list = [auto_x_list, auto_y_list]
        fr_single_list = []

        if self.sio2 != 'n':
            fr_list = []
            num_list = []
            fr_name = 'sio2_supers_outside.xyz'
            fr_single_name = 'sio2_single_outside.xyz'
            fr_list.append(fr_name)
            fr_single_list.append(fr_single_name)
            sio2_layer = self.sio2_num
            item_num_layer = sio2_layer
            num_list.append(item_num_layer)
            if flag=='simple':
                sio2_x = auto_x
                sio2_y = auto_y
            else:
                sio2_x = lbox[0]
                sio2_y = lbox[1]              
            sio2_x_n = str(int(sio2_x/4.978))
            sio2_y_n = str(int(sio2_y/4.978))
            sio2_layer = str(self.sio2_num)
            cmd = 'atomsk SiO2_single.cif -duplicate ' + \
                sio2_x_n+' '+sio2_y_n+' '+sio2_layer + \
                '  '+fr_name
            os.system(cmd)
            cmd = 'atomsk SiO2_single.cif -duplicate ' + \
                sio2_x_n+' '+sio2_y_n+' 1 '+fr_single_name
            os.system(cmd)
            sio2_id += 1
            fr_id = 0
            demo = write_sio2_lt.Write_sio2_lt(
                fr_list=fr_list, layer=num_list, auto_size_list=auto_size_list)
            demo.write_sio2_outside_lt('sio2_supers_outside')
            demo.write_sio2_system_outside_lt(
                'sio2_system_outside')
            demo = write_sio2_lt.Write_sio2_lt(
                fr_list=fr_single_list, layer=num_list)
            demo.write_sio2_outside_lt('sio2_single_outside')
            demo.write_sio2_single_system_outside_lt(
                'sio2_single_system_outside')
            fr_id += 1

        if self.gra != 'n':
            item_x_y = [auto_x, auto_y]
            fw_name = 'graphene_walls_outside.lt'
            system_name = 'graphene_system_outside.lt'

            graphene_layer = self.gra_num

            item_num_layer = graphene_layer
            demo_wall = get_graphene_single.Write_graphene_wall(
                item_x_y=item_x_y, item_num_layer=item_num_layer)
            demo_wall.write_graphene()
            demo_wall.write_graphene_single_outside()
            demo_wall.write_graphene_outside_wall(fw_name)
            demo_wall.write_graphene_outside_system(
                system_name)
