import tkinter as tk
from graph_gui import GraphGUI

root = tk.Tk()
root.geometry("800x600")  # 设置根窗口初始大小为 800x600
app = GraphGUI(root)
root.configure(bg="black")  # 设置根窗口背景颜色为黑色
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()