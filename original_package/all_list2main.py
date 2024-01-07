import get_all_list
import os
from workflow_composite_inside import Workflow_composite_inside
from workflow_composite_outside import Workflow_composite_outside
from workflow_composite_mix import Workflow_composite_mix
from write_system_lt import Write_all_system_lt
from write_moltemplate import Write_moltemplate
from write_npt import Write_npt
from write_nvt import Write_nvt
import dcd2data
import data2pdb
import packmol
import write_lts
demo = get_all_list.Inp2py('in.inp')  # 从inp文件获得建模参数
# demo = get_all_list.Inp2py('inside.inp')  # 从inp文件获得建模参数
# demo = get_all_list.Inp2py('outside.inp')  # 从inp文件获得建模参数
all_list = demo.inp2py()


"""
ncore= 6 #核数 all_list[0][0]
outfilename= tes #输出文件前缀 all_list[0][1]
filename= pc_h pc pn pc_t #
npoly= 12 42   #分别多少种聚合度 all_list[1][1]  列表
mix_npoly_style= [10,10];[20,20] #是否嵌段共聚 all_list[1][2]
chain_style= disorder #单链是否有序 all_list[1][3]
linkatom= C7 C8 # all_list[1][4]
rs= 15 #单链参数1 all_list[1][5]
rb= 7.996 #单链参数2 all_list[1][6]
box= 100 100 400 #单链盒子 all_list[1][7] 列表
nchain= 2 3#每种聚合度的链数 all_list[1][8] 列表
system_style= random #高分子体系指定为非晶 all_list[1][9]
composite_style=mix #是否复合 all_list[1][10] n/inside/outside/mix
composite_item=[[sio2,graphene];[sio2,graphene]] #二维复合材料类型 all_list[1][11] 列表
item_x_y= [[11,10],[20,20]];[21,21] #二维材料大小 all_list[1][12] 列表
#inside: sio2 type1 type2 ;graphene type1       outside sio2  graphene auto
item_num_layer= [[1,2],[3]];[4,5]#二维材料的数目或层数 all_list[1][13] 列表
#inside: sio2 type1*1 type2*2 graphene type1*3;outside sio2 auto*4 graphene auto*5
item_site=[2,2];[5,0]  #composite_style= auto 默认在z方向 z=0 z=max all_list[1][15] 列表
lbox= 100 100 50#整体盒子大小 all_list[1][14] 列表
annealing= y #是否退火 all_list[2][0]
step= 1000  5000  #npt nvt退火步长 all_list[2][1] 列表
xrd_style= y #是否xrd  all_list[3][0]
pres= 10 70 90 #xrd参数1 all_list[3][1] 列表
grid= 0.1 0.1 0.1 #xrd参数2 all_list[3][2] 列表
"""
# print(all_list)

ncore = all_list[0][0]
output_file = all_list[0][1]
pc_list = all_list[1][0]  # 单体名称们
npoly = all_list[1][1]  # 聚合度列表
mix_style = all_list[1][2]  # 是否共聚
chain_style = all_list[1][3]  # 单链是否有序
linkatoms = all_list[1][4]  # 连接原子序号
rs = all_list[1][5]  # 单链参数1
rb = all_list[1][6]  # 单链参数2
box_size_list = all_list[1][7]  # 单链所占盒子大小
tes_chain = all_list[1][8]  # 每种聚合度对应的链数列表
system_style = all_list[1][9]  # 高分子体系指定为非晶
composite_style = all_list[1][10]
composite_item = all_list[1][11]  # 二维复合材料类型
item_x_y = all_list[1][12]  # 二维材料大小
item_num_layer = all_list[1][13]  # 二维材料的数目或层数
item_site = all_list[1][14]  # 涂层位置
lbox_size_list = all_list[1][15]  # 聚合物所占盒子大小
npt_step = all_list[2][1][0]
nvt_step = all_list[2][1][1]
data_list = []
for poly in npoly:
    poly = str(poly)
    data = output_file + poly
    data_list.append(data)


def workflow_polymer():
    fw = open('flow.sh', 'w')
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
    os.system('nohup sh flow.sh > polymer.log &')


def workflow_composite_inside():
    pass


def workflow_composite_outside():
    pass


def workflow_composite_mix():
    pass


def model_style(composite_style):
    if composite_style == 'n':
        workflow_polymer()  # 非复合膜

    elif composite_style == 'inside':
        workflow_composite_inside()  # 掺杂复合膜
        print('掺杂')
        demo = Workflow_composite_inside(output_file, pc_list, npoly, mix_style, chain_style, linkatoms,
                                         rs, rb, box_size_list, tes_chain, system_style, composite_item, item_x_y, item_num_layer, item_site, lbox_size_list)
        inside_system_list = demo.step_1()
        sio2_inside_system_lt = inside_system_list[-2]
        sio2_inside_single_system_lt = inside_system_list[-1]
        graphene_inside_system_lt = inside_system_list[-4]
        graphene_inside_single_system_lt = inside_system_list[-3]
        all_inside_list = [sio2_inside_single_system_lt, sio2_inside_system_lt,
                           graphene_inside_single_system_lt, graphene_inside_system_lt]
        fr_sio2_list = inside_system_list[0]
        sio2_list = []
        for sio2 in fr_sio2_list:
            sio2_list.append(sio2[:-3])
        fr_graphene_list = inside_system_list[1]
        graphene_list = []
        for graphene in fr_graphene_list:
            graphene_list.append(graphene[:-3])
        demo = Write_all_system_lt(npoly, tes_chain, inside_sio2_layer=item_num_layer[0][0], inside_graphene_layer=item_num_layer[0][1],
                                   fr_sio2_list=fr_sio2_list, fr_graphene_list=fr_graphene_list)
        demo.write_all_inside_system_lt()
        demo_write_moltemplate_inside = Write_moltemplate(
            all_inside_list, npoly=npoly, output_file=output_file)
        demo_write_moltemplate_inside.write_moltemplate_inside()
        # print(sio2_inside_system_lt, sio2_inside_single_system_lt,
        #       graphene_inside_system_lt, graphene_inside_single_system_lt)
    elif composite_style == 'outside':
        workflow_composite_outside()  # 涂层复合膜
        print('涂层')
        demo = Workflow_composite_outside(output_file, pc_list, npoly, mix_style, chain_style, linkatoms,
                                          rs, rb, box_size_list, tes_chain, system_style, composite_item, item_x_y, item_num_layer, item_site, lbox_size_list)
        demo.step_7()

        demo = Write_all_system_lt(
            npoly, tes_chain, outside_sio2_layer=item_num_layer[-1][0], outside_graphene_layer=item_num_layer[-1][1])
        demo.write_all_outside_system_lt()
    elif composite_style == 'mix':
        workflow_composite_mix()  # 掺杂+涂层复合膜
        print('掺杂+涂层')
        # demo = write_lts.Car2lt(pc_list=pc_list, npoly=npoly, tes_chain=tes_chain,
        #                         box_size_list=box_size_list, lbox_size_list=lbox_size_list, mix_style=mix_style)
        # demo.main()
        # demo = Workflow_composite_mix(output_file, pc_list, npoly, mix_style, chain_style, linkatoms,
        #                               rs, rb, box_size_list, tes_chain, system_style, composite_item, item_x_y, item_num_layer, item_site, lbox_size_list)

        demo = Workflow_composite_inside(output_file, pc_list, npoly, mix_style, chain_style, linkatoms,
                                         rs, rb, box_size_list, tes_chain, system_style, composite_item, item_x_y, item_num_layer, item_site, lbox_size_list)
        # demo.step_1()
        # fr_sio2_list = demo.step_1()[0]
        # fr_graphene_list = demo.step_1()[1]
        inside_system_list = demo.step_1()
        sio2_inside_system_lt = inside_system_list[-2]
        sio2_inside_single_system_lt = inside_system_list[-1]
        graphene_inside_system_lt = inside_system_list[-4]
        graphene_inside_single_system_lt = inside_system_list[-3]
        all_inside_list = [sio2_inside_single_system_lt, sio2_inside_system_lt,
                           graphene_inside_single_system_lt, graphene_inside_system_lt]
        # print(all_inside_list)
        fr_sio2_list = inside_system_list[0]
        fr_graphene_list = inside_system_list[1]
        demo = Workflow_composite_outside(output_file, pc_list, npoly, mix_style, chain_style, linkatoms,
                                          rs, rb, box_size_list, tes_chain, system_style, composite_item, item_x_y, item_num_layer, item_site, lbox_size_list)
        demo.step_7()
        demo = Write_all_system_lt(npoly, tes_chain, inside_sio2_layer=item_num_layer[0][0], inside_graphene_layer=item_num_layer[0][1],
                                   outside_sio2_layer=item_num_layer[1][0], outside_graphene_layer=item_num_layer[1][1], fr_sio2_list=fr_sio2_list, fr_graphene_list=fr_graphene_list)
        demo.write_all_mix_system_lt()
        demo_write_moltemplate_inside = Write_moltemplate(
            all_inside_list, npoly=npoly, output_file=output_file)
        demo_write_moltemplate_inside.write_moltemplate_inside()
        demo = Write_npt(data_list=data_list, npt_step=npt_step)
        demo.write_chain_npt_in()
        demo.write_chain_npt_sh()
        demo = Write_nvt(data_list=data_list, nvt_step=nvt_step)
        demo.write_chain_nvt_in()
        demo.write_chain_nvt_sh()
        demo_dcd2data = dcd2data.Dcd2data(data_list=data_list)
        demo_dcd2data.dcd2data()

        new_data_list = []
        for data_id in data_list:
            new_data_id = data_id+'_un'
            new_data_list.append(new_data_id)
        sio2_list = []
        for fr_sio2 in sio2_inside_single_system_lt:
            fr_sio2 = fr_sio2[:-3]
            new_data_list.append(fr_sio2)
            sio2_list.append(fr_sio2)
        graphene_list = []
        for fr_graphene in graphene_inside_single_system_lt:
            fr_graphene = fr_graphene[:-3]
            new_data_list.append(fr_graphene)
            graphene_list.append(fr_graphene)
        for new_data_id in new_data_list:
            # print(new_data_id)
            demo_data2pdb = data2pdb.Data2pdb(data=new_data_id)
            demo_data2pdb.data2pdb()
        # print(sio2_list, graphene_list)

        demo_packmol = packmol.Packmol(
            pdb_chain_list=data_list, pdb_num_list=tes_chain, lbox_list=lbox_size_list, sio2_list=sio2_list, sio2_num=item_num_layer[0][0], graphene_list=graphene_list, graphene_num=item_num_layer[0][1])
        demo_packmol.write_packmol_in()
        demo_packmol.write_sub_packmol_in()
        demo_packmol.write_system_sh()


model_style(composite_style)
# print(all_list[2])

# print(str(all_list[0][0])+'#核数')
# print(str(all_list[0][1])+'#输出文件前缀')
# print(str(all_list[1][0])+' #pc_list all_list')
# print(str(all_list[1][1])+' #分别多少种聚合度')
# print(str(all_list[1][2])+'#是否嵌段共聚')
# print(str(all_list[1][3])+'#单链是否有序')
# print(str(all_list[1][4])+'#连接原子序号')
# print(str(all_list[1][5])+'#单链参数1')
# print(str(all_list[1][6])+'#单链参数2')
# print(str(all_list[1][7])+'#单链盒子')
# print(str(all_list[1][8])+'#每种聚合度的链数')
# print(str(all_list[1][9])+'#高分子体系指定为非晶')
# print(str(all_list[1][10])+'#是否复合')
# print(str(all_list[1][11])+'#二维复合材料类型')
# print(str(all_list[1][12])+'#二维材料大小')
# print(str(all_list[1][13])+'#二维材料的数目或层数')
# print(str(all_list[1][14])+'#涂层位置')
# print(str(all_list[1][15])+'#整体盒子大小')
# print(str(all_list[2][0])+'#是否优化')
# print(str(all_list[2][1][0])+'#npt步长')
# print(str(all_list[2][1][1])+'#nvt步长')
