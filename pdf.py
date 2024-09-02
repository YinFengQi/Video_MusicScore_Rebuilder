import os
import configparser
# 定义文件夹路径和常量
current_directory = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join (current_directory,"recut") 

config = configparser.ConfigParser()# 读取每一页有多少行
config.read('config.ini')
constant=int(config['pdf']['lines'])


# 获取文件夹中所有的数字命名的PDF文件
pdf_files = sorted(
    [f for f in os.listdir(folder_path) if f.endswith('.pdf') and f[:-4].isdigit()],
    key=lambda x: int(x[:-4])
)

# 生成LaTeX文件
with open('output.tex', 'w', encoding='utf-8') as tex_file:
    tex_file.write("\\documentclass{ctexart}\n")
    tex_file.write("\\usepackage{graphicx}\n")
    tex_file.write("\\usepackage{geometry}\n")
    tex_file.write("\\geometry{left=1cm, right=1cm, top=1cm, bottom=1cm}\n")
    tex_file.write("\\title{山雀}\n")
    tex_file.write("\\begin{document}\n")
    tex_file.write("\\maketitle\n")

    total_files = len(pdf_files)
    full_pages = total_files // constant
    remainder = total_files % constant

    # 写入完整的页面
    for i in range(full_pages):
        tex_file.write("% 第{}页\n".format(i + 1))
        tex_file.write("\\noindent\n")
        for j in range(constant):
            tex_file.write("\\includegraphics[width=\\textwidth]{{{}}}\\vfill\n".format(pdf_files[i * constant + j]))
        tex_file.write("\\newpage\n\n")

    # 写入最后一页
    if remainder > 0:
        tex_file.write("% 第{}页\n".format(full_pages + 1))
        tex_file.write("\\noindent\n")
        for i in range(remainder - 1):
            tex_file.write("\\includegraphics[width=\\textwidth]{{{}}}\\vfill\n".format(pdf_files[full_pages * constant + i]))
        tex_file.write("\\includegraphics[width=\\textwidth]{{{}}}\\\\[1cm]\n".format(pdf_files[full_pages * constant + remainder - 1]))

    tex_file.write("\\end{document}\n")

print("LaTeX 文件已生成：output.tex")