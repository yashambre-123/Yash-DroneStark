#include "SerialData.h"
#include "cytron_driver.h"

const char startL = "S";
const char endL = "E";
int stopThatDamnVehicle = 0;
int stopForBlue = 0;

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

  else if(marker == 'L'){   // turn Left
    data.t = marker;
    ack = 'R';
    Serial.write(ack);
  }

  else if(marker == 'R'){
    data.t = marker;
    ack = 'R';
    Serial.write(ack);
  }

  else if(marker == 'U'){    // U turn
    data.t = marker;
    ack = 'R';
    Serial.write(ack);
  }

  else if(marker == 'F'){
    data.t = marker;
    ack = 'R';
    Serial.write(ack);
  }
  else if(marker == 'P'){     // reverse
    data.t = marker;
    ack = 'R';
    Serial.write(ack);
  }
  else if(marker == 'C'){     // creep forward
    data.t = marker;
    ack = 'R';
    Serial.write(ack);
  }
  else if(marker == 'W'){     // wait when blue
    //data.t = marker;
    ack = 'R';
    Serial.write(ack);
    stopForBlue += 1;
  }
  else if(marker == 'S'){     // clear wait for blue
    //data.t = marker;
    ack = 'R';
    Serial.write(ack);
    stopForBlue = 0;
  }
  else if(marker == 'O'){     // for on-spot turn
    data.t = marker;
    ack = 'R';
    Serial.write(ack);
  }
  else if(marker == 'Y'){     // clear stop no line
    data.mode = AUTO;    
    ack = 'R';
    Serial.write(ack);
    stopThatDamnVehicle = 0;
  }
  else if(marker == 'Z'){     // stop when no line
    data.mode = USER;
    ack = 'R';
    stopThatDamnVehicle += 1;
  }
  else if(marker == 'D'){
    data.t = marker;
    ack = 'R';
    Serial.write(ack);
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
