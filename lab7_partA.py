import RPi.GPIO as GPIO
import socket
from time import sleep
import threading

GPIO.setmode(GPIO.BCM)

LED1, LED2, LED3 = 23, 24, 25
LED_PINS = {'LED1': LED1, 'LED2': LED2, 'LED3': LED3}

pwm = {}
for key, pin in LED_PINS.items():
    GPIO.setup(pin, GPIO.OUT)
    pwm[key] = GPIO.PWM(pin, 1000)
    pwm[key].start(0)

brightness = {"LED1": 0, "LED2": 0, "LED3": 0}

def web_page():
    html = f"""
    <!DOCTYPE html>
    <html>
    <body>
    <h2>Brightness level:</h2>

    <form action="/" method="POST">
        <input type="range" name="slider1" min="0" max="100" value="50"><br>
        <p>Select LED:</p>
        <input type="radio" name="option" value="LED1"> LED1 ({brightness['LED1']}%)<br>
        <input type="radio" name="option" value="LED2"> LED2 ({brightness['LED2']}%)<br>
        <input type="radio" name="option" value="LED3"> LED3 ({brightness['LED3']}%)<br><br>
        <input type="submit" value="Submit">
    </form>
    </body>
    </html>
    """
    return html

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

def update_led(option, slider_val):
    if option in pwm:
        pwm[option].ChangeDutyCycle(slider_val)
        brightness[option] = slider_val
        print(f"{option} brightness set to {slider_val}%")

def serve_web_page():
    while True:
        print("Waiting for connection...")
        conn, (client_ip, client_port) = s.accept()
        print(f"Connection from {client_ip}:{client_port}")
        request = conn.recv(2048).decode('utf-8')
        print(request)

        if "POST" in request:
            data_dict = parsePOSTdata(request)
            if 'option' in data_dict and 'slider1' in data_dict:
                update_led(data_dict['option'], int(data_dict['slider1']))

        response = web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response.encode('utf-8'))
        conn.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
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

