#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class

import time
import whisper
import speech_recognition as sr
import os
from os import system
import sys
#import pyttsx3
import tts

tiny_model_path = os.path.expanduser('~/.cache/whisper/tiny.pt') # C:\Users\[Your Username]]\.cache\whisper / C:/Users/joaoc/.cache/whisper/tiny.pt
base_model_path = os.path.expanduser('~/.cache/whisper/base.pt')
tiny_model = whisper.load_model(tiny_model_path)
base_model = whisper.load_model(base_model_path)

# if sys.platform != 'darwin':
#     engine = pyttsx3.init()
#     engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')


def callbackWhisper(model, audio):
    start_time = time.time()
    try:
        with open("prompt.wav", "wb") as f:
            f.write(audio.get_wav_data())
        result = model.transcribe('prompt.wav')
        prompt_text = result['text']
        # if len(prompt_text.strip()) == 0:
        #     print("Empty prompt. Please speak again.")
        #     speak("Empty prompt. Please speak again.")
        # else:
        print('User: ' + prompt_text)
        #speak(prompt_text)
        #print('\nIm listening... \n')
    except Exception as e:
        print("Prompt error: ", e)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"The function Whisper took {elapsed_time} seconds to complete.")

def speak(text):
    if sys.platform == 'darwin':
        ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?!-_$:+-/ ")
        clean_text = ''.join(c for c in text if c in ALLOWED_CHARS)
        system(f"say '{clean_text}'")
    else:
        #engine = pyttsx3.init()
        #engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')
        #engine.say(text)
        #engine.runAndWait()
        mytts = tts.TTS()
        mytts.start(text)
        del(mytts)

# this is called from the background thread
def callbackGoogle(recognizer, audio):
    # received audio data, now we'll recognize it using Google Speech Recognition
    start_time = time.time()
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        prompt_text = recognizer.recognize_google(audio)
        print("Google Speech Recognition thinks you said: " + prompt_text)
        #speak(prompt_text)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"The function Google took {elapsed_time} seconds to complete.")

# this is called from the background thread
def callback(recognizer, audio):
    callbackGoogle(recognizer, audio)
    callbackWhisper(tiny_model, audio)
    callbackWhisper(base_model, audio)

r = sr.Recognizer()
m = sr.Microphone()
with m as source:
    r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening

# start listening in the background (note that we don't have to do this inside a `with` statement)
stop_listening = r.listen_in_background(m, callback)
# `stop_listening` is now a function that, when called, stops background listening
print('\nSaysomething? \n')
## do some unrelated computations for 5 seconds
#for _ in range(50): time.sleep(0.1)  # we're still listening even though the main thread is doing other things
## calling this function requests that the background listener stop listening
#stop_listening(wait_for_stop=False)
#print('\nStoped listening? \n')
# do some more unrelated things

while True: time.sleep(0.1)  # we're not listening anymore, even though the background thread might still be running for a second or two while cleaning up and stopping