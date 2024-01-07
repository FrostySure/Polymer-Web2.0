
import ast


class Inp2py():
    def __init__(self, inp):
        self.inp = inp

    def inp2py(self):
        fr = open(self.inp, 'r', encoding='UTF-8')
        # all_list=[[ncore,outfilename],[model_list],[annealing_list],[xrd_list]]
        from_inp_list = []
        modeling_list = []
        annealing_list = []
        xrd_list = []
        for line in fr:
            if '#' in line:
                line = line[:line.index('#')]
            if line[:len('ncore')] == 'ncore':  # 使用核数
                line = line.lstrip('ncore=')
                line = line.strip('\n')
                line = line.strip(' ')
                from_inp_list.append(line)
            elif line[:len('outfilename')] == 'outfilename':  # 输出文件名
                line = line.lstrip('outfilename=')
                line = line.strip('\n')
                line = line.strip(' ')
                from_inp_list.append(line)
            elif line[:len('filename')] == 'filename':  # 高分子单体结构 filename= pc_h pc pc_t
                line = line.lstrip('filename=')
                line = line.strip('\n')
                line = line.split(' ')
                file_list = []
                for i in line:
                    if i:
                        file_list.append(i)
                modeling_list.append(file_list)
            elif line[:len('re_style')] == 're_style':
                if 'disorder_chain' in line:  # 建模
                    from_inp_list.append('disorder_chain')
                elif 'diff' in line:  # 计算扩散
                    from_inp_list.append('diff')
                elif 'gcmc' in line:  # 计算吸附
                    from_inp_list.append('gcmc')
            # elif line[:len('nus')] == 'nus':  # 基本结构单元数目
            #     pass
            #modeling_list = [[filename], outfilename, [npoly], [linkatom], rs, rb, box, nchain, chain_style, random, lbox]
            elif line[:len('npoly')] == 'npoly':  # 单链聚合度
                line = line.lstrip('nploy=')
                line = line.strip('\n')
                line = line.split(' ')
                nploy_list = []
                for i in line:
                    if i:
                        nploy_list.append(i)
                modeling_list.append(nploy_list)
            # 高分子中混合的单体 mix_npoly_style=10 10 10
            elif line[:len('mix_npoly_style')] == 'mix_npoly_style':
                line = line.lstrip('mix_npoly_style=')
                line = line.strip('\n')
                if 'n' in line:
                    modeling_list.append(['n'])
                else:
                    line = line.strip(' ')
                    line = line.split(';')
                    file_list = []
                    for i in line:
                        if i:
                            i = ast.literal_eval(i)
                            file_list.append(i)
                    modeling_list.append(file_list)
            elif line[:len('chain_style')] == 'chain_style':  # 单链是否有序
                line = line.lstrip('chain_style=')
                line = line.strip('\n')
                line = line.strip(' ')
                modeling_list.append(line)

            elif line[:len('linkatom')] == 'linkatom':  # 单体连接分子
                line = line.lstrip('linkatom=')
                line = line.strip('\n')
                line = line.split(' ')
                linkatom_list = []
                for i in line:
                    if i:
                        linkatom_list.append(i)
                modeling_list.append(linkatom_list)

            elif line[:len('nchain')] == 'nchain':  # 聚合物链数
                line = line.lstrip('ncahin=')
                line = line.strip('\n')
                line = line.split(' ')
                # line = line.split(';')
                nchain_list = []
                for i in line:
                    if i:
                        i = ast.literal_eval(i)
                        nchain_list.append(int(i))
                modeling_list.append(nchain_list)
                # modeling_list.append(int(line))

                # from_inp_list.append(modeling_list)
            elif line[:len('system_style')] == 'system_style':  # 聚合物是否有序
                line = line.lstrip('system_style=')
                line = line.strip('\n')
                line = line.strip(' ')
                modeling_list.append(line)
            elif line[:len('composite_style')] == 'composite_style':  # 是否复合
                line = line.lstrip('composite_style')
                line = line.strip('=')
                line = line.strip('\n')
                line = line.strip(' ')
                modeling_list.append(line)

            elif line[:len('composite_item')] == 'composite_item':  # 二维复合材料类型
                line = line.lstrip('composite_item')
                line = line.strip('=')
                line = line.strip('\n')
                line = line.strip(' ')

                line = line.split(',')

                # composite_item_list = []
                # # for i in line:
                # for j in line:
                #     if j:
                #         j = j.split(',')
                #         composite_item_list.append(j)
                modeling_list.append(line)
            elif line[:len('item_x_y')] == 'item_x_y':  # 二维复合材料大小
                line = line.lstrip('item_x_y')
                line = line.strip('=')
                line = line.strip('\n')
                line = line.strip(' ')
                line = line.split(';')
                item_x_y_list = []
                if 'auto' in line:
                    modeling_list.append('auto')
                else:
                    for i in line:
                        if i:
                            i = ast.literal_eval(i)
                            item_x_y_list.append(i)
                    modeling_list.append(item_x_y_list)
            elif line[:len('item_num')] == 'item_num':  # 二维复合材料数目和层数
                line = line.lstrip('item_num=')
                line = line.strip('\n')
                line = line.strip(' ')
                line = line.split(';')
                item_num_layer_list = []
                for i in line:
                    if i:
                        i = ast.literal_eval(i)
                        item_num_layer_list.append(i)
                modeling_list.append(item_num_layer_list)
            elif line[:len('lbox')] == 'lbox':  # 体系盒子大小
                line = line.lstrip('lbox=')
                line = line.strip('\n')
                line = line.split(' ')
                lbox_list = []
                for i in line:
                    if i:
                        lbox_list.append(i)
                modeling_list.append(lbox_list)
            elif line[:len('step')] == 'step':  # 体系盒子大小
                line = line.lstrip('step=')
                line = line.strip('\n')
                line = line.split(' ')
                step_list = []
                for i in line:
                    if i:
                        step_list.append(i)
                modeling_list.append(step_list)
            elif line[:len('item_site')] == 'item_site':  # 二维复合材料数目和层数
                line = line.lstrip('item_site=')
                line = line.strip('\n')
                line = line.strip(' ')
                line = line.split(';')
                item_site_list = []
                for i in line:
                    if i:
                        i = ast.literal_eval(i)
                        item_site_list.append(i)
                modeling_list.append(item_site_list)

            elif line[:len('annealing')] == 'annealing':  # 是否退火
                line = line.lstrip('annealing=')
                line = line.strip('\n')
                line = line.strip(' ')
                annealing_list.append(line)

            elif line[:len('r_style')] == 'r_style':  # 退火步数
                line = line.lstrip('r_style=')
                line = line.strip('\n')
                line = line.strip(' ')
                annealing_list.append(line)
            elif line[:len('d_style')] == 'd_style':  # 退火步数
                line = line.lstrip('d_style=')
                line = line.strip('\n')
                line = line.strip(' ')
                annealing_list.append(line)

            elif line[:len('rise_step')] == 'rise_step':  # 是否计算出xrd图像
                line = line.lstrip('rise_step=')
                line = line.strip('\n')
                line = line.strip(' ')
                annealing_list.append(line)
            elif line[:len('rise_equil_step')] == 'rise_equil_step':  # xrd参数1
                line = line.lstrip('rise_equil_step=')
                line = line.strip('\n')
                line = line.strip(' ')
                annealing_list.append(line)

            elif line[:len('down_step')] == 'down_step':  # 是否退火
                line = line.lstrip('down_step=')
                line = line.strip('\n')
                line = line.strip(' ')
                annealing_list.append(line)
            elif line[:len('down_equil_step')] == 'down_equil_step':  # 是否退火
                line = line.lstrip('down_equil_step=')
                line = line.strip('\n')
                line = line.strip(' ')
                annealing_list.append(line)
            elif line[:len('anneal_tmp_start')] == 'anneal_tmp_start':  # 是否退火
                line = line.lstrip('anneal_tmp_start=')
                line = line.strip('\n')
                line = line.strip(' ')
                annealing_list.append(line)
            elif line[:len('anneal_tmp_down')] == 'anneal_tmp_down':  # 是否退火
                line = line.lstrip('anneal_tmp_down=')
                line = line.strip('\n')
                line = line.strip(' ')
                annealing_list.append(line)
        all_inp_list = [from_inp_list, modeling_list, annealing_list]
        # print(all_inp_list)
        return all_inp_list

    def main(self):
        all_inp_list = Inp2py.inp2py(self)
        # print(all_inp_list[1])


# demo = Inp2py('in.inp')
# demo.main()
