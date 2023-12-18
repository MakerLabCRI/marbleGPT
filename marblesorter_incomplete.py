import serial
import serial.tools.list_ports
import time

def determine_color(r, g, b):
    # Define color thresholds based on real RGB readings for your specific marbles
    # TODO: define the logic here
    # should return 'Red', 'Blue', 'White', or 'Yellow' as a string and nothing else

    return 'Red' #as a placeholder, consider all marbles red..


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
    # command hardware to input a marble, read the sensor and then receive the RGB:
    r, g, b = read_sensor(ser) 
    if r is not None and g is not None and b is not None: #sanity check
        print(f"RGB Values: R: {r}, G: {g}, B: {b}")      #print to terminal for debugging and sampling of data
        color = determine_color(r, g, b)                  #decide which color marble it is. This function should be tuned based on real world data samples
        print(f"Detected color: {color}")                 #debug output

        chute_number = get_chute_number(color)
        print(f"Outputting marble to chute {chute_number}...")
        send_command(ser, f"O{chute_number}")
        time.sleep(0.5)                                   #the chute servo takes some time to move, wait so as not to crowd the serial connection
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

def wait_for_sensor_data(ser):  #hardware servo takes some time to move, and sensor reading takes almost a second. Wait for a reply so as not to crown the serial.
    start_time = time.time()
    timeout = 5  # Timeout in seconds

    while (time.time() - start_time) < timeout:
        if ser.in_waiting:
            line = ser.readline().decode().strip()
            print(f"[Received] {line}")
            if line.startswith("R:"):   #the RGB data comes as a line like R: 300 G: 812 B: 642
                parts = line.split(", ")
                if len(parts) == 3:
                    r = int(parts[0].split(": ")[1])
                    g = int(parts[1].split(": ")[1])
                    b = int(parts[2].split(": ")[1])
                    return r, g, b
        time.sleep(0.1)

    return None, None, None

def get_chute_number(color):
    return {
        'Red': 1,
        'Blue': 2,
        'Yellow': 3,
        'White': 4
    }.get(color, 1)

def main():
    arduino_port = find_arduino_serial_port()
    if arduino_port is None:
        print("Hardware not found. Please check the connection.")
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
