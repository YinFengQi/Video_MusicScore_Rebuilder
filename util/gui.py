import tkinter as tk

class my_gui(tk.Tk):
    '''
    自定义 gui 类, 具有 new_folder 等 property 类型的方法 

    如下代码
    >>> a = my_gui()
    >>> a.mainloop()
    >>> a.new_folder 
    
    会返回 boolean 值, 表示复选框 new_folder 是否被选中
    '''
    def __init__(self):
        super().__init__()

        self.title("Video Score Rebuilder")

        # 滚动条
        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 文本框
        text_box = tk.Text(self, yscrollcommand=scrollbar.set)
        text_box.pack(side=tk.LEFT, fill=tk.BOTH)
        # 文本框内容
        with open('config.ini', 'r') as f:
            text_box.insert(tk.END, f.read())


        # 复选框布尔变量    作为私有对象
        self.__new_folder = tk.BooleanVar()
        self.__capture    = tk.BooleanVar()
        self.__remove     = tk.BooleanVar()
        self.__stitch     = tk.BooleanVar()
        self.__detect     = tk.BooleanVar()
        self.__recut      = tk.BooleanVar()
        self.__pdf        = tk.BooleanVar()

        # 创建复选框
        tk.Checkbutton(self, text="New Folder", variable=self.__new_folder).pack()
        tk.Checkbutton(self, text="Capture",    variable=self.__capture   ).pack()
        tk.Checkbutton(self, text="Remove",     variable=self.__remove    ).pack()
        tk.Checkbutton(self, text="Stitch",     variable=self.__stitch    ).pack()
        tk.Checkbutton(self, text="Detect",     variable=self.__detect    ).pack()
        tk.Checkbutton(self, text="Recut",      variable=self.__recut     ).pack()
        tk.Checkbutton(self, text="PDF",        variable=self.__pdf       ).pack()

        # 运行脚本按钮
        tk.Button(self, text="Run Script", command=self.destroy).pack()


    # 定义公开对象          不能像这样定义:   self.new_folder = self.__new_folder.get()
    @property
    def new_folder(self):
        return self.__new_folder.get()
    @property
    def capture(self):
        return self.__capture.get()
    @property
    def remove(self):
        return self.__remove.get()
    @property
    def stitch(self):
        return self.__stitch.get()
    @property
    def detect(self):
        return self.__detect.get()
    @property
    def recut(self):
        return self.__recut.get()
    @property
    def pdf(self):
        return self.__pdf.get()
    


if __name__ == '__main__':
    import auxiliary
    auxiliary.message_dont_run(__file__)