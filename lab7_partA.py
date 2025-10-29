import RPi.GPIO as GPIO # GPIO Module
import socket # Socket Module
from time import sleep # Sleep Module
import threading # Threading Module

GPIO.setmode(GPIO.BCM) #

# LED configuration
ledpins = {'LED1': 17, 'LED2': 27, 'LED3': 22}
brightness = {"LED1": 0, "LED2": 0, "LED3": 0}

# PWM Initialization
pwm = {}
for led, pin in ledpins.items():
    GPIO.setup(pin, GPIO.OUT)
    pwm[led] = GPIO.PWM(pin, 1000)
    pwm[led].start(0)

def web_page():
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>LED Brightness Control</title>
</head>
<body>
    <h2>Brightness level:</h2>
    
    <form action="/" method="POST">
        <p>Select LED:</p>
        <input type="radio" name="led" value="LED1"> LED 1 ({brightness['LED1']}%)<br>
        <input type="radio" name="led" value="LED2"> LED 2 ({brightness['LED2']}%)<br>
        <input type="radio" name="led" value="LED3"> LED 3 ({brightness['LED3']}%)<br><br>
        
        <input type="range" name="brightness" min="0" max="100" value="50">
        <br><br>
        <input type="submit" value="Change Brightness">
    </form>
</body>
</html>
"""
    return bytes(html, 'utf-8')

def parsePOSTdata(data): # From lecture
    data_dict = {}
    idx = data.find('\r\n\r\n') + 4
    body = data[idx:]
    pairs = body.split('&')
    for pair in pairs:
        key_val = pair.split('=')
        if len(key_val) == 2:
            data_dict[key_val[0]] = key_val[1]
    return data_dict

def update_LED(led, brightness_value):
    if led in pwm: # LED Availability
        pwm[led].ChangeDutyCycle(brightness_value) # PWM --> LED
        brightness[led] = brightness_value # Brightness Tracker
        print(f"{led} brightness set to {brightness_value}%")

def serve_web_page():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 8080))
    s.listen(3)
    print("Server listening on port 8080...")
    
    while True:
        conn, (client_ip, client_port) = s.accept()
        print(f"Connection from {client_ip}:{client_port}")
        request = conn.recv(2048).decode('utf-8')

        # POST Requests 
        if "POST" in request:
            data_dict = parsePOSTdata(request)
            print(f"POST data: {data_dict}")
            
            if 'led' in data_dict and 'brightness' in data_dict:
                led = data_dict['led']
                try:
                    brightness_value = int(data_dict['brightness']) # Grabs b val
                    update_LED(led, brightness_value) # Changes the LED
                except ValueError:
                    print("Invalid value")

       # Server WebPage response
        response = web_page()
        conn.send(b'HTTP/1.1 200 OK\r\n')
        conn.send(b'Content-Type: text/html\r\n')
        conn.send(b'Connection: close\r\n\r\n')
        conn.sendall(response)
        conn.close()

try:
    web_thread = threading.Thread(target=serve_web_page)
    web_thread.daemon = True # automatic termination
    web_thread.start()
    print("Web Server Available. Access http://<your-pi-ip>:8080")
    print("Ctrl + C to cancel program")
    
    while True:
        sleep(1)
except KeyboardInterrupt:
    print("\nGPIO Cleanup Incoming...")
    for n in pwm.values():
        n.stop()
    GPIO.cleanup()




