import RPi.GPIO as GPIO # GPIO Pins
import socket # Imported Socket Module
from time import sleep # Imported sleep from the time module
import threading # Threading Module

GPIO.setmode(GPIO.BCM) # BCM Numbering

LED1 = 17 # Assigned to GPIO Pin 17
LED2 = 27 # Assigned to GPIO Pin 27
LED3 = 22 # Assigned to GPIO Pin 22
LED_PINS = {'LED1': LED1, 'LED2': LED2, 'LED3': LED3}

pwm = {}
for key, pin in LED_PINS.items():
    GPIO.setup(pin, GPIO.OUT)
    pwm[key] = GPIO.PWM(pin, 1000)
    pwm[key].start(0)

brightness = {"LED1": 0, "LED2": 0, "LED3": 0}

def web_page(led_brightness):
    html = f"""
    <!DOCTYPE html>
    <html>
    <body>
    <h2>Brightness level:</h2>

    <form action="/" method="POST">
        <input type="range" name="brightness" min="0" max="100" value="50"><br>
        <p>Select LED:</p>
        <input type="radio" name="LED_PINS" value="0"> LED1 ({brightness['LED1']}%)<br>
        <input type="radio" name="LED_PINS" value="1"> LED2 ({brightness['LED2']}%)<br>
        <input type="radio" name="LED_PINS" value="2"> LED3 ({brightness['LED3']}%)<br><br>
        <input type="submit" value="Modify Brightness">
    </form>
    </body>
    </html>
    """
    return bytes(html, 'utf-8')

def parsePOSTdata(data):
    data_dict = {}
    idx = data.find('\r\n\r\n') + 4
    body = data[idx:]
    pairs = body.split('&')
    for pair in pairs:
        if '=' in pair:
            k, v = pair.split('=', 1)
            data_dict[k] = v
    return data_dict

def update_led(LED_PINS, brightness):
    if LED_PINS in pwm:
        pwm[LED_PINS].ChangeDutyCycle(brightness)
        brightness[LED_PINS] = slider_val
        print(f"{LED_PINS} brightness set to {brightness}%")

def serve_web_page():
    while True:
        print("Waiting for connection...")
        conn, (client_ip, client_port) = s.accept()
        print(f"Connection from {client_ip}:{client_port}")
        request = conn.recv(2048).decode('utf-8')
        print(request)

        if "POST" in request:
            data_dict = parsePOSTdata(request)
            if 'LED_PINS' in data_dict and 'brightness' in data_dict:
                update_led(data_dict['LED_PINS'], int(data_dict['brightness']))

        response = web_page()
        conn.send('HTTP/1.1 200 OK\r\n')
        conn.send('Content-Type: text/html\r\n')
        conn.send('Connection: close\r\n\n')
        conn.sendall(response)
        conn.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 8080))
s.listen(3)

try:
    web_thread = threading.Thread(target=serve_web_page)
    web_thread.start()
    while True:
        sleep(1)
except KeyboardInterrupt:
    print("Cleaning up GPIO...")
    s.close()
    GPIO.cleanup()






