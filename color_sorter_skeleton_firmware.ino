#include <Wire.h>
#include <Servo.h>
#include "Adafruit_TCS34725.h"

Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_614MS, TCS34725_GAIN_1X);

Servo servoGate;  // Servo to control the gate
Servo servoChute; // Servo to control the chute

const int servoGatePin = 9;  // Change to your servo pin
const int servoChutePin = 10; // Change to your servo pin

// Servo angles for the gate
const int gateOpenAngle = 140;
const int gateCloseAngle = 80;
const int gateDispenseAngle = 30;

// Servo angles for the chute
const int chutePositions[6] = {60, 80, 110, 140, 20, 175}; // Positions for chutes 1, 2, 3, and 4, and 5

void setup() {
  Serial.begin(9600);
  Serial.println("Serial interface found.");
  servoGate.attach(servoGatePin);
  Serial.println("Gate servo initialized.");
  servoChute.attach(servoChutePin);
  Serial.println("Chute servo initialized.");
  
  if (tcs.begin()) {
    Serial.println("Color sensor initialized.");
  } else {
    Serial.println("No TCS34725 found ... check your connections");
    while (1); // Stop if no sensor found
  }

  Serial.println("Hello, I am a marble color sorter. Firmware version 1.8 by Akaki at LPI MakerLab.");
  Serial.println("Send '?' for instructions.");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');

    if (command == "?") {
      printInstructions();
    } else if (command.startsWith("G")) {
      int a = command.substring(1).toInt();
      moveServo(servoGate, a, "Gate");
      //Serial.println("Gate servo moved to " + a);
    } else if (command.startsWith("C")) {
      int a = command.substring(1).toInt();
      moveServo(servoChute, a, "Chute");
      //Serial.println("Chute servo moved to " + a);
    } else if (command == "S") {
      readSensor();
    } else if (command == "I") {
      inputMarble();
    } else if (command.startsWith("O")) {
      int chuteIndex = command.substring(1).toInt() - 1;
      outputMarble(chuteIndex);
    } else if (command == "xyzzy") {
      Serial.println("I am an easter egg");
    } else {
      Serial.println("Unknown command: " + command);
    }
    
    Serial.flush(); // Clear the serial buffer after handling a command
  }
}

void moveServo(Servo &servo, int angle, const String &servoName) {
  if (angle >= 0 && angle <= 180) {
    servo.write(angle);
    //Serial.println(servoName + " servo moved to " + angle);
  } else {
    Serial.println("Invalid angle for " + servoName + " servo: " + angle);
  }
}

void readSensor() {
  uint16_t r, g, b, c;
  tcs.getRawData(&r, &g, &b, &c);
  Serial.print("R: ");
  Serial.print(r, DEC);
  Serial.print(", G: ");
  Serial.print(g, DEC);
  Serial.print(", B: ");
  Serial.println(b, DEC);
}

void inputMarble() {
  moveServo(servoGate, gateOpenAngle, "Gate");
  delay(800);
  moveServo(servoGate, gateCloseAngle, "Gate");
  delay(800);
  readSensor();
}

void outputMarble(int chuteIndex) {
  if (chuteIndex >= 0 && chuteIndex < 5) {
    moveServo(servoChute, chutePositions[chuteIndex], "Chute");
    moveServo(servoGate, gateDispenseAngle, "Gate");
  } else {
    Serial.println("Invalid chute number: " + String(chuteIndex + 1));
  }
  delay(500);
}

void printInstructions() {
  Serial.println("Instructions:");
  Serial.println("  I: Input a marble and read its color.");
  Serial.println("  Example output: R: 302, G: 850, B: 569");
  Serial.println("  O#: Output marble to chute # (1-4). Example: O1");
  Serial.println("  G#: Move Gate servo to angle # (0-180). Example: G90");
  Serial.println("  C#: Move Chute servo to angle # (0-180). Example: C45");
  Serial.println("  S: Read color sensor and output R, G, B values.");
  
}
