#ifndef __MOTOR_H
#define __MOTOR_H

#if defined(ARDUINO) && ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif
#include "wiring_private.h"

#ifndef __TYPE_REDEFINE
#define __TYPE_REDEFINE
typedef uint8_t u8;
typedef int8_t  s8;
//typedef uint16_t u16;
typedef int16_t  s16;
typedef uint32_t u32;
typedef int32_t  s32;
#endif

//#define MOTOR_V1
#define MOTOR_V2

#ifdef MOTOR_V1
#define A_EN                2
#define A_RPWM              3    //OC2B
#define A_DIS               4
#define A_LPWM              5    //OC0B

#define B_EN                8
#define B_RPWM              9    //OC1A
#define B_DIS               7
#define B_LPWM              6    //OC0A

#define A_RPWM_ON()         sbi(TCCR2A, COM2B1);
#define A_RPWM_OFF()        cbi(TCCR2A, COM2B1);
#define A_LPWM_ON()         sbi(TCCR0A, COM0B1);
#define A_LPWM_OFF()        cbi(TCCR0A, COM0B1);

#define B_RPWM_ON()         sbi(TCCR1A, COM1A1);
#define B_RPWM_OFF()        cbi(TCCR1A, COM1A1);
#define B_LPWM_ON()         sbi(TCCR0A, COM0A1);
#define B_LPWM_OFF()        cbi(TCCR0A, COM0A1);

#define MOTOR_CLK_PRESCALER 8

#elif defined MOTOR_V2

#define A_EN                2
#define A_RPWM              3    //OC2B
#define A_DIS               4
#define A_LPWM              11    //OC2A

#define B_EN                8
#define B_RPWM              9    //OC1A
#define B_DIS               7
#define B_LPWM              10    //OC1B

#define A_RPWM_ON()         sbi(TCCR2A, COM2B1);
#define A_RPWM_OFF()        cbi(TCCR2A, COM2B1);
#define A_LPWM_ON()         sbi(TCCR2A, COM2A1);
#define A_LPWM_OFF()        cbi(TCCR2A, COM2A1);

#define B_RPWM_ON()         sbi(TCCR1A, COM1A1);
#define B_RPWM_OFF()        cbi(TCCR1A, COM1A1);
#define B_LPWM_ON()         sbi(TCCR1A, COM1B1);
#define B_LPWM_OFF()        cbi(TCCR1A, COM1B1);

#define MOTOR_CLK_PRESCALER 8
#else
 #error("Motor version undefined.");
#endif


typedef enum{
    A=0,
    B=1,
}motor_ch_type;
typedef enum{
    FORWARD,
    REVERSE,
}motor_direction_type;

class MOTOR_CLASS{
public:
    MOTOR_CLASS(void);
    void begin(void);
    void set(motor_ch_type ch, u8 speed, motor_direction_type dir);
    void close(motor_ch_type ch);
private:
    void close_pwm(motor_ch_type ch);
};

extern MOTOR_CLASS motor;

#ifdef MOTOR_V1
unsigned long motor_micros();
unsigned long motor_millis();
void motor_delay(unsigned long ms);
#elif defined MOTOR_V2
#define motor_micros()		micros()
#define motor_millis()		millis()
#define motor_delay(x)		delay(x)
#endif

#endif
