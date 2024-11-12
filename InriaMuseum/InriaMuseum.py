from bottle import route, run, static_file, Bottle, template,response, request
import requests
import json
from SmartMeshSDK            import sdk_version
from SmartMeshSDK.utils      import JsonManager
from smartmeshsdk3.app         import  JsonServer
SERVERtoLISTEN = "http://localhost:8080/json"
app = Bottle()
# Dictionary to store distance reported by each mote by MAC address
mote_detecting = {}
@app.route('/')
def index():
    return template('InriaMuseum.html')  
@app.route('/<filename:path>')
def serve_static(filename):
    print("fct '/<filename:path>'")
    return static_file(filename, root='.')
@app.route('/detecting', method='GET')
def detect_presence():
    response.content_type = 'application/json'
    return json.dumps(mote_detecting)
#callback fct, triggered whenever the JsonManager receives notifications
def notif_cb(notifName, notifJson):
    print("get_distances")
    print(notifName)
    if (notifName == "notifData"):
        notification = requests.get('http://127.0.0.1:1880/notifData')
        mac_address = notification['fields']['macAddress']
        data = notification['fields']['data']
        detect = data[0]                                    # 1 to indicate presence else 0
        mote_detecting[mac_address] = detect
    else:
        print("not notif data")
#start the web server
if __name__ == '__main__':
    try:
        json_manager = JsonManager.JsonManager(
            autoaddmgr=True,
            autodeletemgr=True,
            serialport='/dev/ttyUSB3',
            configfilename='JsonServer.config',
            notifCb=notif_cb
        )
        print("Connected to SmartMesh Manager and started JSON server.")
    except Exception as e:
        print(f"Error initializing JsonManager: {e}")
        exit(1)
    run(app, host='localhost', port=8080)