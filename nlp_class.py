"""
This file takes a path to the training files and an annotated conllx file.
Ex: python test_groundings ~/pathto/gsim/data ~/pathto/gsim/data/user_num/experiment_num
This file outputs the objects  (in the yaml format) for the moving object and landmark
	object and the number of a location learned by the gmm program
"""

from grounding_all import WordLearner
import sys
import re
import os
import yaml

class nlp():
	def __init__(self):
		self.grounding = {}

	def up_tree(self,line_num,lines, moving_objects,groundings):
		tokens = [t.strip() for t in re.findall(r"[\w']+|[.,!?;:]", re.sub(r"[.,!?;:]",' ',lines[line_num-1]))]
		word = tokens[1]
		if word in groundings:
			for o in moving_objects:
				if (o[3] not in groundings[word]) and (o[4] + 5 not in groundings[word]):
					moving_objects.remove(o)
		next = tokens[6]
	if next == "0":
		return
	else:
		return up_tree(int(next),lines, moving_objects,groundings)

	def down_tree(self,line_num,lines,landmark_objects):
		tokens = [t.strip() for t in re.findall(r"[\w']+|[.,!?;:]", re.sub(r"[,!?;:]",' ',lines[line_num-1]))]
		word = tokens[1]
		hold_landmarks = list(landmark_objects)
		if word in self.groundings and depth != 0:
			for o in landmark_objects:
				if (o[3] not in self.groundings[word]) and (o[4] + 5 not in self.groundings[word]):
					hold_landmarks.remove(o)
		landmark_objects = list(hold_landmarks)
		if(len(landmark_objects) == 1):
			return landmark_objects
		for line in lines:
			tokens = [t.strip() for t in re.findall(r"[\w']+|[.,!?;:]", re.sub(r"[,!?;:]",' ',line))]
			if(tokens != []):
				if int(tokens[6]) == line_num:
					landmark_objects = down_tree(int(tokens[0]),lines,landmark_objects)
		return landmark_objects


	def train(self,training_set):
		path_to_files = "data/"
		learner = WordLearner(path_to_files,training_set)
		learner.ground()
		self.groundings = learner.grounding_dict


	def predict_goal(self,user,exp,num):
		x = 1
		path_to_dependencies = "data/user_"+user+"/experiment_"+exp+"/"

		for file_name in os.listdir(path_to_dependencies):
			if file_name == "worlds.yaml":
				with open(path_to_dependencies + "/" + file_name, 'r') as f:
					world_files = yaml.load(f)
					loc = world_files["worlds"][0]
					with open(path_to_dependencies + "/../../" + loc, 'r') as g:
						world = yaml.load(g)
						task_object = [0,0] + world["task_object"]
						object_list = world["objects"]
						object_list.append(task_object)
		landmark_objects = list(object_list)
		spatial_features = [11,12,13,14,15,16,17,18,19]

		spatial_location = None
		spatial_relation = []
		test = open(path_to_dependencies + "annotations.conllx", 'r')
		lines = test.readlines()
		for line in lines:
			tokens = [t.strip() for t in re.findall(r"[\w']+|[.,!?;:]", re.sub(r"[.,!?;:]",' ',line))]
			word = tokens[1].lower()
			if word in groundings:
				if not set(groundings[word]).isdisjoint(set(spatial_features)):
					spatial_location = tokens[0]
					spatial_relation = groundings[word]
					break
		if(spatial_location != None):
			landmark_objects = down_tree(int(spatial_location),lines,landmark_objects,groundings,0)
		#print(landmark_objects)
		#return([moving_objects,landmark_objects,spatial_relation])





