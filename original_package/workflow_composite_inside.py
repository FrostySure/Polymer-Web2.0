import write_lts
import dcd2data
import packmol
import data2pdb
import os
import get_all_list


class Workflow_composite_inside():
    def __init__(self, output_file, pc_list, npoly, mix_style, chain_style, linkatoms, rs, rb, box_size_list, tes_chain, system_style, composite_item, item_x_y, item_num_layer, item_site, lbox_size_list,   npt_step=1000, nvt_step=5000, ncore='6'):
        self.pc_list = pc_list
        self.npoly = npoly
        self.tes_chain = tes_chain
        self.box_size_list = box_size_list
        self.lbox_size_list = lbox_size_list
        self.linkatoms = linkatoms
        self.mix_style = mix_style
        self.output_file = output_file
        self.ncore = ncore
        self.npt_step = npt_step
        self.nvt_step = nvt_step
        self.chain_style = chain_style
        self.rs = rs
        self.rb = rb
        self.system_style = system_style

    def step_1(self):
        # 写高分子lt文件
        demo_model = write_lts.Car2lt(pc_list=self.pc_list, npoly=self.npoly, tes_chain=self.tes_chain, box_size_list=self.box_size_list,
                                      lbox_size_list=self.lbox_size_list, tes='1', linkatom=self.linkatoms, mix_style=self.mix_style, output_file=self.output_file)
        demo_model.main()
        # 写items_lt文件
        #   composite_item=#[['sio2', 'graphene']]#二维复合材料类型 all_list[1][11] 列表
        # [[[11, 10], [20, 20]], [21, 21]] ##二维材料大小
        item_id = 0
        sio2_id = 0
        graphene_id = 0
        sio2_x_n = 0
        sio2_y_n = 0
        # fr_list = []
        # os.system('del *.xyz')
        os.system('rm -rf *.xyz')
        fr_single_list = []

        for item in self.composite_item[0]:
            if 'sio2' in item:
                fr_list = []
                num_list = []
                sio2_list = []
                # [[11, 10], [20, 20]]
                # self.item_x_y[item_id]=[[11, 10], [20, 20]]

                for item_size in self.item_x_y[item_id]:

                    fr_name = 'sio2_supers_'+str(sio2_id+1)+'.xyz'
                    fr_single_name = 'sio2_single_'+str(sio2_id+1)+'.xyz'
                    fr_list.append(fr_name)
                    fr_single_list.append(fr_single_name)
                    sio2_layer = self.item_num_layer[0][item_id][sio2_id]
                    item_num_layer = sio2_layer
                    num_list.append(item_num_layer)

                    sio2_x = item_size[0]
                    sio2_y = item_size[1]
                    # 每个单胞7.16埃
                    sio2_x_n = str(int(sio2_x/7.16))
                    sio2_y_n = str(int(sio2_y/7.16))
                    sio2_layer = str(self.item_num_layer[0][item_id][sio2_id])
                    # atomsk扩胞sio2
                    cmd = 'atomsk SiO2_single.cif -duplicate ' + \
                        sio2_x_n+' '+sio2_y_n+' '+sio2_layer + \
                        '  '+fr_name
                    # print(cmd)

                    # os.system(cmd)

                    # sio2_single.lt获得单层sio2.data以获得pdb来packmol
                    cmd = 'atomsk SiO2_single.cif -duplicate ' + \
                        sio2_x_n+' '+sio2_y_n+' 1 '+fr_single_name

                    # os.system(cmd)

                    # [[[1, 2], [3]], [4, 5]]#二维材料的数目或层数
                    #[[1, 2], [3]]
                # [1, 2]
                    # 写二氧化硅lt文件

                    sio2_id += 1
                item_id += 1
                fr_id = 0
                demo = write_sio2_lt.Write_sio2_lt(
                    fr_list=fr_list, layer=num_list)
                # print(num_list)
                demo.write_sio2_inside_lt('sio2_supers_inside_')
                sio2_system_inside_list = demo.write_sio2_system_inside_lt(
                    'sio2_system_inside')
                demo = write_sio2_lt.Write_sio2_lt(
                    fr_list=fr_single_list, layer=num_list)
                # demo = write_sio2_lt.Write_sio2_lt(
                #     fr_list=['sio2_superss.xyz', 'sio2_super.xyz'])
                demo.write_sio2_inside_lt('sio2_single_inside_')
                sio2_single_system_inside_list = demo.write_sio2_single_system_inside_lt(
                    'sio2_single_system_inside')
                fr_id += 1
                sio2_list.append(fr_list)
                sio2_list.append(num_list)
            elif 'graphene' in item:
                fr_list = []
                num_list = []
                graphene_list = []
                graphene_inside_system_list = []
                graphene_inside_single_system_list = []
                for item_size in self.item_x_y[item_id]:
                    # print(item_size)
                    # for item_size in item_size:  # [11, 10]
                    # 写石墨烯lt文件
                    # def __init__(self, item_x_y, item_num_layer):
                    item_x_y = item_size
                    fw_name = 'graphene_walls_inside_'+str(graphene_id+1)+'.lt'
                    fr_list.append(fw_name)
                    system_name = 'graphene_system_inside' + \
                        str(graphene_id+1)+'.lt'
                    graphene_inside_system_list.append(system_name)
                    # print(self.item_num_layer[0][item_id])
                    graphene_layer = self.item_num_layer[0][item_id][graphene_id]
                    num_list.append(graphene_layer)

                    # print(item_x_y, graphene_layer)
                    item_num_layer = graphene_layer
                    demo_wall = get_graphene_single.Write_graphene_wall(
                        item_x_y=item_x_y, item_num_layer=item_num_layer)
                    demo_wall.write_graphene()
                    demo_wall.write_graphene_single_inside(graphene_id)
                    graphene_inside_single_system_list.append(
                        'graphene_system_single_inside' + str(graphene_id+1)+'.lt')
                    demo_wall.write_graphene_inside_wall(
                        fw_name, fr_id=graphene_id)
                    demo_wall.write_graphene_inside_system(
                        system_name, graphene_id)
                    graphene_id += 1
                item_id += 1
                graphene_list.append(fr_list)
                graphene_list.append(num_list)
        # print(graphene_inside_system_list, graphene_inside_single_system_list,
        #       sio2_system_inside_list, sio2_single_system_inside_list)
        return sio2_list, graphene_list, graphene_inside_system_list, graphene_inside_single_system_list, sio2_system_inside_list, sio2_single_system_inside_list
        # 运行Moltemplate

    def step_2(self):
        demo_mol_sh = mol_sh.Moltemplate_sh(
            npoly=self.npoly, output_file=self.output_file)
        demo_mol_sh.sh_moltemplate()
        data_list = []

        for poly in self.npoly:
            poly = str(poly)
            data = self.output_file + poly
            data_list.append(data)
        demo_npt = write_npt.Write_npt(data_list=data_list,
                                       npt_step=self.npt_step, ncore=self.ncore)
        demo_npt.write_npt_in()
        demo_npt.write_sub_npt_sh()
        demo_nvt = write_nvt.Write_nvt(data_list=data_list,
                                       nvt_step=self.nvt_step, ncore=self.ncore)
        demo_nvt.write_nvt_in()
        demo_nvt.write_sub_nvt_sh()

    def step_3(self):
        data_list = []
        for poly in self.npoly:
            poly = str(poly)
            data = self.output_file + poly
            data_list.append(data)

    # step 3
    # dcd2data

        demo_dcd2data = dcd2data.Dcd2data(data_list=data_list)
        demo_dcd2data.dcd2data()

    def step_4(self):
        data_list = []
        for poly in self.npoly:
            poly = str(poly)
            data = self.output_file + poly
            data_list.append(data)

        # step 4
        # data2pdb
        new_data_list = []
        for data_id in data_list:
            new_data_id = data_id+'_un'
            new_data_list.append(new_data_id)
        for new_data_id in new_data_list:
            demo_data2pdb = data2pdb.Data2pdb(data=new_data_id)
            demo_data2pdb.data2pdb()

    def step_5(self):
        data_list = []
        for poly in self.npoly:
            poly = str(poly)
            data = self.output_file + poly
            data_list.append(data)

        # step 4
        # data2pdb
        new_data_list = []
        for data_id in data_list:
            new_data_id = data_id+'_un'
            new_data_list.append(new_data_id)
        # step 5
        # packmol
        # print(new_data_list)
        demo_packmol = packmol.Packmol(
            pdb_list=new_data_list, pdb_num_list=self.tes_chain, lbox_list=self.lbox_size_list)
        demo_packmol.write_packmol_in()
        demo_packmol.write_sub_packmol_in()
        demo_packmol.write_system_sh()

    def step_6(self):
        data_list = []
        for poly in self.npoly:
            poly = str(poly)
            data = self.output_file + poly
            data_list.append(data)
            new_data_list = []
            for data_id in data_list:
                new_data_id = data_id+'_un'
                new_data_list.append(new_data_id)
            demo_nvt = write_nvt.Write_nvt(data_list=data_list,
                                           nvt_step=self.nvt_step, ncore=self.ncore)
            demo_nvt.sub_system_npt_nvt_sh()

    def main():
        fw = open('workflow_composite_inside.sh', 'w')
        sh_data = """python step1.py &&
sh sub_moltemplate.sh 
python step2.py &&
sh npt.sh
sh nvt.sh
python step3.py &&
python step4.py &&
python step5.py &&
sh packmol.sh
sh system.sh 
python step6.py &&
sh system_sh.sh """
        fw.write(sh_data)
        os.system('nohup sh workflow_composite_inside.sh > polymer.log &')


# demo = get_all_list.Inp2py('in.inp')  # 从inp文件获得建模参数
# all_list = demo.inp2py()
# ncore = all_list[0][0]
# output_file = all_list[0][1]
# pc_list = all_list[1][0]  # 单体名称们
# npoly = all_list[1][1]  # 聚合度列表
# mix_style = all_list[1][2]  # 是否共聚
# chain_style = all_list[1][3]  # 单链是否有序
# linkatoms = all_list[1][4]  # 连接原子序号
# rs = all_list[1][5]  # 单链参数1
# rb = all_list[1][6]  # 单链参数2
# box_size_list = all_list[1][7]  # 单链所占盒子大小
# tes_chain = all_list[1][8]  # 每种聚合度对应的链数列表
# system_style = all_list[1][9]  # 高分子体系指定为非晶
# composite_style = all_list[1][10]
# composite_item = all_list[1][11]  # 二维复合材料类型
# item_x_y = all_list[1][12]  # 二维材料大小
# item_num_layer = all_list[1][13]  # 二维材料的数目或层数
# item_site = all_list[1][14]  # 涂层位置
# lbox_size_list = all_list[1][15]  # 聚合物所占盒子大小
