import network
import socket
from machine import Pin, PWM, Timer

# Constants
WIFI_SSID = 'YOUR WIFI'
WIFI_PASSWORD = 'YOUR_PASSWORD'
PWM_PIN = 25  # GPIO pin for PWM control
RPM_PIN = 26  # GPIO pin connected to the RPM signal
DESIRED_RPM = 1600  # Initial target RPM

# Variables
pulses = 0
current_rpm = 0
duty_cycle = 512

# Interrupt handler for pulse count
def count_pulse(pin):
    global pulses
    pulses += 1

# Function to calculate RPM
def calculate_rpm(timer):
    global pulses, current_rpm
    revolutions = pulses / 2
    current_rpm = revolutions * 60
    pulses = 0
    print("Current RPM:", current_rpm)  # Debugging line for RPM

# Proportional control to adjust PWM based on RPM
def adjust_pwm(timer):
    global duty_cycle, current_rpm, DESIRED_RPM
    error = DESIRED_RPM - current_rpm
    adjustment = error * 0.1
    duty_cycle += int(adjustment)
    duty_cycle = max(0, min(1023, duty_cycle))
    pwm0.duty(duty_cycle)
    print("Duty Cycle:", duty_cycle)  # Debugging line for Duty Cycle

# Set up the RPM reading pin
rpm_pin = Pin(RPM_PIN, Pin.IN, Pin.PULL_UP)
rpm_pin.irq(trigger=Pin.IRQ_FALLING, handler=count_pulse)

# Set up PWM on GPIO 25
pwm0 = PWM(Pin(PWM_PIN))
pwm0.freq(1000)
pwm0.duty(duty_cycle)

# Timer for RPM calculation
rpm_timer = Timer(0)
rpm_timer.init(period=1000, mode=Timer.PERIODIC, callback=calculate_rpm)

# Timer for PWM adjustment
control_timer = Timer(1)
control_timer.init(period=1000, mode=Timer.PERIODIC, callback=adjust_pwm)

# Connect to WiFi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
    print('network config:', wlan.ifconfig())

connect_wifi(WIFI_SSID, WIFI_PASSWORD)

# Start a web server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

def web_page():
    return """<!DOCTYPE html>
<html>
    <head> <title>Fan Controller</title> </head>
    <body>
        <h1>ESP32 Fan Controller</h1>
        <p>Current RPM: {}</p>
        <form>
            <input type="number" name="rpm" value="{}">
            <input type="submit" value="Set RPM">
        </form>
    </body>
</html>
""".format(current_rpm, DESIRED_RPM)

while True:
    cl, addr = s.accept()
    request = cl.recv(1024)
    request = request.decode('utf-8')

    # Handle GET request for web page
    if 'GET / ' in request or 'GET /?' in request:
        if 'GET /?rpm=' in request:
            index = request.find('GET /?rpm=') + len('GET /?rpm=')
            rpm_str = request[index:request.find(' ', index)]
            DESIRED_RPM = int(rpm_str)
        response = web_page()
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + response)
        print("Handled GET request, serving web page.")

    # Handle GET request for current RPM
    elif 'GET /rpm' in request:
        response = "Current RPM: {}".format(current_rpm)
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n' + response)
        print("Handled GET request for current RPM.")

    # Handle POST request to set desired RPM
    elif 'POST /rpm' in request:
        body_index = request.find('\r\n\r\n') + 4
        body = request[body_index:].strip()
        try:
            new_rpm = int(body)
            DESIRED_RPM = new_rpm
            response = "Desired RPM set to {}".format(new_rpm)
            print("Handled POST request, set RPM to:", new_rpm)
        except ValueError:
            response = "Invalid RPM value"
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n' + response)

    cl.close()
