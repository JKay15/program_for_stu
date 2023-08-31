import tkinter as tk
from math import atan2, degrees, sqrt, cos, sin
from tkinter import simpledialog, ttk, messagebox
from tkinter import Scrollbar
from tkinter import filedialog
from PIL import Image, ImageDraw
import json
import os


class Node:

    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.radius = 30
        self.node = canvas.create_oval(x - self.radius, y - self.radius, x + self.radius, y + self.radius, fill="red")
        self.label = canvas.create_text(x, y, text="", fill="black")  # 空文本
        self.label_text = ""  # 新增
        self.x = x
        self.y = y


class Edge:

    def __init__(self, canvas, start_node, end_node):
        self.canvas = canvas
        self.start_node = start_node
        self.end_node = end_node
        self.selected = False
        self.x = (self.start_node.x + self.end_node.x) / 2
        self.y = (self.start_node.y + self.end_node.y) / 2
        self.label = canvas.create_text(self.x, self.y, text="", fill="black")
        self.label_text = ""  # 新增
        self.update_edge()

    def intersection(self, x1, y1, x2, y2, r1, r2):
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        theta = atan2(dy, dx)
        sig_x = 1 if x2 - x1 > 0 else -1
        sig_y = 1 if y2 - y1 > 0 else -1
        x11 = x1 + sig_x * r1 * cos(theta)
        y11 = y1 + sig_y * r1 * sin(theta)
        x22 = x2 - sig_x * r2 * cos(theta)
        y22 = y2 - sig_y * r2 * sin(theta)
        return x11, y11, x22, y22

    def update_edge(self):
        x1, y1, x2, y2 = self.intersection(
            self.canvas.coords(self.start_node.node)[0] + self.start_node.radius,
            self.canvas.coords(self.start_node.node)[1] + self.start_node.radius,
            self.canvas.coords(self.end_node.node)[0] + self.end_node.radius,
            self.canvas.coords(self.end_node.node)[1] + self.end_node.radius, self.start_node.radius, self.end_node.radius)
        if hasattr(self, 'line'):
            self.canvas.delete(self.line)
        self.line = self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill="black")
        self.canvas.itemconfig(self.label, text=self.label_text)
        self.canvas.coords(self.label, (self.start_node.x + self.end_node.x) / 2, (self.start_node.y + self.end_node.y) / 2)
        if self.selected:
            self.canvas.itemconfig(self.line, fill="red")


class GraphGUI:

    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.w = 800
        self.h = 600
        self.canvas.pack()
        self.nodes = []
        self.edges = []
        self.active_node = None
        self.start_node = None
        self.arrow = None
        self.selected_node = None
        self.selected_nodes = []
        self.save_once = False

        self.selecting = False
        self.selection_box = None
        self.selection_start = None
        self.selection_end = None
        self.selected_edge = None  # 存储选中的边
        self.init_file = None

        # 创建一个容器来包含按钮，并设置为横向排列
        button_frame = tk.Frame(self.canvas)
        button_frame.pack(side=tk.TOP, padx=10, pady=10)

        # 添加按钮到容器
        save_button = tk.Button(button_frame, text="Save Graph", command=self.save_graph)
        save_button.pack(side=tk.LEFT, padx=5)

        load_button = tk.Button(button_frame, text="Load Graph", command=self.load_graph)
        load_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(button_frame, text="Delete Node", command=self.delete_selected_node)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        # 添加按钮用于删除选中的边
        delete_edge_button = tk.Button(button_frame, text="Delete Edge", command=self.delete_selected_edges)
        delete_edge_button.pack(side=tk.LEFT, padx=5)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)
        self.canvas.bind("<B1-Motion>", self.move_node)
        self.canvas.bind("<ButtonRelease-1>", self.release_node)
        self.canvas.bind("<Button-2>", self.right_click)
        self.canvas.bind("<B2-Motion>", self.draw_arrow)
        self.canvas.bind("<ButtonRelease-2>", self.release_arrow)
        self.root.bind("<Configure>", self.on_window_configure)
        self.root.bind("<Key-l>", self.apply_force_directed_layout)

    def delete_selected_edges(self):
        if self.selected_edge:
            self.selected_edge.selected = False
            self.canvas.delete(self.selected_edge.line)
            self.canvas.delete(self.selected_edge.label)
            self.edges.remove(self.selected_edge)
            self.selected_edge = None
            if self.save_once == True:
                self.save_once = False

    def select_node(self, x, y):
        if self.selected_node:
            self.canvas.itemconfig(self.selected_node.node, outline="black")  # 取消前一个选中节点的高亮

        clicked_node = self.find_clicked_node(x, y)

        if clicked_node:
            self.selected_node = clicked_node
            self.canvas.itemconfig(clicked_node.node, outline="red")  # 高亮选中的节点

    def delete_selected_node(self):
        if self.selected_node:
            self.nodes.remove(self.selected_node)
            self.canvas.delete(self.selected_node.node)
            self.canvas.delete(self.selected_node.label)
            self.remove_edges_connected_to_node(self.selected_node)
            if self.selected_node in self.selected_nodes:
                self.selected_nodes.remove(self.selected_node)
            self.selected_node = None
            if self.save_once == True:
                self.save_once = False

        for selected_node in self.selected_nodes:
            self.nodes.remove(selected_node)
            self.canvas.delete(selected_node.node)
            self.canvas.delete(selected_node.label)
            self.remove_edges_connected_to_node(selected_node)
            if self.save_once == True:
                self.save_once = False
        self.selected_nodes.clear()

    def remove_edges_connected_to_node(self, node):
        edges_to_remove = []
        for edge in self.edges:
            if edge.start_node == node or edge.end_node == node:
                self.canvas.delete(edge.line)
                self.canvas.delete(edge.label)
                edges_to_remove.append(edge)
        for edge in edges_to_remove:
            self.edges.remove(edge)

    def on_window_configure(self, event):
        self.update_canvas_size()

    def update_canvas_size(self):
        new_width = self.root.winfo_width()
        new_height = self.root.winfo_height()
        if abs(new_height - self.h) <= 6:
            new_height = self.h
        else:
            self.h = new_height

        if abs(new_width - self.w) <= 6:
            new_width = self.w
        else:
            self.w = new_width

        self.canvas.config(width=new_width, height=new_height)
        self.update_nodes_and_edges_positions(new_width, new_height)

    def update_nodes_and_edges_positions(self, canvas_width, canvas_height):
        for node in self.nodes:
            self.canvas.coords(node.node, node.x - node.radius, node.y - node.radius, node.x + node.radius, node.y + node.radius)
            self.canvas.coords(node.label, node.x, node.y)

        for edge in self.edges:
            edge.update_edge()

    def right_click(self, event):
        x, y = event.x, event.y
        clicked_node = self.find_clicked_node(x, y)

        if clicked_node is not None:
            self.start_node = clicked_node
            self.arrow = self.canvas.create_line(self.canvas.coords(self.start_node.node)[0] + self.start_node.radius,
                                                 self.canvas.coords(self.start_node.node)[1] + self.start_node.radius,
                                                 x,
                                                 y,
                                                 arrow=tk.LAST)

    def draw_arrow(self, event):
        if self.arrow:
            self.canvas.coords(self.arrow,
                               self.canvas.coords(self.start_node.node)[0] + self.start_node.radius,
                               self.canvas.coords(self.start_node.node)[1] + self.start_node.radius, event.x, event.y)

    def release_arrow(self, event):
        if self.arrow:
            self.canvas.delete(self.arrow)
            x, y = event.x, event.y
            clicked_node = self.find_clicked_node(x, y)
            if clicked_node is not None and clicked_node != self.start_node:
                if clicked_node not in self.selected_nodes:
                    end_node = clicked_node
                    self.create_edge(self.start_node, end_node)
                else:
                    for selected_node in self.selected_nodes:
                        if selected_node != self.start_node:
                            self.create_edge(self.start_node, selected_node)
                if self.save_once == True:
                    self.save_once = False
            self.start_node = None

    def create_edge(self, start_node, end_node, label_text=""):
        tag = 1
        for edge in self.edges:
            if edge.start_node == start_node and edge.end_node == end_node:
                tag = 0
                break
        if tag != 0:
            edge = Edge(self.canvas, start_node, end_node)
            if label_text != "":
                edge.label_text = label_text
                edge.update_edge()
            self.edges.append(edge)

    def create_node(self, x, y):
        node = Node(self.canvas, x, y)
        self.nodes.append(node)
        self.active_node = node

    def move_motion(self, event, active_node, dx=0, dy=0):
        x, y = event.x + dx, event.y + dy
        self.canvas.coords(active_node.node, x - active_node.radius, y - active_node.radius, x + active_node.radius, y + active_node.radius)
        self.canvas.coords(active_node.label, x, y)  # 更新标签位置
        active_node.x = x
        active_node.y = y
        self.update_edges()

        # 更新文本位置
        text_x = x
        text_y = y  # 调整文本的垂直位置
        self.canvas.coords(active_node.label, text_x, text_y)

    def move_node(self, event):
        if self.active_node:
            if self.active_node not in self.selected_nodes:
                self.move_motion(event, self.active_node)
            else:
                distance = []
                for active_node in self.selected_nodes:
                    dx, dy = active_node.x - self.active_node.x, active_node.y - self.active_node.y
                    distance.append([dx, dy])
                index = 0
                for active_node in self.selected_nodes:
                    self.move_motion(event, active_node, distance[index][0], distance[index][1])
                    index += 1
            if self.save_once == True:
                self.save_once = False

        elif self.selecting:
            x, y = event.x, event.y
            if not self.selection_box:
                self.selection_box = self.canvas.create_rectangle(self.selection_start[0], self.selection_start[1], x, y, outline="blue")
            else:
                self.canvas.coords(self.selection_box, self.selection_start[0], self.selection_start[1], x, y)

    def release_node(self, event):
        self.active_node = None
        self.update_edges()
        if self.selecting:
            self.selection_end = (event.x, event.y)
            self.select_nodes_in_selection_box()
            self.selecting = False
            if self.selection_box:
                self.canvas.delete(self.selection_box)
                self.selection_box = None

    def select_nodes_in_selection_box(self):
        self.selected_nodes.clear()
        for node in self.nodes:
            node_coords = self.canvas.coords(node.node)
            if min(self.selection_start[0],self.selection_end[0]) <= node_coords[2] and max(self.selection_start[0],self.selection_end[0]) >= node_coords[0] and \
               min(self.selection_start[1],self.selection_end[1]) <= node_coords[3] and max(self.selection_start[1],self.selection_end[1]) >= node_coords[1]:
                self.selected_nodes.append(node)
        self.highlight_selected_nodes(self.selected_nodes)

    def highlight_selected_nodes(self, selected_nodes):
        for node in self.nodes:
            if node in selected_nodes:
                self.canvas.itemconfig(node.node, outline="red")
            else:
                self.canvas.itemconfig(node.node, outline="black")

    def update_edges(self):
        for edge in self.edges:
            edge.update_edge()

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        clicked_node = self.find_clicked_node(x, y)

        if clicked_node is not None:
            self.active_node = clicked_node
            if self.selected_edge:
                self.selected_edge.selected = False
            self.selected_edge = None
            self.select_node(x, y)
        else:
            if self.selected_node:
                self.canvas.itemconfig(self.selected_node.node, outline="black")
                self.selected_node = None
            self.selection_start = (event.x, event.y)
            self.selecting = True
            self.selected_nodes.clear()
            self.highlight_selected_nodes([])
            if self.selected_edge:
                self.canvas.itemconfig(self.selected_edge.line, fill="black")
                self.selected_edge.selected = False
                self.selected_edge = None

            self.selected_edge = self.find_clicked_edge(x, y)
            if self.selected_edge:
                self.selected_edge.selected = True
            self.canvas.itemconfig(self.selected_edge, fill="red")

    def on_canvas_double_click(self, event):
        x, y = event.x, event.y
        clicked_node = self.find_clicked_node(x, y)

        if clicked_node is None:
            clicked_edge = self.find_clicked_edge(x, y)
            if clicked_edge is None:
                self.create_node(x, y)
                new_node = self.nodes[-1]  # 获取新创建的节点
                self.canvas.coords(new_node.label, x, y)  # 更新标签位置
                if self.save_once == True:
                    self.save_once = False
            else:
                self.edit_edge_text(clicked_edge)
        else:
            if clicked_node in self.selected_nodes:
                self.selected_nodes.clear()
                self.highlight_selected_nodes([])
                self.select_node(clicked_node.x, clicked_node.y)
            self.edit_node_text(clicked_node)

    def find_clicked_node(self, x, y):
        for node in self.nodes:
            nx, ny = node.x, node.y
            if nx - node.radius <= x <= nx + node.radius and ny - node.radius <= y <= ny + node.radius:
                return node
        return None

    def find_clicked_edge(self, x, y):
        for edge in self.edges:
            #两个端点的获取
            x1, y1 = edge.start_node.x, edge.start_node.y
            x2, y2 = edge.end_node.x, edge.end_node.y
            #相对距离计算
            l1, l2 = x1 - x, x - x2
            h1, h2 = y1 - y, y - y2
            if abs(h1 * l2 - h2 * l1) < 1000:
                return edge
        return None

    def edit_node_text(self, node):
        if node:
            new_text = simpledialog.askstring("Edit Node Text", "Enter new text for the node:", initialvalue=node.label_text)
            if new_text is not None:
                node.label_text = new_text
                self.canvas.itemconfig(node.label, text=new_text)
                if self.save_once == True:
                    self.save_once = False

    def edit_edge_text(self, edge):
        if edge:
            new_text = simpledialog.askstring("Edit Edge Text", "Enter new text for the edge:", initialvalue=edge.label_text)
            if new_text is not None:
                edge.label_text = new_text
                self.canvas.itemconfig(edge.label, text=new_text)
                if self.save_once == True:
                    self.save_once = False

    def save_graph(self, filename=None):
        filename = self.init_file
        # 提示用户选择保存路径
        if filename == None:
            file_path = filedialog.asksaveasfilename(initialdir=os.getcwd(), defaultextension=".graph", filetypes=[("Graph files", "*.graph")])
        else:
            file_path = filename

        if file_path:
            # 构建图的数据结构，保存节点坐标和标签
            graph_data = {
                "nodes": [{
                    "x": node.x,
                    "y": node.y,
                    "label": node.label_text
                } for node in self.nodes],
                "edges": [{
                    "start": self.nodes.index(edge.start_node),
                    "end": self.nodes.index(edge.end_node),
                    "label": edge.label_text
                } for edge in self.edges]  # 保存边的信息，例如连接的节点索引
            }

            # 保存图的数据到文件
            with open(file_path, "w") as f:
                json.dump(graph_data, f)

            self.save_once = True

    def load_graph(self):
        # 提示用户选择加载路径
        file_path = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=[("Graph files", "*.graph")])

        if file_path:
            # 从文件加载图的数据
            with open(file_path, "r") as f:
                graph_data = json.load(f)

            # 清除当前图的节点和边
            self.clear_graph()

            # 重新创建节点
            for node_data in graph_data["nodes"]:
                self.create_node(node_data["x"], node_data["y"])
                new_node = self.nodes[-1]
                new_node.label_text = node_data["label"]
                self.canvas.itemconfig(new_node.label, text=node_data["label"])

            # 重新创建边
            for edge_data in graph_data["edges"]:
                start_node = self.nodes[edge_data["start"]]
                end_node = self.nodes[edge_data["end"]]
                label_text = edge_data["label"]
                self.create_edge(start_node, end_node, label_text)

    def clear_graph(self):
        for node in self.nodes:
            self.canvas.delete(node.node)
            self.canvas.delete(node.label)
        for edge in self.edges:
            self.canvas.delete(edge.line)
            self.canvas.delete(edge.label)
        self.nodes = []
        self.edges = []

    def ask_to_save_graph(self):
        answer = messagebox.askyesnocancel("保存图", "是否保存当前的图？")
        if answer is None:
            return "cancel"
        elif answer:
            return "save"
        else:
            return "discard"

    def on_closing(self):
        if not self.save_once:
            save_choice = self.ask_to_save_graph()
            if save_choice == "save":
                if self.init_file:
                    self.save_graph(filename)
                else:
                    filename = filedialog.asksaveasfilename(initialdir=os.getcwd(), defaultextension=".graph", filetypes=[("Graph files", "*.graph")])
                    if filename:
                        self.save_graph(filename)
                    else:
                        return
            elif save_choice == "cancel":
                return

        self.root.destroy()
        
    def force_directed_layout(self, iterations=100, attraction=0.1, repulsion=0.5):
        for _ in range(iterations):
            # 初始化节点的受力为零
            node_forces = {node: [0, 0] for node in self.nodes}

            # 计算引力和斥力
            for edge in self.edges:
                dx = edge.end_node.x - edge.start_node.x
                dy = edge.end_node.y - edge.start_node.y
                distance = sqrt(dx ** 2 + dy ** 2)
                force = attraction * distance
                angle = atan2(dy, dx)
                node_forces[edge.start_node][0] += force * cos(angle)
                node_forces[edge.start_node][1] += force * sin(angle)
                node_forces[edge.end_node][0] -= force * cos(angle)
                node_forces[edge.end_node][1] -= force * sin(angle)

            for node1 in self.nodes:
                for node2 in self.nodes:
                    if node1 != node2:
                        dx = node2.x - node1.x
                        dy = node2.y - node1.y
                        distance = sqrt(dx ** 2 + dy ** 2)
                        force = repulsion / distance ** 2
                        angle = atan2(dy, dx)
                        node_forces[node1][0] -= force * cos(angle)
                        node_forces[node1][1] -= force * sin(angle)

            # 更新节点位置
            for node in self.nodes:
                node.x += node_forces[node][0]
                node.y += node_forces[node][1]

            # 更新画布上的节点位置
            self.update_nodes_and_edges_positions(self.w, self.h)
            self.canvas.update()

    def apply_force_directed_layout(self, event=None):
        self.force_directed_layout(iterations=100, attraction=0.1, repulsion=0.5)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")  # 设置根窗口初始大小为 800x600
    app = GraphGUI(root)
    root.configure(bg="black")  # 设置根窗口背景颜色为黑色
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
    
#接下来需要添加的功能：对于一个节点添加一个超链接节点，那个节点是一个graph文件，那个节点的颜色是蓝色
#选择普通节点后点击“add graph”按钮，弹出命名窗口，命名后，可以自动生成一个超链接节点（对应一个仅含有一个名字叫“root”的节点，后续所有节点都必须是其子节点，新开一个窗口开始编辑），默认超链接节点是其子节点
#选择超链接节点后点击“load graph"按钮，可以新开一个窗口，加载出那个节点对应的graph文件
#虽然超链接节点可以有子节点，也可以有超链接子节点，但是一般原则上还是不要这么做比较好，数据分析的时候会很麻烦
#最好也不要出现多个节点指向一个超链接节点的情况，这个也不太好
