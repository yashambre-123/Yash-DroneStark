//this is correct one
#include <avr/wdt.h>
#include "cytron_driver.h" 
#include "SerialData.h" 
#include "PID.h"

#define PWM_STEP  1
#define TURN_TIME 250
#define MIN_STOP  40
#define ABOUT_TURN  400
#define BLIND_MOVE  180

#define AUTO  1
#define MANUAL 2
#define EMERG_STOP  -1

#define FORWARD 1
#define REVERSE -1
#define RIGHT 2
#define LEFT  3

#define MAX_TH  35 
#define ABS_PAN 0.5*MAX_TH 

int throttlePin = 9;    //channel 3  
int panPin = 3;         //channel 1  
int reversePin = 11;    //channel 8
int switchPin = 12;     //chennel 6
int baseThrottle = MAX_TH/2 ;
int prevAngle = 0;
int noLineCount = 0; 
int led = 13;
int turnType = 0;
int stopForBlue = 0;
//int stopThatDamnVehicle = 0;/

/* PID variables */
double kp = 1.5, ki = 0.0, kd = 0.0;
int setpoint = baseThrottle;
int l_acc = 0, l_err = 0, l_prev = 0;
int r_acc = 0, r_err = 0, r_prev = 0;

SerialData serialdata(0);
//extern int dout;
char receivedChar;
int out = 0;

int dir = FORWARD;
int l_prev_spd = 0;
int r_prev_spd = 0;

int l_set_spd = 0;
int r_set_spd = 0;

int inputThrottle = 0;
int inputPan = 0;
int inputRev = 0;
int inputSwitch = 0;

int throttle = 0;
int pan = 0;
int reverse = 0;
int modeSwitch = 0;

volatile int sys_state = MANUAL;
volatile int prev_sys_state = sys_state;
CytronMD rightMtr(PWM_DIR, 6, 4);
CytronMD leftMtr(PWM_DIR, 5, 10);

// --- Common Code ---
void smoothShift(int l_spd, int r_spd, int l_dir, int r_dir){  
  //reverseSw = pulseIn(reversePin, HIGH);
  //reverseSw = 0;
  for(int i = 0; i < 254; i++){
    if(l_prev_spd > l_spd){
      l_prev_spd -= PWM_STEP;
    }
    else if(l_prev_spd < l_spd){
      l_prev_spd += PWM_STEP;
    }
    if(r_prev_spd > r_spd){
      r_prev_spd -= PWM_STEP;
    }
    else if(r_prev_spd < r_spd){
      r_prev_spd += PWM_STEP;
    }    

    l_prev_spd = constrain(l_prev_spd, -2*MAX_TH, 2*MAX_TH);
    r_prev_spd = constrain(r_prev_spd, -2*MAX_TH, 2*MAX_TH);

    
    if(sys_state == MANUAL){
      if((l_prev_spd < 3) && (r_prev_spd < 3)){
        if(reverse >= 0){
          dir = FORWARD;
        }
        else if(reverse == -1){
          dir = REVERSE;
        }
      }
    }else if (sys_state == AUTO){
      dir = FORWARD;
    }
   
//    leftMtr.setSpeed(2*l_prev_spd*l_dir);
//    rightMtr.setSpeed(2*r_prev_spd*r_dir);

    leftMtr.setSpeed(l_prev_spd*l_dir);
    rightMtr.setSpeed(r_prev_spd*r_dir);

    if((l_prev_spd == l_set_spd) && (r_prev_spd == r_set_spd)){
      break;
    }
  }
  
}

void turnVehicle(int turn_dir){
  smoothShift(0,0, FORWARD, FORWARD);
//  delay(3000);
  if(turn_dir == RIGHT){ 
    for(int i =0; i < TURN_TIME - turnType*(0.3*TURN_TIME); i++){
      smoothShift(turnType*baseThrottle, baseThrottle, REVERSE, FORWARD);
      delay(5);
    }
  }
  if(turn_dir == LEFT){
    //smoothShift(baseThrottle, baseThrottle, FORWARD, REVERSE);
    for(int i =0; i < TURN_TIME - turnType*(0.3*TURN_TIME); i++){
      smoothShift(baseThrottle, turnType*baseThrottle, FORWARD, REVERSE);
      delay(5);
    }
  }
  turnType = 0;
  Serial.flush();
  smoothShift(0,0, FORWARD, FORWARD);
}

void aboutTurnVehicle(){
  smoothShift(0,0,FORWARD,FORWARD);
  for(int i = 0; i < 400; i++){
    smoothShift(baseThrottle, baseThrottle, REVERSE, FORWARD);
    delay(5);
  }
  Serial.flush();
  smoothShift(0,0,FORWARD,FORWARD);
}


// --- Manual Code ---
void modeManual() {
//  stopThatDamnVehicle = 0;
//  stopForBlue = 0;
  Serial.flush();

  inputThrottle = pulseIn(throttlePin, HIGH);
  inputPan = pulseIn(panPin, HIGH);

  
  
  if (inputThrottle > 1500){
    throttle = map(inputThrottle, 1500, 2000, 0, MAX_TH);
  }
  else{
    throttle = 0;
  }
  throttle = constrain(throttle, 0, MAX_TH);
 
//  if(1490<inputPan<1510){
//    pan = 1500;
////    Serial.println("from");
//  }
  
  pan = map(inputPan, 2000, 1010, -ABS_PAN, ABS_PAN);
  pan = constrain(pan, -ABS_PAN, ABS_PAN);

  

  if (throttle == 0 && pan == 0){
    inputRev = pulseIn(reversePin, HIGH);
    
    if (inputRev > 1500){
      reverse = map(inputRev, 1010, 2000, -1, 1);
      reverse = 1;
    }
    else{
      reverse = 0;
    }
    reverse = constrain(reverse, -1, 1);
    

    
    delay(500);
  }
  
  if (reverse <= 0) {
    l_set_spd = throttle + pan;
    r_set_spd = throttle - pan;
  }
  else{
    l_set_spd = -throttle - pan;
    r_set_spd = -throttle + pan;
  }

  smoothShift(l_set_spd, r_set_spd, FORWARD, FORWARD);  
}

// --- Auto Code ---
int pid(int spderr, int &prev_val, int &Iterm){
  Iterm += spderr;
  int prev_error = prev_val - setpoint;
  int Dterm = spderr - prev_error;
  int mtr_spd = kp*(spderr) + ki*(Iterm) + kd*(Dterm);
  prev_val = mtr_spd;  
  return mtr_spd;
}

int filter_recv_value(int val){
  val = map(val, -120, 120, -ABS_PAN, ABS_PAN);
  val = constrain(val, -ABS_PAN, ABS_PAN);
  return val;
}

void kickStart(){
  smoothShift(0,0,FORWARD,FORWARD);
//  delay(3000);
  for(int i =0; i < 180; i++){
      smoothShift(baseThrottle, baseThrottle, FORWARD, FORWARD);
      delay(5);
  }
  Serial.flush();
  return;
}

void creepForward(){
  smoothShift(0,0,FORWARD,FORWARD);
  for(int i =0; i < 180/5; i++){
      smoothShift(baseThrottle/2, baseThrottle/2, FORWARD, FORWARD);
      delay(5);
  }
  smoothShift(0,0,FORWARD,FORWARD);
  Serial.flush();
  return;
}

void reverseMotion(){
  smoothShift(0,0,FORWARD,FORWARD);
  for(int i =0; i < 180/2; i++){
      smoothShift(baseThrottle, baseThrottle, REVERSE, REVERSE);
      delay(5);
  }
  Serial.flush();
  smoothShift(0,0,FORWARD,FORWARD);
  return;
}

void modeAuto(){

  if(Serial.available() > 0){
    //out = serialdata.decodeData(serialdata.data);
    serialdata.decodeData(serialdata.data);
    out = serialdata.data.angle;
//    delay(1);
//    Serial.println(out);

    if(out > 360){

  out = prevAngle;
  out = filter_recv_value(out);

  smoothShift(pid((baseThrottle-out), r_prev, r_acc), pid((baseThrottle+out), l_prev, l_acc), FORWARD, FORWARD);
//  Serial.println("out is greater than 360");
  }

  else {            
    out = filter_recv_value(out);
    prevAngle = out;

    smoothShift(pid((baseThrottle-out), r_prev, r_acc), pid((baseThrottle+out), l_prev, l_acc), FORWARD, FORWARD);
//    Serial.println("out is lesser than 360");
  }
//    Serial.println("asadnasdadnanmn");
  }
//  Serial.println("mannered");
//  noInterrupts();
  //Serial.println(serialdata.data.t);
  if(serialdata.data.t == 'L'){
    Serial.println("Left");
//    Serial.println(10);
    out = 0;
    //smoothShift(0,0,FORWARD,FORWARD);    
    turnVehicle(LEFT);
    serialdata.data.t = 'N';
    stopThatDamnVehicle = 0;
    stopForBlue = 0;
    return;
  }
  if(serialdata.data.t == 'R'){
    Serial.println("Right");
//    Serial.println(20);
    out = 0;
    //smoothShift(0,0,FORWARD,FORWARD);
    turnVehicle(RIGHT);
    serialdata.data.t = 'N';
    stopThatDamnVehicle = 0;
    stopForBlue = 0;
    return;
  }
  if(serialdata.data.t == 'U'){
    Serial.println("About Turn");
    out = 0;
    aboutTurnVehicle();
    serialdata.data.t = 'N';
    stopThatDamnVehicle = 0;
    stopForBlue = 0;
    return;
  }
  if(serialdata.data.t == 'F'){
//    Serial.println("Forward");
//    Serial.println(30);
    out = 0;
    kickStart();
    serialdata.data.t = 'N';
    stopThatDamnVehicle = 0;
    stopForBlue = 0;
    return;
  }
  if(serialdata.data.t == 'P'){
    Serial.println("Reverse");
    out = 0;
    reverseMotion();
    serialdata.data.t = 'N';
    stopThatDamnVehicle = 0;
    stopForBlue = 0;
    return;
  }
  if(serialdata.data.t == 'C'){
    out = 0;
    creepForward();
    serialdata.data.t = 'N';
    stopThatDamnVehicle = 0;
    stopForBlue = 0;
    return;
  }
  if(serialdata.data.t == 'O'){    
    turnType = 1;
    serialdata.data.t = 'N';
    return;
  }
  // Let the watch dog reset
  if(serialdata.data.t == 'D'){    
    smoothShift(0,0,FORWARD,FORWARD);
    serialdata.data.t = 'N';
    while(1){}
    return;
  }

  if (serialdata.data.t == 'Z'){
    Serial.println("STOP");
//    smoothShift(/0,0,FORWARD,FORWARD);
//    delay(2000);/
    stopThatDamnVehicle = 15;
    return;
  }

//  if (serialdata.data.t == 'B'){
//    Serial.println("STOP from QR");
////    smoothShift(0,0,FORWARD,FORWARD);
////    delay(2000);
//    stopForBlue = 15;
//    return;
//  }
  
  if(stopForBlue > 10){
    out = 0;
    smoothShift(0,0,FORWARD,FORWARD);
    return;
  }
  if(stopThatDamnVehicle > 10){
    out = 0;   
    smoothShift(0,0, FORWARD, FORWARD);
    //reverseMotion();
    //stopThatDamnVehicle = 0;
    return;
  }
 
//  if(out > 0){
//
//  out = prevAngle;
//  out = filter_recv_value(out);
//
//  smoothShift(pid((baseThrottle+out), l_prev, l_acc), pid((baseThrottle-out), r_prev, r_acc), FORWARD, FORWARD);
////  Serial.println("out is greater than 360");
//  }
//
//  else {            
//    out = filter_recv_value(out);
//    prevAngle = out;
//
//    smoothShift(pid((baseThrottle+out), l_prev, l_acc), pid((baseThrottle-out), r_prev, r_acc), FORWARD, FORWARD);
////    Serial.println("out is lesser than 360");
//  }
  //}
  //debugOutputs();
//  delay(0.1);
  return;
//  }

///-------------------------------------------------------
  
//  if(Serial.available() > 0){
//    char input = Serial.read();
//    if (isAlpha(input)) {
//      receivedChar = input;
//      if (receivedChar == 'Z') {
//        Serial.println("Stop");
//        smoothShift(0, 0, FORWARD, FORWARD);
//        delay(5);
////        smoothShift(baseThrottle, baseThrottle, FORWARD, FORWARD);
//      }
//       
//      if (receivedChar == 'B') {
//        stopForBlue = 15;
//      }
//      
//      if (receivedChar == 'L'){
//        Serial.println("Left");
//        out = 0;
//        turnVehicle(LEFT);
//        serialdata.data.t = 'N';
//        stopThatDamnVehicle = 0;
//        stopForBlue = 0;
//        return;
//      }
//
//      if (receivedChar == 'R'){
//        Serial.println("Right");
//        out = 0;
//        turnVehicle(RIGHT);
//        serialdata.data.t = 'N';
//        stopThatDamnVehicle = 0;
//        stopForBlue = 0;
//        return;
//      }
//
//      if (receivedChar == 'U'){
//        Serial.println("About Turn");
//        out = 0;
//        aboutTurnVehicle();
//        serialdata.data.t = 'N';
//        stopThatDamnVehicle = 0;
//        stopForBlue = 0;
//        return;
//      }
//
//      if (receivedChar == 'F'){
//        serialdata.data.t = 'N';
////        Serial.println("Forward");
////        out = 0;
////        kickStart();
////        aboutTurnVehicle();
////        stopThatDamnVehicle = 0;
////        stopForBlue = 0;
//        return;
//      }
//
//      if (receivedChar == 'P'){
//        Serial.println("Reverse");
//        out = 0;
//        reverseMotion();
//        serialdata.data.t = 'N';
//        stopThatDamnVehicle = 0;
//        stopForBlue = 0;
//        return;
//      }
//
//      if (receivedChar == 'C'){
////        Serial.println("Reverse");
//        out = 0;
//        creepForward();
//        serialdata.data.t = 'N';
//        stopThatDamnVehicle = 0;
//        stopForBlue = 0;
//        return;
//      }
//
//      if (receivedChar == 'O'){
////        Serial.println("Reverse");
//        turnType = 1;
//        serialdata.data.t = 'N';
//        return;
//      }
//
//      if (receivedChar == 'D'){
////        Serial.println("Reverse");
//        smoothShift(0,0,FORWARD,FORWARD);
//        serialdata.data.t = 'N';
//        while(1){}
//        return;
//      }
//
//      if (stopForBlue > 10){
//        out = 0;
//        smoothShift(0,0,FORWARD,FORWARD);
//        return;
//      }
//
//      if (stopThatDamnVehicle > 10){
//        out = 0;   
//        smoothShift(0,0, FORWARD, FORWARD);
//        //reverseMotion();
////        stopThatDamnVehicle = 0;
//        return;
//      }
//    } 
//    else {
//      serialdata.decodeData(serialdata.data);
//      int out = serialdata.data.angle;
//      Serial.println(out);
////      stopThatDamnVehicle = 0;
////      stopForBlue = 0;
//      if(out > 360){
//        out = prevAngle;
//        out = filter_recv_value(out);
//        smoothShift(pid((baseThrottle-out), r_prev, r_acc), pid((baseThrottle+out), l_prev, l_acc), FORWARD, FORWARD);
//      }
//      else {            
//        out = filter_recv_value(out);
//        prevAngle = out;
//        smoothShift(pid((baseThrottle-out), r_prev, r_acc), pid((baseThrottle+out), l_prev, l_acc), FORWARD, FORWARD);
//      }
//    }  
//  }
//  return;
}  

void serialEvent(){
  modeAuto();
}

// --- System Code ---
void setup(){
  Serial.begin(115200);
  wdt_enable(WDTO_4S);    // 4 second watchdog timer
  pinMode(13, OUTPUT);
  pinMode(throttlePin, INPUT);
  pinMode(panPin, INPUT);
  pinMode(reversePin, INPUT);
  pinMode(switchPin, INPUT);
}

void loop(){

  modeAuto();
  
//  serialEvent();
  delay(1);
//  debugsr();

//  wdt_reset();
//  inputSwitch = pulseIn(switchPin, HIGH);
//  modeSwitch = map(inputSwitch, 1010, 2000, -1, 1);
//  modeSwitch = constrain(modeSwitch, -1, 1);
//  digitalWrite(13, LOW);  
//
//  if(modeSwitch >= 0){
//    digitalWrite(13, LOW);
//    noInterrupts();
//    sys_state = MANUAL;
//    modeManual();        
//  }
//  else{
////    digitalWrite(13, LOW);
//    interrupts();
//    sys_state = AUTO;
//    modeAuto();           
//  }  
}


void debugsr(){

  Serial.print("ip throttle: ");
  Serial.print(inputThrottle);

  Serial.print("   ip pan:  ");
  Serial.print(inputPan);
   Serial.print("  op throttle:  ");
  Serial.print(throttle);

  Serial.print("  mot pan: ");
  Serial.print(pan);
  Serial.print("  ip reverse:  ");
    Serial.print(inputRev);
    Serial.print("  op reverse: ");
    Serial.print(reverse);

    Serial.print("  inputSwitch:  ");
    Serial.print(inputSwitch);

    Serial.println("  ");
}
