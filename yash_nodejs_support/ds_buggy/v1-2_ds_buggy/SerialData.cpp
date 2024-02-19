#include "SerialData.h"
#include "cytron_driver.h"

const char startL = "S";
const char endL = "E";
int stopThatDamnVehicle = 0;

SerialData::SerialData(int a1){
  this->data.angle = a1;
}

SerialData::~SerialData(){}

int SerialData::decodeData(Data &data){
  char marker = Serial.read();
  
  char ack = 'N';
  
  if (marker == 'A'){    
    data.mode = AUTO;    
    //Serial.println("received T");
    byte buf[sizeof(data.angle)];
    int count = 0;
    //digitalWrite(13, HIGH);
    if(Serial.available() > 0){
      while(count <= sizeof(data.angle)-1){
        buf[count] = Serial.read();
        count++;
      }
    }
    memmove(&data.angle, buf, sizeof(data.angle));
    ack = 'R';
    //Serial.write(ack);
    //Serial.write((const uint8_t*)&data.angle, sizeof(data.angle));
    return data.angle;
  }

  
//  else if(marker == 'T'){   
////    Serial.println("received A");
//    data.mode = AUTO;
//    ack = 'R';
//    Serial.write(ack);
//  }
//  else if(marker == 'D'){   
//    //Serial.println("Received M");
//    data.mode = USER;
//    Serial.write(ack);
//  }


  else if(marker == 'M'){
    data.mode = USER;
    byte buf[sizeof(data.thr)];
    int count = 0;
    //digitalWrite(13, HIGH);
    if(Serial.available() > 0){
      while(count <= sizeof(data.thr)-1){
        buf[count] = Serial.read();
        count++;
      }
    }
    memmove(&data.thr, buf, sizeof(data.thr));
    
    byte buf2[sizeof(data.pan)];
    count = 0;
    //digitalWrite(13, HIGH);
    if(Serial.available() > 0){
      while(count <= sizeof(data.pan)-1){
        buf[count] = Serial.read();
        count++;
      }
    }
    memmove(&data.pan, buf2, sizeof(data.pan));
    ack = 'R';
    Serial.write(ack);
    Serial.write((const uint8_t*)&data.pan, sizeof(data.pan));
  }

  else if(marker == 'L'){
    data.t = marker;
    ack = 'R';
    Serial.write(ack);
  }

  else if(marker == 'R'){
    data.t = marker;
    ack = 'R';
    Serial.write(ack);
  }

  else if(marker == 'U'){
    data.t = marker;
    ack = 'R';
    Serial.write(ack);
  }

  else if(marker == 'F'){
    data.t = marker;
    ack = 'R';
    Serial.write(ack);
  }
  
  else if(marker == 'Z'){
    data.mode = USER;
    ack = 'R';
    //Serial.write(ack);
    //Serial.write('Z');
    stopThatDamnVehicle += 1;
    //motor.close(A);
    //motor.close(B);
  }
  return;
}

char SerialData::readManual(Data &data){
  int recv = Serial.read();
  memmove(&data.thr, recv, sizeof(data.thr));
  recv = Serial.read();
  memmove(&data.pan, recv, sizeof(data.pan));

  return 'R';
}

char SerialData::readAngle(Data &data){
  char ret = 'N';
  byte buf[sizeof(data.angle)];
//Serial.println(sizeof(data.angle));
  int count = 0;
  if(Serial.available() > 0){
    while(count <= sizeof(data.angle)-1){
      buf[count] = Serial.read();
      count++;
    }
  }
  memmove(&data.angle, buf, sizeof(data.angle));
  return ret;
}
