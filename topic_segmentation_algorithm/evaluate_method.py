from __future__ import division

import json
import collections
import re
import numpy as np
def find_times(file_path):
	file = open(file_path, 'r')
	f = file.read()
	times = []
	timesEnd = []
	l = re.findall("\+\(\d*\.\d*\)",f )
	for i in l:
		i = i.replace("+","")
		i = i.replace("(","")
		i = i.replace(")","")
		times.append(float(i))

	l = re.findall("\-\(\d*\.\d*\)",f )
	for i in l:
		i = i.replace("-","")
		i = i.replace("(","")
		i = i.replace(")","")
		timesEnd.append(float(i))
	file.close()
	return times, timesEnd

def evaluate(dir_path,solution, ground_truth_json_path, shots):
	print(ground_truth_json_path)
	times, timesEnd = find_times(dir_path+"seg.txt")
	with open(ground_truth_json_path) as f:
		data = json.load(f)
		ground_truth = sorted(map(int, data.keys()))
		print(ground_truth)
		not_solution = []
		solution_pitch_mean = []
		solution_volume_mean = []
		solution_pause_mean = []
		non_solution_pitch_mean = []
		non_solution_volume_mean = []
		non_solution_pause_mean = []

		hits = 0
		for gt in ground_truth:

			for u in solution:
				if (times[u] - 10 <= gt  and times[u] + 10 >= gt ):
					solution_pitch_mean.append(shots[u].pitch)
					solution_volume_mean.append(shots[u].volume)
					solution_pause_mean.append(shots[u].pause_duration)
					print(gt, times[u], u)
					hits = hits + 1
					break


		print(hits)

		precision  = float(hits/len(solution))
		recall = float(hits/len(ground_truth))
		if(precision > 0 or recall > 0):
			fscore = 2* float((precision * recall) / (precision + recall))
		else:
			fscore = 0
		print(precision, recall, fscore)
		
		return precision, recall, fscore
