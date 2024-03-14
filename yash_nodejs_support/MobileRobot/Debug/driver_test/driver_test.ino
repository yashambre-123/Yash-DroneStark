#include <avr/wdt.h>
#include "cytron_driver.h"
#include "SerialData.h"
#include "PID.h"

#define PWM_STEP  1
#define TURN_TIME 250
#define ABOUT_TURN  400
#define BLIND_MOVE  180
#define MIN_STOP  40

#define AUTO  1
#define MANUAL  2
#define EMERG_STOP  -1

#define FORWARD 1
#define REVERSE -1
#define RIGHT 2
#define LEFT  3

#define MAX_TH  35
#define ABS_PAN 0.5*MAX_TH

int throttlePin = 9;    // channel 3
int panPin = 3;         // channel 1
int switchPin = 12;     // channel 5
int reversePin = 11;    // channel 6
int baseThrottle = MAX_TH/2 ;
int prevAngle = 0;
int noLineCount = 0;

/* PID variables */
double kp = 1.5, ki = 0.0, kd = 0.0;
int setpoint = baseThrottle;
int l_acc = 0, l_err = 0, l_prev = 0;
int r_acc = 0, r_err = 0, r_prev = 0;


SerialData serialdata(0);

//extern int dout;
int out = 0;

int dir = FORWARD;
int l_prev_spd = 0;
int r_prev_spd = 0;

int l_set_spd = 0;
int r_set_spd = 0;

int inputThrottle = 0;
int inputPan = 0;

int throttle = 0;
int pan = 0;
int modeSwitch = 0;
int reverseSw = 0;

volatile int sys_state = MANUAL;
volatile int prev_sys_state = sys_state;
int turnType = 0;
CytronMD rightMtr(PWM_DIR, 5, 10);
CytronMD leftMtr(PWM_DIR, 6, 4);

// ultrasonic variables
unsigned int dist_pin = 2;   // The Arduino's the Pin2 connection to US-100 Echo / RX
int em_stop = 0;

void setup() {
  Serial.begin(115200);
  wdt_enable(WDTO_4S);    // 4 second watchdog timer
  //Serial.println("Waking up");
  //motor.begin();
  pinMode(13, OUTPUT);
  pinMode(throttlePin, INPUT);
  pinMode(panPin, INPUT);
  pinMode(switchPin, INPUT);
  pinMode(reversePin, INPUT);

  //ultrasonic pin declaration
  pinMode(dist_pin, INPUT);
  //attachInterrupt(digitalPinToInterrupt(dist_pin), dist_handler_high, RISING);
  //sei();
}

int pid(int spderr, int &prev_val, int &Iterm){
  Iterm += spderr;
  int prev_error = prev_val - setpoint;
  int Dterm = spderr - prev_error;
  int mtr_spd = kp*(spderr) + ki*(Iterm) + kd*(Dterm);
  prev_val = mtr_spd;  

  return mtr_spd;
}

void debugOutputs(){
  Serial.print("Mode switch: ");
  Serial.print(modeSwitch);
  Serial.print(" Reverse switch: ");
  Serial.print(reverseSw);
  Serial.print(" Throttle input: ");
  Serial.print(inputThrottle);
  Serial.print("  Pan input: ");
  Serial.print(inputPan);
  Serial.print("  Mapped throttle: ");
  Serial.print(throttle);
  Serial.print("  Mapped pan: ");
  Serial.print(pan);
  Serial.print("  Left Motor PWM: ");
  Serial.print(l_set_spd);
  Serial.print("  Right Motor PWM: ");
  Serial.print(r_set_spd);
  Serial.print("  Direction: ");
  if(dir == FORWARD){
    Serial.print("FORWARD");
  }
  else if(dir == REVERSE){
    Serial.print("REVERSE");
  }
  Serial.println("");
}

void smoothShift(int l_spd, int r_spd, int l_dir, int r_dir){ 
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
      //Serial.println(reverseSw);
      //if((l_prev_spd < 3) && (r_prev_spd < 3)){
        if(reverseSw < 1700){
          l_dir = FORWARD;
          r_dir = FORWARD;
          //Serial.println(l_dir);
          //Serial.println(r_dir);
        }
        else if(reverseSw > 1700){          
          l_dir = REVERSE;
          r_dir = REVERSE;
          //Serial.println(l_dir);
          //Serial.println(r_dir);
        }
      //}
    }
    else if(sys_state == AUTO){
      dir = FORWARD;
    }

    //motor.set(B, r_prev_spd, dir);
    //motor.set(A, l_prev_spd, dir);
    
    leftMtr.setSpeed(l_prev_spd*l_dir);
    rightMtr.setSpeed(r_prev_spd*r_dir);   

    if((l_prev_spd == l_set_spd) && (r_prev_spd == r_set_spd)){
      break;
    }
  }
  
}

void kickStart(){
  smoothShift(0,0,FORWARD,FORWARD);
  for(int i =0; i < BLIND_MOVE; i++){
      smoothShift(baseThrottle, baseThrottle, FORWARD, FORWARD);
      delay(5);
  }
  Serial.flush();
  return;
}

void creepForward(){
  smoothShift(0,0,FORWARD,FORWARD);
  for(int i =0; i < BLIND_MOVE/5; i++){
      smoothShift(baseThrottle/2, baseThrottle/2, FORWARD, FORWARD);
      delay(5);
  }
  smoothShift(0,0,FORWARD,FORWARD);
  Serial.flush();
  return;
}

void reverseMotion(){
  smoothShift(0,0,FORWARD,FORWARD);
  for(int i =0; i < BLIND_MOVE/2; i++){
      smoothShift(baseThrottle, baseThrottle, REVERSE, REVERSE);
      delay(5);
  }
  Serial.flush();
  smoothShift(0,0,FORWARD,FORWARD);
  return;
}

void turnVehicle(int turn_dir){
  smoothShift(0,0, FORWARD, FORWARD);
  if(turn_dir == LEFT){
       
    for(int i =0; i < TURN_TIME - turnType*(0.3*TURN_TIME); i++){
      smoothShift(turnType*baseThrottle, baseThrottle, REVERSE, FORWARD);
      delay(5);
    }
  }
  if(turn_dir == RIGHT){
    
    for(int i =0; i < TURN_TIME - turnType*(0.3*TURN_TIME); i++){
      smoothShift(baseThrottle, turnType*baseThrottle, FORWARD, REVERSE);
      delay(5);
    }
    //delay(TURN_TIME);
  }
  turnType = 0;
  Serial.flush();
  smoothShift(0,0, FORWARD, FORWARD);
}

void aboutTurnVehicle(){
  smoothShift(0,0,FORWARD,FORWARD);
  for(int i = 0; i < ABOUT_TURN; i++){
    smoothShift(baseThrottle, baseThrottle, REVERSE, FORWARD);
    delay(5);
  }
  Serial.flush();
  smoothShift(0,0,FORWARD,FORWARD);
}

int filter_recv_value(int val){
  val = map(val, -120, 120, -ABS_PAN, ABS_PAN);
  val = constrain(val, -ABS_PAN, ABS_PAN);
  return val;
}

void modeAuto(){
  //Serial.println("In auto loop");
  if(Serial.available() > 0){
    //out = serialdata.decodeData(serialdata.data);
    serialdata.decodeData(serialdata.data);
    out = serialdata.data.angle;
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
    stopThatDamnVehicle = 15;
  }
  
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
 
  if(out > 360){

  out = prevAngle;
  out = filter_recv_value(out);

  smoothShift(pid((baseThrottle+out), l_prev, l_acc), pid((baseThrottle-out), r_prev, r_acc), FORWARD, FORWARD);
//  Serial.println("out is greater than 360");
  }

  else {            
    out = filter_recv_value(out);
    prevAngle = out;

    smoothShift(pid((baseThrottle+out), l_prev, l_acc), pid((baseThrottle-out), r_prev, r_acc), FORWARD, FORWARD);
//    Serial.println("out is lesser than 360");
  }
  //}
  //debugOutputs();
//  delay(0.1);
  return;
}

void modeManual(){  
  stopThatDamnVehicle = 0;
  stopForBlue = 0;
  Serial.flush();

  
  inputThrottle = pulseIn(throttlePin, HIGH);
  inputPan = pulseIn(panPin, HIGH);
        
  //throttle = map(inputThrottle, 1010, 2000, 0, MAX_TH);   // FlySky FS-i6 remote
  throttle = map(inputThrottle, 1175, 1816, 0, MAX_TH);     // FlySky FS-CT6B remote
  throttle = constrain(throttle, 0, MAX_TH);

  //pan = map(inputPan, 2000, 1010, -ABS_PAN, ABS_PAN);     // FlySky FS-i6 remote
  pan = map(inputPan, 1160, 1860, -ABS_PAN, ABS_PAN);       // FlySky FS-CT6B remote
  pan = constrain(pan, -ABS_PAN, ABS_PAN);

  if(inputThrottle == 0) throttle = 0;
  if(inputPan == 0) pan = 0;

  if ((throttle < 3) && (abs(pan) < 3)){
    reverseSw = pulseIn(reversePin, HIGH);
  }
  l_set_spd = throttle + pan;
  r_set_spd = throttle - pan;

  //debugOutputs();
  
  smoothShift(l_set_spd, r_set_spd, FORWARD, FORWARD);
}

void serialEvent(){
  //delay(5);
  modeAuto();
}

void testFunc(){
  turnVehicle(LEFT);
  delay(2400);
  turnVehicle(RIGHT);
  delay(2400);
//  Serial.print("Right mtr spd: ");
//  Serial.print(r);
//  Serial.print("  Left mtr spd: ");
//  Serial.print(l);
//  Serial.print("  Right prev: ");
//  Serial.print(r_prev);
//  Serial.print("  Left prev: ");
//  Serial.print(l_prev);
//  Serial.print("  Right acc: ");
//  Serial.print(r_acc);
//  Serial.print("  Left acc: ");
//  Serial.println(l_acc);
  
}

void loop() {

//  Serial.println("start here");

  modeAuto();
  
//  Serial.println("end here");

//  wdt_reset();
//  modeSwitch = pulseIn(switchPin, HIGH);
////  Serial.println(modeSwitch);
//  em_stop = pulseIn(dist_pin, HIGH); 
//  //debugOutputs(); 
//  if(modeSwitch < 10){
//    //Serial.println("Start the goddamn remote");
//    Serial.flush();
//    noInterrupts();
//    smoothShift(0,0,FORWARD, FORWARD);
//  }
//  else if(modeSwitch > 1400){
//    //Serial.println("In mode manual");
//    digitalWrite(13, LOW);
//    noInterrupts();
//    sys_state = MANUAL;
//   
//    modeManual();        
//  }
//  else{
//    //Serial.println("In mode auto");
//    if(em_stop < 1000){
//      digitalWrite(13, LOW);
//      sys_state = AUTO;
//      interrupts();            
//    }
//    else{
//      noInterrupts();
//      Serial.println("yashambre");
//      smoothShift(0,0, FORWARD, FORWARD);
//      Serial.flush();    
//      digitalWrite(13, HIGH);
//    }
//
//  }  
  
}
