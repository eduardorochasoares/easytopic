from sklearn.metrics import silhouette_samples, silhouette_score
from random import randint
import sys
sys.path.insert(0, 'genetic_algorithm/')
from individual import Individual
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances, polynomial_kernel, sigmoid_kernel, cosine_distances
import numpy as np
from joblib import Parallel, delayed
import multiprocessing
class GeneticAlgorithm:
    def __init__(self, population_size, constructiveHeuristic_percent, mutation_rate, cross_over_rate, shots, docSim, n_chunks, generations, local_search_percent, video_length, stopwords, ocr_on):

        self.population_size = population_size
        self.constructiveHeuristic_percent = constructiveHeuristic_percent
        self.mutation_rate = mutation_rate
        self.cross_over_rate = cross_over_rate
        self.individuals = []
        self.shots = shots
        self.docSim = docSim
        self.samples_features = []
        self.dna_size = n_chunks
        self.ocr_on = ocr_on

        self.stopwords = stopwords
        self.empty_transcript_indexes = []
        self.window_size = 10

        self.sim_score_shot_window = []
        self.window_init_indexes = []
        self.getVectorRepresentation()
        self.sim = cosine_similarity(X=self.samples_features)
        self.sim_windows = None
        self.buildWindowSim()
        self.initializePopulation()

        self.generations = generations
        self.local_search_percent = local_search_percent
        self.video_length = video_length
        self.max_topic_duration_in_seconds = 300
        self.min_topic_duration_in_seconds = 300

    '''calculate the similarity between neighbor audio chunks'''
    def buildWindowSim(self):
        sim_win = []
        for i in range(len(self.shots) - 1):
            sim_win.append(self.sim[i][i + 1])
        sim_win.append(0)

        self.sim_windows = sim_win

    '''calculates the fit value of an individual'''
    def calculate_fit_value(self, individual):
        count = 0
        depths = []
        sum_utility_points = 0

        for i in range(len(individual.dna)):
            if individual.dna[i] == 1:
                # calculates the similarity depth between a point and its neighbors
                if i == 0:
                    depths.append(self.sim_windows[i + 1] - self.sim_windows[i])

                elif i == len(individual.dna) - 1:
                    depths.append(self.sim_windows[i - 1] - self.sim_windows[i])
                else:
                    depths.append(self.sim_windows[i - 1] - self.sim_windows[i]
                                  + self.sim_windows[i + 1] - self.sim_windows[i])
                # utility value of a point i
                sum_utility_points += self.shots[i].pause_duration + 0.02 * self.shots[i].duration
                + ((1 + (i/(len(self.shots)-1)) * 0.1) * self.shots[i].volume) + 10 * depths[-1] +\
                                           self.shots[i].pitch * 0.01 + self.shots[i].adv_count
                count += 1

        if count > 0:
            individual.fit_value = 0.4 * sum_utility_points - \
                                   0.6 * count
        else:
            individual.fit_value = -100000

    '''gets the word embeddings representation of audio transcripts'''
    def getVectorRepresentation(self):
        samples = []
        i = 0

        for s in self.shots:
            samples.append(s.word2vec)

        self.samples_features = samples

    '''Implements the 2-point crossover'''
    def crossover(self, individual1, individual2):
        new_dna = []
        point1 = randint(0,self.dna_size -2)
        point2 = randint(0,self.dna_size -2)

        while(point1 == point2):
            point2 = randint(0,len(individual1.dna) -1)

        if(point1 < point2):
            new_dna += individual1.dna[:point1]
            new_dna += individual2.dna[point1:point2]
            new_dna += individual1.dna[point2:]
        else:
            new_dna += individual1.dna[:point2]
            new_dna += individual2.dna[point2:point1]
            new_dna += individual1.dna[point1:]

        return new_dna

    '''Implements the mutation'''
    def mutation(self, individual):
        index = randint(0, self.dna_size - 1)

        if (individual.dna[index] == 1):
            individual.dna[index] = 0
        else:
            individual.dna[index] = 1

    '''Initializes the population'''
    def initializePopulation(self):

        '''Fully random population initialization'''
        for i in range(int(self.population_size*(1-self.constructiveHeuristic_percent))):
            individual = Individual()
            for j in range(self.dna_size):
                gene = randint(0, 1)
                individual.dna.append(gene)

            self.individuals.append(individual)


        '''Heuristic population initialization'''
        for i in range(int(self.population_size*self.constructiveHeuristic_percent)):
            individual = Individual()
            individual.dna = self.constructiveHeuristic()

            self.individuals.append(individual)

    '''Runs the steps of GeneticAlgorithm'''
    def run(self):
        num_cores = multiprocessing.cpu_count()

        iter = 0
        iterations_without_change = 0
        best_solution = None
        best_fit = -1000000
        k_coefficient = 1
        while iter < self.generations:
            num_of_crossovers = self.population_size - int(self.cross_over_rate * self.population_size)

            '''Evaluates the population'''
            for p in self.individuals:
                self.calculate_fit_value(p)

            '''Sort the population in the reverse order by the fit
             value of the individuals'''
            self.individuals.sort(key=lambda x: x.fit_value, reverse=True)

            '''Calls the localsearch on the best individuals'''
            for i in range(int(self.population_size*self.local_search_percent)):
                self.localsearch(self.individuals[i])

            self.individuals.sort(key=lambda x: x.fit_value, reverse=True)

            #print(self.individuals[0].fit_value)
            if(self.individuals[0].fit_value > best_fit):
                print("Objective function value: " + str(self.individuals[0].fit_value))

                best_fit = self.individuals[0].fit_value
                best_solution = self.individuals[0].dna
            else:
                iterations_without_change += 1
                if iterations_without_change > 150:
                    break

            '''Selects the individuals for crossover'''
            for i in range(num_of_crossovers):
                parent1 = randint(0, int(self.cross_over_rate * self.population_size) - 1)
                parent2 = randint(0, int(self.population_size) - 1)
                while parent1 == parent2:
                    parent2 = randint(0, int(self.cross_over_rate * self.population_size) - 1)

                new_dna = self.crossover(self.individuals[parent1], self.individuals[parent2])
                self.individuals[int(self.cross_over_rate * self.population_size)+i].dna = new_dna
                #self.mutation(self.individuals[int(self.cross_over_rate * self.population_size)+i])
            '''Apply mutation on the individuals according to a probability'''
            for i in range(int(self.population_size*self.mutation_rate)):
                individual_index = randint(0, self.population_size-1)
                self.mutation(self.individuals[individual_index])

            iter += 1

        print(best_solution)
        u = [0]
        for i in range(len(best_solution)):
            if best_solution[i] == 1:
                u.append(self.shots[i].init_time)

        '''return the best solution of all generations'''
        return sorted(list(set(u)))

    '''Implements a random greedy constructive heuristic for the problem'''
    def constructiveHeuristic(self):
        hash_map = {}
        dna = [0]
        num_of_topics = randint(0, int((len(self.shots) - 1) / 2))
        depth = 0
        for i in range(len(self.shots)):
            if i == 0:
                depth = (self.sim_windows[i + 1] - self.sim_windows[i])

            elif i == self.dna_size - 1:
                depth = (self.sim_windows[i - 1] - self.sim_windows[i])
            else:
                depth = (self.sim_windows[i - 1] - self.sim_windows[i] +
                self.sim_windows[i + 1] - self.sim_windows[i])

            hash_map[i] = self.shots[i].pause_duration + 0.02 * self.shots[i].duration + \
                          ((1 + (i/(len(self.shots)-1)) * 0.1) * self.shots[i].volume) + \
                          10 * depth + self.shots[i].pitch * 0.01 + self.shots[i].adv_count

        hash_map = sorted(hash_map.items(), key=lambda kv: kv[1], reverse=True)

        chosen_topics = 0
        while chosen_topics < num_of_topics:
            index = randint(0, int(0.3 * len(hash_map)))
            dna.append(hash_map[index][0])
            chosen_topics += 1

        dna = sorted(dna)
        dna_f = []
        for i in range(self.dna_size):
            if i in dna:
                dna_f.append(1)
            else:
                dna_f.append(0)

        return dna_f


    #Divides one topic in two'''
    def divideTopic(self, dna):
        index_split = randint(0, self.dna_size-1)
        max_attempts = 10
        attempts = 0

        while(index_split != 0):
            index_split = randint(0, self.dna_size-1)
            attempts += 1
            if(attempts >= max_attempts):
                break

        if(dna[index_split] == 0):
            dna[index_split] = 1


        return dna

    # Merge two topics in one'''
    def mergeTopic(self, dna):
        index_merge = randint(0, self.dna_size-1)
        max_attempts = 10
        attempts = 0

        while(index_merge != 1):
            index_merge = randint(0, self.dna_size-1)
            attempts+=1
            if(attempts >= max_attempts):
                break
        if(dna[index_merge] == 1):
            dna[index_merge] = 0

        return dna

    # Moves a topic bound to another place'''
    def moveBound(self, dna):
        index_init = randint(0, self.dna_size - 1)
        steps = randint(0, self.dna_size-1 - index_init)
        dna[index_init] = 0
        dna[index_init + steps] = 1

        return dna


    # Explores the neighborhood of a solution trying to improve it'''
    def localsearch(self, individual):
        movement_list = ['merge',  'divide', 'move']
        self.calculate_fit_value(individual)
        current_fit_value = individual.fit_value

        i = 0
        while True:

            previous_individual_dna = individual.dna
            if movement_list[i] == 'merge':
                individual.dna = self.mergeTopic(individual.dna)
            elif movement_list[i] == 'divide':
                individual.dna = self.divideTopic(individual.dna)
            elif movement_list[i] == 'move':
                individual.dna = self.moveBound(individual.dna)

            self.calculate_fit_value(individual)
            post_search_fit_value = individual.fit_value

            if post_search_fit_value > current_fit_value and movement_list[i] != 'move':
                i += 1
            elif post_search_fit_value <= current_fit_value:
                i -= 1

            if i == -1:
                break
