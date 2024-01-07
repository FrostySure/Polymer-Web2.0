
fw=open('dis_sys_equil.in','w')
data="""variable fname index PE_nc10_cl1000.dat
variable simname index PE_nc10_cl1000
# Initialization
 include "system.in.init"  #potential
 read_data  "system.data"   #orginal structure
 include "system.in.settings"  #para
#####################################################
# Uniaxial Tensile Deformation
run 0
variable tmp equal "lx"
variable L0 equal ${tmp}
variable strain equal "(lx - v_L0)/v_L0"
variable p1 equal "v_strain"
variable p2 equal "-pxx/10000*1.01325"
variable p3 equal "-pyy/10000*1.01325"
variable p4 equal "-pzz/10000*1.01325"
variable p5 equal "lx"
variable p6 equal "ly"
variable p7 equal "lz"
variable p8 equal "temp"
variable t2 equal "epair"
variable t3 equal "ebond"
variable t4 equal "eangle"
variable t5 equal "edihed"
#group am id < 16041
#fix 1 all npt temp 1 300 100 z 0 0 1000
minimize 1.0e-5 1.0e-7 1000 10000
write_data min.data

fix             1 all npt temp 1 300 50 x 0 0 1000 y 0 0 1000 drag 2
fix             2 all deform 1 z erate -1e-4 units box remap x
fix def1 all print 100 "${p1} ${p2} ${p3} ${p4} ${p5} ${p6} ${p7} ${p8}" file ${simname}.def1.txt screen no
fix def2 all print 100 "${p1} ${t2} ${t3} ${t4} ${t5}" file ${simname}.def2.txt screen no
#thermo_style   custom step temp pxx pyy pzz lx ly lz epair ebond eangle edihed
thermo_style custom step temp pe press  lx ly lz vol
thermo          1
dump            4 all dcd 100    deform.dcd
  dump_modify   4        unwrap yes

timestep        0.5
reset_timestep  0
restart 100000 deform.restart
run             18000
#run             100
write_data deform.data
unfix 1
unfix 2
unfix def1
unfix def2
undump 4

fix fxnpt all npt temp 1 300 100 z 0 0 1000
 timestep 1
 thermo 100
thermo_style custom step temp pe vol density etotal lx ly lz
dump            4 all dcd 1000    a_r.dcd
  dump_modify   4        unwrap yes
 run   10000
 #run   1000

undump 4
unfix fxnpt
write_data a_r.data

fix fxnpt all npt temp 300 300 100 z 0 0 1000
 timestep 0.5
 thermo 100
thermo_style custom step temp pe vol density etotal lx ly lz
dump            4 all dcd 1000    a_e.dcd
  dump_modify   4        unwrap yes
 run   2000000
 #run   1000

undump 4
unfix fxnpt
write_data a_e.data


"""

fw.write(data)
