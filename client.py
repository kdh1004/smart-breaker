import asyncio
import websockets
import subprocess
import threading

async def listen_for_messages(websocket):
    while True:
        message = await websocket.recv()
        print(f"\nServer: {message}")
        if message == "EMERGENCY":
            print("EMERGENCY 상황 발생! 스트리밍을 시작합니다.")
            start_streaming()
        print('차단기 on or off: ', end='', flush=True)

def start_streaming():
    try:
        gst_cmd = [
            "gst-launch-1.0", "tcpclientsrc", "host=192.168.137.37", "port=5000", "!", 
            "gdpdepay", "!", 
            "rtph264depay", "!", 
            "h264parse", "!", 
            "avdec_h264", "!", 
            "videoconvert", "!", 
            "autovideosink"
        ]

        gst_process = subprocess.Popen(gst_cmd)

        gst_process.communicate()
    except Exception as e:
        print(f"Error occurred: {e}")

async def start_input_loop(loop, websocket):
    while True:
        request = await loop.run_in_executor(None, input)
        if request in ['on', 'off']:
            await websocket.send(request)
        else:
            print("잘못된 요청입니다.\n차단기 on or off: ", end='', flush=True)

async def main():
    uri = "ws://192.168.137.37:58221"
    async with websockets.connect(uri) as websocket:
        print('차단기 on or off: ', end='', flush=True)

        loop = asyncio.get_event_loop()

        listener_task = loop.create_task(listen_for_messages(websocket))

        await start_input_loop(loop, websocket)

        await listener_task

# Get the event loop and run the main coroutine.
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
