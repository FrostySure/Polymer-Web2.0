import re
from pymatgen.io.lammps.data import LammpsData
from pymatgen.core.structure import Structure

# 读取LAMMPS数据文件
data = LammpsData.from_file("final_300K.data")

# 将LAMMPS数据结构转换为pymatgen的Structure对象
structure = data.structure

# 生成CIF文件
cif_str = structure.to(fmt="cif")

# 将CIF字符串写入文件
with open("final_300K.cif", "w") as f:
    f.write(cif_str)
