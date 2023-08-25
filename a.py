from tkinter import *
from tree import Node
from tkinter import ttk
from storage import *

class Application(Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.bind("<Configure>", self.update_scroll_region)
         # 自定义标签样式，设置左对齐
        self.style = ttk.Style()
        self.style.configure("Tree.TLabel", anchor="w")
        self.root_objective = Node("根节点")
        self.current_node = None
        self.createWidget()
        self.canvas.update_idletasks()  # 等待窗口调整完成
        

    def createWidget(self):
        """创建组件"""
        # 创建添加节点的按钮
        self.add_button = Button(self.master, text="添加节点", command=self.add_objective)
        self.add_button.grid(row=0, column=0)
        
        # 创建删除节点的按钮

        self.remove_button = Button(self.master, text="删除节点", command=self.remove_objective)
        self.remove_button.grid(row=0, column=1)

        # 创建清除选择的按钮
        self.clear_button = Button(self.master, text="清除选择", command=self.clear_selection)
        self.clear_button.grid(row=0, column=2)

        # 创建保存树的按钮
        self.save_button = Button(self.master, text="保存树", command=self.activate_save)
        self.save_button.grid(row=1, column=2)
        
        # 创建加载树的按钮
        self.load_button = Button(self.master, text="加载树", command=self.load_tree)
        self.load_button.grid(row=1, column=0)
        
        # 创建用于输入目标名称的文本框
        self.entry = Entry(self.master)
        self.entry.grid(row=1, column=1)
        self.entry.bind("<Return>",lambda event:self.add_objective())
        self.entry.bind("<Shift-Return>", lambda event: self.entry.insert(END, '\n'))
        
        # 创建垂直滚动条
        self.vertical_scrollbar = ttk.Scrollbar(self.master, orient="vertical")
        self.horizontal_scrollbar = ttk.Scrollbar(self.master, orient="horizontal")
        
        # 创建一个Canvas作为容器
        self.canvas = Canvas(self.master, yscrollcommand=self.vertical_scrollbar.set,xscrollcommand=self.horizontal_scrollbar.set)
        self.canvas.grid(row=2, column=1)


        # 将垂直滚动条与Canvas关联
        self.vertical_scrollbar.config(command=self.canvas.yview)
        self.vertical_scrollbar.grid(row=2, column=2, sticky="ns")

        # 创建水平滚动条
        self.horizontal_scrollbar.config(command=self.canvas.xview)
        self.horizontal_scrollbar.grid(row=3, column=0, columnspan=3, sticky="ew")

        # 将Canvas作为TreeFrame的父容器
        self.tree_frame = ttk.Frame(self.master)
        self.tree_frame.bind("<Configure>", self.update_scroll_region)
        self.canvas.create_window((0, 0), window=self.tree_frame, anchor="nw")
        
    def update_scroll_region(self,event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_tree_ui(self):
        # 清除目标树UI
        for widget in self.tree_frame.winfo_children():
            widget.destroy()
        # 重新绘制目标树UI
        self.draw_tree_ui(self.root_objective)
        self.update_scroll_region()

    def edit_node(self, label, node):
        entry = Entry(self.tree_frame)
        entry.insert(0, node.name)
        entry.bind("<Return>", lambda event, e=entry, n=node: self.update_node_name(e, n))
        entry.bind("<FocusOut>", lambda event, e=entry, l=label, n=node: self.update_node_name_on_focus_out(e, l, n))
        entry.grid(row=label.grid_info()["row"], column=label.grid_info()["column"])
        entry.focus_set()
        label.grid_forget()

    def update_node_name(self, entry, node):
        new_name = entry.get()
        node.name = new_name
        entry.destroy()
        self.update_tree_ui()

    def update_node_name_on_focus_out(self, entry, label, node):
        self.update_node_name(entry, node)
        label.grid(row=node.grid_info()["row"], column=node.grid_info()["column"])

    def draw_tree_ui(self, node, indent=""):
        label_text = indent + "|── " + node.name
        label = ttk.Label(self.tree_frame, text=label_text, style="Tree.TLabel")
        label.pack(anchor=W)
        label.bind("<Button-1>", lambda event,node=node: self.select_node(node))
        label.bind("<Double-Button-1>", lambda event, label=label, node=node: self.edit_node(label, node))  # 双击进入编辑模式
        for i, child_node in enumerate(node.children):
            child_indent = indent + "│    "
            self.draw_tree_ui(child_node, indent=child_indent)

    def select_node(self, node):
        self.entry.delete(0, END)  # 清空输入框
        self.entry.insert(END, node.name)  # 在输入框中显示节点名称
        self.current_node = node  # 设置当前节点为选择的节点

    def clear_selection(self):
        self.entry.delete(0, END)  # 清空输入框
        self.current_node = None  # 清除当前节点的选择

    # 添加节点的按钮和事件处理
    def add_objective(self):
        global saved_once
        saved_once = False
        name = self.entry.get()  # 获取输入框中的内容作为目标名称
        self.entry.delete(0, END)  # 清空输入框
        if self.current_node is None:  # 如果当前节点为空，说明是根节点
            self.root_objective.add_child(name)
        else:
            self.current_node.add_child(name)
        # 更新UI显示
        self.update_tree_ui()

    # 删除节点的按钮和事件处理
    def remove_objective(self):
        if self.current_node is None:
            return
        global saved_once
        saved_once = False
        self.current_node.remove_node()
        self.clear_selection()  # 清除当前选择
        self.update_tree_ui()  # 更新UI显示

    #保存树的函数
    def activate_save(self):
        global saved_once
        if not saved_once:
            filename = get_save_filename()
            if filename:
                save_tree_with_unique_name(self.root_objective, filename)
    #关闭窗口自动保存         
    def on_closing(self):
        global saved_once
        if not saved_once:
            save_choice = ask_to_save_tree()
            if save_choice == "save":
                filename = get_save_filename()
                if filename:
                    save_tree_with_unique_name(self.root_objective, filename)
                else:
                    return  # 用户取消保存
            elif save_choice == "cancel":
                return  # 用户取消关闭窗口

        self.master.destroy()
        
    def load_tree_from_file(self, filename):
        loaded_tree = load_tree(filename)
        self.root_objective = loaded_tree
        self.update_tree_ui()

    def load_tree(self):
        filename = filedialog.askopenfilename(initialdir=os.getcwd(), defaultextension=".pkl", filetypes=[("Pickle Files", "*.pkl")])
        if filename:
            self.load_tree_from_file(filename)


if __name__ == "__main__":
    root = Tk()
    root.geometry("800x600")  # 设置窗口初始大小
    root.grid_rowconfigure(2, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.title("ui test")
    app = Application(root)
    app.update_tree_ui()
    root.protocol("WM_DELETE_WINDOW", app.on_closing)  # 绑定窗口关闭事件
    root.mainloop()
    
#树转图
#图转树
#分析引擎
#爬虫