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
data="""
 include "all_sys.in.init"  #potential
 read_data  "all_sys.data"   #orginal structure
 include "all_sys.in.settings"  #para
minimize 1.0e-5 1.0e-7 1000 10000   #force energy
write_data min.data
restart 250000 tuihuo.restart#from 300 - 500

# fix   fxnpt all npt temp 1 300 100.0 iso 1.0 1.0 1000.0  drag 1.0  #
fix fxnpt all npt temp 1 300 100 z 0 0 1000
  timestep 1
thermo 1000 #output every 1000 timestep
thermo_style custom step temp pe vol density etotal lx ly lz
dump            4 all dcd 10000    1-300.dcd
 dump_modify   4        unwrap yes
run   1000000#100w from 0K to 300K
unfix fxnpt
undump 4
write_data 1-300K.data
write_restart 1-300K.restart

fix fxnpt all npt temp 300 300 100 z 0 0 1000
# fix   fxnpt all npt temp 300 300 100.0 iso 1.0 1.0 1000.0  drag 1.0  #
  timestep 1
thermo 1000 #output every 1000 timestep
thermo_style custom step temp pe vol density etotal lx ly lz
dump            4 all dcd 10000    300-300.dcd
 dump_modify   4        unwrap yes
run   1000000#100w  300K equil
unfix fxnpt
undump 4
write_data 300-300K.data
write_restart 300-300K.restart


#increase
#label increase
#variable        t index  300.0 350.0 400.0 450.0 500.0 550.0    
#variable        m equal $t+50.0
 fix   fxnpt all npt temp 300 500 100.0 iso 1.0 1.0 1000.0  drag 1.0  #
  timestep 1
thermo 1000 #output every 1000 timestep
thermo_style custom step temp pe vol density etotal lx ly lz
dump            4 all dcd 10000    300-500.dcd
 dump_modify   4        unwrap yes
run   500000 #rise_step
unfix fxnpt
undump 4

 fix   fxnpt all npt temp 500 500 100.0 iso 1.0 1.0 1000.0  drag 1.0  #
  timestep 1
thermo 1000 #output every 1000 timestep
thermo_style custom step temp pe vol density etotal lx ly lz
dump            4 all dcd 10000    500_equil.dcd
 dump_modify   4        unwrap yes
run   500000 #rise_equil_step
unfix fxnpt
undump 4
write_data 500K_equil.data
write_restart 500K_equil.restart


#anneal
label anneal
variable        t index  500 480 460 440 420 400 380 360 340 320 300 280 260 240 220 
variable        m equal $t-20.0
 fix   fxnpt all npt temp $t $m 100.0 iso 1.0 1.0 1000.0  drag 1.0  #
  timestep 1
thermo 1000 #output every 1000 timestep
thermo_style custom step temp pe vol density etotal lx ly lz
dump            4 all dcd 10000    $m_cool.dcd
 dump_modify   4        unwrap yes
run  250000 #down_step
unfix fxnpt
undump 4

 fix   fxnpt all npt temp $m $m 100.0 iso 1.0 1.0 1000.0  drag 1.0  #
  timestep 1
thermo 1000 #output every 1000 timestep
thermo_style custom step temp pe vol density etotal lx ly lz
dump            4 all dcd 10000    $m_equil.dcd
 dump_modify   4        unwrap yes
run   250000 #down_equil_step
unfix fxnpt
undump 4
write_data $m_equil_decrease.data
write_restart $m_equil_decrease.restart
next t
jump anneal.in anneal

#final equiva
 fix   fxnpt all npt temp 300.0 300.0 100.0 iso 1.0 1.0 1000.0  drag 1.0  #
 timestep 1
thermo 1000 #output every 1000 timestep
thermo_style custom step temp pe vol density etotal lx ly lz
dump            4 all dcd 10000    final_300K.dcd
 dump_modify   4        unwrap yes
run   1000000 
unfix fxnpt
write_data final_300K.data

"""

modified_string = data.replace("run   500000 #rise_step", 'run '+rise_step)
modified_string = modified_string.replace("run   500000 #rise_equil_step", 'run '+rise_equil_step)
modified_string = modified_string.replace("run   250000 #down_step", 'run '+down_step)
modified_string = modified_string.replace("run   250000 #down_equil_step", 'run '+down_equil_step)
temps=''
for temp in range(int(anneal_tmp_start),int(anneal_tmp_down),20):
  temps=str(temp)+' '
modified_string = modified_string.replace("variable        t index  500 480 460 440 420 400 380 360 340 320 ", 'variable        t index  '+temps)

fw=open('anneal.in','w')
fw.write(modified_string)

# data=""" include "all_sys.in.init"  #potential
#  read_data  "all_sys.data"   #orginal structure
#  include "all_sys.in.settings"  #para
# minimize 1.0e-5 1.0e-7 1000 10000   #force energy
# write_data final_300K.data"""
# fw=open('anneal.in','w')
# fw.write(data)
