#!/usr/bin/python3

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
		bssf = None
		start_time = time.time()
		while not foundTour and time.time() - start_time < time_allowance:
			# create a random permutation
			perm = np.random.permutation(len(cities))
			route = []
			# Now build the route using the random permutation
			for i in range(len(cities)):
				route.append(cities[perm[i]])
			bssf = TSPSolution(route)
			count += 1
			if bssf.cost < np.inf:
				# Found a valid route
				foundTour = True
		end_time = time.time()
		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['solution'] = bssf
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

	def greedy(self, time_allowance=60.0, startCity=None):
		# Setup objects
		results = {}
		cities = self._scenario.getCities()
		foundTour = False
		count = 0
		bssf = None
		start_time = time.time()
		if startCity == None:
			startCity = random.choice(cities)
		
		while not foundTour and time.time() - start_time < time_allowance:
			# print(f"\nGreedy Tour: Round {count}")
			# print(f"Starting at {startCity._name}")
			unvisitedCitiesSet = set(cities)
			# visitedCitiesSet = {startCity}
			route = [startCity]
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
					# print(f"visit {nextCity._name}, cost ${greedyCost}")
					# visitedCitiesSet.add(nextCity)
					unvisitedCitiesSet.remove(nextCity)
					route.append(nextCity)
					currentCity = nextCity
				else:
					raise Exception("Unable to visit any city!!")
			
			bssf = TSPSolution(route)
			count += 1
			if bssf.cost < np.inf:
				# Found a valid route
				foundTour = True
			else:
				# Choose a new random city as the start city
				startCity = random.choice(cities)

		# Return results
		end_time = time.time()
		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['solution'] = bssf
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
		
	def branchAndBound(self, time_allowance=60.0):
		pass



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