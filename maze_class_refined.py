import random 
import cv2

'''
The maze class is all the hardware part. Some functions here are currently not used but could be useful.
'''

class Maze() :

	def __init__(self, seed, video_path) :
		self.chamber = {}
		self.odor = {}
		random.seed(seed)
		self.key_points = []
		self.video_capture = cv2.VideoCapture(video_path)
		ret, self.frame_0 = self.video_capture.read()
		if ret:
			#self.frame_0 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			self.key_points.append([206, 206])
			self.old_center = self.key_points[0]
			self.draw_key_points()
		self.chamberchoice()
		self.placeodorrandom()
	
	def draw(self,event,x,y,flags,param):
		if event == cv2.EVENT_LBUTTONDOWN:
			cv2.circle(self.frame_0,(x,y),1,(255,0,0),-1)
			self.key_points.append([x,y])
			print(f"Point {len(self.key_points)} saved : {x}, {y}")
		

	def draw_key_points(self) :
     
		# We ask the user if he wants to recalibrate the maze
		user_input = input("Do you want to recalibrate the maze, be aware that the result will not be reproducable ? (y/n) : ").lower()
		if user_input == 'y':
      
			self.key_points = []
			self.clicks_per_choice = {"Choice1": 2, "Choice2": 4, "Choice3": 6, "Choice4": 8, "Choice5": 10, "Choice6": 12}
			cv2.namedWindow('image')
			cv2.setMouseCallback('image', self.draw)
			print('Please calibrate the maze')
			while(True):
				cv2.imshow('image', self.frame_0)
				if cv2.waitKey(1) & 0xff == 27 or len(self.key_points) >= 42:
					break
			cv2.destroyAllWindows()
			self.choicepoints = {}
			idx = 0
			for choice, n_clicks in self.clicks_per_choice.items():
				self.choicepoints[choice] = self.key_points[idx:idx + n_clicks]
				idx += n_clicks
		else:
			xabs = 16
			yord = 67
			x,y = 108,343

		# Autres valeurs possibles
		# 	xabs = 15
		# 	yord = 66
		# 	x,y = 104,350

			self.choicepoints = {  'Choice1': [[x-6 ,y -7],[x+6 +xabs  ,y -7 ]],
						'Choice2': [[x-xabs, y-yord],[x, y-yord],[x+xabs, y-yord],[x+xabs*2, y-yord]],
						'Choice3': [[x-xabs*2, y-yord*2],[x-xabs, y-yord*2],[x, y-yord*2],[x+xabs, y-yord*2],[x+xabs*2, y-yord*2],[x+xabs*3, y-yord*2]],
						'Choice4': [[x-xabs*3, y-yord*3],[x-xabs*2, y-yord*3],[x-xabs, y-yord*3],[x, y-yord*3],[x+xabs, y-yord*3],[x+xabs*2, y-yord*3],[x+xabs*3, y-yord*3],[x+xabs*4, y-yord*3]],
						'Choice5': [[x-xabs*4, y-yord*4],[x-xabs*3, y-yord*4],[x-xabs*2, y-yord*4],[x-xabs, y-yord*4],[x, y-yord*4],[x+xabs, y-yord*4],[x+xabs*2, y-yord*4],[x+xabs*3, y-yord*4],[x+xabs*4, y-yord*4],[x+xabs*5, y-yord*4]],
						'Choice6': [[x-xabs*5, y-yord*5],[x-xabs*4, y-yord*5],[x-xabs*3, y-yord*5],[x-xabs*2, y-yord*5],[x-xabs, y-yord*5],[x, y-yord*5],[x+xabs, y-yord*5],[x+xabs*2, y-yord*5],[x+xabs*3, y-yord*5],[x+xabs*4, y-yord*5],[x+xabs*5, y-yord*5],[x+xabs*6, y-yord*5]],
		}
		
			
	def placeodorrandom(self):
		for choice, coordinates_list in self.choicepoints.items():
			odorarray = []
			for i in range(0 ,len(coordinates_list) - 1,2):
				pair = [coordinates_list[i], coordinates_list[i + 1]]
				random_coordinates = random.choice(pair)
				odorarray.append(random_coordinates)
			self.odor[choice] = odorarray
	
	def chamberchoice(self):
		# Define a fixed distance below each choice
		distance_below_choice = 17  # Adjust this value as needed
		for choice, points in self.choicepoints.items():
			chamber_midpoints = []  # List to store midpoints for each choice
		# Iterate through pairs of coordinates within each choice
			for i in range(0 ,len(points) - 1,2):
				# Calculate the midpoint between x-coordinates
				chamber_x = round((points[i][0] + points[i + 1][0]) / 2)
				# Set y-coordinate below the choice
				chamber_y = points[i][1] + distance_below_choice
				# Add chamber coordinates to the list
				chamber_midpoints.append([chamber_x, chamber_y])
			# Add the list of midpoints to the chamber dictionary
			self.chamber[choice] = chamber_midpoints
		# Print or use the chamber coordinates as needed
		#print("Chamber coordinates:", self.chamber)
