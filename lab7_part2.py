from flask import Flask, request, jsonify, render_template_string
import RPi.GPIO as GPIO

app = Flask(__name__)

# --- GPIO setup ---
GPIO.setmode(GPIO.BCM)
LED_PINS = {'LED1': 23, 'LED2': 24, 'LED3': 25}

# Create PWM objects
pwm = {}
for name, pin in LED_PINS.items():
    GPIO.setup(pin, GPIO.OUT)
    pwm[name] = GPIO.PWM(pin, 1000)  # 1kHz frequency
    pwm[name].start(0)               # start off

# Store brightness values
brightness = {'LED1': 0, 'LED2': 0, 'LED3': 0}


# --- HTML + JavaScript ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>LED Brightness Control</title>
    <style>
        body { font-family: Arial; text-align: center; margin-top: 50px; }
        .slider-container { margin: 20px auto; width: 300px; }
        input[type=range] { width: 100%; }
        h2 { margin-bottom: 40px; }
    </style>
</head>
<body>
    <h2>LED Brightness Control</h2>

    {% for led in brightness %}
    <div class="slider-container">
        <label>{{ led }}: <span id="{{ led }}_val">{{ brightness[led] }}</span>%</label><br>
        <input type="range" id="{{ led }}" min="0" max="100" value="{{ brightness[led] }}" oninput="updateLED('{{ led }}', this.value)">
    </div>
    {% endfor %}

    <script>
        function updateLED(led, value) {
            document.getElementById(led + '_val').innerText = value;
            
            fetch('/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({led: led, brightness: value})
            })
            .then(response => response.json())
            .then(data => {
                console.log('Updated:', data);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_PAGE, brightness=brightness)


@app.route('/update', methods=['POST'])
def update_led():
    data = request.get_json()
    led = data.get('led')
    value = int(data.get('brightness', 0))

    if led in pwm:
        pwm[led].ChangeDutyCycle(value)
        brightness[led] = value
        return jsonify({'status': 'ok', 'led': led, 'brightness': value})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid LED name'}), 400


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        pass
    finally:
        for p in pwm.values():
            p.stop()
        GPIO.cleanup()

