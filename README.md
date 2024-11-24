My little Jarvis in python 

    * Vosk as speetch to text converter
    * Groq API as Jarvis


https://console.groq.com/docs/quickstart

download the Vosk model you need and put it in the Models file unziped:

https://alphacephei.com/vosk/models

then modify the paths lign 150:
    if langue == "en":
        langue = os.path.join(os.getcwd(), "Models", "vosk-model-small-en-us-0.15")

create your API key

export GROQ_API_KEY=<your-api-key-here>

pip install groq

run:

clear && python3 myJarvis.py Wav/astarion_mono16.wav en

or use voice command:

clear && python3 myJarvis.py voice en
