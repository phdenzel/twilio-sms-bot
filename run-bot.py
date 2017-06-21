# Imports
from flask import Flask, request
from twilio import twiml

# connect to local host w/ Flask (and later to www through ngrok)
app = Flask(__name__)


# Main function
# triggered by a POST request by ngrok
# when an SMS is received, Twilio will send the POST
@app.route('/', methods=['POST'])
def sms():
    """
    Use Twilio API to reply to texts
    """
    message = request.form['Body']      # text from SMS
    response = twiml.Response()         # init a Twilio response
    reply = formulate_reply(message)    # formulate answer to message
    response.message('Hi\n\n' + reply)  # text back
    return str(response)


def formulate_reply(message):
    """
    Identify keywords in message and relply accordingly through various APIs
    """
    message = message.lower().strip()  # reformate message
    answer = ""
    # identify keywords
    if "weather" in message:     # for weather requests
        message = remove_from(message, "weather")
        answer = weather_APIrequest(message)
    elif "wolfram" in message:   # for calculations
        message = remove_from(message, "wolfram")
        answer = wolfram_APIrequest(message)
    elif "wiki" in message:      # for wikipedia searches
        message = remove_from(message, "wiki")
        answer = wiki_APIrequest(message)
    # add more features here
    else:
        answer = "\n Welcome! These are the commands you may use: "
        +" \nWOLFRAM \"wolframalpha request\""
        +" \nWIKI \"wikipedia request\""
        +" \nWEATHER \"place\"\n"
    # limit to 1500 characters
    if len(answer) > 1500:
        answer = answer[0:1500] + "..."
    return answer


def remove_from(message, keyword):
    """
    Strip the message from the keyword
    """
    message = message.replace(keyword, '').strip()
    return message


def weather_APIrequest(message):
    """
    Tell the weather
    """
    import pyowm
    import os
    import datetime
    answer = ""
    # get API key from filename in directory API-keys/weather/
    APIkey = os.listdir("API-keys/weather")[0]
    owm = pyowm.OWM(APIkey)
    try:
        # current weather
        observation = owm.weather_at_place(message)
        curr = observation.get_weather()
        # forecast
        forecast = owm.daily_forecast(message, limit=6)
        fcst = forecast.get_forecast()
        # location
        loc = fcst.get_location().get_name()
    except:
        answer = answer + "Please input a location, e.g. Zurich\n"
        return answer

    answer = answer + "Location: {}\n".format(loc)
    # current weather
    cdstat = curr.get_detailed_status()
    temp = curr.get_temperature(unit='celsius')
    ctmin = temp['temp_min']
    ctmax = temp['temp_max']
    answer = answer + "Currently: {}, {} - {} C\n".format(
        cdstat, ctmin, ctmax)

    # get forecast
    for weather in fcst:
        daycode = weather.get_reference_time('iso').split('+')[0]
        day = datetime.datetime.strptime(
            daycode, "%Y-%m-%d %H:%M:%S").strftime('%a')
        dstat = weather.get_detailed_status()
        temp = weather.get_temperature(unit='celsius')
        tmin = temp['min']
        tmax = temp['max']
        answer = answer + "{}: {}, {} - {} C\n".format(
            day, dstat, tmin, tmax)
    return answer


def wolfram_APIrequest(message):
    """
    Do math
    """
    import wolframalpha
    import os
    answer = ""
    # get API key from filename in directory API-keys/wolfram-alpha/
    APIkey = os.listdir("API-keys/wolfram-alpha")[0]
    try:
        client = wolframalpha.Client(APIkey)
        res = client.query(message)
        answer = next(res.results).text
    except:
        answer = "No valid query for Wolfram|Alpha"
    return answer


def wiki_APIrequest(message):
    """
    Be intellectual ;)
    """
    import wikipedia
    try:
        answer = wikipedia.summary(message)  # get summary from wikipedia
    except:
        # handle problems, that is degeneracy of answers
        answer = "Request was not found using Wikipedia. Be more specific?"
    return answer


if __name__ == '__main__':
    app.run()
