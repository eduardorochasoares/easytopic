import numpy as np
import re
import sys
import wave
from aubio import source
from aubio import pitch as pt
import tempfile
import traceback
import contextlib

def read_wave(path):
    """Reads a .wav file.
    Takes the path, and returns (PCM audio data, sample rate).
    """
    try:
        with contextlib.closing(wave.open(path, 'rb')) as wf:
            num_channels = wf.getnchannels()
            assert num_channels == 1
            sample_width = wf.getsampwidth()
            assert sample_width == 2
            sample_rate = wf.getframerate()
            assert sample_rate in (8000, 16000, 32000, 48000)
            pcm_data = wf.readframes(wf.getnframes())
            return pcm_data, sample_rate
    except Exception as e:
        print(e, flush=True)

def pitch_estimation(filename, sample_rate):

    downsample = 1
    samplerate = sample_rate // downsample

    win_s = 4096 // downsample  # fft size
    hop_s = 512 // downsample  # hop size

    s = source(filename, samplerate, hop_s)
    samplerate = s.samplerate

    tolerance = 0.8

    pitch_o = pt("yin", win_s, hop_s, samplerate)
    pitch_o.set_unit("midi")
    pitch_o.set_tolerance(tolerance)

    pitches = []
    confidences = []
    ste = []
    # total number of frames read
    total_frames = 0
    while True:
        samples, read = s()
        pitch = pitch_o(samples)[0]
        # pitch = int(round(pitch))
        confidence = pitch_o.get_confidence()
        pitches += [pitch]
        ste += [shortTermEnergy(samples)]
        confidences += [confidence]
        total_frames += read
        if read < hop_s: break

    if 0: sys.exit(0)
    pitches = [p for p in pitches if p != 0]
    return np.mean(pitches), np.mean(ste)

def shortTermEnergy(frame):
    return sum([abs(x) ** 2 for x in frame]) / len(frame)
    # plt.savefig(os.path.basename(filename) + '.svg')

'''def getVideoLength(self):
    video_file = self.video_path.split("/")[-2]+".mp4"
    self.video_file = video_file
    print(video_file)
    result = subprocess.Popen(["ffprobe", self.video_path+video_file],
    stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    #print(result.stdout.readlines())
    duration = [x for x in result.stdout.readlines() if b'Duration' in x]
    time = str(duration[0]).split(": ")[1].split(", ")[0]
    #Transforms video length in seconds
    length_seconds = 0
    aux = time.split(":")
    length_seconds += float(aux[0]) *3600
    length_seconds += float(aux[1]) * 60
    length_seconds += float(aux[2])
    self.video_length = length_seconds'''

'''extract pause duration before being voiced of every audio chunk'''
def extractPauseDuration(self):
    file_path = self.video_path + "seg.txt"
    file = open(file_path, 'r')
    f = file.read()
    times = []
    timesEnd = []
    pause_list = []
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
    pause_list.append(times[0])
    for i in range(1, len(timesEnd)):
        pause_list.append(float(times[i] - timesEnd[i-1]))

    return pause_list, times, timesEnd

'''Extract the pitch and volume estimation of each audio chunk'''
def extract_emphasis(file, sample_rate):

    #larm = es.DynamicComplexity(sampleRate=fs)

    pitch, energy = pitch_estimation(file, sample_rate)

    return pitch, energy


def extract(audio_chunk):
    with tempfile.NamedTemporaryFile(mode='w+b', suffix='.wav') as fp:
        try:
            sample_rate = 16000
            wf = wave.open(fp, 'w')
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(np.frombuffer(audio_chunk, dtype=np.uint8))
            wf.close()

            pitch, energy = extract_emphasis(fp.name, sample_rate)
            return pitch if not np.isnan(pitch) else 0, energy if not np.isnan(energy) else 0

        except Exception as e:
            print(traceback.format_exc(), flush=True)