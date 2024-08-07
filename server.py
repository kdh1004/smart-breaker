import asyncio
import websockets
import serial
import threading
import subprocess

arduino_port = '/dev/ttyACM0'
ser = serial.Serial(arduino_port, 9600)
lock = threading.Lock()

List to store connected websockets
connected_websockets = set()

Function to play melody
def play_melody():
with lock:
ser.write(b'0')

Asynchronous function to send message to all clients
async def send_to_all_clients(message):
for websocket in connected_websockets:
try:
await websocket.send(message)
except websockets.exceptions.ConnectionClosedError:
# Remove disconnected websocket from the set
connected_websockets.remove(websocket)

Asynchronous function to handle client
async def handle_client(websocket, path):
connected_websockets.add(websocket)
try:
async for data in websocket:
print(f"request of client: {data}")
if data == 'on':
with lock:
ser.write(b'0')
await websocket.send('blocked ON')
elif data == 'off':
with lock:
ser.write(b'f')
await websocket.send('blocked OFF')
elif data == 'EMERGENCY':
print("EMERGENCY")
await send_to_all_clients("EMERGENCY")
start_streaming()
finally:
# Remove websocket when client disconnects
connected_websockets.remove(websocket)

Function to start server
async def start_server():
server = await websockets.serve(
handle_client, "192.168.137.37", 58221,
ping_interval=30, 
ping_timeout=1000 .
)
print('WebSocket server ready')

await server.wait_closed()
Start the serial reader thread
def serial_reader():
def send_emergency():
asyncio.run_coroutine_threadsafe(send_to_all_clients("EMERGENCY"), asyncio.get_event_loop())


while True:
    received_data = ser.readline().decode().strip()
    if "EMERGENCY" in received_data:
        print("EMERGENCY")
        loop.call_soon_threadsafe(send_emergency)
        start_streaming()
serial_thread = threading.Thread(target=serial_reader)
serial_thread.start()

def start_streaming():
try:
libcamera_cmd = [
"libcamera-vid", "-t", "0", "--inline", "--width", "1280", "--height", "720", "--framerate", "30", "--codec", "h264", "-o", "-"
]

    gst_cmd = [
        "gst-launch-1.0", "fdsrc", "!", 
        "video/x-h264, width=1280, height=720, framerate=30/1", "!", 
        "h264parse", "!", 
        "rtph264pay", "config-interval=1", "pt=96", "!", 
        "gdppay", "!", 
        "tcpserversink", "host=0.0.0.0", "port=5000"
    ]

    libcamera_process = subprocess.Popen(libcamera_cmd, stdout=subprocess.PIPE)
    gst_process = subprocess.Popen(gst_cmd, stdin=libcamera_process.stdout)

    def monitor_keyboard():
        while True:
            if input() == 'q':
                print("q 버튼이 눌려서 스트리밍을 종료합니다.")
                libcamera_process.terminate()
                gst_process.terminate()
                break

    keyboard_thread = threading.Thread(target=monitor_keyboard)
    keyboard_thread.start()

    libcamera_process.stdout.close()  # Ensure libcamera_process receives a SIGPIPE if gst_process exits
    gst_process.communicate()
except Exception as e:
    print(f"Error occurred: {e}")
loop = asyncio.get_event_loop()
loop.run_until_complete(start_server())
ser.close()
