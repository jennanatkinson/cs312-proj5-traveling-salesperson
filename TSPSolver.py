#!/usr/bin/python3

from queue import PriorityQueue
from TSPBranchAndBound import PriorityEntry, State
from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time
import numpy as np
from TSPClasses import *

class TSPSolver:
	def __init__( self, gui_view=None ):
		self._scenario = None

	def setupWithScenario( self, scenario:Scenario):
		self._scenario = scenario


	''' <summary>
		This is the entry point for the default solver
		which just finds a valid random tour.  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of solution, 
		time spent to find solution, number of permutations tried during search, the 
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''
	
	# Randomly generate route and check validity while under the time range
	#   Returns the first found solution
	def defaultRandomTour(self, time_allowance=60.0):
		results = {}
		cities = self._scenario.getCities()
		foundTour = False
		count = 0
		solution = None
		start_time = time.time()
		while not foundTour and time.time() - start_time < time_allowance:
			# create a random permutation
			perm = np.random.permutation(len(cities))
			route = []
			# Now build the route using the random permutation
			for i in range(len(cities)):
				route.append(cities[perm[i]])
			solution = TSPSolution(route)
			count += 1
			if solution.cost < np.inf:
				# Found a valid route
				foundTour = True
		end_time = time.time()
		results['cost'] = solution.cost if foundTour else math.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['solution'] = solution
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results


	''' <summary>
		This is the entry point for the greedy solver, which you must implement for 
		the group project (but it is probably a good idea to just do it for the branch-and
		bound project as a way to get your feet wet).  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found, the best
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''

	# Returns the first greedy solution found
	def greedy(self, time_allowance=60.0, startCity=None):
		# Setup objects
		results = {}
		cities = self._scenario.getCities()
		foundTour = False
		count = 0
		solution = None
		start_time = time.time()
		if startCity == None:
			startCity = cities[0]
		
		while not foundTour and time.time() - start_time < time_allowance:
			unvisitedCitiesSet = set(cities)
			route = []
			currentCity = startCity

			# Build the route greedily
			for _ in range(len(cities)):
				greedyCost, nextCity = None, None
				# Iterate to find the smallest unvisited edge
				for unvisitedCity in unvisitedCitiesSet:
					cost = currentCity.costTo(unvisitedCity)
					# Save the smallest city (or any city, if none have been visited)
					if greedyCost == None or cost < greedyCost:
						greedyCost, nextCity = cost, unvisitedCity

				# Visit the smallest edge
				if nextCity != None:
					unvisitedCitiesSet.remove(nextCity)
					route.append(nextCity)
					currentCity = nextCity
				else:
					raise Exception("Unable to visit any city!!")
			
			solution = TSPSolution(route)
			count += 1
			if solution.cost < np.inf:
				# Found a valid route
				foundTour = True
			else:
				# Choose a new random city as the start city and try again
				startCity = random.choice(cities)

		# Return results
		end_time = time.time()
		results['cost'] = solution.cost if foundTour else math.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['solution'] = solution
		results['max'], results['total'], results['pruned'] = None, None, None
		return results
	
	
	
	''' <summary>
		This is the entry point for the branch-and-bound algorithm that you will implement
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number solutions found during search (does
		not include the initial BSSF), the best solution found, and three more ints: 
		max queue size, total number of states created, and number of pruned states.</returns> 
	'''

	# Continues searching for a better solution until the time runs out or the queue is empty
	def branchAndBound(self, time_allowance=60.0, givenBssf=None):
		print("**Branch and Bound**")
		# Setup objects
		results:object = {}
		cities:list[City] = self._scenario.getCities()
		bssf:TSPSolution = givenBssf
		start_time:float = time.time()
		rootState:State = State(cities=cities)
		count:int = 0
		
		# Start with a greedy solution as the bssf
		if bssf == None:
			greedyResult = self.greedy(time_allowance=time_allowance-(time.time() - start_time))
			bssf:TSPSolution = greedyResult['solution']
			# count = greedyResult['count']
			print(f"({'{: >5}'.format(round(time.time() - start_time, 2))}s)  BSSF:{bssf}")
		# else:
		# 	count = givenBssf.count

		# Priority queue of (priorityNum, State) (Note: anything on the queue is NOT a solution yet)
		pQueue = PriorityQueue() 
		pQueue.put(PriorityEntry(0, 0, rootState))
		maxQueueLen:int = 1
		totalStatesCreated:int = 1
		totalStatesPruned:int = 0

		# Continue searching and expanding states on the queue until time is up or nothing is left
		while pQueue.qsize() != 0 and time.time() - start_time < time_allowance:
			state:State = pQueue.get().data
			# print(state.str_routeSoFar())
			# Expand and evaluate "children" aka a next possible unvisitedCity
			for nextCity in state.unvisitedCitiesSet:
				childState = state.copy()
				totalStatesCreated += 1
				childState.visitCity(nextCity)
				# print(f"    Child:{childState.str_routeSoFar()}", end="")
				# See if there is a solution yet
				route, cost = childState.getSolution()
				# If this is not a valid solution yet,
				if route == None or cost == None:
					if not childState.shouldPrune(bssf.cost):
						# Prioritize state and put back on the queue
						pQueue.put(PriorityEntry(len(childState.cities)-len(childState.unvisitedCitiesSet), childState.costSoFar, childState))
						# print(f": added to queue")
						if pQueue.qsize() > maxQueueLen:
							maxQueueLen = pQueue.qsize()
					# If it should be pruned, it does not go back on the queue
					else:
						# print(f": pruned")
						totalStatesPruned += 1
						del childState
				# If it is a solution, then see if it is better than bssf
				else:
					solution = TSPSolution(route)
					print(f"({'{: >5}'.format(round(time.time() - start_time, 2))}s)  BranchAndBound:{solution}")
					count += 1
					if solution.cost < bssf.cost:
						bssf = solution

		# Return results
		end_time = time.time()
		results['cost'] = bssf.cost
		results['time'] = end_time - start_time
		results['count'] = count
		results['solution'] = bssf
		results['max'] = maxQueueLen
		results['total'] = totalStatesCreated
		results['pruned'] = totalStatesPruned
		return results



	''' <summary>
		This is the entry point for the algorithm you'll write for your group project.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found during search, the 
		best solution found.  You may use the other three field however you like.
		algorithm</returns> 
	'''
		
	def fancy(self,time_allowance=60.0):
		pass