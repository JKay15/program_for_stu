
class Node:

    def __init__(self, canvas, x, y, is_hyperlink=False, file_path=None):
        self.canvas = canvas
        self.radius = 30
        self.node = canvas.create_oval(x - self.radius, y - self.radius, x + self.radius, y + self.radius, fill="red")
        self.label = canvas.create_text(x, y, text="", fill="black")  # 空文本
        self.label_text = ""  # 新增
        self.x = x
        self.y = y
        self.is_hyperlink = is_hyperlink
        self.file_path = file_path
        if is_hyperlink:
            self.node_color = "blue"
            self.canvas.itemconfig(self.node, fill=self.node_color)
        #虽然超链接节点可以有子节点，也可以有超链接子节点，但是一般原则上还是不要这么做比较好，数据分析的时候会很麻烦
        #最好也不要出现多个节点指向一个超链接节点的情况，这个也不太好

    def get_position(self):
        return self.x, self.y