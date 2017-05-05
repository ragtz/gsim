# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 11:33:04 2017

@author: Taylor
"""

import sys
import os
import re
import yaml
import numpy as np
from scipy import stats

class WordLearner():
	def __init__(self, path_to_files, training_set):
		self.word_dict,self.word_feature_dict = {},{}
		self.path_to_files = path_to_files
		self.grounding_dict = {}
		self.training_set = training_set

	def get_entropy(self,distribution):
		return stats.entropy(distribution,base=2)

	def ground(self):
		shapes_seen,colors_seen,spatial_seen = [],[],[]
		for user_experiment in self.training_set:
		#for user_folder in os.listdir(self.path_to_files):
		#	for experiment_folder in os.listdir(self.path_to_files + "/" + user_folder):
			for file_name in os.listdir(self.path_to_files + "/user_" + str(user_experiment[0]) + "/experiment_" + str(user_experiment[1])):
				if file_name.endswith(".txt"):
					sentence_file = file_name
			sentence = open(self.path_to_files + "/user_" + str(user_experiment[0]) + "/experiment_" + str(user_experiment[1]) + "/" + sentence_file, 'r')
			tokens = [t.strip() for t in re.findall(r"[\w']+|[.,!?;:]", re.sub(r"[.,!?;:]",' ',sentence.readline()))]
			#look through every word
			for word in tokens:
				if word.lower() in self.word_dict:
					self.word_dict[word.lower()] = self.word_dict[word.lower()] + 1
				else:
					self.word_dict[word.lower()] = 1
			sentence.close()
			for file_name in os.listdir(self.path_to_files + "/user_" + str(user_experiment[0]) + "/experiment_" + str(user_experiment[1])):
				if file_name == "worlds.yaml":
					with open(self.path_to_files + "/user_" + str(user_experiment[0]) + "/experiment_" + str(user_experiment[1]) + "/" + file_name, 'r') as f:
						world_files = yaml.load(f)
						for loc in world_files["worlds"]:
							colors_seen,shapes_seen,spatial_seen = [],[],[]
							with open(self.path_to_files + "/user_" + str(user_experiment[0]) + "/experiment_" + str(user_experiment[1]) + "/../../" + loc, 'r') as g:
								world = yaml.load(g)
								task_object = [0,0] + world["task_object"]
								object_list = world["objects"]
								object_list.append(task_object)
								for o in object_list:
									sentence = open(self.path_to_files + "/user_" + str(user_experiment[0]) + "/experiment_" + str(user_experiment[1]) + "/" + sentence_file, 'r')
									tokens = [t.strip() for t in re.findall(r"[\w']+|[.,!?;:]", re.sub(r"[.,!?;:]",' ',sentence.readline()))]
									for word in tokens:
										shape,color = o[3], o[4]+5
										if (word.lower(),shape) in self.word_feature_dict:
											if (shape not in shapes_seen):
												self.word_feature_dict[(word.lower(),shape)] = self.word_feature_dict[(word.lower(),shape)] + 1
										else:
											self.word_feature_dict[(word.lower(),shape)] = 1
										if(word.lower(),color) in self.word_feature_dict:
											if (color not in colors_seen):
												self.word_feature_dict[(word.lower(),color)] = self.word_feature_dict[(word.lower(),color)] + 1
										else:
											self.word_feature_dict[(word.lower(),color)] = 1
									sentence.close()
									shapes_seen.append(shape)
									colors_seen.append(color)
								g.close()
					f.close()
				elif file_name.endswith("yaml"):
					with open(self.path_to_files + "/user_" + str(user_experiment[0]) + "/experiment_" + str(user_experiment[1]) + "/" + file_name, 'r') as f:
						displacements = yaml.load(f)
						object_list = displacements["objects"]
						for o in object_list:
							sentence = open(self.path_to_files + "/" + user_folder + "/" + experiment_folder + "/" + sentence_file, 'r')
							tokens = [t.strip() for t in re.findall(r"[\w']+|[.,!?;:]", re.sub(r"[.,!?;:]",' ',sentence.readline()))]
							for word in tokens:
								spatial_relation = o[0] + 11
								if (word.lower(),spatial_relation) in self.word_feature_dict:
									if (spatial_relation not in spatial_seen):
										self.word_feature_dict[(word.lower(),spatial_relation)] = self.word_feature_dict[(word.lower(),spatial_relation)] + 1
								else:
									self.word_feature_dict[(word.lower(),spatial_relation)] = 1
							sentence.close()
							spatial_seen.append(spatial_relation)
						f.close()
		threshold = 3.43
		for word in self.word_dict:
			word = word.lower()
			(best_feature, p_feature, p_features) = self.get_best(word, self.word_feature_dict, self.word_dict)
			if self.get_entropy(p_features) < threshold and p_feature > 0.5:
				self.grounding_dict[word] = best_feature

	def get_best(self,word,pair_counts,word_counts):
		max_list = []
		max_ratio = 0
		ratio_list = []
		for key in pair_counts:
			if key[0] == word:
				Ffn = float(pair_counts[key])
				Fn = 10*float(word_counts[key[0]])
				ratio = float(Ffn/Fn)
				ratio_list.append(ratio)
				if ratio == max_ratio:
					max_list.append(key[1])
				elif ratio > max_ratio:
					max_ratio = ratio
					max_list = [key[1]]
		if(len(ratio_list) < 20):
			diff = 20 - len(ratio_list)
			for i in range(diff):
				ratio_list.append(0.0)
		return(max_list, max_ratio, ratio_list)





