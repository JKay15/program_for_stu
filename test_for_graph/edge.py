from math import atan2, degrees, sqrt, cos, sin
import tkinter as tk

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