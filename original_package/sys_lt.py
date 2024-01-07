import os
silicon = 0
graphene = 0
with open('in.inp', 'r') as infile:
    nchain=0
    for line in infile:
        parts = line.strip().split('=')
        if len(parts) != 2:
            continue
        key, value = parts[0].strip(), parts[1].strip()
        if key == 'ncore':
            ncore = int(value)
        elif key == 'outfilename':
            outfilename = value
        elif key == 'nchain':
            nchain = value
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
        elif key == 'silicon':
            silicon = str(value)
        elif key == 'graphene':
            graphene = str(value)
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

    with open('graphene_all.data', 'r') as data_file:
        for line in data_file:
            if 'xlo' in line:
                gra_xlo, gra_xhi = map(str, line.split()[:2])
            elif 'ylo' in line:
                gra_ylo, gra_yhi = map(str, line.split()[:2])
    xlo=str(max(float(sio2_xlo),float(gra_xlo)))
    xhi=str(max(float(sio2_xhi),float(gra_xhi)))
    ylo=str(max(float(sio2_ylo),float(gra_ylo)))
    yhi=str(max(float(sio2_yhi),float(gra_yhi)))
elif os.path.exists('sio2_single_system_outside.data'):
    with open('sio2_single_system_outside.data', 'r') as data_file:
        for line in data_file:
            if 'xlo' in line:
                xlo, xhi = map(str, line.split()[:2])
            elif 'ylo' in line:
                ylo, yhi = map(str, line.split()[:2])
elif os.path.exists('graphene_all.data'):
    with open('graphene_all.data', 'r') as data_file:
        for line in data_file:
            if 'xlo' in line:
                xlo, xhi = map(str, line.split()[:2])
            elif 'ylo' in line:
                ylo, yhi = map(str, line.split()[:2])  

fw = open('all_sys.lt', 'w')
all_poly=0
if len(npoly)>1:
    for poly in npoly:
        if poly != ' ':
            all_poly+=int(poly)
    all_poly+=2    
    npoly=all_poly
    if not nchain:
        chain=int(float(order_nchain[0])+float(disorder_nchain[0]))
    if graphene:
        fw.write('import "graphene_walls_outside.lt"\nwall = new Wall[1]\n                ['+str(graphene)+'].move(0,0,3.34)\n') 
    if silicon:
        fw.write('import "sio2_supers_outside.lt"\nmembrane_sio2 = new SiO2\n')
    fw.write(' import poly'+str(npoly)+'.lt\n')
    fw.write('polymer = new Poly_' +str(npoly)+'['+str(chain)+']\n')
else:
    for poly in npoly:
        if not nchain:
            chain=int(float(order_nchain[0])+float(disorder_nchain[0]))
        if graphene:
            fw.write('import "graphene_walls_outside.lt"\nwall = new Wall[1]\n                ['+str(graphene)+'].move(0,0,3.34)\n') 
        if silicon:
            fw.write('import "sio2_supers_outside.lt"\nmembrane_sio2 = new SiO2\n')

        fw.write(' import poly'+poly+'.lt\n')
        fw.write('polymer = new Poly_' +str(poly)+'['+str(nchain)+']\n')
                

fw.write('\n write_once("Data Boundary") {\n')
fw.write('     '+str(xlo)+'  '+str(xhi)+'  xlo xhi\n')
fw.write('     '+str(ylo)+'  '+str(yhi)+'  ylo yhi\n')
fw.write('     0 1000  zlo zhi\n')
fw.write('  }\n')
fw.close()
