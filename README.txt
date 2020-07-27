to use the program (cpr.py), the basic function to classify graph lists is tree_wheel_other.
on the bottom of the file, the SOURCE_FILE can be changed, and tree_wheel_other(L) will classify 
	and count automorphisms
If only isomorphisms have to be checked, and the graph is not a wheel or tree, then classify(L) is faster.

there are 3 files made by us: cpr.py (the main program), wheels.py (specific for wheels) and trees.py (specific for ..)
in cpr.py, there are 3 color refinement algorithms, named color_refinement_base_version (the standard color refinement),
color_refinement_old_minimized (the first Hopcroft algorithm) and color_refinement_minimized (the fastest Hopcroft 
	algorithm). all of which are called with 3 parameters: (graph1, graph2, [], bool) with bool the boolean whether
	or not you want the automorphism count.


to change the instance, the program code in "cpr.py" has to be altered: at the end, change SOURCE_FILE to
whatever file you want. then executing cpr.py will print the automorphisms and GI classes on stdout

the basic instances can be timed using time_branching(), no need for parameters. this will print the answer and the
	calculation time on stdout