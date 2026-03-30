/*
 * Swimnerd Bluetooth Racing Clock - STM32 Firmware
 * 
 * Hardware:
 *   - STM32F103 (Blue Pill or similar)
 *   - HC-08 Bluetooth module
 *   - 6-digit 7-segment LED display (MAX7219 or TM1637)
 * 
 * Connections:
 *   HC-08 TX  → STM32 PA10 (USART1 RX)
 *   HC-08 RX  → STM32 PA9  (USART1 TX)
 *   HC-08 VCC → 3.3V
 *   HC-08 GND → GND
 *   
 *   Display DIN  → STM32 PA7 (SPI MOSI)
 *   Display CLK  → STM32 PA5 (SPI SCK)
 *   Display CS   → STM32 PA4
 *   Display VCC  → 5V
 *   Display GND  → GND
 * 
 * Protocol:
 *   Receives ASCII time strings from FinishLynx via Bluetooth
 *   Format: "MM:SS.HH\n" or "CLR\n"
 *   Examples:
 *     "01:23.45\n" - Display 01:23.45
 *     "00:05.67\n" - Display 00:05.67
 *     "CLR\n"      - Clear display
 * 
 * Author: Swimnerd
 * License: MIT
 */

#include <SPI.h>

// Display driver - adjust for your hardware
// Uncomment ONE of these based on your display:
// #define USE_MAX7219
#define USE_TM1637

#ifdef USE_MAX7219
  #include <LedControl.h>
  LedControl lc = LedControl(PA7, PA5, PA4, 1); // DIN, CLK, CS, num devices
#endif

#ifdef USE_TM1637
  #include <TM1637Display.h>
  #define CLK_PIN PA5
  #define DIO_PIN PA7
  TM1637Display display(CLK_PIN, DIO_PIN);
#endif

// Bluetooth serial (USART1)
HardwareSerial bluetooth(USART1);

// Display buffer
char displayBuffer[10];
String timeString = "";

void setup() {
  // Initialize Bluetooth serial at 9600 baud
  bluetooth.begin(9600);
  
  // Initialize debug serial (optional - USB)
  Serial.begin(115200);
  Serial.println("Swimnerd Bluetooth Clock");
  Serial.println("Waiting for FinishLynx...");
  
  // Initialize display
  #ifdef USE_MAX7219
    lc.shutdown(0, false);       // Wake up display
    lc.setIntensity(0, 8);       // Set brightness (0-15)
    lc.clearDisplay(0);          // Clear display
  #endif
  
  #ifdef USE_TM1637
    display.setBrightness(0x0f); // Max brightness
    display.clear();
  #endif
  
  // Show "READY" on startup
  showReady();
}

void loop() {
  // Read incoming data from Bluetooth
  while (bluetooth.available()) {
    char c = bluetooth.read();
    
    if (c == '\n') {
      // End of message - process it
      processTimeString(timeString);
      timeString = "";
    } else {
      // Build message
      timeString += c;
    }
  }
}

void processTimeString(String msg) {
  Serial.print("Received: ");
  Serial.println(msg);
  
  // Check for special commands
  if (msg == "CLR") {
    clearDisplay();
    return;
  }
  
  if (msg == "READY") {
    showReady();
    return;
  }
  
  // Parse time string: "MM:SS.HH"
  // Example: "01:23.45"
  if (msg.length() >= 8) {
    int mm = msg.substring(0, 2).toInt();
    int ss = msg.substring(3, 5).toInt();
    int hh = msg.substring(6, 8).toInt();
    
    displayTime(mm, ss, hh);
  }
}

void displayTime(int minutes, int seconds, int hundredths) {
  #ifdef USE_MAX7219
    // Display on MAX7219 (6 digits, right-to-left)
    lc.setDigit(0, 0, hundredths % 10, false);        // Digit 0: hundredths ones
    lc.setDigit(0, 1, hundredths / 10, true);         // Digit 1: hundredths tens (with decimal point)
    lc.setDigit(0, 2, seconds % 10, false);           // Digit 2: seconds ones
    lc.setDigit(0, 3, seconds / 10, true);            // Digit 3: seconds tens (with colon)
    lc.setDigit(0, 4, minutes % 10, false);           // Digit 4: minutes ones
    lc.setDigit(0, 5, minutes / 10, false);           // Digit 5: minutes tens
  #endif
  
  #ifdef USE_TM1637
    // Display on TM1637 (4 or 6 digit module)
    // Format: MM:SS for 4-digit, MM:SS.HH for 6-digit
    
    // For 4-digit display (show MM:SS only):
    uint8_t data[] = {
      display.encodeDigit(minutes / 10),
      display.encodeDigit(minutes % 10),
      display.encodeDigit(seconds / 10),
      display.encodeDigit(seconds % 10)
    };
    data[1] |= 0x80; // Add colon between MM and SS
    display.setSegments(data);
    
    // For 6-digit display, you'd add hundredths:
    // (Requires TM1637 library that supports 6 digits)
  #endif
  
  Serial.print("Display: ");
  Serial.print(minutes);
  Serial.print(":");
  if (seconds < 10) Serial.print("0");
  Serial.print(seconds);
  Serial.print(".");
  if (hundredths < 10) Serial.print("0");
  Serial.println(hundredths);
}

void clearDisplay() {
  #ifdef USE_MAX7219
    lc.clearDisplay(0);
  #endif
  
  #ifdef USE_TM1637
    display.clear();
  #endif
  
  Serial.println("Display cleared");
}

void showReady() {
  #ifdef USE_MAX7219
    // Show "READY" pattern (or just clear with some segments)
    lc.setChar(0, 5, 'r', false);
    lc.setChar(0, 4, 'E', false);
    lc.setChar(0, 3, 'A', false);
    lc.setChar(0, 2, 'd', false);
    lc.setChar(0, 1, 'y', false);
    lc.setChar(0, 0, ' ', false);
  #endif
  
  #ifdef USE_TM1637
    // Show "00:00" as ready state
    uint8_t data[] = {0x3f, 0x3f, 0x3f, 0x3f}; // All zeros
    data[1] |= 0x80; // Add colon
    display.setSegments(data);
  #endif
  
  Serial.println("Display: READY");
}
