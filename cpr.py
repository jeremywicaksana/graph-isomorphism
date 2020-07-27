import graph
from graph_io import load_graph, write_dot
import time
import os
import wheels #self made class to efficiently calculate wheelstar and wheeljoin
import trees  #self made class to efficiently calculate trees

""" isDiscrete
returns whether every vertex has a unique color (all color classes have length 1)
"""
def isDiscrete(colorclasses):
    for item in colorclasses:
        if len(colorclasses[item]) > 1:
            return False
    return True

""" base_color
gives all vertices of the graph the color corresponding to their own amount of neighbours
"""
def base_color(graph):
    v = graph.vertices
    counter = 0
    ColorClasses = {}
    for vertex in v:
        vertex.weight = len(vertex.neighbours)
        vertex.colornum = vertex.weight
        #create colorclasses, map color to all vertices with that color
        if vertex.weight not in ColorClasses:
            ColorClasses[vertex.weight] = [vertex]
        else:
            ColorClasses[vertex.weight].append(vertex)
        #counter is the highest (weight) class in colorclasses
        if len(vertex.neighbours) > counter:
            counter = len(vertex.neighbours)
    return ColorClasses

""" classify
loops through all combinations of L[0][0] to L[0][n] and stores the equivalent classes
"""
def classify(L):
    res = [[0]]
    for i in range(0, len(L[0])):
        for j in range(i, len(L[0])):
            if i != j:
                #transitivity: if iso(a,b) and iso(b,c) then iso(a,c), no need to check
                if not preprocess(L[0][i], L[0][j]):
                    continue
                for array in res:
                    if i in array:
                        if j in array:
                            continue
                temp = -1
                if trees.is_tree(L[0][i]) and trees.is_tree(L[0][j]):
                    temp = trees.tree_roots(L[0][i], L[0][j])
                    if temp != False:
                        temp = temp[2]
                    else:
                        temp = -1
                elif trees.is_tree(L[0][i]):
                    temp = -1
                else:
                    temp =  branching(L[0][i],L[0][j], [], False)
                if temp >= 1:
                    found = False
                    for array in res:
                        if i in array:
                            if j not in array:
                                array.append(j)
                            found = True
                    if not found:
                        res.append([i, j])
    for i in range(0, len(L[0])):
        found = False
        for array in res:
            if i in array:
                found = True
                break
        if not found:
            res.append([i])
    print("isomorph groups: ")
    for item in res:
        print(item)
        pass

""" classify_trees
test first if any of the graphs are trees:
take way shorter to calculate
"""
def classify_trees(L):
    classes = []
    res = {}
    for i in range(0, len(L[0])):
        for j in range(i, len(L[0])):
            if i != j and trees.is_tree(L[0][i]):
                if trees.is_tree(L[0][j]):
                    t = trees.tree_roots(L[0][i], L[0][j])
                    if t == False:
                        continue
                    else:
                        t = t[2]
                    found = False
                    if t > 0:
                        if i in res:
                            if not j in res:
                                for array in classes:
                                    if i in array:
                                        array.append(j)
                                res[j] = t
                                break
                        else:
                            res[i] = t
                            res[j] = t
                            classes.append([i, j])
    for array in classes:
        print(array, "    ", res[array[0]])

""" preprocess
checks if graphs are even compatible
"""
def preprocess(graph1, graph2):
    if not trees.is_tree(graph1) == trees.is_tree(graph2):
        #one is tree, one is not
        return False
    if len(graph1.vertices) != len(graph2.vertices):
        #not the same amount of vertices
        return False
    if len(graph1.edges) != len(graph2.edges):
        #not the same amount of edges
        return False
    return True

""" extended_classify (WITH AUTOMORPHISMS, only use on small graphs)
gives the result in the demanded format with automorphisms
"""
def extended_classify(L):
    res = []
    auto = {}
    temp = -1
    for i in range(0, len(L[0])):
        for j in range(i, len(L[0])):
            if i != j:
                if not preprocess(L[0][i], L[0][j]):
                    continue
                for array in res:
                    if i in array:
                        if j in array:
                            continue
                        else: #if i is already in array, then we know the automorphisms of i, so no need to calc amount of isomorphs with j
                            if trees.is_tree(L[0][i]):
                                if trees.is_tree(L[0][j]):
                                    temp = trees.tree_roots(L[0][i], L[0][j])  #still ounts automorphs, but only takes .5 seconds
                                    if temp != False:
                                        temp = temp[2]
                                    else:
                                        #false means graphs are not isomorphic
                                        continue
                                else:
                                    #one is tree, one is not
                                    continue
                            else:
                                temp = extended_branching(L[0][i],L[0][j], [], False)
                    else: # if i not in array, count isomorphisms (doesnt change runtime if there were no isomorphs)
                        if trees.is_tree(L[0][i]):
                            if trees.is_tree(L[0][j]):
                                temp = trees.tree_roots(L[0][i], L[0][j])
                                if temp != False:
                                    temp = temp[2]
                                else:
                                    continue
                            else:
                                continue
                        else:
                            temp = extended_branching(L[0][i],L[0][j], [], True)
                if len(res) == 0:
                    if trees.is_tree(L[0][i]):
                        if trees.is_tree(L[0][j]):
                            temp = trees.tree_roots(L[0][i], L[0][j])
                            if temp != False:
                                temp = temp[2]
                            else:
                                continue
                        else:
                            continue
                    else:
                        temp = extended_branching(L[0][i],L[0][j], [], True)
                    
                #j is not yet classified
                if temp >= 1:
                    found = False
                    for array in res:
                        if i in array:
                            if j not in array:
                                array.append(j)
                                auto[j] = auto[i]
                            found = True
                    if not found:
                        auto[i] = temp
                        auto[j] = temp
                        res.append([i, j])
    for i in range(0, len(L[0])):
        found = False
        for array in res:
            if i in array:
                found = True
                break
        if not found:
            res.append([i])
            if trees.is_tree(L[0][i]):
                temp = trees.tree_roots(L[0][i], L[1][i])
                auto[i] = temp[2]
            else:
                auto[i] = extended_branching(L[0][i],L[1][i], [], True)
            if auto[i] == 0:
                auto[i] = 1
    result = []
    for array in res:
        result.append([array, auto[array[0]]])
    print("isomorph:       #auth:")
    for item in result:
        print('{:<15s}'.format(str(item[0])), item[1])
    return result

""" find_twins
uses colorclasses, returns map of vertex to twin_array
"""
def find_twins(colorclass):
    twin_array = []
    neighbour_array = []
    for c in colorclass:
        for v in colorclass[c]:
            neigh = get_sorted_neighbours(v)
            if neigh in neighbour_array:
                twin_array[neighbour_array.index(neigh)].append(v)
            else:
                neighbour_array.append(neigh)
                twin_array.append([v])
    rem = []
    for array in twin_array:
        if len(array) == 1:
            rem.append(array)
    for item in rem:
        twin_array.remove(item)
    return twin_array

""" get_sorted_neighbours
makes sure that the neighbours are in order of label ascending
necessary for comparing neighbour array
"""
def get_sorted_neighbours(v):
    neigh = v.neighbours
    res = []
    for i in range(0, len(neigh)):
        max = 999999
        vertex = None
        for n in neigh:
            if n.label < max:
                max = n.label
                vertex = n
        neigh.remove(vertex)
        res.append(vertex)
    return res

""" color_refinement_base_version
color refinement colors the graph, making sure that same color vertices have identical neighbourhoods
"""
def color_refinement_base_version(graph1, graph2, colored=False, colorclass1=None, colorclass2=None):
    if not colored:
        colorclass1 = base_color(graph1)
        colorclass2 = base_color(graph2)
    v1 = graph1.vertices
    v2 = graph2.vertices
    counter = max(colorclass1)
    p, i = 0, 0
    unbalanced = False
    while p < len(v1): #amount of iterations needed to converge (each iteration changes 0 or 1 color) (max amount of colors is len(v1) = n)
        if not balanced(colorclass1, colorclass2):
            #invariant: colorclasses are equal at every iteration
            return colorclass1, colorclass2

        map = {}
        updated = False
        while i < len(v1): # check all vertices if they can be color-updated
            temp = get_neighbour_colors(v1[i])
            if v1[i].weight not in map:
                map[v1[i].weight] = temp
            elif map[v1[i].weight] != temp:
                updated = True
                counter += 1  #next color class = previous color class + 1
                map[counter] = temp
                oldweight = v1[i].weight
                colorclass1[counter] = []
                colorclass2[counter] = []
                rem = [] #check all elements in same colorclass if they have to be changed
                for elem in colorclass1[oldweight]:
                    neigh = get_neighbour_colors(elem)
                    if neigh == temp:
                        rem.append(elem)
                for item in rem:
                    item.weight = counter
                    item.colornum = counter
                    colorclass1[counter].append(item)
                    colorclass1[oldweight].remove(item)
                rem = []
                for elem in colorclass2[oldweight]:
                    neigh = get_neighbour_colors(elem)
                    if neigh == temp:
                        rem.append(elem)
                for item in rem:
                    item.weight = counter
                    item.colornum = counter
                    colorclass2[counter].append(item)
                    colorclass2[oldweight].remove(item)
                break
            i += 1
        if not updated:
            break
        p += 1
        i = 0
    #print("this graph is discrete: " + str(isDiscrete(colorclass1))) #debug message
    store_graph(graph1, 'result0.dot')
    store_graph(graph2, 'result1.dot')

    return colorclass1, colorclass2

""" color_refinement DFA minimization (OLD version)
color refinement, but based on dfa minimization algorithm (faster)
"""
def color_refinement_old_minimized(graph1, graph2, colored, colorclass1=None, colorclass2=None):
    if not colored:
        colorclass1 = base_color(graph1)
        colorclass2 = base_color(graph2)
    v1 = graph1.vertices
    v2 = graph2.vertices
    counter = max(colorclass1)
    
    #alorithm to append the smallest colorclasses to the queue
    q = []
    q_c = []
    maxi = -1
    max_len = 0
    for c in colorclass1:
        l = len(colorclass1[c])
        if l <= max_len:
            q.append((l, c))
            q_c.append(c)
        else:
            if maxi != -1:
                q.append((max_len, maxi))
                q_c.append(maxi)
            maxi = c
            max_len = l
    q.sort()
    i = 0
    changed = True
    while len(q) > 0:
        #changed = False
        current = q[0][1]
        if current not in colorclass2:
            return colorclass1, colorclass2
        if not balanced(colorclass1, colorclass2):
            return colorclass1, colorclass2
        q.pop(0)
        q_c.remove(current)
        map1 = {}
        map2 = {}
        update = {}
        for v in colorclass1[current]:
            for neigh in v.neighbours:
                i += 1
                c = neigh.colornum
                if c in update:
                    update[c] += 1
                else:
                    update[c] = 1
                if neigh in map1:
                    map1[neigh] += 1
                else:
                    map1[neigh] = 1
        for v in colorclass2[current]:
            for neigh in v.neighbours:
                i += 1
                if neigh in map2:
                    map2[neigh] += 1
                else:
                    map2[neigh] = 1
        new_colors = {}
        for v in map1:
            i += 1
            c = v.colornum
            l = map1[v]
            if (c,l) in new_colors:
                v.colornum = new_colors[(c,l)]
            elif update[c] != len(colorclass1[c]):
                counter += 1
                v.colornum = counter
                new_colors[(c,l)] = counter
            else:
                new_colors[(c,l)] = c
                update[c] = -1
            if v.weight != v.colornum:
                if v.colornum in colorclass1:
                    colorclass1[v.colornum].append(v)
                    colorclass1[v.weight].remove(v)
                else:
                    colorclass1[v.colornum] = [v]
                    colorclass1[v.weight].remove(v)
                v.weight = v.colornum
        for v in map2:
            i += 1
            c = v.colornum
            l = map2[v]
            if (c,l) in new_colors:
                v.colornum = new_colors[(c,l)]
            else:
                colorclass2[v.colornum].remove(v)
                v.colornum = counter + 1
                colorclass2[v.colornum] = [v]
                return colorclass1, colorclass2
            if v.weight != v.colornum:
                if v.colornum in colorclass2:
                    colorclass2[v.colornum].append(v)
                    colorclass2[v.weight].remove(v)
                    v.weight = v.colornum
                else:
                    colorclass2[v.colornum] = [v]
                    colorclass2[v.weight].remove(v)
                    v.weight = v.colornum
        changed = new_colors.values()
        undetermined = {}
        for (c,l) in new_colors:
            i += 1
            n_c = new_colors[(c,l)]
            if c in q_c:
                if n_c not in q_c:
                    q_c.append(n_c)
                    q.append((len(colorclass1[n_c]), n_c))
            else:
                if c in undetermined:
                    undetermined[c].append(n_c)
                else:
                    if n_c != c:
                        undetermined[c] = [c, n_c]
                    else:
                        undetermined[c] = [c]
        for o_c in undetermined:
            i += 1
            maxi = -1
            max_len = -1
            for n_c in undetermined[o_c]:
                l = len(colorclass1[n_c])
                if l <= max_len:
                    if n_c not in q_c:
                        q.append((l, n_c))
                        q_c.append(n_c)
                else:
                    if maxi != -1:
                        if maxi not in q_c:
                            q.append((max_len, maxi))
                            q_c.append(maxi)
                    maxi = n_c
                    max_len = l
        i += 1
        q.sort
    store_graph(graph1, "g1.dot")
    return colorclass1, colorclass2

""" color_refinement_minimized
uses DFA-minimization for color refinement
"""
def color_refinement_minimized(graph1, graph2, colored=False,  colorclass1=None, colorclass2=None):
    if not colored:
        colorclass1=base_color(graph1)
        if graph2:
            colorclass2=base_color(graph2)
    counter=max(colorclass1)+1

    maxi=0
    maxic=-1
    q=[]
    if len(colorclass1)!=1:
        for color in colorclass1:
            l=len(colorclass1[color])
            if l>maxi:
                maxi=l
                if maxic != -1:
                    q.append(maxic)
                maxic=color
            else:
                q.append(color)
    else:
        q=list(colorclass1.keys())
    while q:
        color=q[0]
        q.pop(0)
        map1={}
        map2={}
        if graph2:
            # if color not in colorclass2:
            #     return colorclass1, colorclass2
            if not balanced(colorclass1, colorclass2):
                return colorclass1, colorclass2
        added=[]
        for v in colorclass1[color]:
            for n in v.neighbours:
                if n.weight != color and n not in added:
                    count = get_neighbour_colors(n).count(color)
                    if (n.weight, count) not in map1:
                        map1[(n.weight, count)] = [n]

                        added.append(n)
                    else:
                        map1[(n.weight, count)].append(n)

                        added.append(n)
        added = []
        if graph2:
            for v in colorclass2[color]:
                for n in v.neighbours:
                    if n.weight != color and n not in added:
                        count = get_neighbour_colors(n).count(color)
                        if (n.weight, count) not in map2:
                            map2[(n.weight, count)] = [n]
                            added.append(n)
                        else:
                            map2[(n.weight, count)].append(n)

                            added.append(n)
        updated={}
        new_coloring={}
  #      if graph2:
 #           if map1.keys()!=map2.keys():
#
 #               colorclass2[0]=[]
  #              return colorclass1, colorclass2
   #         else:
    #             for key in map1:
     #                if len(map1[key])!=len(map2[key]):
      #                   colorclass2[0]=[]
       #                  return  colorclass1, colorclass2
        for key in map1:
            oldweight = key[0]
            newc = counter
            counter=counter+1
            if len(map1[key]) < len(colorclass1[oldweight]):
                if oldweight in updated:
                    updated[oldweight].append(newc)
                else:
                    updated[oldweight]=[newc]
                colorclass1[newc] = []
                new_coloring[key] = newc
                for v in map1[key]:
                    colorclass1[oldweight].remove(v)
                    v.weight = newc
                    v.colornum = newc
                    colorclass1[newc].append(v)
        if graph2:
            for key in new_coloring:
                oldweight = key[0]
                if key in map2:
                    newc = new_coloring[key]
                    colorclass2[newc] = []

                    for v in map2[key]:
                        colorclass2[oldweight].remove(v)
                        v.weight = newc
                        v.colornum = newc
                        colorclass2[newc].append(v)

        for key in updated:
            if key in q:
                for newc in updated[key]:
                    q.append(newc)
            else:
                maxi=key
                for newc in updated[key]:


                    if len(colorclass1[newc])<=len(colorclass1[maxi]):
                        q.append(newc)
                    else:
                        q.append(maxi)
                        maxi=newc

    if graph2 != None:
        return colorclass1, colorclass2
    else:
        return colorclass1

""" get_neighbour_colors
returns an array of the weights of the neighbours, ordered from lowest to highest
this defines the neighbourhood for this vertex
"""
def get_neighbour_colors(vertex):
    temp = []
    for elem in vertex.neighbours:
       temp.append(elem.weight)
    temp.sort()
    return temp

""" store_graph
saving the graph in .dot file
"""
def store_graph(graph, name):
    with open(os.path.join(os.getcwd(), name), 'w') as f:
        write_dot(graph, f, False)

""" balanced
returns if colorclass1 is equivalent to colorclass2 (boolean)
"""
def balanced(colorclass1, colorclass2):
    res = {}
    res2 = {}
    for elem in colorclass1:
        if elem not in colorclass2:
            return False
        if len(colorclass1[elem]) != len(colorclass2[elem]):
            return False
    return True

""" branching
Graph 1 is first graph to test
Graph 2 is second graph to test
automorph = true returns amount of isomorphism between 1 and 2 (1==2 means returns automorphisms)
automorph = false returns true or false (true for #isomorphisms > 0)
fixed_elements is tuples of (v1, v2) with v1 vertex of graph 1, v2 vertex of graph2, v1 and v2 get unique color
"""
def branching(graph1, graph2, fixed_elements, automorph: bool = False):
    c1, c2 = base_color(graph1), base_color(graph2)
    c1, c2 = color_fixed(c1, c2, fixed_elements)
    c1, c2 = color_refinement(graph1, graph2, True, c1, c2)
    if not balanced(c1, c2):
        return 0
    if isDiscrete(c1):
        return 1
        
    #no usable twins: pick smallest color class >= 2
    min = 999999
    color = -1
    for item in c1:
        l = len(c1[item])
        if l < min and l >= 2:
            min = l
            color = item
    v1 = c1[color][0]
    v2_array = c2[color]
    total = 0

    for elem in v2_array:
        temp = fixed_elements.copy()
        temp.append((v1, elem))
        score = branching(graph1, graph2, temp, automorph)
        if not automorph and score > 0:
            total = 1
            break
        elif score > 0:
            total += score
    return total 

""" extended_branching
this algorithm uses false twins to prune the branching a little
if an element with subtree n has a twin, that twin has the same subtree n
"""
def extended_branching(graph1, graph2, fixed_elements, automorph: bool = False):
    c1, c2 = base_color(graph1), base_color(graph2)
    c1, c2 = color_fixed(c1, c2, fixed_elements)
    c1, c2 = color_refinement_minimized(graph1, graph2, True, c1, c2)
    if not balanced(c1, c2):
        return 0
    if isDiscrete(c1):
        return 1
    
    twins = find_twins(c2)
    twin_colors = {}
    for array in twins:
        c = array[0].colornum
        twin_colors[c] = array
    
    # select smallest colorclass (or colorclass with largest amount of twins)
    min = 999999
    min_c = -1
    for color in c1:
        l = len(c1[color])
        tw = 0
        if color in twin_colors:
            tw = len(twin_colors[color])*2
        if l >= 2 and l-tw < min:
            min = l-tw
            min_c = color
            
    v1 = c1[min_c][0]
    v2_array = c2[min_c]
    total = 0
    tw = []
    if min_c in twin_colors:
        tw = twin_colors[min_c]
    found_twins = {}
    for vertex in v2_array:
        if vertex in found_twins:
            total += found_twins[vertex]
        else:
            temp = fixed_elements.copy()
            temp.append((v1, vertex))
            score = branching(graph1, graph2, temp, automorph)
            if vertex in tw:
                for i in tw:
                    found_twins[i] = score
            if score > 0 and not automorph:
                return 1
            elif score > 0:
                total += score
    return total

""" color_fixed
fixed = array of tuples of vertices (v1, v2) from graph1, graph2 respectively that have a unique same color
"""    
def color_fixed(colorclass1, colorclass2, fixed):
    counter = max(colorclass1) + 1
    if fixed != None:
        for elem in fixed:
            for array in colorclass1:
                if elem[0] in colorclass1[array]:
                    elem[0].weight = elem[0].colornum = counter
                    colorclass1[array].remove(elem[0])
                    colorclass1[counter] = [elem[0]]
                    break
            for array in colorclass2:
                if elem[1] in colorclass2[array]:
                    elem[1].weight = elem[1].colornum = counter
                    colorclass2[array].remove(elem[1])
                    colorclass2[counter] = [elem[1]]
                    break
            counter += 1
    return colorclass1, colorclass2

""" fact
factorial function
"""
def fact(n):
    tot = 1
    for i in range(1, n+1):
        tot = tot * i
    return tot

""" time_branching
test the computation time of basic instances (hardcoded)
"""
def time_branching():
    SC1 = 'basicGI1.grl' #'colorref_smallexample_6_15.grl'
    SC2 = 'basicGI2.grl'
    SC3 = 'basicGI3.grl'
    SC4 = 'basicGIAut.grl'
    SC5 = 'basicAut1.gr'
    SC6 = 'basicAut2.gr'
    with open(SC1) as f:
        L1=load_graph(f,read_list=True)
    with open(SC1) as f:
        K =load_graph(f,read_list=True)
        L1 = [L1[0]]
        L1.append(K[0])
    with open(SC2) as f:
        L2=load_graph(f,read_list=True)
    with open(SC2) as f:
        K =load_graph(f,read_list=True)
        L2 = [L2[0]]
        L2.append(K[0])
    with open(SC3) as f:
        L3=load_graph(f,read_list=True)
    with open(SC3) as f:
        K =load_graph(f,read_list=True)
        L3 = [L3[0]]
        L3.append(K[0])
    with open(SC4) as f:
        L4=load_graph(f,read_list=True)
    with open(SC4) as f:
        K =load_graph(f,read_list=True)
        L4 = [L4[0]]
        L4.append(K[0])
    with open(SC5) as f:
        L5=load_graph(f,read_list=True)
    with open(SC5) as f:
        K =load_graph(f,read_list=True)
        L5 = [L5[0]]
        L5.append(K[0])
    with open(SC6) as f:
        L6=load_graph(f,read_list=True)
    with open(SC6) as f:
        K =load_graph(f,read_list=True)
        L6 = [L6[0]]
        L6.append(K[0])
    print("basicGI1")
    t0 = time.time()
    classify(L1)
    print(time.time()-t0)
    print("basicGI2")
    t0 = time.time()
    classify(L2)
    print(time.time()-t0)
    print("basicGI3")
    t0 = time.time()
    classify(L2)
    print(time.time()-t0)
    print("basicGIAut")
    t0 = time.time()
    extended_classify(L4)
    print(time.time()-t0)
    print("basicAut1")
    t0 = time.time()
    extended_classify(L5)
    print(time.time()-t0)
    print("basicAut2")
    t0 = time.time()
    extended_classify(L6)
    print(time.time()-t0)

""" tree_wheel_other (select suitable alorithm for automorph)
this sends the graph to be processed by specific algorithms 
"""
def tree_wheel_other(L):
    if len(L[0][0].vertices) <= 6:
        print("other")
        extended_classify(L)
        return "done"
    if trees.is_tree(L[0][0]):
        print("tree")
        classify_trees(L)
        return "done"
    temp = wheels.count_if_wheel(L[0][0])
    if temp != "Not Wheel":
        dic = {}
        for i in range(0,len(L[0])):
            a = wheels.count_if_wheel(L[0][i])
            if a in dic:
                dic[a].append(i)
            else:
                dic[a] = [i]
        for i in dic:
            print(dic[i], "auto: ", i)
        return "done"
    else:
        print("other")
        extended_classify(L)
        return "done"

SOURCE_FILE = 'bigtrees3.grl'
with open(SOURCE_FILE) as f:
    L =load_graph(f,read_list=True)

tree_wheel_other(L)


