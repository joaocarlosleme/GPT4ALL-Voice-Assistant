from os import system
import speech_recognition as sr
from playsound import playsound
from gpt4all import GPT4All
import sys
import whisper
import warnings
import time
import os
import tts

wake_word = 'kate'
stop_word = 'stop'
model = GPT4All(model_name="ggml-model-gpt4all-falcon-q4_0.bin", model_path="models/", allow_download=False)
r = sr.Recognizer()
tiny_model_path = os.path.expanduser('~/.cache/whisper/tiny.pt') # tiny_model_path = os.path.expanduser('C:\\Users\\joaoc\\.cache\\whisper\\tiny.pt') 
base_model_path = os.path.expanduser('~/.cache/whisper/base.pt')
tiny_model = whisper.load_model(tiny_model_path)
base_model = whisper.load_model(base_model_path)
listening_for_wake_word = True
source = sr.Microphone() 
warnings.filterwarnings("ignore", category=UserWarning, module='whisper.transcribe', lineno=114)
speachRecognitionLibrary = 'google' # 'whisper' or 'google'


# if sys.platform != 'darwin':
#     import pyttsx3
#     engine = pyttsx3.init() 

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

# speach recognition
def audio_to_text(audio):
    try:
        if speachRecognitionLibrary == 'whisper':
            # using Whisper
            with open("wake_detect.wav", "wb") as f:
                f.write(audio.get_wav_data())
            result = tiny_model.transcribe('wake_detect.wav')
            recognized_text = result['text']
        else:
            # using Google
            recognized_text = r.recognize_google(audio)
            # try:
            #     # for testing purposes, we're just using the default API key
            #     # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            #     # instead of `r.recognize_google(audio)`
            #     recognized_text = r.recognize_google(audio)
            # except sr.UnknownValueError:
            #     print("Google Speech Recognition could not understand audio")
            #     recognized_text = ""
            # except sr.RequestError as e:
            #     print("Could not request results from Google Speech Recognition service; {0}".format(e))
            #     recognized_text = ""
    except Exception as e:
        # print("Audio to text error: ", e)
        recognized_text = ""
    print("Audio to text: ", recognized_text)
    return recognized_text.strip()

def listen_for_wake_word(audio):
    global listening_for_wake_word

    recognized_text = audio_to_text(audio)

    # if speachRecognitionLibrary == 'whisper':
    #     # using Whisper
    #     with open("wake_detect.wav", "wb") as f:
    #         f.write(audio.get_wav_data())
    #     result = tiny_model.transcribe('wake_detect.wav')
    #     text_input = result['text']
    # else:
    #     # using Google
    #     try:
    #         # for testing purposes, we're just using the default API key
    #         # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
    #         # instead of `r.recognize_google(audio)`
    #         text_input = r.recognize_google(audio)
    #     except sr.UnknownValueError:
    #         #print("Google Speech Recognition could not understand audio")
    #         text_input = ""
    #     except sr.RequestError as e:
    #         print("Could not request results from Google Speech Recognition service; {0}".format(e))
    #         text_input = ""
    
    # if wake_word in recognized_text.lower().strip():
    #     print("Wake word detected. Please speak your prompt to GPT4All.")
    #     speak('Listening')
    #     listening_for_wake_word = False

    recognized_text_lower = recognized_text.lower()
    
    index = recognized_text_lower.find(wake_word)

    if index != -1:
        listening_for_wake_word = False
        print("Wake word detected.")
        portion_after_wakeword = recognized_text[index + len(wake_word):]
        if len(portion_after_wakeword.strip()) == 0:
            print("Wake word detected. Please speak your prompt to GPT4All.")
            speak('Listening')
        else:
            prompt_gptTxt(portion_after_wakeword)


def prompt_gpt(audio):
    recognized_text = audio_to_text(audio)
    prompt_gptTxt(recognized_text)

def prompt_gptTxt(recognized_text):
    global listening_for_wake_word
    try:
        # if speachRecognitionLibrary == 'whisper':
        #     # using Whisper
        #     with open("prompt.wav", "wb") as f:
        #         f.write(audio.get_wav_data())
        #     result = base_model.transcribe('prompt.wav')
        #     prompt_text = result['text']
        # else:
        #     # using Google
        #     prompt_text = r.recognize_google(audio)

        # if len(recognized_text.strip()) == 0:
        #     print("Empty prompt. Please speak again.")
        #     #speak("Empty prompt. Please speak again.")
        #     #print('\nSay', wake_word, 'to wake me up. \n')
        #     #listening_for_wake_word = True
        # else:

        recognized_text_lower = recognized_text.lower()
        if stop_word in recognized_text_lower:
            print("Stop word detected. I will sleep now.")
            speak('Stop word detected. I will sleep now.')
            listening_for_wake_word = True
        elif len(recognized_text) != 0:
            print('User: ' + recognized_text)
            output = model.generate(recognized_text, max_tokens=200)
            print('GPT4All: ', output)
            speak(output)
            #print('\nSay', wake_word, 'to wake me up. \n')
            #listening_for_wake_word = True
    except Exception as e:
        print("Prompt error: ", e)

def callback(recognizer, audio):
    global listening_for_wake_word
    if listening_for_wake_word:
        listen_for_wake_word(audio)
    else:
        prompt_gpt(audio)

def start_listening():
    with source as s:
        r.adjust_for_ambient_noise(s, duration=2)
    print('\nSay', wake_word, 'to wake me up. \n')
    r.listen_in_background(source, callback)
    while True:
        time.sleep(1) 

if __name__ == '__main__':
    start_listening() 
