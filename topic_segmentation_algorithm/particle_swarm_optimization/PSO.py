from pyswarm import pso
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class PSO:
    def __init__(self, shots, doc_sim):
        self.shots = shots
        self.docSim = doc_sim
        self.samples_features = []
        self.__get_vector_representation__()
        self.distances = cosine_similarity(X=self.samples_features)

        self.sim_windows = None
        self.__build_window_sim__()

    def __get_vector_representation__(self):
        samples = []
        i = 0

        for s in self.shots:
            samples.append(s.word2vec)

        self.samples_features = samples

    def __build_window_sim__(self):
        sim_win = []
        for i in range(len(self.shots) - 1):
            sim_win.append(self.distances[i][i + 1])
        sim_win.append(0)

        self.sim_windows = sim_win

    def __fit_function__(self, X):
        value = 0
        for i in range(len(self.shots)):
            depth = 0
            if i == 0:
                depth = self.sim_windows[i + 1] - self.sim_windows[i]

            elif i == len(X) - 1:
                depth = self.sim_windows[i - 1] - self.sim_windows[i]
            else:
                depth = self.sim_windows[i - 1] - self.sim_windows[i] + self.sim_windows[i + 1] - self.sim_windows[i]

            value += X[i] * (0.4 * depth + (self.shots[i].pause_duration + (1 + ((i)/(len(self.shots)-1)) * 0.1) *
                                            self.shots[i].volume + 0.001 * self.shots[i].pitch) +
                             self.shots[i].adv_count - 0.6)

        return -value

    def __con__(self, X):
        const = []
        for i in range(len(self.shots)):
            const.append(-X[i] ** 2 + X[i])

        return const

    def run_PSO(self):
        lb = np.array([0 for i in range(len(self.shots))])
        ub = np.array([1 for i in range(len(self.shots))])
        xopt, fopt = pso(self.__fit_function__, lb, ub, swarmsize=200, f_ieqcons=self.__con__, phig=0.6, phip=0.6,
                         maxiter=500, debug=False)
        print(fopt)
        print(xopt)
        boundaries = []

        for i in range(len(xopt)):
            if xopt[i] == 1:
                boundaries.append(self.shots[i].id)

        return boundaries
