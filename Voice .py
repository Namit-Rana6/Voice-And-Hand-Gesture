import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser
import os
import smtplib
import urllib.parse
import pyautogui
import requests
import pywhatkit
import json
import random
import googletrans
from googletrans import Translator
import openai
import time
import ctypes
import psutil
import platform
import subprocess
import threading
import keyboard
import GGSIPU  # Import your head gesture file here

# Initialize OpenAI GPT
openai.api_key = 'YOUR_OPENAI_API_KEY'  # <-- Replace

engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)

def speak(audio):
    print(f"Jarvis: {audio}")
    engine.say(audio)
    engine.runAndWait()

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning!")
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am Jarvis, your personal assistant. Say 'Hello Jarvis' to wake me up.")

def takeCommand(timeout=5):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        try:
            audio = r.listen(source, timeout=timeout)
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"You said: {query}")
        except Exception as e:
            print("Listening timed out or error occurred.")
            return "None"
    return query

def check_keyboard():
    while True:
        if keyboard.is_pressed('v'):
            speak("Starting Head Gesture Control...")
            import GGSIPU
            threading.Thread(target=GGSIPU.start_head_control, daemon=True).start()  # Run GGSIPU in background thread
            break  # Optional: stop listening after starting once


def sendEmail(to, content):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login("your_email@example.com", "your_password")  # <-- Replace
    server.sendmail("your_email@example.com", to, content)
    server.close()



def getNews():
    news_api = "YOUR_NEWS_API_KEY"  # <-- Replace
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={news_api}"
    response = requests.get(url)
    news = response.json()
    articles = news["articles"]
    speak("Here are the top news headlines:")
    for i, article in enumerate(articles[:5]):
        speak(f"News {i+1}: {article['title']}")

def gptConversation(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    answer = response.choices[0].text.strip()
    speak(answer)

def translateSpeech():
    translator = Translator()
    speak("Speak the sentence to translate...")
    sentence = takeCommand()
    speak("Which language to translate to?")
    lang = takeCommand().lower()

    lang_dict = {'spanish': 'es', 'french': 'fr', 'german': 'de', 'hindi': 'hi'}
    if lang in lang_dict:
        translation = translator.translate(sentence, dest=lang_dict[lang])
        speak(f"The translation is: {translation.text}")
    else:
        speak("Sorry, language not supported yet.")

def setReminder():
    speak("What should I remind you about?")
    reminder_text = takeCommand()
    speak("In how many seconds should I remind you?")
    seconds = int(takeCommand())
    speak(f"Setting reminder for {seconds} seconds.")
    time.sleep(seconds)
    speak(f"Reminder: {reminder_text}")

def scrollDown():
    pyautogui.scroll(-500)

def scrollUp():
    pyautogui.scroll(500)

def tellJoke():
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "I'm reading a book about anti-gravity. It's impossible to put down!",
        "Why did the math book look sad? Because it had too many problems!"
    ]
    joke = random.choice(jokes)
    speak(joke)

def systemStatus():
    speak("Checking system status...")
    battery = pyautogui.screenshot()
    speak("System seems operational. No issues detected.")

def setAlarm(alarm_time):
    speak(f"Setting alarm for {alarm_time}")
    alarm_hour, alarm_minute = map(int, alarm_time.split(":"))
    while True:
        if datetime.datetime.now().hour == alarm_hour and datetime.datetime.now().minute == alarm_minute:
            speak("Alarm ringing! Wake up!")
            os.system("start alarm.mp3")  # You must place a 'alarm.mp3' file in same folder
            break
        time.sleep(30)

def controlVolume(action):
    if action == "up":
        for _ in range(5):
            pyautogui.press("volumeup")
    elif action == "down":
        for _ in range(5):
            pyautogui.press("volumedown")

def brightnessControl(level):
    try:
        import screen_brightness_control as sbc
        sbc.set_brightness(level)
        speak(f"Brightness set to {level} percent.")
    except:
        speak("Brightness control not supported on this device.")

def shutdownPC():
    speak("Shutting down your computer.")
    os.system("shutdown /s /t 5")

def restartPC():
    speak("Restarting your computer.")
    os.system("shutdown /r /t 5")

def sleepPC():
    speak("Putting your PC to sleep.")
    if platform.system() == "Windows":
        subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def rememberThat(note):
    memory_file = "memory.txt"  # Define the memory file
    with open(memory_file, "a") as f:
        f.write(note + "\n")
    speak("I have remembered that for you.")

def recallMemory():
    memory_file = "memory.txt"
    if os.path.exists(memory_file):
        with open(memory_file, "r") as f:
            memories = f.readlines()
        speak("You asked me to remember the following:")
        for memory in memories:
            speak(memory.strip())
    else:
        speak("I have no memories yet.")

def sendWhatsappMessage(contact_number, message):
    speak("Sending your WhatsApp message.")
    now = datetime.datetime.now()
    pywhatkit.sendwhatmsg(contact_number, message, now.hour, now.minute + 2)
def connectToWiFi(wifi_name):
    speak(f"Connecting to {wifi_name}")
    command = f'netsh wlan connect name="{wifi_name}"'
    subprocess.run(command, shell=True)
def pairBluetoothDevice(device_name):
    speak(f"Trying to pair with {device_name}")
    command = f'PowerShell.exe "Get-PnpDevice | Where-Object {{$_.FriendlyName -like \'{device_name}*\'}} | Enable-PnpDevice -Confirm:$false"'
    subprocess.run(command, shell=True)

def gpt_conversation(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    answer = response['choices'][0]['message']['content'].strip()
    speak(answer)
    print(answer)

def getWeather(city_name):
    api_key = "YOUR_OPENWEATHER_API_KEY"  # Replace
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
    response = requests.get(url)
    weather = response.json()
    if weather["cod"] != "404":
        temp = weather["main"]["temp"]
        description = weather["weather"][0]["description"]
        speak(f"The temperature in {city_name} is {temp} degrees Celsius with {description}")
    else:
        speak("City not found.")

def tossCoin():
    outcome = random.choice(["Heads", "Tails"])
    speak(f"It's {outcome}")

def rollDice():
    dice = random.randint(1,6)
    speak(f"You rolled a {dice}")

def randomFact():
    facts = [
        "Honey never spoils.",
        "Bananas are berries, but strawberries are not.",
        "A group of flamingos is called a flamboyance.",
        "Octopuses have three hearts."
    ]
    speak(random.choice(facts))

def trendingSongs():
    speak("Playing trending songs on YouTube.")
    pywhatkit.playonyt("trending songs 2025")
def voiceNavigation():
    speak("Voice navigation mode activated. Say 'exit navigation' to stop.")
    while True:
        command = takeCommand().lower()

        if "mouse up" in command:
            pyautogui.moveRel(0, -200)
        elif "mouse down" in command:
            pyautogui.moveRel(0, 200)
        elif "move mouse left" in command:
            pyautogui.moveRel(-200, 0)
        elif "move mouse right" in command:
            pyautogui.moveRel(200, 0)
        elif "click left" in command:
            pyautogui.click(button='left')
        elif "click right" in command:
            pyautogui.click(button='right')
        elif "double click" in command:
            pyautogui.doubleClick()
        elif "scroll up" in command:
            pyautogui.scroll(300)
        elif "scroll down" in command:
            pyautogui.scroll(-300)
        elif "switch to browser" in command:
            os.system('start chrome')  # or use specific application launching
        elif "open spotify" in command:
            os.startfile("C:\\Users\\khush\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Spotify.lnk")
        elif "minimize all" in command:
            pyautogui.hotkey('win', 'd')
        elif "exit navigation" in command:
            speak("Exiting voice navigation mode.")
            break
        else:
            speak("Command not recognized.")

# Main Program
if __name__ == "__main__":
    speak("Initializing Jarvis...")
    wishMe()

    # 🧠 Start the keyboard listener in background
    threading.Thread(target=check_keyboard, daemon=True).start()

    ACTIVATED = False

    while True:
        if not ACTIVATED:
            query = takeCommand(timeout=7).lower()
            if "hello" in query:
                ACTIVATED = True
                speak("Hello! I am ready for your commands.")
        else:
            query = takeCommand().lower()


            if "wikipedia" in query:
                speak("Searching Wikipedia...")
                query = query.replace("wikipedia", "")
                results = wikipedia.summary(query, sentences=2)
                speak("According to Wikipedia")
                speak(results)

            elif "open youtube" in query:
                webbrowser.open("youtube.com")

            elif "open google" in query:
                webbrowser.open("google.com")

            elif "open stack overflow" in query:
                webbrowser.open("stackoverflow.com")

            elif "play music" in query:
                speak("Which song would you like to hear?")
                song_query = takeCommand()
                if song_query != "None":
                    pywhatkit.playonyt(song_query)
                    speak(f"Playing {song_query} on YouTube now!")

            elif "the time" in query:
                strTime = datetime.datetime.now().strftime("%H:%M:%S")
                speak(f"The time is {strTime}")
            elif "alarm" in query:
                speak("Tell me the time to set alarm, for example 7:30")
                alarm_time = takeCommand()
                setAlarm(alarm_time)
            elif "turn on wi-fi" in query:
                turnOnWiFi()

           
           

            elif "volume up" in query:
                controlVolume("up")

            elif "volume down" in query:
                controlVolume("down")

            elif "brightness" in query:
                speak("Tell me the brightness percentage")
                brightness = takeCommand()
                if brightness.isdigit():
                    brightness = int(brightness)
                    if 0 <= brightness <= 100:
                        speak(f"Setting brightness to {brightness} percent.")
                        
                brightnessControl(brightness)

            elif "shutdown" in query:
                shutdownPC()

            elif "restart" in query:
                restartPC()

            elif "sleep" in query:
                sleepPC()

            elif "remember that" in query:
                speak("What should I remember?")
                note = takeCommand()
                rememberThat(note)

            elif "what do you remember" in query:
                recallMemory()

            elif "send whatsapp" in query:
                speak("Tell me the number with country code")
                number = takeCommand()
                speak("What is the message?")
                message = takeCommand()
                sendWhatsappMessage(number, message)

            elif "talk to me" in query:
                speak("What do you want to talk about?")
                prompt = takeCommand()
                gpt_conversation(prompt)

            elif "weather" in query:
                speak("Which city?")
                city = takeCommand()
                getWeather(city)

            elif "toss a coin" in query:
                tossCoin()

            elif "roll a dice" in query:
                rollDice()

            elif "fun fact" in query:
                randomFact()

            elif "trending songs" in query:
                trendingSongs()

            elif "open code" in query:
                codePath = "C:\\Users\\khush\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Visual Studio Code\\Visual Studio Code.lnk"
                os.startfile(codePath)

            elif "open spotify" in query:
                spotify_path = "C:\\Users\\khush\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Spotify.lnk"
                os.startfile(spotify_path)

            elif "email to khushi" in query:
                try:
                    speak("What should I say?")
                    content = takeCommand()
                    to = "receiver_email@example.com"  # <-- Replace
                    sendEmail(to, content)
                    speak("Email has been sent!")
                except Exception as e:
                    speak("Sorry, I am unable to send the email.")

            elif "weather" in query:
                getWeather()

            elif "news" in query:
                getNews()

            elif "talk to me" in query or "chat" in query:
                speak("What should we talk about?")
                prompt = takeCommand()
                gptConversation(prompt)

            elif "translate" in query:
                translateSpeech()

            elif "remind me" in query:
                setReminder()

            elif "scroll down" in query:
                scrollDown()

            elif "scroll up" in query:
                scrollUp()

            elif "tell me a joke" in query:
                tellJoke()

            elif "system status" in query:
                systemStatus()
            elif "voice navigation" in query:
                voiceNavigation()

            elif "save and close" in query or "exit" in query:
                speak("Saving work and shutting down. Goodbye!")
                break

            else:
                speak("I did not catch that. Please say again.")
 