#include <TimerOne.h>

#define DIST_LIM  30
#define NO_OF_AVG 10

// ultrasonic variables
unsigned int EchoPin = 2;  // RX
unsigned int TrigPin = 7;  // TX
unsigned long Time_Echo_us = 0; 
unsigned long Len_cm  = 0;
int outPin = 3;
unsigned long avg_dist = 0;
int loop_cnt = 0;

void setup() {
  Serial.begin(115200);
  // put your setup code here, to run once:
    //ultrasonic pin declaration
  pinMode(EchoPin, INPUT);    //  The set EchoPin input mode.
  pinMode(TrigPin, OUTPUT);   //  The set TrigPin output mode.  
  pinMode(outPin, OUTPUT);
  pinMode(13, OUTPUT);
  //sei();

}

unsigned long obstacle_detection(){
  digitalWrite(TrigPin, HIGH);                         // Send pulses begin by Trig / Pin
  delayMicroseconds(50);                               // Set the pulse width of 50us (> 10us)
  digitalWrite(TrigPin, LOW);                          // The end of the pulse    
  Time_Echo_us = pulseIn(EchoPin, HIGH);               // A pulse width calculating US-100 returned  
  if((Time_Echo_us < 60000) && (Time_Echo_us > 1)) {   // Pulse effective range (1, 60000).
    Len_cm = (Time_Echo_us*34/100)/2/10;                   // Calculating the distance by a pulse width.     
    //Serial.println(Len_cm); 
    Len_cm = constrain(Len_cm, 3, 100);
    return Len_cm; 
  }
  else {
    return 100;
  }
}



void loop() {
  // put your main code here, to run repeatedly:
  while(loop_cnt < NO_OF_AVG){
    avg_dist += obstacle_detection();
    loop_cnt++;
  }
  avg_dist /= NO_OF_AVG;
  if(avg_dist < DIST_LIM){
    //digitalWrite(outPin, HIGH);
    analogWrite(outPin, 250);   
    digitalWrite(13, HIGH); 
  }
  else{
    //digitalWrite(outPin, LOW);
    analogWrite(outPin, 10);
    digitalWrite(13, LOW);
  }
  Serial.println(avg_dist);
  loop_cnt = 0;
  avg_dist = 0;
  //obstacle_detection();

}
