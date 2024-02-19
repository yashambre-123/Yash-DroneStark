#include "sbus.h"
#include <Servo.h>

Servo throttleServo;
Servo panServo;
Servo switchServo;

bfs::SbusTx sbus_tx1(&Serial1);
bfs::SbusData radio_data;

bfs::SbusRx sbus_rx_serial(&Serial1);
bfs::SbusTx sbus_tx_serial(&Serial1);
bfs::SbusData data;

bfs::SbusTx sbus_tx1_1(&Serial2);
bfs::SbusData physical_remote_radio_data;

bfs::SbusTx sbus_tx2(&Serial3);
bfs::SbusData remote_radio_data;

int inputModeSwitch = 0;
int inputThrottle = 0;
int inputPan = 0;

int panPin = 3;         // channel 1
int throttlePin = 9;    // channel 3
int switchPin = 12;     // channel 5
int modeChangePin = 4;

int throttle_value, yaw_value, pitch_value, roll_value, slider_1_value, slider_2_value, toggle_1_value, toggle_2_value;
int physical_throttle_value, physical_yaw_value, physical_pitch_value, physical_roll_value, physical_slider_1_value, physical_slider_2_value, physical_toggle_1_value, physical_toggle_2_value;

const int numChars = 32;
char receivedChars[numChars];

int acceleration = 0;
int pan_control = 0;
int tilt = 0;
int directionSwitch = 0;

void setup() {
  Serial.begin(115200);
  sbus_tx1.Begin();
  sbus_tx1_1.Begin();
  sbus_tx2.Begin();
  sbus_rx_serial.Begin();
  sbus_tx_serial.Begin();
  pinMode(panPin, OUTPUT);
  pinMode(throttlePin, OUTPUT);
  pinMode(switchPin, OUTPUT);
  throttleServo.attach(throttlePin);
  panServo.attach(panPin);
  switchServo.attach(switchPin);
}

void remote_rc_data() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
//    String data = Serial.read
    if (data.startsWith("REMOTE")) {
      int parsed_values[9];

      int parsed_count = sscanf(data.c_str(), "REMOTE,%d,%d,%d,%d,%d,%d,%d,%d", &parsed_values[0], &parsed_values[1], &parsed_values[2], &parsed_values[3], &parsed_values[4], &parsed_values[5], &parsed_values[6], &parsed_values[7]);
      if (parsed_count == 8) {
        roll_value = parsed_values[0];
        pitch_value = parsed_values[1];
        throttle_value = parsed_values[2];
        yaw_value = parsed_values[3];
        toggle_1_value = parsed_values[4];
        slider_1_value = parsed_values[5];
        toggle_2_value = parsed_values[6];
        slider_2_value = parsed_values[7];

        remote_radio_data.ch[0] = roll_value;
        remote_radio_data.ch[1] = pitch_value;
        remote_radio_data.ch[2] = throttle_value;
        remote_radio_data.ch[3] = yaw_value;
        remote_radio_data.ch[4] = toggle_1_value;
        remote_radio_data.ch[5] = slider_1_value;
        remote_radio_data.ch[6] = toggle_2_value;
        remote_radio_data.ch[7] = slider_2_value;

        throttleServo.writeMicroseconds(throttle_value);
        panServo.writeMicroseconds(roll_value);
        switchServo.writeMicroseconds(toggle_1_value);

         Serial.print("   Roll: ");
         Serial.print(remote_radio_data.ch[0]);
         Serial.print("   Pitch: ");
         Serial.print(remote_radio_data.ch[1]);
         Serial.print("   Throttle: ");
         Serial.print(remote_radio_data.ch[2]);
         Serial.print("   Yaw: ");
         Serial.print(remote_radio_data.ch[3]);
         Serial.print("   Toggle 1: ");
         Serial.print(remote_radio_data.ch[4]);
         Serial.print("   Slider 1: ");
         Serial.print(remote_radio_data.ch[5]);
         Serial.print("   Toggle 2: ");
         Serial.print(remote_radio_data.ch[6]);
         Serial.print("   Slider 2: ");
         Serial.println(remote_radio_data.ch[7]);

        sbus_tx_serial.data(remote_radio_data);
        sbus_tx_serial.Write();

      } else {
        Serial.println("Parsing error. Data not in the expected format.");
      }

    }
    else{
      Serial.println("data doesnt start with");
    }  
    }
 
    }

void all_sbus() {
  if (sbus_rx_serial.Read()) {
    data = sbus_rx_serial.data();
    if (992 < data.ch[6] && data.ch[6] <= 1500) {
      remote_rc_data();
    } 
//    else if (1500 < data.ch[6] && data.ch[6] < 2000) {
//      physical_rc();
//    }
    if (!(1500 < data.ch[6] && data.ch[6] < 2000)) {
      for (int8_t i = 0; i < data.NUM_CH; i++) {
      Serial.print(data.ch[i]);
      Serial.print("\t");
      if (i == 0) {
        int throttleValue = map(data.ch[i], 172, 1811, 0, 2000);
        throttleServo.writeMicroseconds(throttleValue);
      } else if (i == 1) {
        int panValue = map(data.ch[i], 172, 1811, 0, 2000);
        panServo.writeMicroseconds(panValue);
      } else if (i == 5) {
        int switchValue = map(data.ch[i], 172, 1811, 0, 2000);
        switchServo.writeMicroseconds(switchValue);
      }
    }
    Serial.print(data.lost_frame);
    Serial.print("\t");
    Serial.println(data.failsafe);
    sbus_tx_serial.data(data);
    sbus_tx_serial.Write();
    }
  }
}

void loop() {
  all_sbus();
}
