#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright (C) 2013 KeiraZhao <zhaohan2009011312@gmail.com>
#
# Distributed under terms of the Tsinghua University license.

import numpy as np
import csv
import time
import sys
import matplotlib.pyplot as plt
from hmm import HMM
from learner import SpectralLearner
from EM import BaumWelch

class SPClassifier(object):
    
    def __init__(self, trainfile, testfile):
        '''
        @trainfile:
            type:    string
            param:   Filename of the training data
            
        @testfile:
            type:    string
            param:   Filename of the testing data
        '''
        data = self._loadData(trainfile)
        trsize = len(data)
        self.trainSet = data[:trsize]
        self.testSet = self._loadData(testfile)
        self.sl_learner = SpectralLearner()
#        self.oom_learner = OOMLearner()
#        self.emlearner = BaumWelch(4, 4)
        
    def _loadData(self, filename):
        '''
        @filename:
            type:    string
            param:   Filename of input data
        
        @return:
            type:    list[list_1, list_2, ... list_dsize]
            param:   Observation sequences generated by model
        '''
        with file(filename, 'r') as f:
            reader = csv.reader(f)
            data = [map(int, row) for row in reader]
        return data
    
    def loadModel(self, modelpath):
        '''
        @modelpath:
            type:    string
            param:   Model path of HMM parameters
        '''
        self.model = HMM(filename=modelpath)
    
    def train(self):
        t_start = time.time()
        self.sl_learner.train(self.trainSet)
        t_end = time.time()
        print 'Time used for Spectral learner and OOM learner:', (t_end - t_start)
        
    
    def KLDiv(self, tprob, sprob):
        '''
        @tprob:
            type:    list()
            param:   True probability distribution
            
        @sprob:    
            type:    list()
            param:   Simulated probability distribution 
        '''
        tprob = np.array(tprob, dtype=np.float)
        sprob = np.array(sprob, dtype=np.float)
        return np.sum(tprob * np.log(tprob / sprob))
        
    def draw(self, tprob, sprob, eprob):
        '''
        @tprob:
            type:    list()
            param:   True probability distribution
            
        @sprob:    
            type:    list()
            param:   Simulated probability distribution 
        '''
        coor = range(len(tprob))
        plt.plot(coor, tprob, label='True distribution', color='blue', linewidth=2)
        plt.plot(coor, sprob, label='Spectral learning distribution', color='red', linewidth=2)
        plt.plot(coor, eprob, laebl='EM-algorithm distribution', color='green', linewidth=2)
        plt.xlabel('Observation sequence')
        plt.ylabel('Probability')
        plt.title('Probability distribution of P[X1, X2, X3, X4]')
        plt.xlim(1, len(tprob))
        plt.legend()
        plt.show()
        
    
    def testing(self, outfile):
        records = list()
        for seq in self.testSet:
            model_prob = self.model.probability(seq)
            sl_prob = self.sl_learner.predict(seq)
#            oom_prob = self.oom_learner.predict(seq)
            records.append((model_prob, sl_prob))
    
        with file(outfile, 'w') as out:
            out.write('The value of m used in spectral learning algorithm: %d\n' % self.sl_learner.m)
            out.write('Model probability\tSpectral learning probability\n')
            for idx, record in enumerate(records):
                line = '%e\t%e\t%s\n' %(record[0], record[1], self.testSet[idx])
                out.write(line)
                
        
    def test(self, outfile):
        records = list()
        for seq in self.testSet:
            modelprob = self.model.probability(seq)
            predprob = self.learner.predict(seq)
            emprob = self.emlearner.predict(seq)
            specerror = predprob - modelprob
            emerror = emprob - modelprob
            records.append((modelprob, predprob, emprob, specerror, emerror, len(seq)))
        
        with file(outfile, 'w') as out:
            out.write('Model prob\tSpecPred prob\tEMPred\n')
            for record in records:
                out.write(str(record[0]) + '\t' + str(record[1]) + '\t' + 
                          str(record[2]) + '\n')
        
            out.write('-' * 50 + '\n')
            out.write(str(sum(record[0] for record in records)) + '\t' + 
                      str(sum(record[1] for record in records)) + '\t' + 
                      str(sum(record[2] for record in records)) + '\n')
            out.write('-' * 50 + '\n')
            tprob = [record[0] for record in records]
            sprob = [record[1] for record in records]
            eprob = [record[2] for record in records]
            speckldiv = self.KLDiv(tprob, sprob)
            emkldiv = self.KLDiv(tprob, eprob)
            out.write('Spectral learning Kullback-Leibler Divergence: %f\n' % (speckldiv))
            out.write('EM algorithm Kullback-Leibler Divergence: %f\n' % (emkldiv))
#            self.draw(tprob, sprob, eprob)
    
def main(modelpath, trainfile, testfile):
    t_start = time.time()
    classifier = SPClassifier(trainfile, testfile)
    t_end = time.time()
    print 'Time used to load data:', t_end - t_start, ' seconds'
    print '-' * 50
    
    t_start = time.time()
    classifier.loadModel(modelpath)
    t_end = time.time()
    print 'Time used to load HMM model:', t_end - t_start, ' seconds'
    print '-' * 50
    
    print '+' * 50
    print 'Training set:', len(classifier.trainSet)
    
    t_start = time.time()
    classifier.train()
    t_end = time.time()
    print 'Time used to train classifier:', t_end - t_start, ' seconds'
    print '-' * 50
    
    t_start = time.time()
    classifier.testing('HMM_SL.log')
    t_end = time.time()
    print 'Time used to test Spectral learning and OOM learning...', t_end - t_start, ' seconds'
    
    
if __name__ == '__main__':
    usage = './SPClassifier modelpath trainset testset'
    if len(sys.argv) < 4:
        print usage
        exit()
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3]) 
    
    
    
    
    
