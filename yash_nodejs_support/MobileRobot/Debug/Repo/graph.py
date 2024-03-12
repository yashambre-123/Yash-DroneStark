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
    g = Graph('0')

    g.add_edge('12', '10')
    g.add_edge('12', '11')
    g.add_edge('12', '13')
    g.add_edge('12', '14')
    g.add_edge('12', '15')
    g.add_edge('12', '16')
    g.add_edge('12', '17')

    print(g.graph)

