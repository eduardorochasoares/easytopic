
from nltk import tokenize, pos_tag
import matplotlib.pyplot as plt
import numpy as np
from statsmodels import robust
import seaborn as sns


'''Shot representation'''
class Shot:
    def __init__(self, id, pitch, volume, pause, mfcc_vector, init_time, end_time):
        self.id = id            #shot id
        self.pitch = pitch      #pitch value
        self.volume = volume    #volume contained in a chunk
        self.pause_duration  = pause # pause time before the shot being voiced
        self.surprise = 0  #bayesian surprise value of f0 in a windowed audio signal
        self.transcript = None  #transcription from ASR of a shot
        self.ocr = None #text extracted from ocr
        self.mfcc_vector = mfcc_vector
        self.adv_count = 0
        self.init_time = init_time
        self.end_time = end_time
        self.duration = end_time - init_time
        self.word2vec = None
        self.valid_vector = None

    '''extract the transcripts and related concepts from CSO ontology'''
    def extractTranscriptAndConcepts(self, transcript, ocr_on, docSim):

        aux = ""
        #f2 = open(video_path + "transcript/transcript"+str(self.id)+".txt")
        a = transcript
        cue_phrases = ['actually',  'further',  'otherwise', 'also' , 'furthermore'
         'right' , 'although',  'generally',
        'say',  'and', 'however',  'second', 'basically',  'indeed',  'see',
        'because', 'let' ,'similarly','but','look', 'since',
        'essentially', 'next', 'so',
        'except', 'no' ,'then',
        'finally' ,'now', 'therefore',
        'first', 'ok', 'well',
        'firstly', 'or', 'yes' ]

        words = tokenize.word_tokenize(a, language='english')

        words = [word.lower() for word in words]
        if words:
            if words[0] in cue_phrases:
                self.adv_count = 1
            else:
                self.adv_count = 0
        else:
            self.adv_count = 0

        '''Apply pos_tag in the transcript to extract only adjectives and nouns'''
        words = [word for (word, pos) in pos_tag(words) if pos == 'NN' or
        pos == 'JJ' or pos == 'NNS' or pos == 'JJR' or pos == 'JJR']

        transcript = ' '.join(words)


        self.transcript = transcript
        self.valid_vector, self.word2vec = docSim.vectorize(self.transcript)
        #f2.close()
