data="""variable fname index PE_nc10_cl1000.dat
variable simname index PE_nc10_cl1000
# Initialization
 include "system.in.init"  #potential
 read_data  "final_300K.data"   #orginal structure
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
fix             1 all npt temp 300 300 50 y 0 0 1000 z 0 0 1000 drag 2
fix             2 all deform 1 x erate 1e-6 units box remap x
fix def1 all print 100 "${p1} ${p2} ${p3} ${p4} ${p5} ${p6} ${p7} ${p8}" file ${simname}.def1.txt screen no
fix def2 all print 100 "${p1} ${t2} ${t3} ${t4} ${t5}" file ${simname}.def2.txt screen no
#thermo_style   custom step temp pxx pyy pzz lx ly lz epair ebond eangle edihed
thermo_style custom step temp pe press pxx pyy pzz pxy pxz pyz lx ly lz vol
thermo          1
timestep        1
reset_timestep  0
#restart 10000 deform.restart
run             200000
unfix 1
unfix 2
unfix def1
unfix def2
"""
fw=open('deform.in','w')
fw.write(data)