#include "sbus.h"
#include <Servo.h>

Servo throttleServo;
Servo panServo;
Servo switchServo;

Servo pwm1;
Servo pwm2;
Servo pwm3;
Servo pwm4;
Servo pwm5;
Servo pwm6;
Servo pwm7;
Servo pwm8;

//bfs::SbusTx sbus_tx1(&Serial1);
bfs::SbusData radio_data;

bfs::SbusRx sbus_rx_serial(&Serial1);
bfs::SbusTx sbus_tx_serial(&Serial1);
bfs::SbusData data1;
bfs::SbusData datab;

bfs::SbusTx sbus_tx1_1(&Serial2);
bfs::SbusData physical_remote_radio_data;
bfs::SbusData physical_remote_radio_datab;

bfs::SbusTx sbus_tx2(&Serial3);
bfs::SbusData remote_radio_data;
bfs::SbusData remote_radio_datab;

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
  //sbus_tx1.Begin();
  sbus_tx1_1.Begin();
  sbus_tx2.Begin();
  sbus_rx_serial.Begin();
  sbus_tx_serial.Begin();
  pinMode(panPin, OUTPUT);
  pinMode(throttlePin, OUTPUT);
  pinMode(switchPin, OUTPUT);
  pwm1.attach(2);
  pwm2.attach(3);
  pwm3.attach(4);
  pwm4.attach(5);
  pwm5.attach(6);
  pwm6.attach(7);
  pwm7.attach(8);
  pwm8.attach(9);
  throttleServo.attach(throttlePin);
  panServo.attach(panPin);
  switchServo.attach(switchPin);

//  long int t1 = millis();
  
//  all_sbus();
  //  passVJ();

//  long int t2 = millis();

//  Serial.print("Time taken by the task: "); Serial.print(t2-t1); Serial.println(" milliseconds");
}

void loop() {

//  long int t1 = millis();

  all_sbus();
  //  passVJ();

//  long int t2 = millis();

//  Serial.print("Time taken by the task: "); Serial.print(t2-t1); Serial.println(" milliseconds");

}

void rc_data() {
  inputThrottle = pulseIn(throttlePin, HIGH);
  inputPan = pulseIn(panPin, HIGH);
  inputModeSwitch = pulseIn(switchPin, HIGH);

  inputThrottle = map(inputThrottle, 1000, 2000, 0, 2000);
  inputPan = map(inputPan, 1000, 2000, 0, 2000);
  inputModeSwitch = map(inputModeSwitch, 1000, 2000, 0, 2000);

  inputThrottle = constrain(inputThrottle, 0, 2000);
  inputPan = constrain(inputPan, 0, 2000);
  inputModeSwitch = constrain(inputModeSwitch, 0, 2000);

  radio_data.ch[0] = inputPan;
  radio_data.ch[1] = inputThrottle;
  radio_data.ch[2] = inputModeSwitch;
  radio_data.ch[3] = 0;
  radio_data.ch[4] = 0;
  radio_data.ch[5] = 0;
  radio_data.ch[6] = 0;
  radio_data.ch[7] = 0;

  // Serial.print("   Pan: ");
  // Serial.print(radio_data.ch[0]);
  // Serial.print("   Throttle: ");
  // Serial.print(radio_data.ch[1]);
  // Serial.print("   ModeSwitch: ");
  // Serial.println(radio_data.ch[2]);

  sbus_tx_serial.data(radio_data);
  sbus_tx_serial.Write();
  pwm1.writeMicroseconds(radio_data.ch[0]);
  pwm2.writeMicroseconds(radio_data.ch[1]);
  pwm3.writeMicroseconds(radio_data.ch[2]);
  pwm4.writeMicroseconds(radio_data.ch[3]);
  pwm5.writeMicroseconds(radio_data.ch[4]);
  pwm6.writeMicroseconds(radio_data.ch[5]);
  pwm7.writeMicroseconds(radio_data.ch[6]);
  pwm8.writeMicroseconds(radio_data.ch[7]);
  //  analogWrite(pwm1, radio_data.ch[0]);
  //  analogWrite(pwm2, radio_data.ch[1]);
  //  analogWrite(pwm3, radio_data.ch[2]);
  //  analogWrite(pwm4, radio_data.ch[3]);
  //  analogWrite(pwm5, radio_data.ch[4]);
  //  analogWrite(pwm6, radio_data.ch[5]);
  //  analogWrite(pwm7, radio_data.ch[6]);
  //  analogWrite(pwm8, radio_data.ch[7]);
}

void remote_rc_data() {
  if (Serial.available()) {
    String data1 = Serial.readStringUntil('k');

//    Serial.println(data1);
    //    String data1 = Serial.read
    if (data1.startsWith("REMOTE")) {
      int parsed_values[9];

      int parsed_count = sscanf(data1.c_str(), "REMOTE,%d,%d,%d,%d,%d,%d,%d,%d", &parsed_values[0], &parsed_values[1], &parsed_values[2], &parsed_values[3], &parsed_values[4], &parsed_values[5], &parsed_values[6], &parsed_values[7]);
      if (parsed_count == 8) {
        roll_value = parsed_values[0];
        pitch_value = parsed_values[1];
        throttle_value = parsed_values[2];
        yaw_value = parsed_values[3];
        toggle_1_value = parsed_values[4];
        slider_1_value = parsed_values[5];
        toggle_2_value = parsed_values[6];
        slider_2_value = parsed_values[7];

        //        all the changes are made here only
        remote_radio_datab.ch[0] = roll_value;
        remote_radio_datab.ch[1] = pitch_value;
        remote_radio_datab.ch[2] = throttle_value;
        remote_radio_datab.ch[3] = yaw_value;
        remote_radio_datab.ch[4] = toggle_1_value;
        remote_radio_datab.ch[5] = slider_1_value;
        remote_radio_datab.ch[6] = slider_2_value;
        remote_radio_datab.ch[7] = toggle_2_value;

        remote_radio_data.ch[0] = yaw_value;
        remote_radio_data.ch[1] = pitch_value;
        remote_radio_data.ch[2] = throttle_value;
        remote_radio_data.ch[3] = roll_value;
        remote_radio_data.ch[4] = toggle_1_value;
        remote_radio_data.ch[5] = slider_1_value;
        remote_radio_data.ch[6] = slider_2_value;
        remote_radio_data.ch[7] = toggle_2_value;

        //        throttleServo.writeMicroseconds(throttle_value);
        //        panServo.writeMicroseconds(roll_value);
        //        switchServo.writeMicroseconds(toggle_1_value);

        //         Serial.print("   Roll: ");
        //         Serial.print(remote_radio_data.ch[0]);
        //         Serial.print("   Pitch: ");
        //         Serial.print(remote_radio_data.ch[1]);
        //         Serial.print("   Throttle: ");
        //         Serial.print(remote_radio_data.ch[2]);
        //         Serial.print("   Yaw: ");
        //         Serial.print(remote_radio_data.ch[3]);
        //         Serial.print("   Toggle 1: ");
        //         Serial.print(remote_radio_data.ch[4]);
        //         Serial.print("   Slider 1: ");
        //         Serial.print(remote_radio_data.ch[5]);
        //         Serial.print("   Toggle 2: ");
        //         Serial.print(remote_radio_data.ch[6]);
        //         Serial.print("   Slider 2: ");
        //         Serial.println(remote_radio_data.ch[7]);

        //   sbus_tx2.data(remote_radio_data);
        // sbus_tx2.Write();
        sbus_tx_serial.data(remote_radio_datab);
        sbus_tx_serial.Write();

        //       remote_radio_data.ch[0] = map(remote_radio_data.ch[0], 172, 1811, 1000, 2000);
        //       remote_radio_data.ch[1] = map(remote_radio_data.ch[1], 172, 1811, 1000, 2000);
        //       remote_radio_data.ch[2] = map(remote_radio_data.ch[2], 172, 1811, 1000, 2000);
        //       remote_radio_data.ch[3] = map(remote_radio_data.ch[3], 172, 1811, 1000, 2000);
        //       remote_radio_data.ch[4] = map(remote_radio_data.ch[4], 172, 1811, 1000, 2000);
        //       remote_radio_data.ch[5] = map(remote_radio_data.ch[5], 172, 1811, 1000, 2000);
        //       remote_radio_data.ch[6] = map(remote_radio_data.ch[6], 172, 1811, 1000, 2000);
        //       remote_radio_data.ch[7] = map(remote_radio_data.ch[7], 172, 1811, 1000, 2000);
        remote_radio_data.ch[0] = map(remote_radio_data.ch[0], 170, 1811, 1000, 2000);
        remote_radio_data.ch[1] = map(remote_radio_data.ch[1], 170, 1811, 1000, 2000);
        remote_radio_data.ch[2] = map(remote_radio_data.ch[2], 170, 1811, 1000, 2000);
        remote_radio_data.ch[3] = map(remote_radio_data.ch[3], 170, 1811, 1000, 2000);
        remote_radio_data.ch[4] = map(remote_radio_data.ch[4], 170, 1811, 1000, 2000);
        remote_radio_data.ch[5] = map(remote_radio_data.ch[5], 170, 1811, 1000, 2000);
        remote_radio_data.ch[6] = map(remote_radio_data.ch[6], 170, 1811, 1000, 2000);
        remote_radio_data.ch[7] = map(remote_radio_data.ch[7], 170, 1811, 1000, 2000);

        remote_radio_data.ch[0] = constrain(remote_radio_data.ch[0], 1000, 2000);
        remote_radio_data.ch[1] = constrain(remote_radio_data.ch[1], 1000, 2000);
        remote_radio_data.ch[2] = constrain(remote_radio_data.ch[2], 1000, 2000);
        remote_radio_data.ch[3] = constrain(remote_radio_data.ch[3], 1000, 2000);
        remote_radio_data.ch[4] = constrain(remote_radio_data.ch[4], 1000, 2000);
        remote_radio_data.ch[5] = constrain(remote_radio_data.ch[5], 1000, 2000);
        remote_radio_data.ch[6] = constrain(remote_radio_data.ch[6], 1000, 2000);
        remote_radio_data.ch[7] = constrain(remote_radio_data.ch[7], 1000, 2000);

        Serial.print(remote_radio_data.ch[0]);
        Serial.print("  ");
        Serial.print(remote_radio_data.ch[1]);
        Serial.print("  ");
        Serial.print(remote_radio_data.ch[2]);
        Serial.print("  ");
        Serial.print(remote_radio_data.ch[3]);
        Serial.print("  ");
        Serial.print(remote_radio_data.ch[4]);
        Serial.print("  ");
        Serial.print(remote_radio_data.ch[5]);
        Serial.print("  ");
        Serial.print(remote_radio_data.ch[6]);
        Serial.print("  ");
        Serial.print(remote_radio_data.ch[7]);
        Serial.println(" ");

        pwm1.writeMicroseconds(remote_radio_data.ch[0]);
        pwm2.writeMicroseconds(remote_radio_data.ch[1]);
        pwm3.writeMicroseconds(remote_radio_data.ch[2]);
        pwm4.writeMicroseconds(remote_radio_data.ch[3]);
        pwm5.writeMicroseconds(remote_radio_data.ch[4]);
        pwm6.writeMicroseconds(remote_radio_data.ch[5]);
        pwm7.writeMicroseconds(remote_radio_data.ch[6]);
        pwm8.writeMicroseconds(remote_radio_data.ch[7]);
        //       analogWrite(pwm1, remote_radio_data.ch[0]);
        //       analogWrite(pwm2, remote_radio_data.ch[1]);
        //       analogWrite(pwm3, remote_radio_data.ch[2]);
        //       analogWrite(pwm4, remote_radio_data.ch[3]);
        //       analogWrite(pwm5, remote_radio_data.ch[4]);
        //       analogWrite(pwm6, remote_radio_data.ch[5]);
        //       analogWrite(pwm7, remote_radio_data.ch[6]);
        //       analogWrite(pwm8, remote_radio_data.ch[7]);

        // delay(2000);

      } else {
        Serial.println("Parsing error. Data not in the expected format.");
      }

    }
    else {
      Serial.println("data doesnt start with");
    }
  }

}

void physical_rc() {
  if (Serial.available()) {
    String data1 = Serial.readStringUntil('\n');
    if (data1.startsWith("PHYSICAL_REMOTE")) {
      int parsed_values[9];

      int parsed_count = sscanf(data1.c_str(), "PHYSICAL_REMOTE,%d,%d,%d,%d,%d,%d,%d,%d", &parsed_values[0], &parsed_values[1], &parsed_values[2], &parsed_values[3], &parsed_values[4], &parsed_values[5], &parsed_values[6], &parsed_values[7]);

      Serial.println(parsed_count);

      if (parsed_count == 8) {
        physical_roll_value = parsed_values[0];
        physical_pitch_value = parsed_values[1];
        physical_throttle_value = parsed_values[2];
        physical_yaw_value = parsed_values[3];
        physical_toggle_1_value = parsed_values[4];
        physical_slider_1_value = parsed_values[5];
        physical_toggle_2_value = parsed_values[6];
        physical_slider_2_value = parsed_values[7];

        physical_remote_radio_datab.ch[0] = physical_roll_value;
        physical_remote_radio_datab.ch[1] = physical_pitch_value;
        physical_remote_radio_datab.ch[2] = physical_throttle_value;
        physical_remote_radio_datab.ch[3] = physical_yaw_value;
        physical_remote_radio_datab.ch[4] = physical_toggle_1_value;
        physical_remote_radio_datab.ch[5] = physical_slider_1_value;
        physical_remote_radio_datab.ch[6] = physical_toggle_2_value;
        physical_remote_radio_datab.ch[7] = physical_slider_2_value;

        physical_remote_radio_data.ch[0] = physical_yaw_value;
        physical_remote_radio_data.ch[1] = physical_pitch_value;
        physical_remote_radio_data.ch[2] = physical_throttle_value;
        physical_remote_radio_data.ch[3] = physical_roll_value;
        physical_remote_radio_data.ch[4] = physical_toggle_1_value;
        physical_remote_radio_data.ch[5] = physical_slider_1_value;
        physical_remote_radio_data.ch[6] = physical_slider_2_value;
        physical_remote_radio_data.ch[7] = physical_toggle_2_value;

        // Serial.print("   Roll: ");
        // Serial.print(physical_remote_radio_data.ch[0]);
        // Serial.print("   Pitch: ");
        // Serial.print(physical_remote_radio_data.ch[1]);
        // Serial.print("   Throttle: ");
        // Serial.print(physical_remote_radio_data.ch[2]);
        // Serial.print("   Yaw: ");
        // Serial.print(physical_remote_radio_data.ch[3]);
        // Serial.print("   Toggle 1: ");
        // Serial.print(physical_remote_radio_data.ch[4]);
        // Serial.print("   Slider 1: ");
        // Serial.print(physical_remote_radio_data.ch[5]);
        // Serial.print("   Toggle 2: ");
        // Serial.print(physical_remote_radio_data.ch[6]);
        // Serial.print("   Slider 2: ");
        // Serial.println(physical_remote_radio_data.ch[7]);

        //        sbus_tx1_1.data(physical_remote_radio_data);
        //        sbus_tx1_1.Write();
        sbus_tx_serial.data(physical_remote_radio_datab);
        sbus_tx_serial.Write();

        physical_remote_radio_data.ch[0] = map(physical_remote_radio_data.ch[0], 170, 1811, 1000, 2000);
        physical_remote_radio_data.ch[1] = map(physical_remote_radio_data.ch[1], 1811, 170, 2000, 1000);
        physical_remote_radio_data.ch[2] = map(physical_remote_radio_data.ch[2], 1811, 170, 2000, 1000);
        physical_remote_radio_data.ch[3] = map(physical_remote_radio_data.ch[3], 170, 1811, 1000, 2000);
        physical_remote_radio_data.ch[4] = map(physical_remote_radio_data.ch[4], 170, 1811, 1000, 2000);
        physical_remote_radio_data.ch[5] = map(physical_remote_radio_data.ch[5], 170, 1811, 1000, 2000);
        physical_remote_radio_data.ch[6] = map(physical_remote_radio_data.ch[6], 170, 1811, 1000, 2000);
        physical_remote_radio_data.ch[7] = map(physical_remote_radio_data.ch[7], 170, 1811, 1000, 2000);

        physical_remote_radio_data.ch[0] = constrain(physical_remote_radio_data.ch[0], 1000, 2000);
        physical_remote_radio_data.ch[1] = constrain(physical_remote_radio_data.ch[1], 2000, 1000);
        physical_remote_radio_data.ch[2] = constrain(physical_remote_radio_data.ch[2], 2000, 1000);
        physical_remote_radio_data.ch[3] = constrain(physical_remote_radio_data.ch[3], 1000, 2000);
        physical_remote_radio_data.ch[4] = constrain(physical_remote_radio_data.ch[4], 1000, 2000);
        physical_remote_radio_data.ch[5] = constrain(physical_remote_radio_data.ch[5], 1000, 2000);
        physical_remote_radio_data.ch[6] = constrain(physical_remote_radio_data.ch[6], 1000, 2000);
        physical_remote_radio_data.ch[7] = constrain(physical_remote_radio_data.ch[7], 1000, 2000);

        //        Serial.print("   Roll: ");
        //        Serial.print(physical_remote_radio_data.ch[0]);
        //        Serial.print("   Pitch: ");
        //        Serial.print(physical_remote_radio_data.ch[1]);
        //        Serial.print("   Throttle: ");
        //        Serial.print(physical_remote_radio_data.ch[2]);
        //        Serial.print("   Yaw: ");
        //        Serial.print(physical_remote_radio_data.ch[3]);
        //        Serial.print("   Toggle 1: ");
        //        Serial.print(physical_remote_radio_data.ch[4]);
        //        Serial.print("   Slider 1: ");
        //        Serial.print(physical_remote_radio_data.ch[5]);
        //        Serial.print("   Toggle 2: ");
        //        Serial.print(physical_remote_radio_data.ch[6]);
        //        Serial.print("   Slider 2: ");
        //        Serial.println(physical_remote_radio_data.ch[7]);

        pwm1.writeMicroseconds(physical_remote_radio_data.ch[0]);
        pwm2.writeMicroseconds(physical_remote_radio_data.ch[1]);
        pwm3.writeMicroseconds(physical_remote_radio_data.ch[2]);
        pwm4.writeMicroseconds(physical_remote_radio_data.ch[3]);
        pwm5.writeMicroseconds(physical_remote_radio_data.ch[4]);
        pwm6.writeMicroseconds(physical_remote_radio_data.ch[5]);
        pwm7.writeMicroseconds(physical_remote_radio_data.ch[6]);
        pwm8.writeMicroseconds(physical_remote_radio_data.ch[7]);
        //        analogWrite(pwm1, physical_remote_radio_data.ch[0]);
        //        analogWrite(pwm2, physical_remote_radio_data.ch[1]);
        //        analogWrite(pwm3, physical_remote_radio_data.ch[2]);
        //        analogWrite(pwm4, physical_remote_radio_data.ch[3]);
        //        analogWrite(pwm5, physical_remote_radio_data.ch[4]);
        //        analogWrite(pwm6, physical_remote_radio_data.ch[5]);
        //        analogWrite(pwm7, physical_remote_radio_data.ch[6]);
        //        analogWrite(pwm8, physical_remote_radio_data.ch[7]);

      } else {
        Serial.println("Parsing error. Data not in the expected format.");
      }
    }
  }
}

void passVJ()
{
  sbus_rx_serial.Read();
  data1 = sbus_rx_serial.data();
  Serial.println(data1.ch[4]);
  ////  if (sbus_rx_serial.Read()){
  //    if (1500<data1.ch[4]<2011) {
  //      Serial.print(data1.ch[4]);
  ////      Serial.println("mode 3");
  ////      remote_rc_data();?/
  //    } else if (1000<data1.ch[4]<1500) {
  ////      physical_rc();
  //      Serial.print(data1.ch[4]);
  ////      Serial.println("mode 2");
  //    }
  //    else if (0<data1.ch[4]<900) {
  //      Serial.print(data1.ch[4]);
  ////      Serial.println("mode 1");
  //
  //}

}






void all_sbus() {
  if (sbus_rx_serial.Read()) {
    data1 = sbus_rx_serial.data();
    if (data1.ch[4] == 1811) {
      remote_rc_data();
    }
    else if (data1.ch[4] == 992) {
      physical_rc();
    }
    else if (data1.ch[4] == 172) {
      for (int8_t i = 0; i < data1.NUM_CH; i++) {
        //      Serial.print(data1.ch[i]);
        //      Serial.print("\t");
        if (i == 1) {
          int throttleValue = map(data1.ch[i], 172, 1811, 0, 2000);
          //        Serial.println(data1.ch[2]);
          //        Serial.print(throttleValue);
          throttleServo.writeMicroseconds(throttleValue);
        } else if (i == 3) {
          int panValue = map(data1.ch[i], 172, 1811, 0, 2000);
          panServo.writeMicroseconds(panValue);
        } else if (i == 5) {
          int switchValue = map(data1.ch[i], 172, 1811, 0, 2000);
          switchServo.writeMicroseconds(switchValue);
        }
      }
      //    Serial.print(data1.lost_frame);
      //    Serial.print("\t");
      //    Serial.println(data1.failsafe);
      datab.ch[0] = map(data1.ch[0], 172, 1811, 1000, 2000);
      datab.ch[1] = map(data1.ch[1], 172, 1811, 1000, 2000);
      datab.ch[2] = map(data1.ch[2], 172, 1811, 1000, 2000);
      datab.ch[3] = map(data1.ch[3], 172, 1811, 1000, 2000);
      datab.ch[4] = map(data1.ch[4], 172, 1811, 1000, 2000);
      datab.ch[5] = map(data1.ch[5], 172, 1811, 1000, 2000);
      datab.ch[6] = map(data1.ch[6], 172, 1811, 1000, 2000);
      datab.ch[7] = map(data1.ch[7], 172, 1811, 1000, 2000);
      // Serial.println(data1.ch[2]);
      /*
        datab.ch[0] = data1.ch[0];
        datab.ch[1] = data1.ch[1];
        datab.ch[2] = data1.ch[2];
        datab.ch[3] = data1.ch[3];
        datab.ch[4] = data1.ch[4];
        datab.ch[5] = data1.ch[5];
        datab.ch[6] = data1.ch[6];
        datab.ch[7] = data1.ch[7];
      */
      data1.ch[0] = data1.ch[3];
      data1.ch[1] = data1.ch[1];
      data1.ch[2] = data1.ch[6];
      data1.ch[3] = data1.ch[7];
      data1.ch[4] = data1.ch[4];
      data1.ch[5] = data1.ch[5];
      data1.ch[6] = data1.ch[2];
      data1.ch[7] = data1.ch[0];

          Serial.print(datab.ch[0]);
          Serial.print("  ");
          Serial.print(datab.ch[1]);
          Serial.print("  ");
          Serial.print(datab.ch[2]);
          Serial.print("  ");
          Serial.print(datab.ch[3]);
          Serial.print("  ");
          Serial.print(datab.ch[4]);
          Serial.print("  ");
          Serial.print(datab.ch[5]);
          Serial.print("  ");
          Serial.print(datab.ch[6]);
          Serial.print("  ");
          Serial.print(datab.ch[7]);
          Serial.println(" ");

      sbus_tx_serial.data(data1);
      sbus_tx_serial.Write();


      pwm1.writeMicroseconds(datab.ch[0]);
      pwm2.writeMicroseconds(datab.ch[1]);
      pwm3.writeMicroseconds(datab.ch[2]);
      pwm4.writeMicroseconds(datab.ch[3]);
      pwm5.writeMicroseconds(datab.ch[4]);
      pwm6.writeMicroseconds(datab.ch[5]);
      pwm7.writeMicroseconds(datab.ch[6]);
      pwm8.writeMicroseconds(datab.ch[7]);

      //    Serial.print(data1.ch[0]);
      //    Serial.print("  ");
      //    Serial.print(data1.ch[1]);
      //    Serial.print("  ");
      //    Serial.print(data1.ch[2]);
      //    Serial.print("  ");
      //    Serial.print(data1.ch[3]);
      //    Serial.print("  ");
      //    Serial.print(data1.ch[4]);
      //    Serial.print("  ");
      //    Serial.print(data1.ch[5]);
      //    Serial.print("  ");
      //    Serial.print(data1.ch[6]);
      //    Serial.print("  ");
      //    Serial.print(data1.ch[7]);
      //    Serial.println(" ");
      //    analogWrite(pwm1, data1.ch[0]);
      //    analogWrite(pwm2, data1.ch[1]);
      //    analogWrite(pwm3, data1.ch[2]);
      //    analogWrite(pwm4, data1.ch[3]);
      //    analogWrite(pwm5, data1.ch[4]);
      //    analogWrite(pwm6, data1.ch[5]);
      //    analogWrite(pwm7, data1.ch[6]);
      //    analogWrite(pwm8, data1.ch[7]);

    }
  }
}
