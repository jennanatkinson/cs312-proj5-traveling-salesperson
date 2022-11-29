import math

from TSPClasses import City


INF_STRING = "-"

# TODO: should prune if the column of 0 is all inf, should prune if the lower bound is bigger than the bssf

class State:
	#unvisitedCitiesSet, set of cities that haven't been visited yet
	#matrix, dictionary to show which edges can be used next
	#cities, reference to the list of cities
	#routeSoFar, list of cities in order of what we have visited so far
	#costSoFar, the cost we have accumulated on our route
	def __init__(self, unvisitedSet:set=set(), matrix:dict=dict(), cities=[], route=[], costSoFar:int=0):
		self.unvisitedCitiesSet = unvisitedSet
		self.matrix = matrix
		self.cities = cities
		self.routeSoFar = route
		self.costSoFar = costSoFar
		self.isVisitStart = False

		# If given nothing but a list of cities, construct the root state
		if len(cities) != 0 and costSoFar == 0 and len(matrix) == 0 and len(unvisitedSet) == 0 and len(route) == 0:
			self.generateRootStateFromCities()

	# Given a list of cities, return an init state
	def generateRootStateFromCities(self):
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
		self.reduceCostOnMatrix()

	# # Returns true if there is a node that still can return to the starting city
	# def isReturnToStart(self) -> bool:
	# 	for i in range(len(self.cities)):
	# 		if self.matrix.get(tuple((i, 0))) != None:
	# 			return True
	# 	return False

	# Sees if this State yields a solution
	def isSolution(self) -> bool:
		return len(self.unvisitedCitiesSet) == 0 and self.costSoFar != math.inf and len(self.matrix) == 0

	# Return the route if a solution
	def getSolution(self):
		if self.isSolution():
			return self.routeSoFar, self.costSoFar
		else:
			return None, None

	# TODO: fix function
	def isInfinity(self, city:City) -> bool: #row:bool, city:City) -> bool:
		# if len(self.routeSoFar) <= 1:
		# 	return False
		# # If the first element in the route is 0, and the start hasn't been visited, then the first row will be inf, but not the column
		# if city == self.routeSoFar[0] and not self.isVisitStart:
		# 	return row
		# # If it is the last element in the route, then only the column will be inf, not the row
		# elif city == self.routeSoFar[len(self.routeSoFar)-1]:
		# 	return not row
		# else:
		# 	return True
		return False

	# TODO: when pruning, should check to see the len of unvisited cities at the end. if it is zero, then make sure to add the remaining cost to get back to the start
	# or set up a flag??


	def _generateTuple(self, rowMajor:bool, i:int, j:int):
		if rowMajor:
			return tuple((i, j))
		else: # Rows and columns are reversed here
			return tuple((j, i))
	
	# Ensures at least one zero on the rows/columns of the matrix (besides inf)
	def findMinCostAndNormalize(self, rowMajor:bool=True):
		# Look at row each row/column to find the minCost
		for i in range(len(self.cities)):
			print(f"i: {i}")
			# If the whole row/column is going to be infinities, move on
			if self.isInfinity(self.cities[i]):
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
				print(f"cell:{cell} mincost:{minCost}")
			
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
			print(self)

	# Ensures at least one zero on the rows and columns of the matrix (besides inf)
	# Adjusts costSoFar as needed
	def reduceCostOnMatrix(self):
		self.findMinCostAndNormalize(rowMajor=True)
		self.findMinCostAndNormalize(rowMajor=False)

	# Marks the city as visited, updates the matrix and then does reduceCost to normalize the matrix again
	def visitCity(self, cityToVisit:City):
		assert(len(self.routeSoFar) != 0)
		prevCity = self.routeSoFar[len(self.routeSoFar)-1]
		print(prevCity._index)

		# Ensure that there is actually a path to the other city
		cost = self.matrix[tuple((prevCity._index, cityToVisit._index))]
		if cost == None:
			return
		# Update cost after traveling to city
		self.costSoFar += cost
		
		self.unvisitedCitiesSet.remove(cityToVisit)
		self.routeSoFar.append(cityToVisit)

		# Remove all the impossible routes now
		for i in range(len(self.cities)):
			# Update matrix to remove all items from row prevCity
			self.matrix.pop(tuple((prevCity._index, i)), None)

			# Update matrix to remove all items from col cityToVisit
			self.matrix.pop(tuple((i, cityToVisit._index)), None)

		# Update matrix to remove the inverse (cityToVisit -> prevCity) as well
		self.matrix.pop(tuple((cityToVisit._index, prevCity._index)), None)

		if cityToVisit == self.cities[0]:
			self.isVisitStart = True
			assert(len(self.matrix) == 0)
		
		else:
			self.reduceCostOnMatrix()

	def __str__(self) -> str:
		string = "State{"
		if len(self.routeSoFar) != 0:
			for city in self.routeSoFar:
				string += f"{city._name}->"
		else:
			string += "*empty*"
		string += f"}}\nCost so far: {self.costSoFar}\n"
		string += "Unvisited Cities: "
		if len(self.unvisitedCitiesSet) != 0:
			for city in self.unvisitedCitiesSet:
				string += f"{city._name} "
		else:
			string += "*empty*"

		string += '\nMatrix:\n'
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

		return string