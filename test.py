import math
import random
import signal
import sys
import time
from Proj5GUI import Proj5GUI


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
#   pass
