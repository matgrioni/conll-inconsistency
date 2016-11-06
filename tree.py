class Tree(object):
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []

    def add_children(self, *children):
        for child in children:
            child.parent = self
            self.children.append(child)

    # Returns the subtrees whose root nodes equal the provided node.
    # If there are no such trees than an empty list is returned.
    def find_trees_by_node(self, node):
        trees = []

        if self.node == node:
            trees.append(self)
        else:
            for child in children:
                child_matches = child.find_trees_by_node(node)
                if child_matches:
                    trees += child_matches

        return tree

    # Checks if the given node is in the tree and returns a boolean
    # response. To be used with `in` operator.
    def __contains__(self, value):
        contains = self.node == value
        if not contains:
            for child in self.children:
                contains = value in child

                if contains:
                    break

        return contains

    def size(self):
        s = 0

        if self.node:
            s += 1

        for child in self.children:
            s += child.size()

        return s
