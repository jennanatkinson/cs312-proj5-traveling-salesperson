import math

from TSPClasses import City
from copy import copy, deepcopy


INF_STRING = "-"

class PriorityEntry(object):
	def __init__(self, numVisited:int, costSoFar:int, data):
			self.data = data
			# Negative so the biggerNum will be sorted first (reverse pQueue)
			# self.numVisited:int = -abs(numVisited)
			self.numVisited:int = numVisited
			self.costSoFar:int = costSoFar

	def __lt__(self, other): #less than
			if self.numVisited == other.numVisited:
				return self.costSoFar < other.costSoFar
			return self.numVisited > other.numVisited

# Keeps track/adjusts the current route, matrix and cost when adding new cities to the route
class State:
	#unvisitedCitiesSet:set, set of cities that haven't been visited yet
	#matrix:dict(tuple(rowIndex, colIndex):reducedCost), dictionary to show which edges can be used next (inf entries do not exist)
	#cities:list[City], reference to the list of cities
	#routeSoFar:list[City], list of cities in order of what we have visited so far
	#costSoFar:int, the cost we have accumulated on our route
	#isReturnVisitToStart:bool, if the route has finished through all the cities and returned back to the start
	def __init__(self, unvisitedSet:set=set(), matrix:dict=dict(), cities:list[City]=[], route:list=[], costSoFar:int=0):
		self.unvisitedCitiesSet:set = unvisitedSet
		self.matrix:dict = matrix
		self.cities:list[City] = cities # should be readOnly
		self.routeSoFar:list[City] = route
		self.costSoFar:int = costSoFar
		self._isReturnVisitToStart:bool = False # should ONLY be updated if len(unvisitedSet) == 0

		# If given nothing but a list of cities, construct the root state
		if len(cities) != 0 and costSoFar == 0 and len(matrix) == 0 and len(unvisitedSet) == 0 and len(route) == 0:
			self._generateRootStateFromCities()

	# Given a list of cities, return an init state with the first city as the start
	def _generateRootStateFromCities(self):
		# Unvisited cities should exclude the start node, so it is not revisited before the end
		self.unvisitedCitiesSet = set(self.cities[1:])

		# Route should include the start node
		self.routeSoFar = [self.cities[0]]

		#Initialize the matrix
		matrix = dict()
		for city in self.cities:
			for otherCity in self.cities:
				if city != otherCity:
					cost = city.costTo(otherCity)
					if cost != math.inf:
						matrix[tuple((city._index, otherCity._index))] = cost
		self.matrix = matrix
		self._reduceCostOnMatrix()

	# Returns true if route is impossible or not going to yield a better result
	# Should be used if branch is not a solution yet, but trying to determine if we should continue exploring or not
	def shouldPrune(self, bssf:int=math.inf) -> bool:
		return self.costSoFar == math.inf or self.costSoFar >= bssf

	# Sees if this State yields a solution
	def isSolution(self) -> bool:
		return len(self.unvisitedCitiesSet) == 0 and self.costSoFar != math.inf and len(self.matrix) == 0 and self._isReturnVisitToStart

	# Return the route if a solution
	# (will try to return to start if that is possible and hasn't been done yet)
	def getSolution(self):
		self._tryReturnToStart()
		if self.isSolution():
			return self.routeSoFar, self.costSoFar
		else:
			return None, None

	# If all other nodes have been visited, try to return to the start from the last city (unless already returned)
	# This will update the matrix and costSoFar if this is impossible
	def _tryReturnToStart(self):
		if self._isReturnVisitToStart: return
		if len(self.unvisitedCitiesSet) == 0 and self.costSoFar != math.inf and len(self.matrix) == 0:
			self.visitCity(self.cities[0])

	# Looks at the matrix and determines if a row or column will be inf (based on visit status)
	def _isInfinity(self, rowMajor:bool, city:City) -> bool:
		# If the city has been visited (aka at least an edge inbound or outbound, which is the only way to be inf)
		if not (city in self.unvisitedCitiesSet):
			if len(self.routeSoFar) <= 1:
				return False
			# If the city is the startCity
			if city == self.routeSoFar[0] and not self._isReturnVisitToStart:
				# If the route has finished and returned back to the start, then the row and col will be inf
				if self._isReturnVisitToStart:
					return True
				else:
					# If startCity hasn't been visited, then the first row will be inf, but not the column
					# print(f"skipping inf:startCity, rowMajor={rowMajor}")
					return rowMajor
			# If city == most recently visited in route, then only the column will be inf, not the row
			elif city == self.routeSoFar[len(self.routeSoFar)-1]:
				# print(f"skipping inf:lastCityVisited, rowMajor={rowMajor}")
				return not rowMajor
			# Otherwise, the city will have an outbound and an inbound edge already logged, so the col and row == inf
			else:
				# print(f"skipping inf:middleCityVisited, rowMajor={rowMajor}")
				return True
		else:
			return False

	# Generates the correct cell tuple based on if we are aiming for a row or a column in the loop (see findMinCostAndNormalize)
	def _generateTuple(self, rowMajor:bool, i:int, j:int):
		if rowMajor:
			return tuple((i, j))
		else: # Rows and columns are reversed here
			return tuple((j, i))
	
	# Ensures at least one zero on the rows/columns of the matrix (besides inf)
	def _findMinCostAndNormalize(self, rowMajor:bool=True):
		# Look at row each row/column to find the minCost
		for i in range(len(self.cities)):
			# If the whole row/column is going to be infinities, move on
			if self._isInfinity(rowMajor, self.cities[i]):
				continue
			
			minCost = math.inf

			#Examine each cell in a row/column to find the minCost
			for j in range(len(self.cities)):
				cell = self._generateTuple(rowMajor, i, j)
				cost = self.matrix.get(cell)
				if cost != None and cost < minCost:
					minCost = cost
					if minCost == 0:
						break
			
			# If we are taking on additional costs, we need to readjust the costSoFar and row/column numbers
			if minCost != 0 and minCost < math.inf:
				self.costSoFar += minCost

			# Update all costs in same row/column to normalize
				for j in range(len(self.cities)):
					cell = self._generateTuple(rowMajor, i, j)
					cost = self.matrix.get(cell)
					# If not infinity, update cell's cost
					if cost != None:
						self.matrix[cell] = cost - minCost
			# print(self)

	# Ensures at least one zero on the rows and columns of the matrix (besides inf)
	# Adjusts costSoFar as needed
	def _reduceCostOnMatrix(self):
		self._findMinCostAndNormalize(rowMajor=True)
		self._findMinCostAndNormalize(rowMajor=False)

	# Marks the city as visited, updates the matrix and then does reduceCost to normalize the matrix again
	def visitCity(self, cityToVisit:City):
		if (self.costSoFar == math.inf or self._isReturnVisitToStart):
			return
		assert(len(self.routeSoFar) != 0)
		prevCity = self.routeSoFar[len(self.routeSoFar)-1]
		
		# Ensure that there is actually a path to the other city
		cost = self.matrix.get(tuple((prevCity._index, cityToVisit._index)))
		if cost == None:
			self.costSoFar = math.inf #TODO: maybe change?
			return
		# Update cost after traveling to city
		self.costSoFar += cost

		# Remove all the impossible routes
		for i in range(len(self.cities)):
			# Update matrix to remove all items from row prevCity
			self.matrix.pop(tuple((prevCity._index, i)), None)

			# Update matrix to remove all items from col cityToVisit
			self.matrix.pop(tuple((i, cityToVisit._index)), None)

		# Update matrix to remove the inverse (cityToVisit -> prevCity) as well
		self.matrix.pop(tuple((cityToVisit._index, prevCity._index)), None)

		# Can only visit the startCity after visiting all other cities
		if cityToVisit == self.cities[0]:
			assert(len(self.unvisitedCitiesSet) == 0)
			assert(len(self.matrix) == 0)
			self._isReturnVisitToStart = True
		else:
			self.unvisitedCitiesSet.discard(cityToVisit)
			self.routeSoFar.append(cityToVisit)
			self.reduceCostOnMatrix()
			
	def __deepcopy__(self, memo):
		cls = self.__class__
		result = cls.__new__(cls)
		memo[id(self)] = result
		for k, v in self.__dict__.items():
				setattr(result, k, deepcopy(v, memo))
		return result

	def str_routeSoFar(self):
		string = "State{"
		if len(self.routeSoFar) != 0:
			for city in self.routeSoFar:
				string += f"{city._name}->"
		else:
			string += "*empty*"
		string += "}\n"
		return string
	
	def str_costSoFar(self):
		return f"Cost so far: {self.costSoFar}\n"
	
	def str_unvisitedCitiesSet(self):
		string += "Unvisited Cities: "
		if len(self.unvisitedCitiesSet) != 0:
			for city in self.unvisitedCitiesSet:
				string += f"{city._name} "
		else:
			string += "*empty*"
		string += '\n'
		return string
	
	def str_matrix(self):
		string += 'Matrix:\n'
		# Format the matrix printing
		table_data = [[]]
		# Print the names of the cities at the top
		for rowIndex in range(-1, len(self.cities)):
			if rowIndex == -1:
				table_data[0].append(" ")
			else:
				#assert(type(self.cities[i]) == City)
				table_data[0].append(self.cities[rowIndex]._name)
		
		for rowIndex in range(0, len(self.cities)):
			table_data.append([])
			last = len(table_data)-1
			for colIndex in range(-1, len(self.cities)):
				# Append the name of the city for the row
				if colIndex == -1:
					table_data[last].append(self.cities[rowIndex]._name)
				# Print the same city -> same city as inf
				elif colIndex == rowIndex:
					table_data[last].append(INF_STRING)
				# Lookup in dictionary and see if it exists
				else:
					cost = self.matrix.get(tuple((rowIndex, colIndex)))
					if cost != None:
						table_data[last].append(f"{cost}")
					else:
						table_data[last].append(INF_STRING)

		formatString = "{: >5} "
		for row in table_data:
			for item in row:
				string += formatString.format(item)
			string += '\n'
		string += '\n'

	def __str__(self) -> str:
		string = self.str_routeSoFar()
		string += self.str_costSoFar()
		string += self.str_unvisitedCitiesSet()
		string += self.str_matrix()
		return string