from bottle import route, run, static_file, Bottle, template, response, request
import requests
import json
from SmartMeshSDK import sdk_version
from SmartMeshSDK.utils import JsonManager
from smartmeshsdk3.app import JsonServer
SERVERtoLISTEN = "http://localhost:8080/json"
app = Bottle()
mote_detecting = {}
manager = '/dev/ttyUSB3'
@app.route('/')
def index():
    return template('InriaMuseum.html')  
@app.route('/<filename:path>')
def serve_static(filename):
    print("fct '/<filename:path>'")
    return static_file(filename, root='.')
@app.route('/send_data', method='POST')
def send_data():
    payload        = request.json
    macAddress  = payload.get('macAddress')
    print(macAddress)
    priority    = payload.get('priority')
    srcPort     = payload.get('srcPort')
    dstPort     = payload.get('dstPort')
    options     = payload.get("options")
    data        = payload.get('data')
    data = [data]
    response    = send_data_to_mote(macAddress, priority, srcPort, dstPort, options, data)
def send_data_to_mote(macAddress, priority, srcPort, dstPort, options, data):
    """
    Send data to a mote using the sendData method from JsonManager.
    """
    try:
        response = json_manager.raw_POST(
            commandArray=["sendData"],
            fields={
                "macAddress": macAddress,
                "priority": priority,
                "srcPort": srcPort,
                "dstPort": dstPort,
                "options": options,
                "data": data
            },
            manager=manager
        )
        print(f"Response from raw_POST: {response}")
        return response
    except Exception as e:
        print(f"Failed to send data: {e}")
        return None
# Callback function, triggered whenever the JsonManager receives notifications
def notif_cb(notifName, notifJson):
    if notifName == "notifData":
        print("Received data notification")
        mac_address = notifJson['fields']['macAddress']
        data = notifJson['fields']['data']
        detect = data[0]  # 1 to indicate presence, else 0
        mote_detecting[mac_address] = detect
        print(mote_detecting)
@app.route('/detecting', method='GET')
def detect_presence():
    response.content_type = 'application/json'
    print(mote_detecting)
    return json.dumps(mote_detecting)
# Start the web server
if __name__ == '__main__':
    try:
        # Initialize the JsonManager with the appropriate settings
        json_manager = JsonManager.JsonManager(
            autoaddmgr=True,
            autodeletemgr=False,
            serialport=manager,
            configfilename=None,
            notifCb=notif_cb
        )
    except Exception as e:
        print(f"Error initializing JsonManager: {e}")
        exit(1)
    run(app, host='localhost', port=8080)
