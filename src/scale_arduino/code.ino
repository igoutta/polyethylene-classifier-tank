#include <LCD-I2C.h>
#include <HX711_ADC.h>

LCD_I2C lcd(0x27, 16, 2); // Default address of most PCF8574 modules, change according

//pins:
const int HX711_dout = 3; //mcu > HX711 dout pin, must be external interrupt capable
const int HX711_sck = 5; //mcu > HX711 sck pin

//HX711 constructor:
HX711_ADC LoadCell(HX711_dout, HX711_sck);

const int calVal_eepromAdress = 0;
unsigned long t = 0;
volatile boolean newDataReady;

void setup() {
  lcd.begin();
  lcd.display();
  lcd.backlight();

  Serial.begin(115200);
  delay(10);
  Serial.println();
  Serial.println("Starting...");

  float calibrationValue; // calibration value (see example file "Calibration.ino")
  calibrationValue = 696.0; // uncomment this if you want to set the calibration value in the sketch
  //EEPROM.get(calVal_eepromAdress, calibrationValue); // uncomment this if you want to fetch the calibration value from eeprom

  LoadCell.begin();
  //LoadCell.setReverseOutput();
  unsigned long stabilizingtime = 2000; // tare preciscion can be improved by adding a few seconds of stabilizing time
  boolean _tare = true; //set this to false if you don't want tare to be performed in the next step
  LoadCell.start(stabilizingtime, _tare);
  if (LoadCell.getTareTimeoutFlag()) {
    Serial.println("Timeout, check MCU>HX711 wiring and pin designations");
    while (1);
  }
  else {
    LoadCell.setCalFactor(calibrationValue); // set calibration value (float)
    Serial.println("Startup is complete");
  }

  attachInterrupt(digitalPinToInterrupt(HX711_dout), dataReadyISR, FALLING);
}

//interrupt routine:
void dataReadyISR() {
  if (LoadCell.update()) {
    newDataReady = 1;
  }
}

void loop() {
  const int serialPrintInterval = 10; //increase value to slow down serial print activity

  // get smoothed value from the dataset:
  if (newDataReady) {
    if (millis() > t + serialPrintInterval) {
      float i = LoadCell.getData();
      newDataReady = 0;

      Serial.print("Load_cell output val: ");
      Serial.println(i);
      //LCD Print
      lcd.clear(); // Clears the display 
      lcd.setCursor(0,0);  // set the cursor to column 0, line 0
      lcd.print("Peso(g): ");
      String s = String(int(i));
      lcd.setCursor(15 - s.length(),1);  // set the cursor to column 0, line 0
      lcd.print(s);

      delay(500);
      t = millis();
    }
  }
}