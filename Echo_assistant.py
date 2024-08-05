import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pyttsx3
import pyautogui
import speech_recognition as sr
import os
import subprocess
import cv2 as c
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import webbrowser
import requests
import wikipedia
import urllib.parse
import pywhatkit as kit
import smtplib
import sys
import time
import winsound
import pygetwindow as gw
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the text-to-speech engine
engine = pyttsx3.init('sapi5')

def sendEmail(to, content):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
    server.sendmail(os.getenv("EMAIL_USER"), to, content)
    server.close()

def list_voices():
    voices = engine.getProperty('voices')
    for voice in voices:
        print(f"ID: {voice.id}, Name: {voice.name}, Lang: {voice.languages}")

def set_voice(language):
    voices = engine.getProperty('voices')
    for voice in voices:
        if language in voice.languages:
            engine.setProperty('voice', voice.id)
            return
    print(f"No voice found for language: {language}. Setting default voice.")
    engine.setProperty('voice', voices[0].id)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def play_specific_spotify_music(query):
    results = sp.search(q=query, type='track', limit=1)
    tracks = results['tracks']['items']
    if not tracks:
        speak("No music found.")
        return
    
    track = tracks[0]
    track_url = track['external_urls']['spotify']
    track_name = track['name']
    artist_name = track['artists'][0]['name']
    
    print(f"Playing {track_name} by {artist_name}")
    speak(f"Playing {track_name} by {artist_name}")
    
    webbrowser.open(track_url)
    
    speak("Enjoy the music!")

def switch_window(window_title):
    windows = gw.getWindowsWithTitle(window_title)
    if windows:
        window = windows[0]  # Use the first match
        window.activate()
        speak(f"Switched to window: {window_title}")
    else:
        speak(f"No window with title '{window_title}' found.")

def take():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        try:
            print("Listening...")
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"Your command: {query}")
        except sr.WaitTimeoutError:
            print("No speech detected within the timeout period.")
            speak("I didn't hear anything. Please try again.")
            return "none"
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            speak("An error occurred. Please try again.")
            return "none"
    return query

def wishing():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        print("Good morning")
        speak("Good morning")
    elif hour >= 12 and hour < 18:
        print("Good afternoon")
        speak("Good afternoon")
    else:
        print("Good evening")
        speak("Good evening")

def set_alarm(hour, minute):
    now = datetime.datetime.now()
    alarm_time = datetime.datetime(now.year, now.month, now.day, hour, minute)
    
    if alarm_time < now:
        alarm_time += datetime.timedelta(days=1)
    
    while datetime.datetime.now() < alarm_time:
        time.sleep(1)
    
    speak("Alarm ringing!")
    winsound.Beep(1000, 5000)

def get_joke():
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    joke = response.json()
    joke_text = f"{joke['setup']} - {joke['punchline']}"
    speak(joke_text)
    print(joke_text)

# Shutdown the system
def shutdown_system():
    speak("Shutting down the system.")
    os.system("shutdown /s /t 1")

# Restart the system
def restart_system():
    speak("Restarting the system.")
    os.system("shutdown /r /t 1")

# Sleep mode
def sleep_system():
    speak("Putting the system to sleep.")
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

# Get news headlines
def get_news_headlines(api_key):
    url = 'https://newsapi.org/v2/top-headlines'
    params = {'country': 'in', 'apiKey': api_key}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        articles = response.json()['articles']
        headlines = [article['title'] for article in articles]
        return headlines
    return ["Error fetching news."]

# Send email with attachment
def send_email_with_attachment(to_email, subject, body, file_path, smtp_server, smtp_port, from_email, password):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Attach the file
    attachment = MIMEBase('application', 'octet-stream')
    try:
        with open(file_path, 'rb') as file:
            attachment.set_payload(file.read())
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
        msg.attach(attachment)
    except Exception as e:
        print(f"Error attaching file: {e}")
        speak("Failed to attach the file.")

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
        speak("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")
        speak("Failed to send the email.")

def get_weather(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200:
        main = data['main']
        weather = data['weather'][0]
        temperature = main['temp']
        description = weather['description']
        return f"The current temperature in {city} is {temperature}°C with {description}."
    else:
        return "Sorry, I couldn't retrieve the weather data. Please try again."

# Initialize Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
))

if __name__ == '__main__':
    wishing()
    speak("Hello, my name is Echo. How can I help you?")

    query = take().lower()
    
    if 'open notepad' in query:
        path = "C:/WINDOWS/system32/notepad.exe"
        speak("Opening Notepad from your system")
        os.startfile(path)
    elif 'open command prompt' in query:
        speak("Opening Command Prompt from your system")
        subprocess.run("start cmd", shell=True, check=True)
    elif "please open camera" in query:
        speak("Opening camera")
        cam = c.VideoCapture(0)  # Use internal camera
        if not cam.isOpened():
            print("Error: Camera not accessible.")
            speak("Error: Camera not accessible.")
        else:
            while True:
                ret, img = cam.read()
                if not ret:
                    print("Error: Unable to capture video.")
                    speak("Error: Unable to capture video.")
                    break
                c.imshow('Webcam', img)
                key_cam = c.waitKey(50)
                if key_cam == 27:  # Press 'Esc' to exit
                    break
            cam.release()
            c.destroyAllWindows()
    elif 'play' in query:
        song_query = query.replace('play', '').strip()
        
        if 'hindi' in song_query:
            set_voice('hi')
        else:
            set_voice('en')

        speak("Playing the song from Spotify")
        if song_query:
            play_specific_spotify_music(song_query)
        else:
            speak("I didn't catch the name of the song. Please try again.")
    elif 'ip address' in query:
        ip = requests.get("https://api.ipify.org").text
        speak(f"The IP address of your system is {ip}")
        print(ip)
    elif 'wikipedia' in query:
        speak('Searching Wikipedia')
        query = query.replace('wikipedia', "").strip()
        try:
            results = wikipedia.summary(query, sentences=2)
            speak(results)
            print(results)
        except wikipedia.exceptions.DisambiguationError as e:
            speak("There are multiple results. Please be more specific.")
            print(e)
        except wikipedia.exceptions.PageError:
            speak("No results found.")
    elif 'youtube' in query:
        speak("What do you want to search on YouTube?")
        video_query = take().lower().strip()
        
        if video_query:
            encoded_query = urllib.parse.quote(video_query)
            search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            webbrowser.open(search_url)
            speak(f"Searching for {video_query} on YouTube")
        else:
            speak("I didn't catch the name of the video. Please try again.")
    elif 'linkedin' in query:
        webbrowser.open('linkedin.com')
        speak("Opening LinkedIn")
    elif 'facebook' in query:
        webbrowser.open("facebook.com")
        speak("Opening Facebook")
    elif "stack overflow" in query:
        webbrowser.open("stackoverflow.com")
        speak("Opening Stack Overflow")
    elif "whatsapp web" in query:
        webbrowser.open("web.whatsapp.com")
        speak("Opening WhatsApp Web")
    elif "chatgpt" in query:
        webbrowser.open("chatgpt.com")
        speak("Opening ChatGPT")
    elif "open google" in query:
        webbrowser.open('google.com')
        speak("opening google.com")
        speak("which word do you want to search on google")
        cm = take().lower()
        webbrowser.open(f"https://www.google.com/search?q={cm}")
    elif "send email" in query:
        speak("say the subject")
        subject = take().lower().strip()
        speak("say the message you want to send")
        content = take().lower()
        to = input()
        sendEmail(to, content)
    elif 'send file' in query:
        speak("Please provide the file path")
        file_path = input("Enter the file path: ").strip()
        speak("Please provide the email subject")
        subject = take().strip()
        speak("Please provide the email body")
        body = take().strip()
        speak("recipient's email")
        to_email = input()
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        from_email = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASSWORD")
        send_email_with_attachment(to_email, subject, body, file_path, smtp_server, smtp_port, from_email, password)
    elif 'switch to' in query:
        title = query.replace('switch to', '').strip()
        switch_window(title)
    elif 'set alarm' in query:
        speak("At what hour?")
        hour = int(take().strip())
        speak("At what minute?")
        minute = int(take().strip())
        set_alarm(hour, minute)
        speak("Alarm set")
    elif 'get joke' in query:
        get_joke()
    elif 'shutdown' in query:
        shutdown_system()
    elif 'restart' in query:
        restart_system()
    elif 'sleep' in query:
        sleep_system()
    elif 'news' in query:
       api_key = os.getenv('NEWS_API_KEY')
       headlines = get_news_headlines(api_key)
       for headline in headlines:
          speak(headline)
          print(headline)
    elif "tell me my location" in query:
        speak("Let me check")
        ipadd = requests.get("https://api.ipify.org").text
        url = f'https://get.geojs.io/v1/ip/geo/{ipadd}.json'
        gdata = requests.get(url).json()
        print(gdata)
        city = gdata['city']
        state = gdata['region']
        country = gdata['country']
        speak(f"You are in {city}, {state}, {country}")
    elif "take screenshot" in query:
        name = take().lower()
        time.sleep(3)
        img = pyautogui.screenshot()
        img.save("user.png")
        speak("Screenshot taken and saved")
    elif 'weather' in query:
        api_key = os.getenv("WEATHER_API_KEY")
        city = take()
        weather_report = get_weather(api_key, city)
        speak(weather_report)
        print(weather_report)
    elif "call" in query:
        sid = os.getenv("TWILIO_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        client = Client(sid, token)

        message = client.calls \
            .create(
                twiml='<Response><Say>test</Say></Response>',
                from_=os.getenv("TWILIO_PHONE_NUMBER"),
                to="Your Phone number"
            )
        speak("Calling...")

    else:
        speak("Thank you, have a good day!")
        sys.exit()
