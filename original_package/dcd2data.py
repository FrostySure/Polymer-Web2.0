import MDAnalysis


class Dcd2data():
    def __init__(self, data_list):
        self.data_list = data_list

    def dcd2data(self):
        for data_id in self.data_list:
            u = MDAnalysis.Universe(
                data_id+"_npt.data", data_id+"_npt.dcd", format="LAMMPS")
            # data_id+".data", data_id+".dcd", format="LAMMPS")
            for ts in u.trajectory[-1:]:
                # if take_this_frame == True:
                with MDAnalysis.Writer(data_id+'_un.data') as W:
                    W.write(u.atoms)
                    # print('yes')
                    # break


#demo_dcd2data = Dcd2data(['tes'])
#demo_dcd2data.dcd2data()
