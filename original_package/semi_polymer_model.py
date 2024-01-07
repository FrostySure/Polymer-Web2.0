import get_all_list
import os
from workflow_composite_inside import Workflow_composite_inside
from workflow_semi import Workflow_semi

# import get_graphene_single


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
        elif key == 'nchain':
            nchain = list(map(str, value.split()))
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
        elif key == 'silicon':
            silicon = str(value)
        elif key == 'graphene':
            graphene = str(value)

# print(silicon)
demo = Workflow_semi(output_file=outfilename, pc_list=filename, npoly=npoly,   linkatoms=linkatom,  box_size_list=lbox, order_nchain=order_nchain,disorder_nchain=disorder_nchain,
                        npt_step=step[0], nvt_step=step[0], ncore=ncore)
demo.step_1()





# if silicon!='n':
#     demo = Write_coatings(sio2=sio2, gra=gra,
#                      sio2_num=sio2_num_layer, gra_num=gra_num_layer)
#     demo.write_coatings()
