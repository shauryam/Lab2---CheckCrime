
from collections import Counter
import requests
from spyne import Application, AnyDict
from spyne import ServiceBase, Float
from spyne import srpc
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication


class HelloWorldService(ServiceBase):
    @srpc(Float, Float, float, _returns=AnyDict())
    def checkcrime(lat, lon, radius):
        # type: (object, object, object) -> object
        url = 'https://api.spotcrime.com/crimes.json?lat={}&lon={}&radius={}&key=.'.format(lat, lon, radius)
        data = requests.get(url).json()
        response = {}
        total_crimes = len(data["crimes"])
        response["total_crimes"] = total_crimes
        crimeTypeCount = crimeType(data)
        crimePlaces = topThree(data)
        eventTimes = eventTimeCounts(data)
        report={
            "total_crime":total_crimes,
            "crime_type_count": crimeTypeCount,
            "event_time_count": eventTimes,
            "the_most_dangerous_streets": crimePlaces
        }
        return report


application = Application([HelloWorldService],
    tns='spyne.examples.hello',
    in_protocol=HttpRpc(validator='soft'),
    out_protocol=JsonDocument()
)

def eventTimeCounts(data):
    crimes = data["crimes"]
    timeCount = {
        "12:01am-3am": 0,
        "3:01am-6am": 0,
        "6:01am-9am": 0,
        "9:01am-12noon": 0,
        "12:01pm-3pm": 0,
        "3:01pm-6pm": 0,
        "6:01pm-9pm": 0,
        "9:01pm-12midnight": 0
    }
    for crime in crimes:
        time = crime["date"]
        hour = int(time[9:11])
        min = int(time[12:14])
        if time[-2].lower() == "a":
            if ((hour==12 and min > 0) or hour==1 or hour == 2 or (hour==3 and min==0)):
                timeCount["12:01am-3am"] += 1
            elif (hour==3 or hour==4 or hour == 5 or (hour==6 and min==0)):
                timeCount["3:01am-6am"] += 1
            elif (hour==6 or hour==7 or hour == 8 or (hour==9 and min==0)):
                timeCount["6:01am-9am"] += 1
            elif (hour==9 or hour==10 or hour == 11 or (hour==12 and min==0)):
                timeCount["9:01am-12noon"] += 1
        else:
            if ((hour==12 and min > 0) or hour==1 or hour == 2 or (hour==3 and min==0)):
                timeCount["12:01pm-3pm"] += 1
            elif (hour==3 or hour==4 or hour == 5 or (hour==6 and min==0)):
                timeCount["3:01pm-6pm"] += 1
            elif (hour==6 or hour==7 or hour == 8 or (hour==9 and min==0)):
                timeCount["6:01pm-9pm"] += 1
            elif (hour==9 or hour==10 or hour == 11 or (hour==12 and min==0)):
                timeCount["9:01pm-12midnight"] += 1
    return timeCount

def crimeType(data):
    crimes = data["crimes"]
    crimeType = {}
    for crime in crimes:
        type = crime["type"]
        if(crimeType.has_key(type)):
            crimeType[type] += 1
        else:
            crimeType[type] = 1

    return crimeType

def topThree(data):
    crimes = data["crimes"]
    crimePlaces = []
    for crime in crimes:
        place = crime["address"]
        place = place.split(" BLOCK ")[-1]
        place = place.split("BLOCK ")[-1]
        place = place.split(" OF ")[-1]
        place = place.split("OF ")[-1]
        place = place.split(" & ")[-1]
        place = place.split("& ")[-1]

        crimePlaces.append(place)

    crimePlaces = Counter(crimePlaces)
    crimePlaces = crimePlaces.most_common(3)
    temp = []
    for crime in crimePlaces:
        temp.append(crime[0])

    return temp

if __name__ == '__main__':
    # You can use any Wsgi server. Here, we chose
    # Python's built-in wsgi server but you're not
    # supposed to use it in production.
    from wsgiref.simple_server import make_server
    wsgi_app = WsgiApplication(application)
    server = make_server('0.0.0.0', 8000, wsgi_app)
    server.serve_forever()