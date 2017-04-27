# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 11:33:04 2017

@author: Taylor
"""

import sys
import os
import re
import yaml

#pass in path to user folders (the data folder)
path_to_files = sys.argv[1]
#words, word/color pairs, word/shape pairs
counts = [0,0,0]
word_dict, word_color_dict, word_shape_dict = {},{},{}
word_color_in_world , word_shape_in_world = [],[]
colors_seen,shapes_seen = [],[]

for user_folder in os.listdir(path_to_files):
	for experiment_folder in os.listdir(path_to_files + "/" + user_folder):
		for file_name in os.listdir(path_to_files + "/" + user_folder + "/" + experiment_folder):
			if file_name.endswith(".txt"):
				sentence_file = file_name
		sentence = open(path_to_files + "/" + user_folder + "/" + experiment_folder + "/" + sentence_file, 'r')
		tokens = [t.strip() for t in re.findall(r"[\w']+|[.,!?;:]", re.sub(r"[.,!?;:]",' ',sentence.readline()))]
		#look through every word
		for word in tokens:
			counts[0] = counts[0] + 1
			if word.lower() in word_dict:
				word_dict[word.lower()] = word_dict[word.lower()] + 1
			else:
				word_dict[word.lower()] = 1
		sentence.close()
		for file_name in os.listdir(path_to_files + "/" + user_folder + "/" + experiment_folder):
			if file_name.endswith(".yaml"):
				with open(path_to_files + "/" + user_folder + "/" + experiment_folder + "/" + file_name, 'r') as f:
					world_files = yaml.load(f)
					loc_count = 0
					for loc in world_files["worlds"]:
						loc_count = loc_count + 1
						colors_seen,shapes_seen = [],[]
						with open(path_to_files + "/" + user_folder + "/" + experiment_folder + "/../../" + loc, 'r') as g:
							world = yaml.load(g)
							task_object = [0,0] + world["task_object"]
							object_list = world["objects"]
							object_list.append(task_object)
							o_count = 0
							for o in object_list:
								o_count = o_count + 1
								sentence = open(path_to_files + "/" + user_folder + "/" + experiment_folder + "/" + sentence_file, 'r')
								tokens = [t.strip() for t in re.findall(r"[\w']+|[.,!?;:]", re.sub(r"[.,!?;:]",' ',sentence.readline()))]
								for word in tokens:
									shape,color = o[3], o[4]
									if (word.lower(),shape) in word_shape_dict:
										if (shape not in shapes_seen):
											word_shape_dict[(word.lower(),shape)] = word_shape_dict[(word.lower(),shape)] + 1
											counts[2] = counts[2] + 1
									else:
										word_shape_dict[(word.lower(),shape)] = 1
										counts[2] = counts[2] + 1
									if(word.lower(),color) in word_color_dict:
										if (color not in colors_seen):
											word_color_dict[(word.lower(),color)] = word_color_dict[(word.lower(),color)] + 1
											counts[1] = counts[1] + 1
									else:
										word_color_dict[(word.lower(),color)] = 1
										counts[1] = counts[1] + 1
								sentence.close()
								shapes_seen.append(shape)
								colors_seen.append(color)
							g.close()
				f.close()
		

colors = ["blue","red","green","purple","yellow","orange"]
shapes = ["circle","square","triangle","star","diamond"]

max_list = []
max_ratio = 0
#print("red")
print("\n")
for key in word_shape_dict:
	if(key[0] == "blue"):
		Ffn = float(word_shape_dict[key])#/float(counts[2])
		Fn = 10*float(word_dict[key[0]])#/float(counts[0])
		ratio = float(Ffn/Fn)
		print(ratio)
		if(ratio == max_ratio):
			max_list.append(key[1])
		elif(ratio > max_ratio):
			max_ratio = ratio
			max_list = [key[1]]
		#print(key, word_color_dict[key]/word_dict[key[0]])
print(max_list, max_ratio)
print("\n")


