class Tree(object):
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []

    def add_children(self, *children):
        for child in children:
            child.parent = self
            self.children.append(child)

    def size(self):
        s = 0

        if self.node:
            s += 1

        for child in self.children:
            s += child.size()

        return s
