# Swimnerd Bluetooth Racing Clock - Complete Build Guide

## Hardware Components

### Required Parts

| Component | Quantity | Notes |
|-----------|----------|-------|
| STM32F103C8T6 (Blue Pill) | 1 | Main microcontroller |
| HC-08 Bluetooth Module | 1 | Bluetooth 4.0 serial module |
| 6-Digit 7-Segment Display | 1 | MAX7219 or TM1637 driver |
| 5V Power Supply | 1 | 1A minimum |
| Wires & Breadboard | - | For prototyping |
| Enclosure (optional) | 1 | 3D printed or plastic box |

### Alternative Components

- **STM32:** Any STM32 (F103, F401, etc.) or Arduino (Uno, Nano, Mega)
- **Bluetooth:** HC-05, HC-06, HC-08, or BLE modules
- **Display:** MAX7219, TM1637, or individual 7-segment displays

---

## Step 1: HC-08 Bluetooth Module Setup

### HC-08 Pin Connections

```
HC-08        STM32F103
------       ----------
VCC    →     3.3V
GND    →     GND
TXD    →     PA10 (USART1 RX)
RXD    →     PA9  (USART1 TX)
```

**⚠️ Important:** HC-08 is 3.3V logic. Do NOT connect to 5V!

### HC-08 Configuration (AT Commands)

Before using the HC-08, you may need to configure it:

**Default settings:**
- Name: `HC-08`
- Baud Rate: `9600`
- PIN: `1234`

**To change settings (optional):**

1. Connect HC-08 to USB-to-Serial adapter
2. Open serial terminal (PuTTY, Arduino Serial Monitor, etc.)
3. Set baud rate to `9600`
4. Send AT commands:

```
AT                    // Test connection (should reply "OK")
AT+NAME=SWIMNERD      // Set device name
AT+BAUD4              // Set baud to 9600 (4 = 9600)
AT+PIN1234            // Set pairing PIN
```

**HC-08 AT Command Reference:**

| Command | Description |
|---------|-------------|
| `AT` | Test (reply: OK) |
| `AT+NAME?` | Query name |
| `AT+NAME=xxx` | Set name |
| `AT+BAUD?` | Query baud rate |
| `AT+BAUD4` | Set 9600 baud |
| `AT+PIN?` | Query PIN |
| `AT+PIN1234` | Set PIN |
| `AT+RESET` | Reset module |

---

## Step 2: Display Wiring

### Option A: MAX7219 7-Segment Display

```
MAX7219      STM32F103
--------     ----------
VCC    →     5V
GND    →     GND
DIN    →     PA7 (SPI MOSI)
CLK    →     PA5 (SPI SCK)
CS     →     PA4
```

**Library:** `LedControl` (install via Arduino Library Manager)

### Option B: TM1637 6-Digit Display

```
TM1637       STM32F103
-------      ----------
VCC    →     5V
GND    →     GND
CLK    →     PA5
DIO    →     PA7
```

**Library:** `TM1637Display` (install via Arduino Library Manager)

### Option C: Individual 7-Segment Displays

Use GPIO pins to drive segments directly (requires more pins and resistors).

---

## Step 3: STM32 Firmware Upload

### Install Arduino IDE Support for STM32

1. **Install Arduino IDE** (1.8.x or 2.x)

2. **Add STM32 Boards:**
   - Arduino → Preferences → Additional Boards Manager URLs:
   ```
   https://github.com/stm32duino/BoardManagerFiles/raw/main/package_stmicroelectronics_index.json
   ```
   - Tools → Board → Boards Manager → Install "STM32 MCU based boards"

3. **Select Board:**
   - Tools → Board → STM32 → Generic STM32F1 series
   - Tools → Board part number → BluePill F103C8

4. **Select Upload Method:**
   - Tools → Upload method → STLink (recommended) or Serial/UART

### Upload Firmware

1. Open `stm32_bluetooth_clock.ino` in Arduino IDE

2. **Select display type** (edit code):
   ```cpp
   // Uncomment ONE:
   // #define USE_MAX7219
   #define USE_TM1637
   ```

3. **Install required libraries:**
   - Sketch → Include Library → Manage Libraries
   - Search and install:
     - `LedControl` (for MAX7219)
     - `TM1637Display` (for TM1637)

4. **Compile and upload:**
   - Click **Upload** button
   - Wait for "Done uploading"

5. **Test via Serial Monitor:**
   - Tools → Serial Monitor → Set to `115200` baud
   - You should see: `Swimnerd Bluetooth Clock`

---

## Step 4: Bluetooth Pairing

### Windows

1. **Open Settings → Devices → Bluetooth & other devices**
2. Click **Add Bluetooth or other device**
3. Select **Bluetooth**
4. Wait for `HC-08` (or `SWIMNERD`) to appear
5. Click it and enter PIN: `1234`
6. Windows will assign a COM port (e.g., `COM5`)

**Find the COM port:**
- Device Manager → Ports (COM & LPT)
- Look for "Standard Serial over Bluetooth link (COM5)"
- **Remember this COM port number!**

### macOS

1. **System Preferences → Bluetooth**
2. Wait for `HC-08` to appear
3. Click **Pair**
4. Enter PIN: `1234`
5. macOS will create a device at `/dev/cu.HC-08-DevB`

**Find the device:**
```bash
ls /dev/cu.*
# Look for /dev/cu.HC-08-DevB or similar
```

### Linux

```bash
# Scan for devices
bluetoothctl
scan on

# Pair (replace MAC with your HC-08 address)
pair XX:XX:XX:XX:XX:XX
1234

# Connect
connect XX:XX:XX:XX:XX:XX

# Bind to serial port
sudo rfcomm bind /dev/rfcomm0 XX:XX:XX:XX:XX:XX
```

---

## Step 5: FinishLynx Configuration

### Add Bluetooth Scoreboard

1. **Open FinishLynx**

2. **File → Options → Hardware → Scoreboard**

3. **Click "Add" to create new scoreboard:**

   **Settings:**
   - **Name:** Swimnerd Bluetooth Clock
   - **Script:** `swimnerd_bluetooth_clock.lss`
   - **Port:** `COM5` (Windows) or `/dev/cu.HC-08-DevB` (Mac)
   - **Baud Rate:** `9600`
   - **Data Bits:** `8`
   - **Parity:** `N` (None)
   - **Stop Bits:** `1`
   - **Enabled:** ✓ (checked)

4. **Click OK**

5. **Test connection:**
   - Run a test race in FinishLynx
   - Clock should display running time
   - When race finishes, clock shows final time

---

## Step 6: Testing

### Test 1: Bluetooth Connection

**Send test data manually:**

**Windows (PowerShell):**
```powershell
$port = new-Object System.IO.Ports.SerialPort COM5,9600,None,8,one
$port.open()
$port.WriteLine("01:23.45")
$port.Close()
```

**macOS/Linux:**
```bash
echo "01:23.45" > /dev/cu.HC-08-DevB
```

**Expected:** Clock displays `01:23.45`

### Test 2: FinishLynx Integration

1. Open FinishLynx
2. Create a test race
3. Start timer
4. **Clock should show running time** updating every second
5. Stop timer
6. **Clock should show final time**

### Test 3: Clear Command

Send `CLR` to clear the display:
```bash
echo "CLR" > /dev/cu.HC-08-DevB
```

---

## Troubleshooting

### Clock doesn't display anything

**Check:**
- Power: Is STM32 powered? (LED should be on)
- Display wiring: Verify connections (DIN, CLK, CS)
- Firmware: Re-upload and check Serial Monitor for errors
- Display brightness: Try increasing in code

### Bluetooth won't pair

**Check:**
- HC-08 power: Is it getting 3.3V?
- HC-08 LED: Should be blinking (unpaired) or solid (paired)
- PIN code: Default is usually `1234` or `0000`
- Distance: Stay within 10 meters during pairing

### FinishLynx can't connect to COM port

**Check:**
- COM port number: Device Manager → Ports
- Bluetooth paired: Must be paired first
- Port in use: Close other programs using the port
- Drivers: Update Bluetooth drivers

### Clock shows wrong time or garbled data

**Check:**
- Baud rate: Must be 9600 on both sides
- Data format: Should be "MM:SS.HH\n"
- Serial buffer: Add delay in LSS script if too fast

**Add delay to LSS script:**
```lss
; Add 100ms delay between messages
\11\00\ff\64
\11\01%s\0a
```

### Display shows random segments

**Check:**
- Wiring: Verify DIN/CLK/CS connections
- Power: Display needs stable 5V
- Library: Correct library for your display type
- Code: Verify USE_MAX7219 or USE_TM1637 is defined

---

## Advanced Features

### Add Lap/Split Display

Modify firmware to cycle through splits:

```cpp
void displaySplit(int splitNum, int time) {
  // Show "SP 1" then time
  // Alternate every 2 seconds
}
```

### Add Sound Alerts

Connect buzzer to STM32 PA8:

```cpp
#define BUZZER_PIN PA8

void beepStart() {
  tone(BUZZER_PIN, 1000, 200); // 1kHz beep for 200ms
}
```

### Add Lane Number Display

Extend to 8 digits: `LL:MM:SS.HH` (lane + time)

### Wireless Range Extension

- Use HC-08 Long Range version (100m)
- Add external antenna
- Use Bluetooth Class 1 module (100m range)

---

## Power Options

### Option 1: USB Power
- Connect STM32 to USB power bank
- Portable, rechargeable

### Option 2: Wall Adapter
- 5V 1A wall adapter
- Most reliable for stationary use

### Option 3: Battery Pack
- 3x AA batteries (4.5V)
- Use voltage regulator to 5V
- 8+ hours runtime

### Option 4: Solar (Outdoor)
- 6V solar panel
- LiPo battery + charging circuit
- Good for outdoor/open water events

---

## Enclosure Design

### 3D Printable Case

**Dimensions (suggested):**
- 150mm x 80mm x 40mm
- Front panel cutout for display
- Side holes for power/programming
- Mounting holes for wall/tripod

**STL files:** (coming soon)

### Off-the-Shelf Enclosure

**Recommended:**
- Hammond 1591XXXX series
- BUD Industries CU-series
- DIN rail mount case (for permanent install)

---

## Bill of Materials (BOM)

| Item | Qty | Unit Price | Total | Source |
|------|-----|------------|-------|--------|
| STM32F103C8T6 Blue Pill | 1 | $3 | $3 | AliExpress, eBay |
| HC-08 Bluetooth Module | 1 | $5 | $5 | Amazon, AliExpress |
| MAX7219 6-Digit Display | 1 | $4 | $4 | Amazon, AliExpress |
| 5V Power Supply | 1 | $5 | $5 | Amazon |
| Wires/Breadboard | 1 | $5 | $5 | Amazon |
| **TOTAL** | | | **$22** | |

**Optional:**
- Enclosure: $10-$20
- PCB (custom): $5-$10 (MOQ 5)
- STLink programmer: $3-$10

---

## Next Steps

### Production Version

1. **Design custom PCB:**
   - Single board with STM32 + HC-08 + display drivers
   - SMD components for compact size
   - USB-C power input

2. **Firmware improvements:**
   - OTA (Over-The-Air) firmware updates
   - Configuration via Bluetooth app
   - Multiple display modes (time, splits, pace)

3. **Mobile App:**
   - iOS/Android app to configure clock
   - Backup display on phone
   - Cloud sync with FinishLynx

4. **Certification:**
   - FCC (USA)
   - CE (Europe)
   - For commercial sale

---

## Support

**Hardware questions:**
- Swimnerd Forum: (TBD)
- Email: support@swimnerd.com

**Software/firmware:**
- GitHub Issues: https://github.com/swimnerdtim/finishlynx-integration/issues

**FinishLynx support:**
- https://finishlynx.com/contact/tech-support-contact/

---

## License

Hardware design: MIT License  
Firmware: MIT License  
Documentation: CC BY-SA 4.0

---

**Built with ❤️ for the swimming and timing communities**
