from __future__ import division
import random
import math
import collections
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import itertools
#dimensions in form [y,x]

def distance(p0, p1):#simple distance formula
	return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

def generateCities(city_num, dimensions):
	city_list = []
	for i in range(city_num):
		coordinate = [random.randint(0,dimensions[0]),random.randint(0,dimensions[1])]
		city_list.append(coordinate)
	return city_list

def generatePaths(path_num, city_num):
	path_list = []
	original_path = range(city_num)
	for i in range(path_num):
		path = list(original_path)
		random.shuffle(path)
		path_list.append(path)
	return path_list

#path in form [0,1,2,3]
def fitness(path, city_list):
	total_distance = 0
	current_city = 0
	next_city = 1
	while next_city < len(city_list):
		the_distance = distance(city_list[path[current_city]],city_list[path[next_city]])
		total_distance += the_distance
		current_city += 1
		next_city += 1
	total_distance += distance(city_list[path[0]],city_list[path[-1]])
	return total_distance

def singlePointCrossover(parent1, parent2):
	crossover_point = random.randint(0,len(parent1))
	child = parent1[:crossover_point]
	for i in parent2:
		if i not in child:
			child.append(i)
	return child

#return 2 parents
def rouletteSelection(fitness_list):
	invertedList = [1/i**2 for i in fitness_list]
	max = sum(invertedList)
	pick = random.uniform(0,max)
	currentValue = 0
	index = 0
	for i in invertedList:
		currentValue += i
		if currentValue > pick:
			break
		index+=1
	return index

def mate(path_list, fitness_list):
	parent1 = path_list[rouletteSelection(fitness_list)]
	parent2 = path_list[rouletteSelection(fitness_list)]
	return singlePointCrossover(parent1,parent2)

def mutate(path_list, mutation_percent, swap_number):
	if type(path_list[0]) == int:
		if random.uniform(0,100) <= mutation_percent:
			lst = list(path_list)
			for l in range(swap_number):
				indices = random.sample(range(0, len(lst)), 2)
				j = indices[0]
				k = indices[1]
				lst[j], lst[k] = lst[k], lst[j]
			return lst
	return_list = []
	for i in path_list:
		if random.uniform(0,100) <= mutation_percent:
			lst = list(i)
			for l in range(swap_number):
				indices = random.sample(range(0, len(i)), 2)
				j = indices[0]
				k = indices[1]
				lst[j], lst[k] = lst[k], lst[j]
			return_list.append(lst)
		else:
			return_list.append(i)
	return return_list

def numUnique(paths):
	unique_num = 0
	existing = []
	for path in paths:
		if path not in existing:
			existing.append(path)
			unique_num += 1
	return unique_num

def makeImage(dimensions, path, city_list):
	with Drawing() as draw:
		with Image(width=dimensions[1], height=dimensions[0], background=None) as image:

			current_city = 0
			next_city = 1
			all_lines = []
			while next_city < len(path):
				line_dimensions = ((city_list[path[current_city]],city_list[path[next_city]]))
				all_lines.append(line_dimensions)
				current_city += 1
				next_city += 1
			all_lines.append((city_list[path[0]],city_list[path[-1]]))

			for a_line in all_lines:
				draw.line(a_line[0], a_line[1])
				draw(image)
			for city in city_list:
				draw.circle(city,(city[0]+10,city[1]+10))
				draw.stroke_color = Color('black')
				draw.stroke_width = 2
				draw.fill_color = Color('white')
				draw(image)

			image.save(filename = 'testimage.png')

def makeCluster(dimensions, path_list, city_list):
	with Drawing() as draw:
		with Image(width=dimensions[1], height=dimensions[0], background=None) as image:
			all_lines = []
			for path in path_list:
				current_city = 0
				next_city = 1
				while next_city < len(path):
					line_dimensions = ((city_list[path[current_city]],city_list[path[next_city]]))
					all_lines.append(line_dimensions)
					current_city += 1
					next_city += 1
				all_lines.append((city_list[path[0]],city_list[path[-1]]))
			for a_line in all_lines:
				draw.line(a_line[0], a_line[1])
				draw(image)

			draw.stroke_color = Color('black')
			draw.stroke_width = 2
			draw.fill_color = Color('white')
			for city in city_list:
				draw.circle(city,(city[0]+10,city[1]+10))
				draw.stroke_color = Color('black')
				draw.stroke_width = 2
				draw.fill_color = Color('white')
				draw(image)

			image.save(filename = 'cluster.png')

def computeBest(cities):
	all_possible_paths = itertools.permutations(range(len(cities)))
	previous_best = float("inf")
	best_one = []
	for path in all_possible_paths:
		if fitness(path,cities) < previous_best:
			previous_best = fitness(path,cities)
			best_one = path
	return best_one

#if something occurs too often, mutate all except 1
def diversify(path_list, threshold):
	path_list.sort()
	first = 0
	second = 0
	return_list = []
	while second <= len(path_list):
		if second == len(path_list):
			# print 'block',path_list[first:second]
			if len(path_list[first:second]) > threshold:
				for i in range(first,second-1):
					return_list.append(mutate(path_list[i],100,1))
				return_list.append(path_list[first])
			else:
				return_list = return_list + path_list[first:second]
		elif path_list[first] != path_list[second]:
			# print 'block', path_list[first:second]
			if len(path_list[first:second]) > threshold:
				for i in range(first,second-1):
					return_list.append(mutate(path_list[i],100,1))
				return_list.append(path_list[first])
			else:
				return_list = return_list + path_list[first:second]
			first = second
		second += 1
	return return_list

def main(num_cities, num_paths, num_generation, dimensions=[500,500], elite_num=1,diversify_threshold=10):
	cities = generateCities(num_cities,dimensions)
	paths = generatePaths(num_paths, num_cities)
	lowest_score = float('inf')
	best_path = []
	for generation in range(num_generation):
		new_generation = []
		fitnesses = []
		for path in paths:
			fitnesses.append(fitness(path,cities))

		if min(fitnesses) < lowest_score:
			best_path = paths[fitnesses.index(min(fitnesses))]
			lowest_score = min(fitnesses)

		# print sum(fitnesses)/num_paths, numUnique(paths)

		while len(new_generation) < num_paths-elite_num:
			new_generation.append(mate(paths,fitnesses))
		
		fit_copy = list(fitnesses)
		fit_copy.sort()
		for i in fit_copy[:elite_num]:
			new_generation.append(paths[fitnesses.index(i)])
		
		new_generation = mutate(new_generation, 2, 1)
		paths = new_generation
		paths = diversify(paths,diversify_threshold)

	# makeCluster(dimensions,paths,cities)
	BEST = computeBest(cities)
	if fitness(BEST,cities) != lowest_score:
		return 0
	else:
		return 1
	# print 'best', BEST, fitness(BEST,cities)
	# print 'mybest', best_path, lowest_score
	# makeImage(dimensions, lowest, cities)




def tester(num_trials, generations):
	result_list = []
	for trial in range(num_trials):
		print 'trialnum', trial
		result_list.append(main(num_cities=8,num_paths=50,num_generation=generations))
	return sum(result_list)


# 100 trials 30 generations 41%
# 100 trials 40 generations 49%
# 100 trials 50 generations 54%
print tester(100,50)



# main(num_cities=8,num_paths=50,num_generation=30)
# cities = generateCities(10,[100,100])#took 54 seconds
# computeBest(cities)




