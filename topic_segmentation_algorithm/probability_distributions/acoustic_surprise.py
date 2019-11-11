from scipy.special import gamma
from math import pow, log
import sys
'''
 * Copyright 2011-2012 B. Schauerte. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *
 *    1. Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *
 *    2. Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in
 *       the documentation and/or other materials provided with the
 *       distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY B. SCHAUERTE ''AS IS'' AND ANY EXPRESS OR
 * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL B. SCHAUERTE OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 * BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
 * ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * The views and conclusions contained in the software and documentation
 * are those of the authors and should not be interpreted as representing
 * official policies, either expressed or implied, of B. Schauerte.
 *
'''



'''**
 * A Ring buffer that calculates the (windowed) mean/variance/surprise.
 * Since it is a template class, you can also use data vectors, matrices,
 * etc. and calculate the (independent) variance/surprise for each element.
 *
 * This is a simple demonstration implementation. If you consider to use it
 * for real applications, then you need to take care about the numerical
 * stability! E.g., you can use the full data buffer to recalculate the
 * variance/mean non-iterative at some intervals (e.g., after every 1000
 * pushes) - however, this leads to a discontinuity. Well, that's where
 * you need to get creative and I don't want to spoil the fun ;)
 * (see, e.g., "Variance Estimation over Sliding Windows", 2007, L. Zhang
 *  and Y. Guan and/or "Maintaining variance and k-medians over data stream
 *  windows", 2003, B. Babcock, M. Datar, R. Motwani, and L. O’Callaghan.)
 *
 * This is a prototypic implementation (small & simple). Windowed Gaussian
 * surprise has been applied/presented in [1] to calculate the auditory
 * saliency / auditory surprise (acoustic surprise) using spectrograms.
 *
 * [1] B. Schauerte, B. Kuehn, K. Kroschel, R. Stiefelhagen, "Multimodal
 *     Saliency-based Attention for Object-based Scene Analysis". In Proc.
 *     Int. Conf. Intelligent Robots and Systems (IROS), 2011.
 *
 * @author B. Schauerte
 * @date   2011-2012
 * @url    http://cvhci.anthropomatik.kit.edu/~bschauer/
 *'''
'''Ported from C++ to Python 3.5 by Eduardo Soares, Master's degree student in Computer Science'''
class GaussianWindowedSurpriseRingBuffer:
    def __init__(self, window_size):
        self.window_size = window_size #size of the history (window size)
        self.window_size_plus_one = window_size + 1 # (helper)
        self.min_variance_value = sys.float_info.epsilon
        self.count = 0 # number of already pushed/inserted elements
        self.index = 0 # current index
        self.mean = 0  #current mean
        self.variance =  sys.float_info.epsilon # current variance
        self.var_sum = 0 # (helper)
        self.surprise = 0 #surprise value of the last pushed element
        self.data = [0 for i in range(self.window_size)] #we need to keep a full history


    def push_element(self, element):
        next_index = (self.index + 1) % self.window_size

        '''Calculate/Update the mean and variance'''

        new_mean = self.mean + (element - self.data[next_index]) / self.window_size
        new_var_sum = 0
        new_variance = 0

        tmp_mean = element
        tmp_index = (next_index + 1) % self.window_size

        '''Calculate the variance (welfords algorithm)'''
        for i in range(1, self.window_size):
            delta = (self.data[tmp_index] - tmp_mean)
            tmp_mean += delta / (i + 1)
            new_var_sum += delta * (self.data[tmp_index] - tmp_mean)
            tmp_index = (tmp_index + 1) % self.window_size

        new_variance = new_var_sum / self.window_size


        '''Calculate the surprise, etc'''
        mean_plus_one = (self.mean * self.window_size + element) / self.window_size_plus_one
        var_sum_plus_one = self.var_sum + (element - self.mean) * (element - mean_plus_one)
        variance_plus_one = var_sum_plus_one  / self.window_size_plus_one

        if(new_var_sum < 0):
            new_var_sum = 0

        if(new_variance < self.min_variance_value):
            new_variance = self.min_variance_value

        '''The Surprise Calculation'''
        if(variance_plus_one == 0):
            self.surprise = 0
        else:
            self.surprise  = (pow(mean_plus_one - self.mean, 2) + (variance_plus_one - self.variance)) / (2*self.variance)
            + log(self.variance / variance_plus_one) / 2;

        '''Update the values and indices'''

        self.data[next_index] = element
        self.index = next_index
        self.mean = new_mean
        self.var_sum = new_var_sum
        self.variance = new_variance
        self.count += 1
