import math

from TSPClasses import City


INF_STRING = "-"

# Given a list of cities, return an init state
def generateRootStateFromCities(cities):
	#Start with the first city as "visited"
	state = State(unvisitedSet=set(cities), cities=cities)

	#Initialize the matrix
	matrix = dict()
	for city in cities:
		for otherCity in cities:
			if city != otherCity:
				cost = city.costTo(otherCity)
				if cost != math.inf:
					matrix[tuple((city._index, otherCity._index))] = cost
	state.matrix = matrix
	state.reduceCostOnMatrix()
	return state

class State:
	#unvisitedCitiesSet, set of cities that haven't been visited yet
	#matrix, dictionary to show which edges can be used next
	#cities, reference to the list of cities
	#routeSoFar, list of cities in order of what we have visited so far
	#costSoFar, the cost we have accumulated on our route
	def __init__(self, unvisitedSet=set(), matrix=dict(), cities=[], route=[], costSoFar:int=0):
		self.unvisitedCitiesSet = unvisitedSet
		self.matrix = matrix
		self.cities = cities
		self.routeSoFar = route
		self.costSoFar = costSoFar

	# Sees if this State yields a solution
	def isSolution(self) -> bool:
		return len(self.unvisitedCitiesSet) == 0 and self.costSoFar != math.inf

	# Return the route if a solution
	def getSolutionRoute(self):
		if self.isSolution():
			return self.routeSoFar
		else:
			return None

	def isVisitedCity(self, city:City) -> bool:
		return not (city in self.unvisitedCitiesSet)

	# Ensures at least one zero on the rows/columns of the matrix (besides inf)
	# Note: comments/names are the to show rows, but it reverses for columns
	def findMinCostAndNormalize(self, row:bool=True):
		# Look at rows to find the minCost
		for rowIndex in range(len(self.cities)):
			# If the whole row is going to be infinities, move on
			if (self.isVisitedCity(self.cities[rowIndex])):
				continue
			
			minCost = math.inf

			#Examine each cell to find the minCost
			for colIndex in range(len(self.cities)):
				if row:
					cell = tuple((rowIndex, colIndex))
				else: # Rows and columns are reversed here
					cell = tuple((colIndex, rowIndex))
				
				cost = self.matrix.get(cell)
				if cost != None and cost < minCost:
					minCost = cost
					if minCost == 0:
						break
			
			# If we are taking on additional costs, we need to readjust the costSoFar and row/column numbers
			if minCost != 0 and minCost < math.inf:
				self.costSoFar += minCost

			# Update all costs in same row/column to normalize
				for colIndex in range(len(self.cities)):
					if row:
						cell = tuple((rowIndex, colIndex))
					else: # Rows and columns are reversed here
						cell = tuple((colIndex, rowIndex))
					cost = self.matrix.get(cell)
					# If not infinity, update cell's cost
					if cost != None:
						self.matrix[cell] = cost - minCost

	# Ensures at least one zero on the rows and columns of the matrix (besides inf)
	# Adjusts costSoFar as needed
	def reduceCostOnMatrix(self):
		self.findMinCostAndNormalize(row=True)
		self.findMinCostAndNormalize(row=False)

	# Marks the city as visited, updates the matrix and then does reduceCost to normalize the matrix again
	def visitCity(self, prevCity:City, cityToVisit:City):
		self.unvisitedCitiesSet.remove(cityToVisit)

		# Update cost after traveling to city
		cost = self.matrix[tuple((prevCity, cityToVisit))]
		self.costSoFar += cost
		
		# Remove all the impossible routes now
		for i in range(len(self.cities)):
			# Update matrix to remove all items from row prevCity
			del self.matrix[tuple((prevCity, i))]

			# Update matrix to remove all items from col cityToVisit
			del self.matrix[tuple((i, cityToVisit))]
			
		# Update matrix to remove the inverse (cityToVisit -> prevCity) as well
		del self.matrix[tuple((cityToVisit, prevCity))]

		self.reduceCostOnMatrix()

	def __str__(self) -> str:
		string = "**STATE**\n"
		string += f"Cost so far (lower bound): {self.costSoFar}\n"
		string += "RouteSoFar: "
		if len(self.routeSoFar) != 0:
			for city in self.routeSoFar:
				string += f" -> {city._name}({city._index})"
		else:
			string += "*empty*"
		string += "\nUnvisited Nodes: "
		if len(self.unvisitedCitiesSet) != 0:
			for city in self.unvisitedCitiesSet:
				string += f"{city._name}({city._index}) "
		else:
			string += "*empty*"

		string += '\nMatrix:\n'
		# Format the matrix printing
		table_data = [[]]
		# Print the names of the cities at the top
		for colIndex in range(-1, len(self.cities)):
			if colIndex == -1:
				table_data[0].append(" ")
			else:
				#assert(type(self.cities[i]) == City)
				table_data[0].append(self.cities[colIndex]._name)
		
		for colIndex in range(0, len(self.cities)):
			table_data.append([])
			last = len(table_data)-1
			for rowIndex in range(-1, len(self.cities)):
				# Append the name of the city for the row
				if rowIndex == -1:
					table_data[last].append(self.cities[colIndex]._name)
				# Print the same city -> same city as inf
				elif rowIndex == colIndex:
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