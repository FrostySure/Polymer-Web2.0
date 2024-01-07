variable        mu index -8.1
variable        disp index 0.5
variable        temp index 298.0
units real
atom_style full
bond_style hybrid class2
angle_style hybrid class2
dihedral_style hybrid class2
improper_style hybrid class2
pair_style lj/class2/coul/long 10.0
pair_modify mix sixthpower tail yes
special_bonds lj/coul 0.0 0.0 1.0 dihedral yes
kspace_style pppm 0.0001
read_data  last.data
include  gcmc.in.settings
neigh_modify    every 1 delay 10 check yes
group  mol type 125
velocity        all create ${temp} 54654
fix 2 all nvt temp 298 298 100
compute  mol_msd mol msd com yes
fix msd mol  ave/time 10 100 1000 c_mol_msd[*] file msd.dat 
dump 3 all dcd 1000 msd.dcd
dump_modify 3 unwrap yes
timestep 1
thermo 1000
thermo_style custom step temp press pe ke
run             1000000
