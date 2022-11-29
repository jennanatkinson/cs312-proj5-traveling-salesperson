import math
import random
import signal
import sys
import time
from Proj5GUI import Proj5GUI
from TSPBranchAndBound import State
from TSPClasses import City, Scenario


from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtWidgets import *
	from PyQt5.QtGui import *
	from PyQt5.QtCore import *
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtGui import *
	from PyQt4.QtCore import *
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))


def test_should_solve_defaultRandom():
  signal.signal(signal.SIGINT, signal.SIG_DFL)

  app = QApplication(sys.argv)
  w = Proj5GUI()
  # app.exec()
  # assert(False)
  w.generateNetwork()
  w.solver.setupWithScenario(w._scenario)

  max_time = float(60)
  results = w.solver.defaultRandomTour(max_time)
  assert(results['cost'] < math.inf)
  assert(results['solution'] is not None)
  

# def test_should_solve_greedy():
#   w = Proj5GUI()
#   w.diffDropDown.setCurrentIndex(4) # Hard (Deterministic)
#   w.generateNetwork()
#   w.solver.setupWithScenario(w._scenario)

# Sets up matrix from Homework 19
def setup_scenario(givenScenario=None):
  if givenScenario == None:
  # 2D-Arrays are used for ease of testing (a dict is used for State's matrix)
    scenario = [[math.inf, 7, 3, 12],
              [3, math.inf, 6, 14],
              [5, 8, math.inf, 6],
              [9, 3, 5, math.inf]]
  else:
    scenario = givenScenario
  
  correctStateMatrix = [[math.inf, 4, 0, 8],
                        [0, math.inf, 3, 10],
                        [0, 3, math.inf, 0],
                        [6, 0, 2, math.inf]]
  
  # Because test is set to true, the cities will return the cost at an index of the double array
  city1 = City(None, None, scenario=scenario, index=0, name='A', test=True)
  city2 = City(None, None, scenario=scenario, index=1, name='B', test=True)
  city3 = City(None, None, scenario=scenario, index=2, name='C', test=True)
  city4 = City(None, None, scenario=scenario, index=3, name='D', test=True)
  cities = [city1, city2, city3, city4]

  return scenario, correctStateMatrix, cities

# Assert that the dictionaries values are equal to the matrix's values
def assert_matrix(testMatrixDict, correctMatrixArr, len):
  for i in range(len):
    for j in range(len):
      correctCost = correctMatrixArr[i][j]
      if correctCost == math.inf:
        assert(testMatrixDict.get(tuple((i, j))) == None)
      else:
        assert(testMatrixDict.get(tuple((i, j))) == correctCost)

# Verifies that the initial State is set up correctly, with the matrix normalized and the costSoFar correct
def test_init_state():
  _, correctStateMatrix, cities = setup_scenario()
  testState = State(cities=cities)
  print(testState)
  assert(len(testState.unvisitedCitiesSet) == len(cities)-1)
  #assert_matrix(testState.matrix, correctStateMatrix, len(cities))
  assert(testState.cities == cities)
  assert(testState.routeSoFar == [cities[0]])
  assert(testState.costSoFar == 15)
  assert(testState.isSolution() == False)
  
# Visit one city (B), assert that matrix/cost adjusts
def test_visit_city():
  _, _, cities = setup_scenario()
  correctStateMatrix = [[math.inf, math.inf, math.inf, math.inf],
                        [math.inf, math.inf, 0, 7],
                        [0, math.inf, math.inf, 0],
                        [4, math.inf, 0, math.inf]]
  testState = State(cities=cities)
  testState.visitCity(cities[1])

  assert(len(testState.unvisitedCitiesSet) == len(cities)-2)
  assert_matrix(testState.matrix, correctStateMatrix, len(cities))
  assert(testState.cities == cities)
  assert(testState.routeSoFar == [cities[0], cities[1]])
  assert(testState.costSoFar == 24)
  assert(testState.isSolution() == False)

  # Visit so route is 0-2-3-1, assert that matrix/cost adjusts
def test_visit_city_fullRoute():
  _, _, cities = setup_scenario()
  correctStateMatrix = [[math.inf, math.inf, math.inf, math.inf],
                        [0, math.inf, math.inf, math.inf],
                        [math.inf, math.inf, math.inf, math.inf],
                        [math.inf, math.inf, math.inf, math.inf]]
  testState = State(cities=cities)
  testState.visitCity(cities[2])
  testState.visitCity(cities[3])
  testState.visitCity(cities[1])

  assert(len(testState.unvisitedCitiesSet) == 0)
  assert_matrix(testState.matrix, correctStateMatrix, len(cities))
  assert(testState.cities == cities)
  assert(testState.routeSoFar == [cities[0], cities[2], cities[3], cities[1]])
  assert(testState.costSoFar == 15)
  assert(testState.isSolution() == False)

  testState.visitCity(cities[0])
  assert(len(testState.unvisitedCitiesSet) == 0)
  assert(len(testState.matrix) == 0)
  assert(testState.cities == cities)
  correctRoute = [cities[0], cities[2], cities[3], cities[1]]
  assert(testState.routeSoFar == correctRoute)
  correctCost = 15
  assert(testState.costSoFar == correctCost)
  assert(testState.isSolution() == True)
  testFinalRoute, testFinalCost = testState.getSolution()
  assert(testFinalRoute == correctRoute)
  assert(testFinalCost == correctCost)

# Test where visiting the final city still does not yield a solution
def test_state_notSolution():
  scenario = [[math.inf, 7, 3, 12],
              [math.inf, math.inf, 6, 14],
              [5, 8, math.inf, 6],
              [9, 3, 5, math.inf]]
  _, _, cities = setup_scenario(scenario)
  # correctStateMatrix = [[math.inf, math.inf, math.inf, math.inf],
  #                       [math.inf, math.inf, math.inf, math.inf],
  #                       [math.inf, math.inf, math.inf, math.inf],
  #                       [math.inf, math.inf, math.inf, math.inf]]
  testState = State(cities=cities)
  testState.visitCity(cities[2])
  assert(testState.isSolution() == False)
  testState.visitCity(cities[3])
  assert(testState.isSolution() == False)
  testState.visitCity(cities[1])
  assert(testState.isSolution() == False)

  testState.visitCity(cities[0])
  assert(len(testState.unvisitedCitiesSet) == 0)
  assert(len(testState.matrix) == 0)
  assert(testState.cities == cities)
  assert(testState.routeSoFar == [cities[0], cities[2], cities[3], cities[1]])
  assert(testState.costSoFar == math.inf)
  assert(testState.isSolution() == False)
