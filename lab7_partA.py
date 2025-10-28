import RPi.GPIO as GPIO
import socket
from time import sleep
import threading

GPIO.setmode(GPIO.BCM)

# LED configuration
LED_PINS = {'LED1': 17, 'LED2': 27, 'LED3': 22}
brightness = {"LED1": 0, "LED2": 0, "LED3": 0}

# Initialize PWM for all LEDs
pwm = {}
for key, pin in LED_PINS.items():
    GPIO.setup(pin, GPIO.OUT)
    pwm[key] = GPIO.PWM(pin, 1000)
    pwm[key].start(0)

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
</html>"""
    return bytes(html, 'utf-8')

def parsePOSTdata(data):
    data_dict = {}
    idx = data.find('\r\n\r\n') + 4
    body = data[idx:]
    pairs = body.split('&')
    for pair in pairs:
        if '=' in pair:
            k, v = pair.split('=', 1)
            # URL decode the values
            v = v.replace('+', ' ')  # Simple decoding for spaces
            data_dict[k] = v
    return data_dict

def update_led(led_name, brightness_value):
    if led_name in pwm:
        pwm[led_name].ChangeDutyCycle(brightness_value)
        brightness[led_name] = brightness_value
        print(f"{led_name} brightness set to {brightness_value}%")

def serve_web_page():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 8080))
    s.listen(3)
    print("Server listening on port 8080...")
    
    while True:
        conn, (client_ip, client_port) = s.accept()
        print(f"Connection from {client_ip}:{client_port}")
        request = conn.recv(2048).decode('utf-8')
        print(f"Request: {request.split()[0]} {request.split()[1]}")

        # Handle POST requests
        if "POST" in request:
            data_dict = parsePOSTdata(request)
            print(f"POST data: {data_dict}")
            
            if 'led' in data_dict and 'brightness' in data_dict:
                led_name = data_dict['led']
                try:
                    brightness_value = int(data_dict['brightness'])
                    update_led(led_name, brightness_value)
                except ValueError:
                    print("Invalid brightness value")

        # Send response
        response = web_page()
        conn.send(b'HTTP/1.1 200 OK\r\n')
        conn.send(b'Content-Type: text/html\r\n')
        conn.send(b'Connection: close\r\n\r\n')
        conn.sendall(response)
        conn.close()

try:
    web_thread = threading.Thread(target=serve_web_page)
    web_thread.daemon = True
    web_thread.start()
    print("Web server started. Access at http://<your-pi-ip>:8080")
    print("Press Ctrl+C to stop the server")
    
    while True:
        sleep(1)
except KeyboardInterrupt:
    print("\nCleaning up GPIO...")
    GPIO.cleanup()
