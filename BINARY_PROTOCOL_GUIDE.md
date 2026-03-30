# Swimnerd Clock Binary Protocol Guide

## Problem: Your Clock Uses Binary, Not ASCII

FinishLynx LSS scripts can send binary data, but they **can't convert** formatted time strings (`"01:23.45"`) into binary.

**Solution:** Use a **bridge script** to convert:

```
FinishLynx → ASCII (TCP) → Bridge Script → Binary (Bluetooth) → Swimnerd Clock
```

---

## Step 1: Determine Your Clock's Binary Format

Run the test script to find out which format your clock expects:

```bash
# Windows
python3 test_binary_formats.py --port COM5

# Mac
python3 test_binary_formats.py --port /dev/cu.HC-08-DevB
```

### The Test Will Try:

**Test 1: Packed BCD** (most common)
```
Bytes: 0x01 0x23 0x45
Displays: 01:23.45
```

**Test 2: Raw Binary**
```
Bytes: 0x01 0x17 0x2D
Displays: 01:23.45
```

**Test 3: With Header/Footer**
```
Bytes: 0xFF 0x01 0x23 0x45 0xFE
Displays: 01:23.45
```

**Test 4: 16-bit Values**
```
Bytes: 0x01 0x00 0x17 0x00 0x2D 0x00
Displays: 01:23.45
```

**Test 5: Total Milliseconds**
```
Bytes: 0x3A 0x46 0x01 0x00
Displays: 01:23.45 (83,450 ms)
```

### Watch Your Clock

For each test:
1. Script sends binary data
2. **Does the clock display "01:23.45"?**
3. Press Enter to try next format
4. **Remember which test number worked!**

---

## Step 2: Configure the Bridge Script

Once you know the format, edit `finishlynx_to_swimnerd_bridge.py`:

### If Test 1 Worked (Packed BCD):
```python
def send_binary_time(self, minutes, seconds, hundredths):
    # Packed BCD - most common
    data = bytes([minutes, seconds, hundredths])
    self.ser.write(data)
```

### If Test 2 Worked (Raw Binary):
```python
def send_binary_time(self, minutes, seconds, hundredths):
    # Raw binary values
    data = struct.pack('BBB', minutes, seconds, hundredths)
    self.ser.write(data)
```

### If Test 3 Worked (With Header/Footer):
```python
def send_binary_time(self, minutes, seconds, hundredths):
    # With markers: 0xFF [data] 0xFE
    data = bytes([0xFF, minutes, seconds, hundredths, 0xFE])
    self.ser.write(data)
```

### If Test 4 Worked (16-bit):
```python
def send_binary_time(self, minutes, seconds, hundredths):
    # 16-bit little-endian
    data = struct.pack('<HHH', minutes, seconds, hundredths)
    self.ser.write(data)
```

### If Test 5 Worked (Milliseconds):
```python
def send_binary_time(self, minutes, seconds, hundredths):
    # Total milliseconds as 32-bit integer
    total_ms = (minutes * 60 * 1000) + (seconds * 1000) + (hundredths * 10)
    data = struct.pack('<I', total_ms)
    self.ser.write(data)
```

---

## Step 3: Run the Bridge

### Start the Bridge Server

```bash
# Windows
python3 finishlynx_to_swimnerd_bridge.py --finishlynx-port 1024 --clock-port COM5

# Mac
python3 finishlynx_to_swimnerd_bridge.py --finishlynx-port 1024 --clock-port /dev/cu.HC-08-DevB
```

**You should see:**
```
[12:34:56.789] Connected to Swimnerd clock on COM5
[12:34:56.790] Listening for FinishLynx on port 1024
[12:34:56.790] Configure FinishLynx to send to localhost:1024
```

### Configure FinishLynx

1. **File → Options → Hardware → Scoreboard → Add**

2. **Settings:**
   - **Name:** Swimnerd Clock (via Bridge)
   - **Script:** `swimnerd.lss` (from main repo)
   - **Port:** `-1` (TCP/IP)
   - **IP Address:** `127.0.0.1` (localhost)
   - **Port Number:** `1024`

3. **Enable the scoreboard**

### Test the Flow

1. **Start a race in FinishLynx**
2. **Bridge receives:**
   ```
   [12:35:10.123] FinishLynx connected from 127.0.0.1:54321
   [12:35:10.124] RX: 00:01.23
   [12:35:10.124] TX: 00:01.23 → 00 01 23
   ```
3. **Clock displays the time!**

---

## Step 4: If None of the Tests Worked

### Option A: Get the Firmware Source

If you have the STM32 firmware code, look for:

```c
// Bluetooth receive handler
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    // How is rx_buffer parsed?
    // What structure is expected?
}

// Or in Arduino:
void loop() {
    if (Serial.available()) {
        // What format is read here?
    }
}
```

**Send me the code** and I'll write the exact bridge format.

### Option B: Use a Logic Analyzer

If you have access to the clock's UART pins:
1. Connect logic analyzer to STM32 RX pin
2. Send time from existing software
3. Capture the binary data
4. Decode the protocol

### Option C: Reverse Engineer with Custom Tests

Create custom test patterns:

```python
# Send every possible single byte
for i in range(256):
    ser.write(bytes([i]))
    time.sleep(0.5)
    # Watch what displays
```

---

## Common Binary Clock Protocols

### Protocol 1: Simple 3-Byte

```
Byte 0: Minutes (0-99)
Byte 1: Seconds (0-59)
Byte 2: Hundredths (0-99)
```

**Example:** `01:23.45` = `[0x01] [0x17] [0x2D]`

### Protocol 2: Packed BCD (Hex Values)

```
Byte 0: Minutes in hex (1 min = 0x01)
Byte 1: Seconds in hex (23 sec = 0x23)
Byte 2: Hundredths in hex (45 = 0x45)
```

**Example:** `01:23.45` = `[0x01] [0x23] [0x45]`

### Protocol 3: Fixed Message Structure

```
[START] [CMD] [LEN] [DATA...] [CHECKSUM] [END]

0xFF    0x01  0x03  MM SS HH   XOR       0xFE
```

**Example:** `01:23.45` =
```
0xFF 0x01 0x03 0x01 0x23 0x45 [checksum] 0xFE
```

### Protocol 4: ASCII with Binary Wrapper

```
[HEADER] "01:23.45" [FOOTER]
0xAA     ASCII      0x0A
```

---

## Advanced: Checksum Calculation

If your protocol uses checksums:

```python
def calculate_checksum(data):
    # XOR checksum
    checksum = 0
    for byte in data:
        checksum ^= byte
    return checksum

# Example
data = [0x01, 0x23, 0x45]
checksum = calculate_checksum(data)
message = bytes([0xFF] + data + [checksum, 0xFE])
```

---

## Troubleshooting

### Clock Shows Garbage

**Problem:** Wrong binary format

**Fix:**
- Try all test formats again
- Check baud rate (try 115200 if 9600 doesn't work)
- Verify Bluetooth pairing

### Clock Shows Nothing

**Problem:** Not receiving data

**Fix:**
- Check Bluetooth connection (LED should be solid, not blinking)
- Verify COM port in Device Manager
- Test with simple bytes: `ser.write(bytes([0xFF]))`

### Clock Shows Wrong Time

**Problem:** Byte order is reversed

**Fix:**
- Try reversed: `bytes([hundredths, seconds, minutes])`
- Try big-endian instead of little-endian

### Bridge Crashes

**Problem:** Serial port error

**Fix:**
- Close other apps using the COM port
- Re-pair Bluetooth
- Check serial permissions (Mac/Linux: `chmod 666 /dev/cu.*`)

---

## Production Deployment

Once you know the format:

### Option 1: Keep the Bridge

**Pros:**
- Easy to modify
- Logs all communication
- Can serve multiple clocks

**Cons:**
- Requires Python on FinishLynx computer
- Extra process to manage

### Option 2: Custom LSS Script (Advanced)

If the format is simple (e.g., 3 bytes, no checksum):

```lss
; Direct binary output (no conversion)
; Only works for fixed formats
\11\00\01\23\45  ; Hardcoded for 01:23.45
```

**Problem:** Can't dynamically convert time string to bytes in LSS.

### Option 3: Modify FinishLynx Plugin (Advanced)

Write a FinishLynx plugin (C/C++) that:
- Intercepts time data
- Converts to binary
- Sends directly to Bluetooth

**Requires:** FinishLynx SDK (contact FinishLynx support)

---

## Next Steps

1. **Run `test_binary_formats.py`** to find your format
2. **Tell me which test worked** (1-7)
3. **I'll configure the bridge script** for you
4. **Test with FinishLynx** and verify it works
5. **Deploy** for production use

---

## Support

**Can't figure out the format?**

Send me:
1. STM32 firmware code (if available)
2. Test results from all 7 formats
3. Any documentation you have
4. Photos/videos of the clock in action

I'll reverse-engineer the protocol and build the exact bridge you need.

---

**Email:** support@swimnerd.com  
**GitHub:** https://github.com/swimnerdtim/finishlynx-integration/issues
