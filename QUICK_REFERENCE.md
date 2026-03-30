# Swimnerd Bluetooth Clock - Quick Reference Card

## Hardware Setup (30 seconds)

### Connections

```
HC-08           STM32F103        Display (MAX7219)
------          ----------       ------------------
VCC   →         3.3V             VCC   →   5V
GND   →         GND              GND   →   GND
TXD   →         PA10 (RX)        DIN   →   PA7
RXD   →         PA9  (TX)        CLK   →   PA5
                                 CS    →   PA4
```

### Power
- **STM32:** 5V via USB or VIN pin
- **HC-08:** 3.3V (from STM32)
- **Display:** 5V

---

## Software Setup (5 minutes)

### 1. Upload Firmware
```bash
# Arduino IDE
File → Open → stm32_bluetooth_clock.ino
Tools → Board → STM32F1 → BluePill F103C8
Tools → Upload
```

### 2. Pair Bluetooth
**Windows:** Settings → Bluetooth → Add Device → PIN: `1234`  
**Mac:** System Prefs → Bluetooth → Pair → PIN: `1234`

### 3. Find COM Port
**Windows:** Device Manager → Ports (e.g., COM5)  
**Mac:** Terminal → `ls /dev/cu.*` (e.g., /dev/cu.HC-08-DevB)

### 4. Configure FinishLynx
```
File → Options → Hardware → Scoreboard → Add
Name: Swimnerd Clock
Script: swimnerd_bluetooth_clock.lss
Port: COM5 (or your port)
Baud: 9600
Enable: ✓
```

---

## Testing (1 minute)

### Test 1: Send Time Manually

**Windows PowerShell:**
```powershell
$port = new-Object System.IO.Ports.SerialPort COM5,9600,None,8,one
$port.open()
$port.WriteLine("01:23.45")
$port.Close()
```

**Mac/Linux:**
```bash
echo "01:23.45" > /dev/cu.HC-08-DevB
```

**Expected:** Clock shows `01:23.45`

### Test 2: FinishLynx
- Start a race in FinishLynx
- Clock should update in real-time
- Stop race → clock shows final time

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Clock doesn't light up | Check 5V power to display |
| No Bluetooth | Check HC-08 has 3.3V power |
| Can't pair | Try PIN: `0000` or `1234` |
| Wrong time | Verify 9600 baud on both sides |
| Garbled display | Check DIN/CLK wiring |
| FinishLynx can't connect | Close other apps using COM port |

---

## Data Format

**FinishLynx sends:**
```
01:23.45\n    // Display time
CLR\n         // Clear display
READY\n       // Show ready state
```

**STM32 parses:**
- `MM:SS.HH` format
- Newline (`\n`) terminated
- ASCII text (not binary)

---

## AT Commands (HC-08 Config)

| Command | Function |
|---------|----------|
| `AT` | Test (reply: OK) |
| `AT+NAME=SWIMNERD` | Set device name |
| `AT+BAUD4` | Set 9600 baud |
| `AT+PIN1234` | Set pairing PIN |

**How to send:**
1. Connect HC-08 RX/TX to USB-Serial adapter
2. Open serial terminal at 9600 baud
3. Type command + Enter

---

## Default Settings

| Setting | Value |
|---------|-------|
| Bluetooth Name | HC-08 |
| Baud Rate | 9600 |
| Pairing PIN | 1234 |
| Data Format | 8-N-1 |
| Display Brightness | Max (adjustable in code) |

---

## File Reference

| File | Purpose |
|------|---------|
| `swimnerd_bluetooth_clock.lss` | FinishLynx script |
| `stm32_bluetooth_clock.ino` | STM32 firmware |
| `BLUETOOTH_CLOCK_GUIDE.md` | Full setup guide |
| `test_clock_output.py` | Test script |

---

## Support

- **GitHub:** https://github.com/swimnerdtim/finishlynx-integration
- **Email:** support@swimnerd.com
- **Issues:** https://github.com/swimnerdtim/finishlynx-integration/issues

---

**Print this page for on-site reference!**
