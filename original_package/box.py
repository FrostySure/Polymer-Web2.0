import os


class Get_box_size():
    def __init__(self, data_list):
        self.data_list = data_list

    def get_atom(line):
        cnt = 0
        for i in line:
            if 'Atoms' in i:
                break
            cnt += 1
        return cnt

    def get_box_size(self):
        boxs = []
        x_min = 0
        x_max = 0
        y_min = 0
        y_max = 0
        z_min = 0
        z_max = 0
        for data in self.data_list:
            data = data + '.data'
            fr = open(data, 'r')
            line = fr.readlines()
            fr.close()
            cnt = Get_box_size.get_atom(line)
            fr = open(data, 'r')
            # atoms = []

            for line in fr.readlines()[cnt+2:]:
                if line == '\n':
                    break
                data = []
                line = line.split(' ')
                for string in line:
                    if string:
                        data.append(string)
                if x_min > float(data[4]):
                    x_min = float(data[4])
                if x_max < float(data[4]):
                    x_max = float(data[4])
                if y_min > float(data[5]):
                    y_min = float(data[5])
                if y_max < float(data[5]):
                    y_max = float(data[5])
                if z_min > float(data[6]):
                    z_min = float(data[6])
                if z_max < float(data[6]):
                    z_max = float(data[6])
                # atoms.append(data[4:])
            x_min, x_max, y_min, y_max, z_min, z_max = x_min - \
                2.5, x_max+2.5, y_min-2.5, y_max+2.5, z_min-2.5, z_max+2.5
            # print(x_min, x_max, y_min, y_max, z_min, z_max)
            fr.close()
            box = [x_min, x_max, y_min, y_max, z_min, z_max]
            boxs.append(box)
        return boxs

    def re_box_size(self):
        data_id = 0
        boxs = Get_box_size.get_box_size(self)
        for data in self.data_list:
            data_name = data+'.data'
            box = boxs[data_id]
            fr = open(data_name, 'r')
            fw = open(data_name[:-5]+'_re.data', 'w')
            for line in fr:
                if 'xlo' in line:
                    x_min = box[0]
                    x_max = box[1]
                    line = ' '+str(x_min)+' '+str(x_max)+' xlo xhi\n'
                if 'ylo' in line:
                    y_min = box[2]
                    y_max = box[3]
                    line = ' '+str(y_min)+' '+str(y_max)+' ylo yhi\n'

                if 'zlo' in line:
                    z_min = box[4]
                    z_max = box[5]
                    line = ' '+str(z_min)+' '+str(z_max)+' zlo zhi\n'
                fw.write(line)
            data_id += 1
            fr.close()
            re_name = data_name[:-5]+'_re.data'
            cmd = 'mv '+re_name+' '+data_name
            os.system(cmd)

demo = Get_box_size(['tes10'])
demo.re_box_size()
