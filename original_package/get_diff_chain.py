import MDAnalysis
from data2pdb import *
import os

# This is can get polymer consist of different  chain.
# file_list = ['10'] 10.data is obtende from moltemplate
# Get_diff_chain(file_list, box_x, box_y, box_z)


class Get_diff_chain():
    def __init__(self, file_list, box_x, box_y, box_z):
        self.file_list = file_list
        # file_list=[300,600]
        self.box_x = str(box_x)
        self.box_y = str(box_y)
        self.box_z = str(box_z)

    def write_steps(self):
        fw1 = open('step1.py', 'w')  # get nvt.data
        fw1.write('from polymer2 import *\ndemo = Get_diff_chain('+str(self.file_list)+','+self.box_x+',' +
                  self.box_y+','+self.box_z+')\ndemo.write_npt_in()\ndemo.write_nvt_in()\n\n')
        fw1.close()
        fw2 = open('step2.py', 'w')  # get un.data
        fw2.write('from polymer2 import *\ndemo = Get_diff_chain('+str(self.file_list) +
                  ','+self.box_x+','+self.box_y+','+self.box_z+')\ndemo.dcd2data()\n')
        fw2.close()
        fw3 = open('step3.py', 'w')  # un.data to ub.pdb
        fw3.write('from polymer2 import *\ndemo = Get_diff_chain('+str(self.file_list) +
                  ','+self.box_x+','+self.box_y+','+self.box_z+')\ndemo.data2pdb()\n')
        fw3.close()
        fw4 = open('step4.py', 'w')  # packmol pdb
        fw4.write('from polymer2 import *\ndemo = Get_diff_chain('+str(self.file_list) +
                  ','+self.box_x+','+self.box_y+','+self.box_z+')\ndemo.pack_mol()\n')
        fw4.close()

    def write_npt_in(self):
        for file_name in self.file_list:
            fw = open(file_name+'npt.in', 'w')
            # include "100.in.init"
            fw.write('include "'+file_name+'.in.init"\n')
            # read_data  "100.data"
            fw.write('read_data "'+file_name+'.data"\n')
            # include "100.in.settings"
            fw.write('include "'+file_name+'.in.settings"\n')
            # minimize 1.0e-5 1.0e-7 1000 10000
            fw.write('minimize 1.0e-5 1.0e-7 1000 10000\n fix   fxnpt all npt temp 300.0 300.0 100.0 iso 1.0 1.0 1000.0  drag 1.0\n timestep 1.0\nthermo 100\n')
            # dump            4 all dcd 1000    tes_chain_npt.dcd
            fw.write('dump            4 all dcd 1000    ' +
                     file_name+'npt.dcd\n')
            # dump_modify   4        unwrap yes
            fw.write('dump_modify   4        unwrap yes\nrun   1000\n')
            # write_restart a.data
            # write_data 100npt.data
            fw.write('write_data '+file_name+'npt.data\n')
            fw.close()

    def write_nvt_in(self):
        for file_name in self.file_list:
            fw = open(file_name+'nvt.in', 'w')
            # include "100.in.init"
            fw.write('include "'+file_name+'.in.init"\n')
            # read_data  "100.data"
            fw.write('read_data "'+file_name+'npt.data"\n')
            # include "100.in.settings"
            fw.write('include "'+file_name+'.in.settings"\n')
            # minimize 1.0e-5 1.0e-7 1000 10000
            fw.write(
                'minimize 1.0e-5 1.0e-7 1000 10000\n fix   fxnvt all nvt temp 300.0 300.0 500.0\n timestep 1.0\nthermo 100\n')
            # dump            4 all dcd 1000    tes_chain_nvt.dcd
            fw.write('dump            4 all dcd 1000    ' +
                     file_name+'nvt.dcd\n')
            # dump_modify   4        unwrap yes
            fw.write('dump_modify   4        unwrap yes\nrun   1000\n')
            # write_restart a.data
            # write_data 100nvt.data
            fw.write('write_data '+file_name+'nvt.data\n')
            fw.close()

    def write_job_sh(self):
        fw = open('job.sh', 'w')
        fw.write('')
        for file_name in self.file_list:
            fw.write('mpirun -np 8 lmp < '+file_name +
                     'npt.in > '+file_name+'npt.log  \n')
        for file_name in self.file_list:
            fw.write('mpirun -np 8 lmp < '+file_name +
                     'nvt.in > '+file_name+'nvt.log  \n')
        # fw.close()
        # get npt\nvt.in
        fw.write('python step1.py\n')
        # nvt.dcd 2 unnvt.data
        fw.write('python step2.py\n')
        # unnvt.data 2 un.pdb
        fw.write('python step3.py\n')
        # get packmol.in and packmol
        fw.write('python step4.py\n')
        # packmol.pdb 2 data
        fw.write('moltemplate.sh -pdb tes_chain.pdb '+self.tes_chain.lt)
        fw.close()
        cmd = 'sh job.sh '
        os.system(cmd)
        # fw.close()

    def dcd2data(self):
        for file_name in self.file_list:
            u = MDAnalysis.Universe(
                file_name+"nvt.data", file_name + "nvt.dcd", format="LAMMPS")
            for ts in u.trajectory[-1:]:
                # if take_this_frame == True:
                with MDAnalysis.Writer(file_name+"un.data") as W:
                    W.write(u.atoms)
                    # print('yes')

    def data2pdb(self):
        for file_name in self.file_list:
            demo = Data2pdb(file_name+"un")
            demo.data2pdb()

    def pack_mol(self):
        fw = open('packmol.in', 'w')
        fw_linse = """tolerance 2.0
output tes_chain.pdb
filetype pdb

        """
        for file_name in self.file_list:
            """structure 100nvt.pdb
  number 1
  inside cube 0 0 0 50
end structure

            """
            fw_linse += 'structure '+file_name+'un.pdb\n  number 1\n  inside box 0 0 0 ' + \
                self.box_x + ' ' + self.box_y+' ' + self.box_z + '\nend structure\n\n'
        fw.write(fw_linse)
        fw.close()
        cmd = 'packmol < packmol.in '
        os.system(cmd)
    # def pdb2data(self):
