import serial
import serial.tools.list_ports
import time

def find_arduino_serial_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'Arduino' in port.description or 'usbmodem' in port.device:
            return port.device
    return None

def initialize_serial_connection(arduino_port):
    try:
        ser = serial.Serial(arduino_port, 9600, timeout=1)
        time.sleep(1)  # Wait for connection to establish
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial connection: {e}")
        return None

def process_marble(ser):
    r, g, b = read_sensor(ser)
    if r is not None and g is not None and b is not None:
        print(f"RGB Values: R: {r}, G: {g}, B: {b}")
        color = determine_color(r, g, b)
        print(f"Detected color: {color}")

        chute_number = get_chute_number(color)
        print(f"Outputting marble to chute {chute_number}...")
        send_command(ser, f"O{chute_number}")
        time.sleep(0.5)
        print("Ready for next marble.")
    else:
        print("Failed to read sensor data.")
        time.sleep(0.5)

def send_command(ser, command):
    print(f"[Sent] {command}")
    ser.write(f"{command}\n".encode())

def read_sensor(ser):
    ser.reset_input_buffer()
    send_command(ser, "I")
    return wait_for_sensor_data(ser)

def wait_for_sensor_data(ser):
    start_time = time.time()
    timeout = 5  # Timeout in seconds

    while (time.time() - start_time) < timeout:
        if ser.in_waiting:
            line = ser.readline().decode().strip()
            print(f"[Received] {line}")
            if line.startswith("R:"):
                parts = line.split(", ")
                if len(parts) == 3:
                    r = int(parts[0].split(": ")[1])
                    g = int(parts[1].split(": ")[1])
                    b = int(parts[2].split(": ")[1])
                    return r, g, b
        time.sleep(0.1)

    return None, None, None

def determine_color(r, g, b):
    # Adjusted thresholds for nuanced color detection
    red_dominance_threshold = 1.2
    blue_dominance_ratio = 1.1
    yellow_rg_ratio = 1.2  # Increase threshold for yellow detection
    yellow_blue_ratio = 0.5
    high_value_threshold = 500  # Adjusted threshold for high values
    color_difference_tolerance = 0.3  # Tolerance for color differences in white detection

    # Check if all colors are high and relatively close to each other for white
    if (r > high_value_threshold and g > high_value_threshold and b > high_value_threshold and
        max(r, g, b) / min(r, g, b) < 1 + color_difference_tolerance):
        return 'White'

    # Check for red
    elif r > g * red_dominance_threshold and r > b * red_dominance_threshold:
        return 'Red'

    # Check for blue
    elif b > r * blue_dominance_ratio and b > g * blue_dominance_ratio:
        return 'Blue'

    # Check for yellow
    elif (r > g / yellow_rg_ratio and r > b * yellow_blue_ratio and
          g > b * yellow_blue_ratio and b < high_value_threshold):
        return 'Yellow'

    # Default case if no other color is determined
    else:
        return 'Unknown'



def get_chute_number(color):
    return {
        'Red': 1,
        'Blue': 2,
        'Yellow': 3,
        'White': 4,
        'Unknown': 5
    }.get(color, 1)

def main():
    arduino_port = find_arduino_serial_port()
    if arduino_port is None:
        print("Arduino not found. Please check the connection.")
        return

    ser = initialize_serial_connection(arduino_port)
    if ser is None:
        return

    try:
        while True:
            process_marble(ser)
    except KeyboardInterrupt:
        print("Program interrupted by user")
    finally:
        if ser:
            ser.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    main()
