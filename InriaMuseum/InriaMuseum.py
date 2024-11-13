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
    data = request.json
    mote_mac_address = data.get('mote_mac_address')
    options = data.get("options")
    src_port = data.get('src_port')
    dest_port = data.get('dest_port')
    priority = data.get('priority')
    payload = data.get('payload')
    response = send_data_to_mote(mote_mac_address, priority, src_port, dest_port, options, payload)
    if response:
        return {"status": "success", "message": "Data sent successfully"}
    else:
        return {"status": "error", "message": "Failed to send data"}
def send_data_to_mote(mote_mac_address, priority, src_port, dest_port, options, payload):
    """
    Send data to a mote using the sendData method from JsonManager.
    """
    try:
        response = json_manager.raw_POST(
            commandArray   = ["sendData"],
            fields         = {
                "macAddress":mote_mac_address,  
                "priority":priority,   
                "srcPort":src_port,                
                "dstPort":dest_port,             
                "options":options,
                "data":payload
            },
            manager        = manager,                
        )
        print(f"Response from raw_POST: {response}")
        return response
    except Exception as e:
        print(e.message)
        print(f"Failed to send data: {e}")
        return None
@app.route('/detecting', method='GET')
def detect_presence():
    response.content_type = 'application/json'
    return json.dumps(mote_detecting)
#callback fct, triggered whenever the JsonManager receives notifications
def notif_cb(notifName, notifJson):
    print("get_distances")
    print(notifName)
    if (notifName == "notifData"):
        response = requests.get('http://127.0.0.1:1880/notifData')
        notification = json.loads(response)
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
            serialport=manager,
            configfilename=None,
            notifCb=notif_cb
        )
    except Exception as e:
        print(f"Error initializing JsonManager: {e}")
        exit(1)
    run(app, host='localhost', port=8080)