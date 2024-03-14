//this is correct one

#include "cytron_driver.h" 
#include "SerialData.h" 
#include "PID.h"

#define PWM_STEP  1
#define TURN_TIME 250
#define MIN_STOP  40 

#define AUTO  1
#define MANUAL 0
#define EMERG_STOP  -1

#define FORWARD 1
#define REVERSE 1
#define RIGHT 1
#define LEFT  -1

#define MAX_TH  50 
#define ABS_PAN 0.5*MAX_TH 

int throttlePin = 9;    //channel 3  
int panPin = 3;         //channel 1  
int reversePin = 11;    //channel 8
int switchPin = 12;     //chennel 6
int baseThrottle = MAX_TH/2 ;
int prevAngle = 0;
int noLineCount = 0; 
int led = 13;

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
    }else{
      dir = FORWARD;
    }
   
    leftMtr.setSpeed(2*l_prev_spd*l_dir);
    rightMtr.setSpeed(2*r_prev_spd*r_dir); 

    if((l_prev_spd == l_set_spd) && (r_prev_spd == r_set_spd)){
      break;
    }
  }
  
}

void turnVehicle(int turn_dir){
  smoothShift(0,0, FORWARD, FORWARD);
  if(turn_dir == LEFT){ 
    for(int i =0; i < TURN_TIME; i++){
      smoothShift(0, baseThrottle, REVERSE, FORWARD);
      delay(5);
    }
  }
  if(turn_dir == RIGHT){
    //smoothShift(baseThrottle, baseThrottle, FORWARD, REVERSE);
    for(int i =0; i < TURN_TIME; i++){
      smoothShift(baseThrottle, 0, FORWARD, REVERSE);
      delay(5);
    }
  }
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
  stopThatDamnVehicle = 0;
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
  for(int i =0; i < 180; i++){
      smoothShift(baseThrottle, baseThrottle, FORWARD, FORWARD);
      delay(5);
  }
  Serial.flush();
  return;
}

void reverseMotion(){
  smoothShift(0,0,FORWARD,FORWARD);
  for(int i =0; i < 180; i++){
      smoothShift(baseThrottle, baseThrottle, REVERSE, REVERSE);
      delay(5);
  }
  Serial.flush();
  return;
}

void modeAuto(){
  if(Serial.available() > 0){
    char input = Serial.read();
    if (isAlpha(input)) {
      receivedChar = input;
      if (receivedChar == 'Z') {
        smoothShift(0, 0, FORWARD, FORWARD);
        delay(5);
        smoothShift(baseThrottle, baseThrottle, FORWARD, FORWARD);
        } 
      else if (receivedChar == 'B') {
        smoothShift(0, 0, FORWARD, FORWARD);
      }
    } 
    else {
      serialdata.decodeData(serialdata.data);
      int out = serialdata.data.angle;
      if(out > 360){
        out = prevAngle;
        out = filter_recv_value(out);
        smoothShift(pid((baseThrottle-out), r_prev, r_acc), pid((baseThrottle+out), l_prev, l_acc), FORWARD, FORWARD); 
      }
      else {            
        out = filter_recv_value(out);
        prevAngle = out;
        smoothShift(pid((baseThrottle-out), r_prev, r_acc), pid((baseThrottle+out), l_prev, l_acc), FORWARD, FORWARD);
      }
    }  
  }
  return;
}  

void serialEvent(){
  modeAuto();
}

// --- System Code ---
void setup(){
  Serial.begin(115200);
  pinMode(13, OUTPUT);
  pinMode(throttlePin, INPUT);
  pinMode(panPin, INPUT);
  pinMode(reversePin, INPUT);
  pinMode(switchPin, INPUT);
}

void loop(){
  delay(1);
  debugsr();

  inputSwitch = pulseIn(switchPin, HIGH);
  modeSwitch = map(inputSwitch, 1010, 2000, -1, 1);
  modeSwitch = constrain(modeSwitch, -1, 1);
  digitalWrite(13, LOW);  

  if(modeSwitch >= 0){
    digitalWrite(13, LOW);
    noInterrupts();
    sys_state = MANUAL;
    modeManual();        
  }
  else{
    digitalWrite(13, LOW);
    sys_state = AUTO;
    interrupts();            
  }  
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
