class Node:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = []

    def add_child(self, name):
        new_node = Node(name, self)
        self.children.append(new_node)
    
    def remove_node(self):
        if self.parent is not None:
            self.parent.children.remove(self)
        for child in self.children:
            child.remove_node()
    