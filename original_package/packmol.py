import os
# Initialize variables




class Packmol():
    def __init__(self, pdb_chain_list, pdb_num_list, lbox_list, mix_box_list='', sio2_num='', graphene_num='', sio2_list=[], graphene_list=[]):
        self.pdb_chain_list = pdb_chain_list
        self.pdb_num_list = pdb_num_list
        self.lbox_list = lbox_list
        self.mix_box_list = mix_box_list
        self.sio2_list = sio2_list
        self.graphene_list = graphene_list
        self.sio2_num = sio2_num
        self.graphene_num = graphene_num

    def get_box(self):
        xlo = None
        xhi = None
        ylo = None
        yhi = None

        # Read the 'order_system.data' file and extract the values
        with open('order_system.data', 'r') as data_file:
            for line in data_file:
                if 'xlo' in line:
                    xlo, xhi = map(float, line.split()[:2])
                elif 'ylo' in line:
                    ylo, yhi = map(float, line.split()[:2])
        return(xlo,xhi,ylo,yhi)

    def write_packmol_in(self):
        fw = open('packmol.in', 'w')
        fw.write('tolerance 2.0\nfiletype pdb\noutput system.pdb\n\n')
        id = 0
        xlo,xhi,ylo, yhi=Packmol.get_box(self)
        for i in range(len(self.pdb_chain_list)):
            fw.write('filetype pdb\nstructure ' +
                     str(self.pdb_chain_list[id])+'.pdb\n  number '+str(self.pdb_num_list[id])+'\n\n')
            # fw.write('  inside box 0. 0. 0. ' +
            #          self.lbox_list[0]+' '+self.lbox_list[1]+' '+self.lbox_list[2]+'\nend structure\n')
            fw.write('  inside box '+xlo+' '+ylo+' 0. ' +
                     xhi+' '+yhi+' '+'1000\nend structure\n')         
            id += 1
        if self.sio2_num and self.sio2_list:
            sio2_num_id = 0
            sio2_id = 0
            for sio2 in self.sio2_list:
                fw.write('filetype pdb\nstructure ' +
                         str(self.sio2_list[sio2_id])+'.pdb\n  number '+str(self.sio2_num[sio2_num_id])+'\n\n')
                fw.write('  inside box 0. 0. 0. ' +
                         self.mix_box_list[0]+' '+self.mix_box_list[1]+' '+self.mix_box_list[2]+'\nend structure\n')
                sio2_num_id += 1
                sio2_id += 1
        if self.graphene_num and self.graphene_list:
            graphene_num_id = 0
            graphene_id = 0
            for graphene in self.graphene_list:
                fw.write('filetype pdb\nstructure ' +
                         str(self.graphene_list[graphene_id])+'.pdb\n  number '+str(self.graphene_num[graphene_num_id])+'\n\n')
                fw.write('  inside box 0. 0. 0. ' +
                         self.mix_box_list[0]+' '+self.mix_box_list[1]+' '+self.mix_box_list[2]+'\nend structure\n')
                graphene_num_id += 1
                graphene_id += 1
        fw.close()

    def write_sub_packmol_in(self):
        fw = open('packmol.sh', 'w')
        fw.write('packmol < packmol.in > packmol.log \n ')
        fw.close()
        cmd = 'sh packmol.sh'

    def write_system_sh(self):
        fw = open('system.sh', 'w')
        fw.write('moltemplate.sh -pdb system.pdb system.lt')
        fw.close()
     #   os.system(cmd)

