import write_lts
import dcd2data
import packmol
import data2pdb
import os


class Workflow_pure():
    def __init__(self, output_file, pc_list, npoly,  linkatoms, box_size_list, tes_chain,  mix_style='n',npt_step=1000, nvt_step=5000, ncore='6'):
        self.pc_list = pc_list
        self.npoly = npoly
        self.tes_chain = tes_chain
        self.box_size_list = box_size_list
        self.linkatoms = linkatoms
        self.mix_style = mix_style
        self.output_file = output_file
        self.ncore = ncore
        self.npt_step = npt_step
        self.nvt_step = nvt_step

        # self.chain_style = chain_style
        # self.system_style = system_style

    def step_1(self):
        # 写高分子lt文件
        demo_model = write_lts.Car2lt(pc_list=self.pc_list, npoly=self.npoly, tes_chain=self.tes_chain, box_size_list=self.box_size_list,
                                        lbox_size_list=self.box_size_list,linkatom=self.linkatoms, mix_style=self.mix_style, output_file=self.output_file)
        demo_model.main()

    def step_2(self):
        demo_mol_sh = mol_sh.Moltemplate_sh(
            npoly=self.npoly, output_file=self.output_file)
        demo_mol_sh.sh_moltemplate()
        data_list = []

        for poly in self.npoly:
            poly = str(poly)
            data = self.output_file + poly
            data_list.append(data)
        demo_npt = write_npt.Write_npt(data_list=data_list,
                                       npt_step=self.npt_step, ncore=self.ncore)
        demo_npt.write_npt_in()
        demo_npt.write_sub_npt_sh()
        demo_nvt = write_nvt.Write_nvt(data_list=data_list,
                                       nvt_step=self.nvt_step, ncore=self.ncore)
        demo_nvt.write_nvt_in()
        demo_nvt.write_sub_nvt_sh()

    def step_3(self):
        data_list = []
        for poly in self.npoly:
            poly = str(poly)
            data = self.output_file + poly
            data_list.append(data)

    # step 3
    # dcd2data

        demo_dcd2data = dcd2data.Dcd2data(data_list=data_list)
        demo_dcd2data.dcd2data()

    def step_4(self):
        data_list = []
        for poly in self.npoly:
            poly = str(poly)
            data = self.output_file + poly
            data_list.append(data)

        # step 4
        # data2pdb
        new_data_list = []
        for data_id in data_list:
            new_data_id = data_id+'_un'
            new_data_list.append(new_data_id)
        for new_data_id in new_data_list:
            demo_data2pdb = data2pdb.Data2pdb(data=new_data_id)
            demo_data2pdb.data2pdb()

    def step_5(self):
        data_list = []
        for poly in self.npoly:
            poly = str(poly)
            data = self.output_file + poly
            data_list.append(data)

        # step 4
        # data2pdb
        new_data_list = []
        for data_id in data_list:
            new_data_id = data_id+'_un'
            new_data_list.append(new_data_id)
        # step 5
        # packmol
        # print(new_data_list)
        demo_packmol = packmol.Packmol(
            pdb_list=new_data_list, pdb_num_list=self.tes_chain, lbox_list=self.lbox_size_list)
        demo_packmol.write_packmol_in()
        demo_packmol.write_sub_packmol_in()
        demo_packmol.write_system_sh()

    def step_6(self):
        data_list = []
        for poly in self.npoly:
            poly = str(poly)
            data = self.output_file + poly
            data_list.append(data)
            new_data_list = []
            for data_id in data_list:
                new_data_id = data_id+'_un'
                new_data_list.append(new_data_id)
            demo_nvt = write_nvt.Write_nvt(data_list=data_list,
                                           nvt_step=self.nvt_step, ncore=self.ncore)
            demo_nvt.sub_system_npt_nvt_sh()

    def main():
        fw = open('workflow_composite_inside.sh', 'w')
        sh_data = """python step1.py &&
sh sub_moltemplate.sh 
python step2.py &&
sh npt.sh
sh nvt.sh
python step3.py &&
python step4.py &&
python step5.py &&
sh packmol.sh
sh system.sh 
python step6.py &&
sh system_sh.sh """
        fw.write(sh_data)
        os.system('nohup sh workflow_composite_inside.sh > polymer.log &')
