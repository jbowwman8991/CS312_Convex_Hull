from math import comb
from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False
		
# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)
		
	def eraseHull(self,polygon):
		self.view.clearLines(polygon)
		
	def showText(self,text):
		self.view.displayStatusText(text)
	

# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()
		points = sorted(points, key=lambda x: x.x())
		t2 = time.time()

		t3 = time.time()
		# this is a dummy polygon of the first 3 unsorted points
		polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3)]
		new_hull = self.divide_conquer(points)
		new_hull_polygon = [QLineF(new_hull[i], new_hull[(i + 1) % len(new_hull)]) for i in range(len(new_hull))]
		t4 = time.time()

		print(t4 - t3)

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(new_hull_polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

	def divide_conquer(self, points):													# Total Time: O(nlog(n)), Total Space: O(n)
		size = len(points)

		if size < 3:
			return points

		L = self.divide_conquer(points[:size//2])										# Time: O(log(n)), Space: O(n/2) depth
		R = self.divide_conquer(points[size//2:])										# Time: O(log(n)), Space: O(n/2) depth

		left_rightmost_index = L.index(max(L, key=lambda x: x.x()))						# Time: O(n), Space: O(1)
		right_leftmost_index = R.index(min(R, key=lambda x: x.x()))						# Time: O(n), Space: O(1)

		# upper tangent
		L_index = left_rightmost_index
		R_index = right_leftmost_index
		top_left, top_right = self.upper_tangent(L, R, L_index, R_index)				# Time: O(n), Space: O(1)

		# lower tangent 
		L_index = left_rightmost_index
		R_index = right_leftmost_index
		bottom_left, bottom_right = self.lower_tangent(L, R, L_index, R_index)			# Time: O(n), Space: O(1)

		# combining 
		return self.combine(L, R, top_left, top_right, bottom_left, bottom_right)		# Time: O(n), Space: O(n)
		
	
	def combine(self, L, R, top_left, top_right, bottom_left, bottom_right):			# Total Time: O(n), Total Space: O(n)
		combined_hull = []																# Time: O(1), Space: O(n) eventually

		t_r = top_right
		while t_r != bottom_right:														# Time: O(n/2), Space: O(1)
			combined_hull.append(R[t_r])
			t_r = (t_r + 1) % len(R)
		combined_hull.append(R[bottom_right])

		b_l = bottom_left
		while b_l != top_left:															# Time: O(n/2), Space: O(1)
			combined_hull.append(L[b_l])
			b_l = (b_l + 1) % len(L)
		combined_hull.append(L[top_left])

		return combined_hull

	def upper_tangent(self, L, R, L_index, R_index):									# Total Time: O(n), Total Space: O(1)
		s = self.find_slope(L[L_index], R[R_index])										# Time: O(1), Space: O(1)

		L_decreasing = False
		R_decreasing = False

		while not L_decreasing or not R_decreasing:										# Time: O(n), Space: O(1)
			L_decreasing = True
			R_decreasing = True

			while L_decreasing:															# Time: O(n/2), Space: O(1)
				L_index = (L_index - 1) % len(L)
				new_s = self.find_slope(L[L_index], R[R_index])							# Time: O(1), Space: O(1)

				if new_s < s:
					s = new_s
				else:
					L_index = (L_index + 1) % len(L)
					L_decreasing = False

			if self.find_slope(L[L_index], R[(R_index + 1) % len(R)]) <= s:				# Time: O(1), Space: O(1)
				break

			while R_decreasing:															# Time: O(n/2), Space: O(1)
				R_index = (R_index + 1) % len(R)
				new_s = self.find_slope(L[L_index], R[R_index])							# Time: O(1), Space: O(1)

				if new_s > s:
					s = new_s
				else:
					R_index = (R_index - 1) % len(R)
					R_decreasing = False

			if self.find_slope(L[(L_index - 1) % len(L)], R[R_index]) >= s:				# Time: O(1), Space: O(1)
				break

		top_left = L_index
		top_right = R_index

		return top_left, top_right

	def lower_tangent(self, L, R, L_index, R_index):									# Total Time: O(n), Total Space: O(1)
		s = self.find_slope(L[L_index], R[R_index])										# Time: O(1), Space: O(1)

		L_decreasing = False
		R_decreasing = False

		while not L_decreasing or not R_decreasing:										# Time: O(n), Space: O(1)
			L_decreasing = True
			R_decreasing = True

			while L_decreasing:															# Time: O(n/2), Space: O(1)
				L_index = (L_index + 1) % len(L)
				new_s = self.find_slope(L[L_index], R[R_index])							# Time: O(1), Space: O(1)

				if new_s > s:
					s = new_s
				else:
					L_index = (L_index - 1) % len(L)
					L_decreasing = False

			if self.find_slope(L[L_index], R[(R_index - 1) % len(R)]) >= s:				# Time: O(1), Space: O(1)
				break

			while R_decreasing:															# Time: O(n/2), Space: O(1)
				R_index = (R_index - 1) % len(R)
				new_s = self.find_slope(L[L_index], R[R_index])							# Time: O(1), Space: O(1)

				if new_s < s:
					s = new_s
				else:
					R_index = (R_index + 1) % len(R)
					R_decreasing = False

			if self.find_slope(L[(L_index + 1) % len(L)], R[R_index]) <= s:				# Time: O(1), Space: O(1)
				break

		bottom_left = L_index
		bottom_right = R_index

		return bottom_left, bottom_right

	def find_slope(self, p, q):															# Total Time: O(1), Total Space: O(1)
		return (q.y() - p.y()) / (q.x() - p.x())
