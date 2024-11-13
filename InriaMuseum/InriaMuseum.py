from bottle import route, run, static_file, Bottle, template, response, request
import requests
import json
from SmartMeshSDK import sdk_version
from SmartMeshSDK.utils import JsonManager
from smartmeshsdk3.app import JsonServer
SERVERtoLISTEN = "http://localhost:8080/json"
app = Bottle()
# Dictionary to store distance reported by each mote by MAC address
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
    data        = request.json
    print(data)
    macAddress  = data.get('macAddress')
    print(macAddress)
    priority    = data.get('priority')
    print(priority)
    srcPort     = data.get('srcPort')
    print(srcPort)
    dstPort     = data.get('dstPort')
    print(dstPort)
    options     = data.get("options")
    print(options)
    data        = data.get('data')
    data = [0, data]
    print(data)
    response    = send_data_to_mote(macAddress, priority, srcPort, dstPort, options, data)
    if response:
        return {"status": "success", "message": "Data sent successfully"}
    else:
        return {"status": "error", "message": "Failed to send data"}

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
@app.route('/detecting', method='GET')
def detect_presence():
    response.content_type = 'application/json'
    return json.dumps(mote_detecting)
# Callback function, triggered whenever the JsonManager receives notifications
def notif_cb(notifName, notifJson):
    print("get_distances")
    print(notifName)
    if notifName == "notifData":
        response = requests.get('http://127.0.0.1:1880/notifData')
        notification = json.loads(response.text)
        mac_address = notification['fields']['macAddress']
        data = notification['fields']['data']
        detect = data[0]  # 1 to indicate presence, else 0
        mote_detecting[mac_address] = detect
    else:
        print("not notif data")
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
        print(f"Connected to SmartMesh Manager and started JSON server.")
        handler = json_manager.managerHandlers.get(manager)
        if handler:
            print(f"Connector: {handler.connector}")
            print(f"Connector Type: {type(handler.connector)}")
        else:
            print(f"Error: Handler for manager '{manager}' not found!")
    except Exception as e:
        print(f"Error initializing JsonManager: {e}")
        exit(1)
    run(app, host='localhost', port=8080)
