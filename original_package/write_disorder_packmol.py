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
def write_packmol(disorder_nchain):
    xlo = None
    xhi = None
    ylo = None
    yhi = None

    # Read the 'order_system.data' file and extract the values
    with open('order_system.data', 'r') as data_file:
        for line in data_file:
            if 'xlo' in line:
                xlo, xhi = map(str, line.split()[:2])
            elif 'ylo' in line:
                ylo, yhi = map(str, line.split()[:2])

    fw = open('packmol.in', 'w')
    fw.write('tolerance 2.0\nfiletype pdb\noutput system.pdb\n\n')
    fw.write('filetype pdb\nstructure ' +
                'tes_un.pdb\n  number '+str(disorder_nchain[0])+'\n\n')
    fw.write('  inside box '+xlo+' '+ylo+' 0. ' +
                xhi+' '+yhi+' '+'1000\nend structure\n')         
demo=write_packmol(disorder_nchain=disorder_nchain)