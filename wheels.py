import graph
from graph import *
from graph_io import load_graph, write_dot
import os

"""
the def calculate_wheel_join and calculate_wheel_star are used to find the total automorph for wheeljoin and wheelstar graphs
"""

""" fact
factorial function
"""
def fact(n):
    tot = 1
    for i in range(1, n+1):
        tot = tot * i
    return tot

"""check_cycle
group vertices based on which wheel they are in
"""
def check_cycle(graph, c = None, cycle = [], center_found = False):
	max = 0
	if not center_found:
		center = None
		for v in graph.vertices:
			if len(v.neighbours) > max:
				center = [v]
				max = len(v.neighbours)
		arr = list(graph.vertices)
		arr.remove(center[0])
	else:
		center = [c, cycle[0]]
		arr = cycle.copy()
		arr.remove(cycle[0])
	counter = 0
	cycle_arr = []
	while counter < len(arr):
		temp = []
		current = arr[0]
		temp.append(current)
		arr.remove(current)
		while True:
			num = 0
			neigh_arr = current.neighbours
			for neigh in neigh_arr:
				if neigh not in temp and neigh not in center:
					if neigh in arr:
						arr.remove(neigh)
					num += 1
					if neigh not in temp:
						current = neigh
					temp.append(neigh)
			if num == 0:
				break	
		cycle_arr.append(temp)
	return cycle_arr

"""find_center
Find the outer center of a wheel_star.
"""	
def find_center(graph):
	arr = []
	for v in graph.vertices:
		if v.degree < 2:
			return False
		elif v.degree != 3:
			arr.append(v)
		elif v.degree == 3:
			passs = True
			for neigh in v.neighbours:
				if neigh.degree == 3:
					passs = False
					break
			if passs:
				arr.append(v)	
	for i in arr:
		arr2 = arr.copy()
		arr2.remove(i)
		check = True
		if i.degree == len(arr2):
			for neigh in i.neighbours:
				if neigh not in arr2:
					check = False
					break
			if check:
				return i
	return False
	
"""inner_center
calculate inner_center of a wheel_star
"""
def inner_center(graph, center):
	inner = []
	for v in graph.vertices:
		if v.degree != 3 and v != center:
			inner.append(v)
	return inner
	
"""is_wheel
check if it is a wheel_join
"""
def is_wheel(graph):
	count = 0
	for v in graph.vertices:
		if len(v.neighbours) != 3:
			count += 1
	if count > 1:
		return False
	elif count == 0:
		return False
	return True

"""find_wheel
find all the inner wheel_joins in a wheel_star
"""
def find_wheel(graph,center = None, inner = []):
	if not inner:
		return False
	arr = inner
	wheels = []
	while len(arr) > 0:
		current = arr[0]
		arr_list = [current]
		temp = [current]
		while len(arr_list) > 0:
			cur = arr_list[0]
			for neigh in cur.neighbours:
				if neigh not in temp and neigh != center:
					arr_list.append(neigh)
					temp.append(neigh)
			arr_list.remove(cur)
		arr.remove(current)
		wheels.append(temp)
	return wheels

"""check_cycle_star
same as check cycle but an array for all the wheel_join in a wheel_star
"""	
def check_cycle_star(graph):
	center = find_center(graph)
	inner = inner_center(graph,center)
	arr = find_wheel(graph, center, inner)
	return arr, center
	
"""is_wheel_star
check if it is a wheel_star
"""		
def is_wheel_star(graph):
	a = find_center(graph)
	if a == False:
		return False
	return True
	
"""calculate_wheel_join
calculate the total automorh of wheel_join
each smaller wheel has (2 * len(vertices)) automorphs
if there are 2 or more smaller wheels with the same len(vertices) --> total automorph * factorial(2 or more) 
(example: if there are 2 small wheels with 5 vertices and 3 small wheels with 6 vertices --> total automorph * fact(2) * fact(3)
"""
def calculate_wheel_join(graph, c = None, cycle = None, center_found = False):
	arr = check_cycle(graph, c, cycle, center_found)
	total = 1
	dict = {}
	for cycle in arr:
		tot = (len(cycle) * 2)
		#print(tot)
		total = total * tot
		if len(cycle) not in dict:
			dict[len(cycle)] = 1
		else:
			dict[len(cycle)] += 1
	ar = []
	for it in list(dict.values()):
		if it > 1:
			ar.append(it)

	for item in ar:
		total = total * fact(item)
	return total
		
"""calculate_wheel_star	
similar to calculate_wheel_join, but the factorial now depends on how many similar smaller wheel_join are inside the wheel_star
"""		
def calculate_wheel_star(graph):
	arr, center = check_cycle_star(graph)
	total = 1
	dict = {}
	for cycle in arr:
		c = check_cycle(graph, center, cycle, True)
		temp = []
		for ce in c:
			temp.append(len(ce))
		temp = tuple(temp)
		if temp not in dict:
			dict[temp] = 1
		else:
			dict[temp] += 1
		tot = calculate_wheel_join(graph, center, cycle, True)
		total *= tot
	count = 0
	ar = []
	for it in list(dict.values()):
		if it > 1:
			ar.append(it)
	ar.sort()
	prev = 0
	for item in ar:
		if prev != item:
			total = total * fact(item)
		prev = item
	return total
		
def count_if_wheel(graph):
	if is_wheel(graph):
		return calculate_wheel_join(graph)
	elif is_wheel_star(graph):
		return calculate_wheel_star(graph)
	return "Not Wheel"
		
def output(L):
	print("Graph:	#Auth:")
	for i in range(len(L[0])):
		a = count_if_wheel(L[0][i])
		print("{}	{}".format(i,a))
        