import tkinter as tk
from tkinter import ttk
from storage import load_tree
from main import on_selection_window_close


root_tmp=None
selection_window = tk.Tk()
selection_window.title("选择界面")

def create_new_tree():
    # 创建新树的逻辑
    global selection_window
    selection_window.destroy()  # 关闭选择窗口
    on_selection_window_close()
    

def load_existing_tree():
    # 加载已有树的逻辑
    filename = tk.filedialog.askopenfilename(defaultextension=".pkl", filetypes=[("Pickle Files", "*.pkl")])
    if filename:
        loaded_tree = load_tree(filename)
        global root_tmp
        root_tmp=loaded_tree
        selection_window.event_generate("<<WM_DELETE_WINDOW>>")
        # selection_window.destroy()  # 关闭选择窗口
        
new_tree_button = tk.Button(selection_window, text="新建树", command=create_new_tree)
new_tree_button.pack(pady=10)

load_tree_button = tk.Button(selection_window, text="加载已有树", command=load_existing_tree)
load_tree_button.pack(pady=10)






