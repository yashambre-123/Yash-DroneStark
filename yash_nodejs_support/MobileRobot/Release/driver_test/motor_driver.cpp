#include "motor_driver.h"

MOTOR_CLASS motor;

/** constructor, do nothing, resevered for future*/
MOTOR_CLASS::MOTOR_CLASS()
{

}

/**
	@brief  Initialize function for 50A-DulaChannelMotorDriver.
            Set Timer0, Timer1, Timer2 clock to F_CPU/8.
            Cotrol port initialize.
	@param NONE
	@note   motor.begin() will change the prescaller of the timer0,
            so the arduino function delay() millis() and micros() are
            8 times slow than it should be. Use motor_delay(), motor_millis(),
            motor_micros() instead.
*/
void MOTOR_CLASS::begin(void)
{
    pinMode(A_EN, OUTPUT);
    pinMode(A_DIS, OUTPUT);
    pinMode(B_EN, OUTPUT);
    pinMode(B_DIS, OUTPUT);

    digitalWrite(A_DIS, LOW);
    digitalWrite(B_DIS, LOW);
    digitalWrite(A_EN, HIGH);
    digitalWrite(B_EN, HIGH);

    /** PWM pin configurate */
    pinMode(A_RPWM, OUTPUT);
    pinMode(A_LPWM, OUTPUT);
    pinMode(B_RPWM, OUTPUT);
    pinMode(B_LPWM, OUTPUT);

    digitalWrite(A_RPWM, HIGH);
    digitalWrite(A_LPWM, HIGH);
    digitalWrite(B_RPWM, HIGH);
    digitalWrite(B_LPWM, HIGH);
#ifdef MOTOR_V1
    /** Timer0 fast PWM 8-bit, CLKio/8 */
    TCCR0A = 0;
    TCCR0B = 0;
    sbi(TCCR0A, WGM01);
    sbi(TCCR0A, WGM00);
    sbi(TCCR0B, CS01);
#endif
    /** Timer1 PWM phase correct 8-bit, CLKio/8 */
    TCCR1A = 0;
    TCCR1B = 0;
    TCCR1C = 0;
    sbi(TCCR1A, WGM10);
    sbi(TCCR1A, WGM10);
    sbi(TCCR1B, CS11);

    /** Timer2 PWM phase correct 8-bit, CLKio/8 */
    TCCR2A = 0;
    TCCR2B = 0;
    sbi(TCCR2A, WGM20);
    sbi(TCCR2B, CS21);

    /** disable timer0 overflow interrupt, FOR TEST */
//	cbi(TIMSK0, TOIE0);
}

/**
	@brief motor control function
	@param ch --> channel to be set, the value must be A or B.
		   speed --> speed level to be set, the value can be 0~255
                     0: slowest, 255:fastest.
		   dir --> rotate direction of the motor, the value must
                    be FORWARD or REVERSE
*/
void MOTOR_CLASS::set(motor_ch_type ch, u8 speed, motor_direction_type dir)
{
    /** change to fit user */
    speed = ~speed;
#ifdef MOTRO_V1
    if(ch == A){
        if(dir == FORWARD){
            OCR2B = speed;
            A_RPWM_ON();
            A_LPWM_OFF();
            digitalWrite(A_LPWM, HIGH);
        }else{
            OCR0B = speed;
            A_LPWM_ON();
            A_RPWM_OFF();
            digitalWrite(A_RPWM, HIGH);
        }
    }else if(ch == B){
        if(dir == FORWARD){
            OCR1A = speed;
            B_RPWM_ON();
            B_LPWM_OFF();
            digitalWrite(B_LPWM, HIGH);
        }else{
            OCR0A = speed;
            B_LPWM_ON();
            B_RPWM_OFF();
            digitalWrite(B_RPWM, HIGH);
        }
    }
#else
	if(ch == A){
        if(dir == FORWARD){
            OCR2B = speed;
            A_RPWM_ON();
            A_LPWM_OFF();
            digitalWrite(A_LPWM, HIGH);
        }else{
            OCR2A = speed;
            A_LPWM_ON();
            A_RPWM_OFF();
            digitalWrite(A_RPWM, HIGH);
        }
    }else if(ch == B){
        if(dir == FORWARD){
            OCR1A = speed;
            B_RPWM_ON();
            B_LPWM_OFF();
            digitalWrite(B_LPWM, HIGH);
        }else{
            OCR1B = speed;
            B_LPWM_ON();
            B_RPWM_OFF();
            digitalWrite(B_RPWM, HIGH);
        }
    }
#endif
}

/**
	@brief close motor
	@param ch --> channel to close, the value must be A or B.
*/
void MOTOR_CLASS::close(motor_ch_type ch)
{
    if(ch == A){
        A_LPWM_OFF();
        A_RPWM_OFF();
        digitalWrite(A_LPWM, HIGH);
        digitalWrite(A_RPWM, HIGH);
    }else if(ch == B){
        B_LPWM_OFF();
        B_RPWM_OFF();
        digitalWrite(B_LPWM, HIGH);
        digitalWrite(B_RPWM, HIGH);
    }
}

/**
    both the two varibles below are in Arduino wiring.c,
    used in timer0 interrupt routine.
*/
extern volatile unsigned long timer0_overflow_count;
extern volatile unsigned long timer0_millis;

#ifdef MOTOR_V1

/**
    rewrite Arduino millis()
*/
unsigned long motor_millis()
{
	unsigned long m;
	uint8_t oldSREG = SREG;

	// disable interrupts while we read timer0_millis or we might get an
	// inconsistent value (e.g. in the middle of a write to timer0_millis)
	cli();
	m = timer0_millis/MOTOR_CLK_PRESCALER;
	SREG = oldSREG;

	return m;
}

/**
    rewrite Arduino micros()
*/
unsigned long motor_micros() {
	unsigned long m;
	uint8_t oldSREG = SREG, t;

	cli();
	m = timer0_overflow_count;
#if defined(TCNT0)
	t = TCNT0;
#elif defined(TCNT0L)
	t = TCNT0L;
#else
	#error TIMER 0 not defined
#endif


#ifdef TIFR0
	if ((TIFR0 & _BV(TOV0)) && (t < 255))
		m++;
#else
	if ((TIFR & _BV(TOV0)) && (t < 255))
		m++;
#endif

	SREG = oldSREG;

	return ((m << 8) + t) * (64 / clockCyclesPerMicrosecond()) / MOTOR_CLK_PRESCALER;
}

/**
    rewrite Arduino delay()
*/
void motor_delay(unsigned long ms)
{
	uint16_t start = (uint16_t)motor_micros();

	while (ms > 0) {
		if (((uint16_t)motor_micros() - start) >= 1000) {
			ms--;
			start += 1000;
		}
	}
}
#endif
