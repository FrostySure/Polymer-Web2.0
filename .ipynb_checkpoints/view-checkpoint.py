import py3Dmol

# 创建 3Dmol 视图
viewer = py3Dmol.view(width=400, height=400)

# 从 PDB 文件加载分子数据
with open("tes_un.pdb", "r") as pdb_file:
    pdb_data = pdb_file.read()
viewer.addModel(pdb_data, "pdb")

# 设置分子样式（可选）
viewer.setStyle({"stick": {}})  # 设置分子样式

# 在 HTML 页面中显示视图
viewer.zoomTo()
viewer.show()
