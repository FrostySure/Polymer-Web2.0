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
            nchain = list(map(str, value.split()))
        elif key == 'lbox':
            lbox = list(map(str, value.split()))  # Split by space and convert to str
        elif key == 'step':
            step = str(value)  # Split by space and convert to str
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
fw=open('dis_equil.in','w')
needname=str(outfilename)+str(npoly[0])
all_poly=0
if len(npoly)>1:
    for poly in npoly:
        if poly != ' ':
            all_poly+=int(poly)
    all_poly+=2    
    npoly=all_poly
    needname=str(outfilename)+str(npoly)
data="""include tes5.in.init
read_data  tes5.data
include tes5.in.settings
neighbor 10 bin 
neigh_modify every 2 delay 10 check yes page 100000 one 10000 
minimize 1.0e-5 1.0e-7 1000 10000
write_data min.data
fix   fxnpt all npt temp 0.1 300.0 100.0 iso 1.0 1.0 1000.0  drag 1.0
 timestep 0.25
 thermo 100
thermo_style custom step temp pe vol density etotal lx ly lz
dump            4 all dcd 1000    tes_r.dcd
  dump_modify   4        unwrap yes
 run   10000
write_data tes_r.data
unfix fxnpt
undump 4

fix   fxnpt all npt temp 300 300.0 100.0 iso 1.0 1.0 1000.0  drag 1.0
 timestep 0.25
 thermo 100
thermo_style custom step temp pe vol density etotal lx ly lz
dump            4 all dcd 100    tes.dcd
  dump_modify   4        unwrap yes
 run   10000
write_data tes.data
unfix fxnpt
undump 4"""
modified_string = data.replace("tes5", needname)
modified_string = modified_string.replace("tes_", str(outfilename)+'_')
#modified_string = modified_string.replace(" run   1000", 'run '+step)

fw.write(modified_string)
