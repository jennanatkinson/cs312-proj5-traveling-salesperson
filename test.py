import math
import random
import signal
import sys
import time
from Proj5GUI import Proj5GUI
from TSPBranchAndBound import State, generateRootStateFromCities
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


# def test_should_solve_defaultRandom():
#   signal.signal(signal.SIGINT, signal.SIG_DFL)

#   app = QApplication(sys.argv)
#   w = Proj5GUI()
#   # app.exec()
#   # assert(False)
#   w.generateNetwork()
#   w.solver.setupWithScenario(w._scenario)

#   max_time = float(60)
#   results = w.solver.defaultRandomTour(max_time)
#   assert(results['cost'] < math.inf)
#   assert(results['solution'] is not None)
  

# def test_should_solve_greedy():
#   w = Proj5GUI()
#   w.diffDropDown.setCurrentIndex(4) # Hard (Deterministic)
#   w.generateNetwork()
#   w.solver.setupWithScenario(w._scenario)

# Verifies that the initial State is set up correctly, with the matrix normalized and the costSoFar correct
# (reference Homework 19)
def test_init_state():
  pass
  scenario = [[math.inf, 7, 3, 12],
              [3, math.inf, 6, 14],
              [5, 8, math.inf, 6],
              [9, 3, 5, math.inf]]
  
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
  
  testState = generateRootStateFromCities(cities)

  assert(len(testState.unvisitedCitiesSet) == len(cities))

  # Assert that the matrix is equal at each value
  for i in range(len(cities)):
    for j in range(len(cities)):
      correctCost = correctStateMatrix[i][j]
      if correctCost == math.inf:
        assert(testState.matrix.get(tuple((i, j))) == None)
      else:
        assert(testState.matrix.get(tuple((i, j))) == correctCost)

  assert(testState.cities == cities)
  assert(len(testState.routeSoFar) == 0)
  assert(testState.costSoFar == 15)
  assert(testState.isSolution() == False)
  

# def setScenario(w:Proj5GUI, points, diff, rand_seed):
#   w._scenario = Scenario( city_locations=points, difficulty=diff, rand_seed=rand_seed )
#   pass
