import graph
from graph_io import load_graph, write_dot

""" is_tree
returns if graph is tree (duh)
"""
def is_tree(graph):
    v1 = graph.vertices
    if len(v1) == len(graph.edges) + 1:
        for v in v1:
            if len(v.neighbours) == 0:
                return False
    else:
        return False
    return True
    
""" tree_roots
find the roots of tree, if roots are returned, graph is isomorphic, if not, then graph not isomorphic
"""
def tree_roots(graph1, graph2):
    if not is_tree(graph1) or not is_tree(graph2):
        return False
    v1 = graph1.vertices[0]
    e1, temp = encode(graph1, v1, None)
    v2 = graph2.vertices
    v_temp = None
    total = 0
    for v in v2:
        e2, tot = encode(graph2, v, None)
        if e1 == e2:
            total += tot
            v_temp = v
    if total > 0:
        return (v1, v_temp, total)
    return False

""" fact
factorial function
"""
def fact(n):
    tot = 1
    for i in range(1, n+1):
        tot = tot * i
    return tot

""" encode
give unique encoding based on root
"""
def encode(g, v, parent):
    neigh = v.neighbours
    if len(neigh) == 1 and parent != None:
        return ("10", 1)
    array = []
    dict = {}
    for elem in neigh:
        if elem != parent:
            temp = encode(g, elem, v)
            array.append(temp[0])
            if temp[0] in dict:
                dict[temp[0]][1] += 1 #found another automorphism
            else:
                dict[temp[0]] = [temp[1], 1] #amount of automorph, once
    array.sort()
    res = ""
    tot = 1
    rem = []
    for string in array:
        res += str(string)
        if string not in rem and (dict[string][1] + dict[string][0] > 2):
            tot = tot * (dict[string][0]**dict[string][1])*(fact(dict[string][1]))
            rem.append(string)
    if tot == 0:
        tot = 1
    return ("1" + res + "0", tot)
