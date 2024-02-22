#ifndef SERIAL_DATA_H
#define SERIAL_DATA_H

#ifdef ARDUINO
        #if ARDUINO < 100
        #include "WProgram.h"
    #else
        #include "Arduino.h"
    #endif
#endif

#define SUCCESS	1
#define FAILURE 0

extern int stopThatDamnVehicle; 
extern int stopForBlue;

enum SYSMODE {AUTO=0, 
               USER,
               REBOOT
               };
class SerialData{  
  private:
    
    typedef struct Data_s{
      uint8_t mode = USER;
      volatile int angle = 0;
      volatile char t = 'N';
      int thr = 0;
      int pan = 0;
    }Data;
    
  public:
    Data data;
    SerialData(int a1);
    ~SerialData();
    int decodeData(Data &data);
    char readAngle(Data &data);
    char readManual(Data &data);
};


    
#endif
