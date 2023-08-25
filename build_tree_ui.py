import tkinter as tk
from tkinter import ttk
from tree import Node
from storage import saved_once,get_save_filename,save_tree_with_unique_name
def create_ui():
    root = tk.Tk()
    root.title("目标树")
    root.geometry("800x600")  # 设置窗口初始大小
    root.grid_rowconfigure(2, weight=1)
    root.grid_columnconfigure(1, weight=1)

    # 自定义标签样式，设置左对齐
    style = ttk.Style()
    style.configure("Tree.TLabel", anchor="w")

    def create_root_objective():
        return Node("根节点")
    # 创建根节点
    root_objective = create_root_objective()
    current_node = None  # 当前选择的节点

    def update_tree_ui():
        # 清除目标树UI
        for widget in tree_frame.winfo_children():
            widget.destroy()
        # 重新绘制目标树UI
        draw_tree_ui(root_objective)
        update_scroll_region()

    def draw_tree_ui(node, indent=""):
        label_text = indent + "|── " + node.name
        label = ttk.Label(tree_frame, text=label_text, style="Tree.TLabel")
        label.pack(anchor=tk.W)
        label.bind("<Button-1>", lambda event, node=node: select_node(node))  # 绑定点击事件，选中节点
        for i, child_node in enumerate(node.children):
            child_indent = indent + "│    "
            draw_tree_ui(child_node, indent=child_indent)


    def select_node(node):
        entry.delete(0, tk.END)  # 清空输入框
        entry.insert(tk.END, node.name)  # 在输入框中显示节点名称
        global current_node
        current_node = node  # 设置当前节点为选择的节点

    def clear_selection():
        entry.delete(0, tk.END)  # 清空输入框
        global current_node
        current_node = None  # 清除当前节点的选择

    # 添加节点的按钮和事件处理
    def add_objective():
        global saved_once
        saved_once=False
        name = entry.get()  # 获取输入框中的内容作为目标名称
        entry.delete(0, tk.END)  # 清空输入框
        if current_node is None:  # 如果当前节点为空，说明是根节点
            root_objective.add_child(name)
        else:
            current_node.add_child(name)
        # 更新UI显示
        update_tree_ui()

    # 删除节点的按钮和事件处理
    def remove_objective():
        if current_node is None:
            return
        global saved_once
        saved_once=False
        current_node.remove_objective()
        clear_selection()  # 清除当前选择
        update_tree_ui()  # 更新UI显示
        
    #保存树的函数
    def activate_save():
        global saved_once
        if not saved_once:
            filename = get_save_filename()
            if filename:
                save_tree_with_unique_name(root_objective, filename)

    # 添加节点的按钮和事件处理
    add_button = tk.Button(root, text="添加节点", command=add_objective)
    add_button.grid(row=0, column=0)

    # 创建删除节点的按钮
    remove_button = tk.Button(root, text="删除节点", command=remove_objective)
    remove_button.grid(row=0, column=1)

    # 创建清除选择的按钮
    clear_button = tk.Button(root, text="清除选择", command=clear_selection)
    clear_button.grid(row=0, column=2)

    # 创建保存树的按钮
    save_button = tk.Button(root, text="保存树", command=activate_save)
    save_button.grid(row=1, column=2)

    # 创建用于输入目标名称的文本框
    entry = tk.Entry(root)
    entry.grid(row=1, column=1)

    def add_objective_on_enter(event):
        add_objective()

    entry.bind("<Return>", add_objective_on_enter)
    entry.bind("<Shift-Return>", lambda event: entry.insert(tk.END, '\n'))

    # 创建垂直滚动条
    vertical_scrollbar = ttk.Scrollbar(root, orient="vertical")
    horizontal_scrollbar = ttk.Scrollbar(root, orient="horizontal")
    # 创建一个Canvas作为容器
    canvas = tk.Canvas(root, yscrollcommand=vertical_scrollbar.set,xscrollcommand=horizontal_scrollbar.set)
    canvas.grid(row=2, column=1)

    # 将垂直滚动条与Canvas关联
    vertical_scrollbar.config(command=canvas.yview)
    vertical_scrollbar.grid(row=2, column=2, sticky="ns")

    # 创建水平滚动条
    horizontal_scrollbar.config(command=canvas.xview)
    horizontal_scrollbar.grid(row=3, column=0, columnspan=3, sticky="ew")

    # 将Canvas作为TreeFrame的父容器
    tree_frame = ttk.Frame(root)
    canvas_window = canvas.create_window((0, 0), window=tree_frame)


    def update_scroll_region(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    canvas.update_idletasks()  # 等待窗口调整完成
    update_tree_ui()
    # 将update_scroll_region绑定到tree_frame的大小变化事件和UI更新后
    tree_frame.bind("<Configure>", update_scroll_region)
    root.bind("<Configure>", update_scroll_region)
    return root,root_objective




