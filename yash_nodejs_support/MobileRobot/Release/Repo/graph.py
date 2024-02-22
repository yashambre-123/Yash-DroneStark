#!/usr/bin/python3

class Graph():

    def __init__(self, base_node):
        self.graph = {}
        self.base_node = base_node

        self.graph[self.base_node] = []

    def add_edge(self, node, new_node):
        """
        add edge between node and new_node
        """
        node_list = self.graph[node]
        node_list.append(new_node)

        if new_node not in self.graph:
            self.graph[new_node] = [node]
        else:
            new_node_list = self.graph[new_node]
            new_node_list.append(node)


# Driver
if __name__ == "__main__":
    g = Graph('S')

    g.add_edge('S', 'A')
    g.add_edge('A', 'B')
    g.add_edge('A', 'D')
    g.add_edge('B', 'C')
    g.add_edge('B', 'F')
    g.add_edge('D', 'E')
    g.add_edge('E', 'F')

    print(g.graph)

