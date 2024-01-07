import MDAnalysis
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

class Dcd2data():
    def __init__(self, data_list):
        self.data_list = data_list

    def dcd2data(self):
        for data_id in self.data_list:
            u = MDAnalysis.Universe(
                data_id+"_e.data", data_id+"_e.dcd", format="LAMMPS")
            # data_id+".data", data_id+".dcd", format="LAMMPS")
            for ts in u.trajectory[-1:]:
                # if take_this_frame == True:
                with MDAnalysis.Writer(data_id+'_un.data') as W:
                    W.write(u.atoms)
                    # print('yes')
                    # break

demo_dcd2data = Dcd2data(['a'])
demo_dcd2data.dcd2data()
