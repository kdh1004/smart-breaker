#include <Servo.h>
#include <StaticThreadController.h>
#include <Thread.h>
#include <ThreadController.h>
#include <LiquidCrystal_I2C.h>

const int motorPin = 9;
const int buzzerPin = 8; 
const int switchPin = 6;

LiquidCrystal_I2C lcd(0x27, 16, 2);

ThreadController controller;
Thread runMotorThread;

Servo motor;

unsigned long melodyStartTime = 0;
const unsigned long melodyDuration = 500;

void playMelody(const char* melody) {
melodyStartTime = millis();

for (int i = 0; melody[i] != '\0'; ++i) {
switch (melody[i]) {
case 'd':
tone(buzzerPin, 261);
delay(500);
noTone(buzzerPin);
break;
case 'm':
tone(buzzerPin, 329);
delay(500);
noTone(buzzerPin);
break;
case 's':
tone(buzzerPin, 392); 
delay(500);
noTone(buzzerPin);
break;
case 'f':
tone(buzzerPin, 523);
delay(500);
noTone(buzzerPin);
break;
case '0':
noTone(buzzerPin);
break;
}
}
}

void setup() {
Serial.begin(9600);
motor.attach(motorPin);
playMelody("dmsf0");
runMotorThread.enabled = false;
runMotorThread.onRun(runMotor);
controller.add(&runMotorThread);
lcd.init();
lcd.backlight();
lcd.clear();
lcd.setCursor(3,0);
lcd.print("CONNECTED");
pinMode(switchPin, INPUT_PULLUP);
}

void runMotor() {
motor.write(90);
delay(1000);
}

bool isMelodyPlayed = false;

void loop() {
if (Serial.available() > 0) {
char command = Serial.read();


if (command == '0' && !isMelodyPlayed) {
  runMotorThread.enabled = true;
  playMelody("dms0"); 
  isMelodyPlayed = true;
  lcd.clear();
  lcd.setCursor(5,0);
  lcd.print("UNLOCK");
} else if (command == 'f') {
  motor.write(0);
  runMotorThread.enabled = false;
  playMelody("smd0");
  isMelodyPlayed = false;
  lcd.clear();
  lcd.setCursor(6,0);
  lcd.print("LOCK");
}
}

if (digitalRead(switchPin) == LOW && !isMelodyPlayed) {
if (runMotorThread.enabled) {
playMelody("s");
isMelodyPlayed = true;

  Serial.println("EMERGENCY");
  lcd.setCursor(3, 1);
  lcd.print("EMERGENCY");
}
else {
  playMelody("s");
  
  Serial.println("EMERGENCY");
  lcd.setCursor(3, 1);
  lcd.print("EMERGENCY");
}
}

if (isMelodyPlayed && (millis() - melodyStartTime >= melodyDuration)) {
isMelodyPlayed = false;
}
controller.run();
}

Get the event loop and run the main coroutine.
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
