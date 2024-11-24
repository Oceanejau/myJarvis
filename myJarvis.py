import wave
import sys
import os
import pyaudio
from vosk import Model, KaldiRecognizer
from groq import Groq

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1  # Mono
RATE = 16000  # Fréquence d'échantillonnage à 16000Hz

# RGB color : \033[38;2;R;G;Bm
# 38 pour le texte et 48 pour le surlignage
# 2 pour true color (RBG) 0 - 255 si on met 5 on passe sur 256 couleurs
RED = '\033[38;2;231;4;4m'
YELLOW = '\033[38;2;255;244;0m'
RESET = '\033[0m'
BLINK = '\033[5m'

def check_pulseaudio():
    pulse_check = os.system("pactl info")
    if pulse_check != 0:
        print(f"{RED}Error:{RESET}\n PulseAudio is not running. Please start PulseAudio.")
        return False
    return True

def voice_to_text(langue):
    output_file = "result.txt"
    model = Model(langue)
    recognizer = KaldiRecognizer(model, RATE)

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print(f"{BLINK}{YELLOW}Enregistrement en cours, dites quelque chose...{RESET}")

    with open(output_file, 'w') as f:
        try:
            while True:
                data = stream.read(CHUNK)
                
                if not data:
                    break

                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    result_text = result.split('"text" : "')[1].split('"')[0]
                    print(result_text)
                    f.write(result_text + '.\n')

            final_result = recognizer.FinalResult()
            print(final_result)
            f.write(final_result)
        
        except KeyboardInterrupt:
            print("\nOpération interrompue. Fermeture du programme...")
    stream.stop_stream()
    stream.close()
    p.terminate()

def speech_to_text(filename, langue):
    print(f"{BLINK}{YELLOW}Speech to txt{RESET}")

    model = Model(langue)
    recognizer = KaldiRecognizer(model, RATE)  # 16000 Hz est la fréquence d'échantillonnage typique

    try:
        wf = wave.open(filename, "rb")
        if wf.getnchannels() != 1:
            print(f"{RED}Error:{RESET}\n Le fichier audio doit être mono (1 canal).")
            return

        with open("result.txt", "w") as f:
            print(f"{BLINK}{YELLOW}Traitement en cours...{RESET}")

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    result_text = result.split('"text" : "')[1].split('"')[0]
                    print(result_text)
                    f.write(result_text + '.\n')
            final_result = recognizer.FinalResult()
            final_text = final_result.split('"text" : "')[1].split('"')[0]
            print(final_text)
            f.write(final_text)
    except FileNotFoundError:
        print(f"{RED}Error:{RESET}\n {filename} doesn't exist")
    except Exception as e:
        print(f"{RED}Error:{RESET}\n {e}")  
    except KeyboardInterrupt:
        print("\nOpération interrompue. Fermeture du programme...")

def get_result_content(file_path):
    try:
        with open(file_path, "r") as file:
            content = file.read().strip()
            return content
    except FileNotFoundError:
        print(f"Error: {file_path} does not exist.")
        return None
    except Exception as e:
        print(f"Error while reading the file: {e}")
        return None

def send_to_GroqAI(result_file_path):
    print(f"{BLINK}{YELLOW}GroqAI:{RESET}")

    file_content = get_result_content(result_file_path)

    if file_content is None:
        return
    client = Groq()
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages = [
            {"role": "system", "content": "You are a Jarvis, my personal assistant."},
            {
                "role": "user",
                "content": f"The transcribed audio says:\n{file_content}\nCan you summarize it?",
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    for chunk in completion:
        print(chunk.choices[0].delta.content or "", end="")
    print("\n")

def main():
    if len(sys.argv) < 3:
        print(f"{RED}Error:{RESET}\n   {YELLOW}{BLINK}Usage:{RESET} {sys.argv[0]} filename.wav langage")
        sys.exit(-1)

    filename = sys.argv[1]
    langue = sys.argv[2]

    if langue == "en":
        langue = os.path.join(os.getcwd(), "Models", "vosk-model-small-en-us-0.15")
    elif langue == "fr":
        langue = os.path.join(os.getcwd(), "Models", "vosk-model-small-fr-0.22")
    else:
        print(f"{RED}Error:{RESET}\n {langue} language model isn't available")
        sys.exit(-1)

    if filename == "voice":
        voice_to_text(langue)
    elif not os.path.exists(filename):
        print(f"{RED}Error:{RESET}\n {filename} doesn't exist")
        sys.exit(-1)

    elif not os.access(filename, os.R_OK):
        print(f"{RED}Error:{RESET}\n You don't have permissions to use {filename}")
        sys.exit(-1)

    if filename != "voice":
        speech_to_text(filename, langue)

    result_file = "result.txt"
    send_to_GroqAI(result_file)


if __name__ == "__main__":
    main()
