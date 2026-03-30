# 6-Digit Racing Clock Setup Guide

## Hardware Setup

### Option 1: Serial Connection (RS-232)

**Equipment needed:**
- Serial cable (DB9 or USB-to-Serial adapter)
- 6-digit clock with serial input

**FinishLynx Settings:**
1. File → Options → Hardware → Scoreboard
2. Add new scoreboard:
   - **Script:** `swimnerd_6digit_clock.lss`
   - **Port:** `COM1` (Windows) or `/dev/ttyUSB0` (Mac/Linux)
   - **Baud Rate:** `9600` (or match your clock)
   - **Data Bits:** `8`
   - **Parity:** `N` (None)
   - **Stop Bits:** `1`

### Option 2: Network Connection (TCP/IP)

**Equipment needed:**
- Network cable or WiFi
- 6-digit clock with network input

**FinishLynx Settings:**
1. File → Options → Hardware → Scoreboard
2. Add new scoreboard:
   - **Script:** `swimnerd_6digit_clock.lss`
   - **Port:** `-1` (TCP/IP mode)
   - **IP Address:** `192.168.1.100` (your clock's IP)
   - **Port Number:** `1024` (or your clock's port)

---

## Testing Your Clock

### Step 1: Find Out What Your Clock Expects

Run the test script to send sample times:

**Serial:**
```bash
python3 test_clock_output.py --serial COM1 --baud 9600
```

**Network:**
```bash
python3 test_clock_output.py --host 192.168.1.100 --port 1024
```

Watch your clock - does it display the times correctly?

### Step 2: Check the Format

Your clock might expect:
- **Plain text:** `01:23.45\r\n`
- **Fixed width:** `012345` (6 digits, no colons/decimals)
- **Binary:** Specific byte sequence
- **Protocol:** Special command header

If plain text doesn't work, you'll need to modify the LSS script.

---

## Common Clock Formats

### Format 1: Plain Text with CRLF (Most Common)
```
01:23.45\r\n
```

**LSS Script (already provided):**
```lss
\11\01%s\0d\0a
```

### Format 2: Fixed 6 Digits (No Separators)
Display shows: `012345` for 01:23.45

**Modified LSS:**
```lss
; Strip colons and decimals, send 6 digits only
\11\00012345\0d\0a
```

But FinishLynx doesn't easily strip characters, so you'd need a bridge script.

### Format 3: Custom Protocol
Some clocks need:
```
STX 01:23.45 ETX
```

Where STX = \02 (start of text) and ETX = \03 (end of text)

**Modified LSS:**
```lss
\11\00\02
\11\01%s
\11\00\03\0d\0a
```

---

## Swimnerd Clock Specifications

**If your clock is custom Swimnerd hardware, tell me:**

1. **Communication method:**
   - Serial (what baud rate?)
   - Network (what port?)
   - USB?

2. **Expected format:**
   - What does it show for time "01:23.45"?
   - Does it need colons and decimals?
   - Any special commands to initialize?

3. **Number of digits:**
   - 6 digits (MM:SS.HH)?
   - 8 digits (MM:SS.HHH)?
   - Can it show lane numbers too?

---

## Advanced: Cycling Through Results

If you want the clock to cycle through lane results (Lane 1 time, Lane 2 time, etc.), you need a bridge script:

**Bridge Script (Python):**
```python
import socket
import time

def receive_from_finishlynx():
    """Receive results from FinishLynx"""
    results = []
    # ... receive and parse RESULT| messages
    return results

def send_to_clock(time_str):
    """Send time to 6-digit clock"""
    with socket.socket() as s:
        s.connect(('192.168.1.100', 1024))
        s.send(f"{time_str}\r\n".encode())

def cycle_results(results):
    """Cycle through results on clock"""
    for result in results:
        send_to_clock(result['time'])
        time.sleep(3)  # Show each time for 3 seconds

# Main loop
while True:
    results = receive_from_finishlynx()
    cycle_results(results)
```

---

## Troubleshooting

### Clock shows garbage characters

**Problem:** Wrong baud rate or data format

**Fix:**
- Try different baud rates: 1200, 2400, 4800, 9600, 19200
- Check parity settings (N, E, O)
- Verify data bits (7 or 8)

### Clock doesn't respond at all

**Problem:** Not receiving data

**Fix:**
- Check cable connection
- Verify serial port name (COM1, /dev/ttyUSB0, etc.)
- Test with a terminal program (PuTTY, screen, minicom)
- Check clock power and mode (is it in "receive" mode?)

### Time updates too slowly

**Problem:** FinishLynx only sends on specific events

**Fix:**
Enable **TimeUpdate** in LSS script (sends every second while running)

### Clock shows time but formatting is wrong

**Problem:** Clock expects different format

**Examples:**
- Clock shows `1:23.45` (missing leading zero) → Needs padding
- Clock shows `01.23.45` (wrong separators) → Needs different delimiters
- Clock shows `012345` (no separators) → Needs fixed-width format

**Solution:** Modify LSS script or use bridge script to reformat

---

## Examples for Common Clocks

### Swimnerd Tiny Pace Clock
```
Format: MM:SS.HH
Protocol: TCP/IP on port 8080
Command: Plain text with \r\n
```

**LSS:**
```lss
; Defaults: -1,0.0.0.0,8080
\11\01%s\0d\0a
```

### Gill 6-Digit Display
```
Format: HH:MM:SS (hours:minutes:seconds)
Protocol: Serial 9600,8,N,1
Command: Plain text with \r\n
```

**LSS:**
```lss
; Defaults: 9600,8,N,1
\11\01%s\0d\0a
```

### Generic LED Clock (Fixed 6 Digits)
```
Format: MMSSCC (minutes, seconds, centiseconds - no separators)
Protocol: Serial 9600,8,N,1
Command: 6 ASCII digits
```

**Needs bridge script** to strip separators.

---

## Next Steps

1. **Test your clock** with `test_clock_output.py`
2. **Determine the format** it expects
3. **Modify the LSS script** if needed
4. **Configure FinishLynx** to use the script
5. **Run a test race** and verify display

---

## Need Help?

**Tell me:**
1. Clock manufacturer/model
2. What it currently displays (if anything)
3. Connection type (serial/network)
4. Any error messages

I'll create a custom LSS script for your specific hardware.
