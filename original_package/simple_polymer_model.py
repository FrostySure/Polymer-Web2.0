import get_all_list
import os
from workflow_composite_inside import Workflow_composite_inside

# from write_moltemplate import Write_moltemplate
from workflow_pure import Workflow_pure


demo = get_all_list.Inp2py('in.inp')  # 从inp文件获得建模参数

all_list = demo.inp2py()
#[['15', 'tes'], [['pc_h', 'pc', 'pc_t'], ['200'], ['C7', 'C8'], [2], ['500', '500', '500'], ['10000', '10000']], ['y', '1000000', '1000000', '1000000', '1000000', '300', '500']]
ncore = all_list[0][0]  # ['12', 'tes']
output_file = all_list[0][1]  #
pc_list = all_list[1][0]  # ['pc_h', 'pc', 'pc_t']
npoly = all_list[1][1]  # 聚合度列表 ['100']
linkatoms = all_list[1][2]  # 连接原子序号 ['C7', 'C8']
tes_chain = all_list[1][3]  # 每种聚合度对应的链数列表 [20]
box_size_list = all_list[1][4]  # 聚合物盒子 ['100', '100', '100']
npt_step = all_list[1][5][0]
nvt_step = all_list[1][5][0]

# ['y', '1', '1', '1000000', '1000000', '1000000', '1000000', '300', '500']
anneal = all_list[2][0]
rise_step = all_list[2][1]
rise_equil_step = all_list[2][2]
down_step = all_list[2][3]
down_equil_step = all_list[2][4]
anneal_tmp_start = all_list[2][5]
anneal_tmp_down = all_list[2][6]
data_list = []
for poly in npoly:
    poly = str(poly)
    data = output_file + poly
    data_list.append(data)
# 1是纯物质膜

demo = Workflow_pure(output_file, pc_list=pc_list, npoly=npoly,   linkatoms=linkatoms,  box_size_list=box_size_list, tes_chain=tes_chain,
                         npt_step=npt_step, nvt_step=nvt_step, ncore=ncore)
demo.step_1()
# demo = Write_all_system_lt(npoly, tes_chain)
# #
# demo.write_all_inside_system_lt()


