import http.client
import os
import tempfile
import wave
import numpy as np
import json
import time

def transcribeAudio(path_to_audio_file, samplerate=16000):
    headers = {"Content-type": "audio/wav; codec=\"audio/pcm\"; samplerate=" + str(samplerate)}

    with open(path_to_audio_file, 'rb') as audio_file:
        response = ""
        try:

            body = audio_file.read()
            # Connect to server to recognize the wave binary

            conn = http.client.HTTPConnection(os.environ['ASR_SERVER'], int(os.environ['GSTREAM_PORT']))

            conn.request("POST", "/client/dynamic/recognize",
                         body, headers)
            response = conn.getresponse().read().decode("UTF-8")
            conn.close()
        finally:
            audio_file.close()

        return response

def main(audio_chunk):
    with tempfile.NamedTemporaryFile(mode='w+b', suffix='.wav') as fp:
        succes = False
        while not succes:
            try:

                sample_rate = 16000
                wf = wave.open(fp, 'w')
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(np.frombuffer(audio_chunk, dtype=np.uint8))
                wf.close()
                res = transcribeAudio(fp.name)
                print(res, flush=True)
                res = json.loads(res)
                if res:
                    print(res['hypotheses'][0]['utterance'], flush=True)
                    succes = True
            except Exception as e:
                print('trying again', flush=True)
                time.sleep(0.5)