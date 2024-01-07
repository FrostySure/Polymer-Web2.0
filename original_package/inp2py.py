"""
This py we get list from in.inp
[['model', 'disorder_chain', 'ncore= 6'], 
[['pc_h', 'pc', 'pc_t'], 'tes', '50', ['C7', 'C8'], 15.0, 7.996, ['1', '1', '2'], 43, 'random', ['100', '100', '50']], 
['y', ['1000', '5000']],
['y', ['10', '70', '90'], ['0.1', '0.1', '0.1']]]
"""
# all_list = [[style,re_style, ncore], [modeling_list], [annealing_list], [xrd], [Tg], [msd], [gcmc]]
# import ast

# 建模需要的参数 输入文件[car1 car2 car3],输出文件前缀，单链排布方式
# modeling_list = [[filename], outfilename, [npoly],
#                  linkatom, rs, rb, box, nchain, re_strcture, random, lbox]
# annealing_list = [y, [nptstep,nvtstep]]
# xrd_list = [y, [pres], [grid]]


class Inp2py():
    def __init__(self, inp):
        self.inp = inp

    def inp2py(self):
        fr = open(self.inp, 'r', encoding='UTF-8')
        from_inp_list = []
        modeling_list = []
        annealing_list = []
        xrd_list = []
        for line in fr:
            if '#' in line:
                line = line[:line.index('#')]

            if line[:len("style")] == 'style':  # 操作类型：model diff
                """
                modeling_list = [[filename], outfilename, [npoly], re_style, linkatom, re_strcture, rs, rb, box, nchain,  random, lbox]
                """
                # from_inp_list = [style, [modeling], [annealing], [xrd], ncore]
                if 'model' in line:  # 建模
                    from_inp_list.append('model')
                elif 'diff' in line:  # 计算扩散和吸附
                    from_inp_list.append('diff')
            # 进一步的细化类型 disorder_chain、diff、gcmc

            elif line[:len('re_style')] == 're_style':
                if 'disorder_chain' in line:  # 建模
                    from_inp_list.append('disorder_chain')
                elif 'diff' in line:  # 计算扩散
                    from_inp_list.append('diff')
                elif 'gcmc' in line:  # 计算吸附
                    from_inp_list.append('gcmc')
            elif line[:len('nus')] == 'nus':  # 基本结构单元数目
                pass
            #modeling_list = [[filename], outfilename, [npoly], [linkatom], rs, rb, box, nchain, re_strcture, random, lbox]
            elif line[:len('filename')] == 'filename':  # 高分子单体结构 filename= pc_h pc pc_t
                line = line.strip('filename=')
                line = line.strip('\n')
                line = line.split(' ')
                file_list = []
                for i in line:
                    if i:
                        file_list.append(i)
                modeling_list.append(file_list)
            # 高分子中混合的单体 mix_npoly_style=10 10 10
            elif line[:len('mix_npoly_style')] == 'mix_npoly_style':
                line = line.strip('mix_npoly_style=')
                line = line.strip('\n')
                if 'n' in line:
                    from_inp_list.append(['n'])
                else:
                    line = line.strip(' ')
                    line = line.split(';')
                    file_list = []
                    for i in line:
                        if i:
                            i = ast.literal_eval(i)
                            file_list.append(i)
                    from_inp_list.append(file_list)

            elif line[:len('outfilename')] == 'outfilename':  # 输出文件名
                line = line.strip('outfilename=')
                line = line.strip('\n')
                line = line.strip(' ')
                modeling_list.append(line)

            elif line[:len('nploy')] == 'nploy':  # 单链聚合度
                line = line.strip('nploy=')
                line = line.strip('\n')
                line = line.split(' ')
                nploy_list = []
                for i in line:
                    if i:
                        nploy_list.append(i)
                modeling_list.append(nploy_list)
            elif line[:len('linkatom')] == 'linkatom':  # 单体连接分子
                line = line.strip('linkatom=')
                line = line.strip('\n')
                line = line.split(' ')
                linkatom_list = []
                for i in line:
                    if i:
                        linkatom_list.append(i)
                modeling_list.append(linkatom_list)
            elif line[:len('rs')] == 'rs':  # 原子之间距离
                line = line.strip('rs=')
                line = line.strip('\n')
                line = line.strip(' ')
                modeling_list.append(float(line))
            elif line[:len('rb')] == 'rb':  # 化学键之间距离
                line = line.strip('rb=')
                line = line.strip('\n')
                line = line.strip(' ')
                modeling_list.append(float(line))
            elif line[:len('ncahin')] == 'ncahin':  # 聚合物链数
                line = line.strip('ncahin=')
                line = line.strip('\n')
                # line = line.strip(' ')
                line = line.split(' ')
                # line = line.split(';')
                # print(line)
                nchain_list = []
                for i in line:
                    if i:
                        i = ast.literal_eval(i)
                        nchain_list.append(i)
                modeling_list.append(nchain_list)
                # print(nchain_list)
                # modeling_list.append(int(line))
            elif line[:len('box')] == 'box':  # 单链盒子
                line = line.strip('box=')
                line = line.strip('\n')
                line = line.split(' ')
                box_list = []
                for i in line:
                    if i:
                        box_list.append(i)
                modeling_list.append(box_list)
            elif line[:len('re_strcture')] == 're_strcture':  # 聚合物是否有序
                line = line.strip('re_strcture=')
                line = line.strip('\n')
                line = line.strip(' ')
                modeling_list.append(line)

            elif line[:len('lbox')] == 'lbox':  # 体系盒子大小
                line = line.strip('lbox=')
                line = line.strip('\n')
                line = line.split(' ')
                lbox_list = []
                for i in line:
                    if i:
                        lbox_list.append(i)
                modeling_list.append(lbox_list)
                # from_inp_list.append(modeling_list)
            elif line[:len('annealing')] == 'annealing':  # 是否退火
                line = line.strip('annealing=')
                line = line.strip('\n')
                line = line.strip(' ')
                annealing_list.append(line)

            elif line[:len('step')] == 'step':  # 退火步数
                line = line.strip('step=')
                line = line.strip('\n')
                line = line.split(' ')
                step_list = []
                for i in line:
                    if i:
                        step_list.append(i)
                annealing_list.append(step_list)
                # print(annealing_list)
                # from_inp_list.append(annealing_list)

            elif line[:len('xrd_style')] == 'xrd_style':  # 是否计算出xrd图像
                line = line.strip('xrd_style=')
                line = line.strip('\n')
                line = line.strip(' ')
                xrd_list.append(line)
            elif line[:len('pres')] == 'pres':  # xrd参数1
                line = line.strip('pres=')
                line = line.strip('\n')
                line = line.split(' ')
                pres_list = []
                for i in line:
                    if i:
                        pres_list.append(i)
                xrd_list.append(pres_list)
            elif line[:len('grid')] == 'grid':  # xrd参数2
                line = line.strip('grid=')
                line = line.strip('\n')
                line = line.split(' ')
                grid_list = []
                for i in line:
                    if i:
                        grid_list.append(i)
                xrd_list.append(grid_list)
            elif line[:len('ncore')] == 'ncore':  # 使用核数
                line = line.strip('xrd_style=')
                line = line.strip('\n')
                line = line.strip(' ')
                from_inp_list.append(line)

        all_inp_list = [from_inp_list, modeling_list, annealing_list, xrd_list]
        # print(annealing_list)
        return all_inp_list

    def main(self):
        all_inp_list = Inp2py.inp2py(self)
        # print(all_inp_list)


# demo = Inp2py('in.inp')
# demo.main()
