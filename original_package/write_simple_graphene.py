from tkinter import Y


class Write_graphene_wall:
    def __init__(self, item_x_y, item_num_layer):
        self.x = item_x_y[0]
        self.y = item_x_y[1]
        self.layer = item_num_layer

    def get_x_n(self):
        layer_x = float(self.x)
        x_n = int(layer_x/2.4595121467478)
        layer_y = float(self.y)
        # y_n = int(layer_y/2.13)*2
        y_n_1 = int((layer_y-0.5*1.42)/(3*1.42)*4+2)
        y_minus = 3-y_n_1 % 3
        y_n = y_n_1+y_minus
        n_list = [x_n, y_n]
        return n_list

    def write_graphene(self):
        fw = open("graphene.lt", 'w')
        data = """import "compass.lt"
Graphene inherits COMPASS{

  # atomID   molID     atomType charge      x              y         z
  write("Data Atoms") {
    $atom:C  $mol:...  @atom:c3a   0.0   0.61487803668695  0.355   0.0000
  }




  }"""
        fw.write(data)
        fw.close()



    def write_graphene_outside_wall(self, fw_name):
        n_list = Write_graphene_wall.get_x_n(self)
        x_n = n_list[0]
        y_n = n_list[1]
        # print(x_n, y_n)

        # fw = open('graphene_walls.lt', 'w')
        fw = open(fw_name, 'w')
        fw.write('import "graphene.lt"\n')
        fw.write("Wall inherits COMPASS{\n")

        # 每种类型的原子均距前一个原子x方向距离2.4595121467478
        side_a = 1.42
        x_move_1 = 1.2297560733739  # 二分之根号三*边长
        x_move_2 = 2.13  # 3a/2
        x_move = 2.4595121467478  # 根号三*边长

        mon_id = 0

        for i in range(y_n):  # n行
            if i % 4 == 0:  # 第4n+1行
                for j in range(x_n):  # n列
                    x = 1.2297560733739+j*x_move
                    y = (i/4)*1.42*3
                    fw.write(
                        'mon['+str(mon_id)+'] = new Graphene.move('+str(x)+', '+str(-y)+', 0)\n')
                    mon_id += 1
            elif (i-1) % 4 == 0:  # 第4n+2行
                for j in range(x_n+1):  # n+1列
                    x = j*x_move
                    y = 0.5*1.42+(i-1)/4*1.42*3
                    fw.write(
                        'mon['+str(mon_id)+'] = new Graphene.move('+str(x)+', '+str(-y)+', 0)\n')
                    mon_id += 1

            elif (i-2) % 4 == 0:  # 第4n+3行
                for j in range(x_n+1):  # n+1列
                    x = j*x_move
                    y = 1.5*1.42+(i-2)/4*1.42*3
                    fw.write(
                        'mon['+str(mon_id)+'] = new Graphene.move('+str(x)+', '+str(-y)+', 0)\n')
                    mon_id += 1

            elif (i-3) % 4 == 0:  # 第4n+4行
                for j in range(x_n):
                    x = 1.2297560733739+j*x_move
                    y = 1.42*2+(i-3)/4*1.42*3
                    fw.write(
                        'mon['+str(mon_id)+'] = new Graphene.move('+str(x)+', '+str(-y)+', 0)\n')
                    mon_id += 1
        n_max = mon_id
        fw.write("\nwrite('Data Bond List') {\n")
        bond_id = 1
        mon_id = 0

        for i in range(y_n):
            if mon_id < n_max:
                if (i) % 4 == 0:  # 第4n+1行
                    for j in range(x_n):
                        if mon_id-x_n > -1:
                            fw.write("         $bond:b"+str(bond_id) +
                                     "  $atom:mon["+str(mon_id)+"]/C $atom:mon["+str(mon_id-x_n)+"]/C\n")
                            bond_id += 1
                        if mon_id+x_n+1 < n_max:
                            fw.write("         $bond:b"+str(bond_id) +
                                     "  $atom:mon["+str(mon_id)+"]/C $atom:mon["+str(mon_id+x_n+1)+"]/C\n")
                            bond_id += 1
                            mon_id += 1
                elif (i-1) % 4 == 0:  # 第4n+2行
                    for j in range(x_n+1):
                        if j == x_n:
                            mon_id += 1

                        else:
                            if mon_id-x_n > -1:

                                fw.write("         $bond:b"+str(bond_id) +
                                         "  $atom:mon["+str(mon_id)+"]/C $atom:mon["+str(mon_id-x_n)+"]/C\n")
                                bond_id += 1
                                mon_id += 1
                elif (i-2) % 4 == 0:  # 第4n+3行
                    for j in range(x_n+1):

                        fw.write("         $bond:b"+str(bond_id) +
                                 "  $atom:mon["+str(mon_id)+"]/C $atom:mon["+str(mon_id-x_n-1)+"]/C\n")
                        bond_id += 1
                        mon_id += 1
                elif (i-3) % 4 == 0:  # 第4n+4行
                    for j in range(x_n):

                        fw.write("         $bond:b"+str(bond_id) +
                                 "  $atom:mon["+str(mon_id)+"]/C $atom:mon["+str(mon_id-x_n-1)+"]/C\n")
                        bond_id += 1
                        fw.write("         $bond:b"+str(bond_id) +
                                 "  $atom:mon["+str(mon_id)+"]/C $atom:mon["+str(mon_id-x_n)+"]/C\n")
                        bond_id += 1
                        mon_id += 1

        fw.write('}\n}')
        fw.close()



    def write_graphene_outside_system(self, fw):
        fw = open(fw, 'w')
        fw.write('import "graphene_walls_outside.lt"\nwall = new Wall [1]\n                ['+str(
            self.layer)+'].move(0,0,3.34)\n')
        data = """write_once("Data Boundary") {
    0.0  52  xlo xhi
    0.0  52  ylo yhi
    0.0  3.34   zlo zhi
}
"""
        fw.write(data)
        fw.close()

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

        elif key == 'graphene':
            graphene = list(map(str, value.split()))        

        elif key == 'silicon':
            filename = list(map(str, value.split()))

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
with open('final_300K.data', 'r') as data_file:
    for line in data_file:
        if 'xlo' in line:
            xlo, xhi = map(float, line.split()[:2])
            x=xhi-xlo
        elif 'ylo' in line:
            ylo, yhi = map(float, line.split()[:2])
            y=ylo-yhi
demo_wall = Write_graphene_wall([x, y], float(graphene))
# demo_wall = Write_graphene_wall([10, 10], 1)
demo_wall.write_graphene()
demo_wall.write_graphene_outside_wall(fw_name='graphene_walls_outside.lt')
demo_wall.write_graphene_outside_system(fw='graphene_all.lt')