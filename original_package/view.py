import py3Dmol

def generate_html(pdb_file):
    # 读取 PDB 文件内容
    with open(pdb_file, 'r') as f:
        pdb_contents = f.read()

    # 创建一个 py3Dmol 的视图对象
    view = py3Dmol.view(width=600, height=400)

    # 从 PDB 文件中添加分子结构
    view.addModel(pdb_contents, 'pdb')

    # 设置视图样式和显示选项
    view.setStyle({'cartoon': {'color': 'spectrum'}})
    view.setBackgroundColor('white')
    view.zoomTo()
    view.show()

    # 生成 HTML 代码
    html = view.render()

    return html
