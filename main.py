# here we have a boat-load of package imports (at first, I wsa having trouble with this part)

from __future__ import print_function
import datetime
import pickle
import os.path
import smtplib
import webbrowser
import randfacts
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time
import pyttsx3
import speech_recognition as sr
import pytz
import subprocess
import pyowm
import pyjokes
from tkinter import *
from tkinter import filedialog
import pandas as pd
from yahoo_fin import stock_info
from pygame import mixer
import datetime as dt
import pandas_datareader.data as web
import plotly.express as px
import plotly.graph_objects as go
import requests



# here I'm defining the days of the week, months of the year, my google caledner api link, as well as a array defining day endings.
# This will come in handy when we are calling a method that will tell us whether or not we are busy on that day

# this will also authorize my google account (don't worry - it's a spam account, it's not my real one)

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november",
          "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]


# this is a speak function
# instead of using google text-to-speech module, we used the python one which is much faster and efficient and does not reqiure a wifi connection


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


# This is s get audio class. Pretty self-explanatory. Basically, what I say is put into text and outputed by the system.

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception: " + str(e))

    return said.lower()


# Here is a function that authenticates our google account. I won't go into depth with this as it is quite complicated

def authenticate_google():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../test/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service


# here is the bread-and-butter of our program. A calender application that uses a google calender api to work. It understands dates etc... And checks my google calender and
#see if there are event(s) on that day
def get_events(day, service):
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day.")

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0]) - 12) + start_time.split(":")[1]
                start_time = start_time + "pm"

            speak(event["summary"] + " at " + start_time)

# Here is our get data function - part of the calender implementation
def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    if month < today.month and month != -1:
        year = year + 1

    if month == -1 and day != -1:
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7

        return today + datetime.timedelta(dif)

    if day != -1:  # FIXED FROM VIDEO
        return datetime.date(month=month, day=day, year=year)


# here is a send email function.

def send_email(subject, msg):
    # email = input("Enter a email address: ")

    email = input("What email ?")

    try:

        import config

        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(config.EMAIL_ADDRESS, config.PASSWORD)
        message = 'Subject: {}\n\n{}'.format(subject, msg)
        server.sendmail(email, email, message)
        server.quit()
        print("Success: Email sent!")
        time.sleep(60)
    except:

        print("Email failed to send.")


def note(text):
    date = datetime.datetime.now()

    file_name = str(date).replace(":", "-") + "note.txt"
    with open(file_name, "w") as f:
        f.write(text)
    subprocess.Popen(["notepad.exe", file_name])


WAKE = "robot"
SERVICE = authenticate_google()
print("Start")

# here we have a bunch of functions for greetings, emailing, music, stocks, and sports...

while True:
    print("listening...")
    text = get_audio()

    if text.count(WAKE) > 0:
        speak("Yes your highness")
        text = get_audio()

        CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy", "what are my plans", "do I have anything",
                         "schedule"]
        for phrase in CALENDAR_STRS:
            if phrase in text:
                date = get_date(text)
                if date:
                    get_events(date, SERVICE)
                else:
                    speak("I don't understand")

        NOTE_STRS = ["make a note", "write this down", "remember this", "note"]

        for phrase in NOTE_STRS:

            if phrase in text:
                speak("What would you like me to write down?")
                note_text = get_audio()
                note(note_text)
                speak("I've made a note of that.")

        if "hello" in text:
            speak("hello , how are you?")

        if "email" in text:
            subject = "A Great Year"

            message = "Hello to one of the students in 8I. Although it's been a tough year for all of us, we've got through " \
                      "it together.We have worked together, in-school and online, to have to 'normailst' eighth grade " \
                      "possible. I hope of all of you have a great summer break! Thanks, Pranav (p.s. this email is AUTOMATED) "

            send_email(subject, message)

        if "send email" in text:

            subject = "A Great Year"

            message = "Hello to one of the students in 8I. Although it's been a tough year for all of us, we've got through " \
                      "it together.We have worked together, in-school and online, to have to 'normailst' eighth grade " \
                      "possible. I hope of all of you have a great summer break! Thanks, Pranav (p.s. this email is AUTOMATED) "

            send_email(subject, message)

        elif "send an email" in text:

            subject = "A Great Year"

            message = "Hello to one of the students in 8I. Although it's been a tough year for all of us, we've got through " \
                      "it together.We have worked together, in-school and online, to have to 'normailst' eighth grade " \
                      "possible. I hope of all of you have a great summer break! Thanks, Pranav (p.s. this email is AUTOMATED) "

            send_email(subject, message)


        elif "send this" in text:

            subject = "A Great Year"

            message = "Hello to one of the students in 8I. Although it's been a tough year for all of us, we've got through " \
                      "it together.We have worked together, in-school and online, to have to 'normailst' eighth grade " \
                      "possible. I hope of all of you have a great summer break! Thanks, Pranav (p.s. this email is AUTOMATED) "

            send_email(subject, message)


        elif "write me an email" in text:

            subject = "A Great Year"

            message = "Hello to one of the students in 8I. Although it's been a tough year for all of us, we've got through " \
                      "it together.We have worked together, in-school and online, to have to 'normailst' eighth grade " \
                      "possible. I hope of all of you have a great summer break! Thanks, Pranav (p.s. this email is AUTOMATED) "

            send_email(subject, message)

        if "how are you" in text:
            speak("I am good, Pranav.")

        if "how is life" in text:
            speak("Life's good, Pranav.")

        if "how's life" in text:
            speak("Life's good, Pranav.")

        if "weather" in text:

            owm = pyowm.OWM("e1fe0e1659254d673cb82b6f2986ad71")

            location = owm.weather_at_place('Toronto')

            weather = location.get_weather()

            print(weather)

            temp = weather.get_temperature('celsius')

            print(temp)

            for key, value in temp.items():
                print(key, value)

        if "outside" in text:

            owm = pyowm.OWM("e1fe0e1659254d673cb82b6f2986ad71")

            location = owm.weather_at_place('Toronto')

            weather = location.get_weather()

            print(weather)

            temp = weather.get_temperature('celsius')

            print(temp)
            for key, value in temp.items():
                print(key, value)

        if "fact" in text:
            x = randfacts.getFact()
            print(x)
            speak(x)

        if "joke" in text:
            joke1 = pyjokes.get_joke(language='en', category='all')
            print(joke1)
            speak(joke1)

        if "music" in text:

            class MusicPlayer:

                def __init__(self, window):
                    window.geometry('320x100');
                    window.title('Pranav MP3 Player');
                    window.resizable(0, 0)
                    Load = Button(window, text='Load', width=10, font=('Times', 10), command=self.load)
                    Play = Button(window, text='Play', width=10, font=('Times', 10), command=self.play)
                    Pause = Button(window, text='Pause', width=10, font=('Times', 10), command=self.pause)
                    Stop = Button(window, text='Stop', width=10, font=('Times', 10), command=self.stop)
                    Load.place(x=0, y=20);
                    Play.place(x=110, y=20);
                    Pause.place(x=220, y=20);
                    Stop.place(x=110, y=60)
                    self.music_file = False
                    self.playing_state = False

                def load(self):
                    self.music_file = filedialog.askopenfilename()

                def play(self):
                    if self.music_file:
                        mixer.init()
                        mixer.music.load(self.music_file)
                        mixer.music.play()

                def pause(self):
                    if not self.playing_state:
                        mixer.music.pause()
                        self.playing_state = True
                    else:
                        mixer.music.unpause()
                        self.playing_state = False

                def stop(self):
                    mixer.music.stop()


            root = Tk()
            app = MusicPlayer(root)
            root.mainloop()

        if "chrome" in text:
            chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
            url = 'http://www.google.com'
            webbrowser.get(chrome_path).open(url)

        if "teams" in text:

            def openFile():

                try:

                    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
                    url = 'https://teams.microsoft.com/_#/school//?ctx=teamsGrid'
                    webbrowser.get(chrome_path).open(url)


                except:
                    print("ERROR")


            openFile()

        if "youtube" in text:
            chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
            url = 'https://www.youtube.com'
            webbrowser.get(chrome_path).open(url)

        if "player" in text:

            def get_NBA_stats():
                year = input("Which NBA season are you interested in?: ")
                player = input("For which player do you want to get stats?: ")
                print("Working...")
                print("Retriving data from database...")
                url = 'https://www.basketball-reference.com/leagues/NBA_{}_per_game.html'.format(year)
                r = requests.get(url)
                r_html = r.text
                soup = BeautifulSoup(r_html, 'html.parser')
                table = soup.find_all(class_="full_table")
                """ Extracting List of column names"""
                head = soup.find(class_="thead")
                column_names_raw = [head.text for item in head][20]
                column_names_polished = column_names_raw.replace("\n", ",").split(",")[2:-1]
                print(column_names_polished)

                {'Player',
                 'Pos',
                 'Age',
                 'Tm',
                 'G',
                 'GS',
                 'MP',
                 'FG',
                 'FGA',
                 'FG%',
                 '3P',
                 '3PA',
                 '3P%',
                 '2P',
                 '2PA',
                 '2P%',
                 'eFG%',
                 'FT',
                 'FTA',
                 'FT%',
                 'ORB',
                 'DRB',
                 'TRB',
                 'AST',
                 'STL',
                 'BLK',
                 'TOV',
                 'PF',
                 'PTS'}
                """Extracting full list of player_data"""
                players = []
                for i in range(len(table)):
                    player_ = []
                    for td in table[i].find_all("td"):
                        player_.append(td.text)
                    players.append(player_)
                df = pd.DataFrame(players, columns=column_names_polished).set_index("Player")
                # cleaning the player's name from occasional special characters
                df.index = df.index.str.replace('*', '')


                print(df.loc[player])



            if __name__ == "__main__":
                get_NBA_stats()

        if " stock" in text:
            # stock = stock_info.get_live_price("AAPL")
            # print(stock)
            def stock_price():
                price = stock_info.get_live_price(e1.get())
                Current_stock.set(price)


            master = Tk()
            Current_stock = StringVar()

            Label(master, text="Company Symbol : ").grid(row=0, sticky=W)
            Label(master, text="Stock Result:").grid(row=3, sticky=W)

            result2 = Label(master, text="", textvariable=Current_stock,
                            ).grid(row=3, column=1, sticky=W)

            e1 = Entry(master)
            e1.grid(row=0, column=1)

            b = Button(master, text="Show", command=stock_price)
            b.grid(row=0, column=2, columnspan=2, rowspan=2, padx=5, pady=5)

            mainloop()






