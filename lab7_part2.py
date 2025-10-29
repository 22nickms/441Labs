import RPi.GPIO as GPIO
import socket
from time import sleep
import threading

GPIO.setmode(GPIO.BCM)

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
    <script>
        function updateLED(led, value) {{
            // Update the brightness display
            document.getElementById(led + '_value').innerText = value + '%';
            
            // Send POST request without page reload
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/', true);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.send('led=' + led + '&brightness=' + value);
        }}
    </script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .slider-container {{ margin: 15px 0; }}
        .slider-label {{ display: inline-block; width: 80px; }}
        .brightness-value {{ display: inline-block; width: 50px; margin-left: 10px; }}
    </style>
</head>
<body>
    <h2>LED Brightness Control</h2>
    
    <div class="slider-container">
        <span class="slider-label">LED 1:</span>
        <input type="range" min="0" max="100" value="{brightness['LED1']}" 
               oninput="updateLED('LED1', this.value)">
        <span class="brightness-value" id="LED1_value">{brightness['LED1']}%</span>
    </div>
    
    <div class="slider-container">
        <span class="slider-label">LED 2:</span>
        <input type="range" min="0" max="100" value="{brightness['LED2']}" 
               oninput="updateLED('LED2', this.value)">
        <span class="brightness-value" id="LED2_value">{brightness['LED2']}%</span>
    </div>
    
    <div class="slider-container">
        <span class="slider-label">LED 3:</span>
        <input type="range" min="0" max="100" value="{brightness['LED3']}" 
               oninput="updateLED('LED3', this.value)">
        <span class="brightness-value" id="LED3_value">{brightness['LED3']}%</span>
    </div>
    
    <p><em>Move any slider to instantly update LED brightness</em></p>
</body>
</html>"""
    return bytes(html, 'utf-8')

def parsePOSTdata(data):
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
    if led in pwm:
        pwm[led].ChangeDutyCycle(brightness_value)
        brightness[led] = brightness_value
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

        # Handle POST requests (from JavaScript)
        if "POST" in request:
            data_dict = parsePOSTdata(request)
            print(f"POST data: {data_dict}")
            
            if 'led' in data_dict and 'brightness' in data_dict:
                led = data_dict['led']
                try:
                    brightness_value = int(data_dict['brightness'])
                    update_LED(led, brightness_value)
                except ValueError:
                    print("Invalid value")

        # Send response (same page for both GET and POST)
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
    for n in pwm.values():
        n.stop()
    GPIO.cleanup()
