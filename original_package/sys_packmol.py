import os
silicon = 0
graphene = 0
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
        elif key == 'nchain':
            nchain = value
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
        elif key == 'silicon':
            silicon = str(value)
        elif key == 'graphene':
            graphene = str(value)
def write_packmol():
    nchain=0
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
                # print(zlo)
    fw = open('sys_packmol.in', 'w')
    fw.write('tolerance 2.0\nfiletype pdb\noutput all_sys.pdb\n\n')
    if graphene:
        fw.write('filetype pdb\nstructure ' +
                    'graphene_all.pdb\n  number 1\n\n')
        fw.write('  fixed 0.0 0.0 '+zlo+' 0. 0. 0. \nend structure\n')  
    if silicon:
        fw.write('filetype pdb\nstructure ' +
                    'sio2_single_system_outside.pdb\n  number 1\n\n')
        fw.write('  fixed 0.0 0.0 '+zlo+' 0. 0. 0. \nend structure\n')  

    if nchain:
        fw.write('filetype pdb\nstructure ' +
                'a_un.pdb\n  number 1\n\n')
        fw.write('  fixed 0.0 0.0 0. 0. 0. 0. \nend structure\n')  
    if not nchain:
        fw.write('filetype pdb\nstructure ' +
                'a_un.pdb\n  number 1\n\n')
        fw.write('  fixed 0.0 0.0 '+str(zhi)+' 0. 0. 0. \nend structure\n')  
        data="""filetype pdb
structure order_system.pdb
number 1

fixed 0. 0. 0 0 0 0
end structure
        """  
        fw.write(data)     

def write_graphene_packmol():
    xlo = None
    xhi = None
    ylo = None
    yhi = None

    # Read the 'order_system.data' file and extract the values
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

    elif os.path.exists('sio2_single_system_outside.data'):
        with open('sio2_single_system_outside.data', 'r') as data_file:
            for line in data_file:
                if 'xlo' in line:
                    xlo, xhi = map(str, line.split()[:2])
                elif 'ylo' in line:
                    ylo, yhi = map(str, line.split()[:2])
                elif 'zlo' in line:
                    zlo, zhi = map(str, line.split()[:2])
    elif os.path.exists('graphene_all.data'):
        with open('graphene_all.data', 'r') as data_file:
            for line in data_file:
                if 'xlo' in line:
                    xlo, xhi = map(str, line.split()[:2])
                elif 'ylo' in line:
                    ylo, yhi = map(str, line.split()[:2])  
                elif 'zlo' in line:
                    zlo, zhi = map(str, line.split()[:2])
    fw = open('sys_packmol.in', 'w')
    fw.write('tolerance 2.0\nfiletype pdb\noutput all_sys.pdb\n\n')
    fw.write('filetype pdb\nstructure ' +
                'graphene_all.pdb\n  number 1\n\n')
    fw.write('  fixed 0.0 0.0 '+zlo+' 0. 0. 0. \nend structure\n')  


    if os.path.exists('order_system.data'):
        fw.write('filetype pdb\nstructure ' +
                'a_un.pdb\n  number 1\n\n')
        fw.write('  fixed 0.0 0.0 '+zhi+' 0. 0. 0. \nend structure\n')  
        data="""filetype pdb
structure order_system.pdb
number 1
fixed 0. 0. 0 0 0 0
end structure
""" 
        fw.write('filetype pdb\nstructure ' +
                    'a_un.pdb\n  number 1\n\n')
        fw.write('  fixed 0.0 0.0 0. 0. 0. 0. \nend structure\n')  
        print(data)
        fw.write(data)  

# if os.path.exists('graphene_all.pdb'):
#     demo=write_graphene_packmol()
# else:
demo=write_packmol()
# demo=write_graphene_packmol()



