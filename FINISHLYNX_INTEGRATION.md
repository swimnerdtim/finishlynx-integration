# FinishLynx Camera Integration for Swimnerd Clock

## What is FinishLynx?

**FinishLynx** is the industry-standard photo-finish timing system for track & field (and other sports). It uses high-speed line-scan cameras to capture race finishes with 1/1000th second accuracy.

### Key Points:
- **Primary use:** Track & field, but used in some swim meets (especially open water)
- **Cameras:** High-speed digital line-scan cameras at the finish line
- **Software:** FinishLynx software processes images and generates results
- **Output:** Results, splits, times, and rankings

---

## How .LSS Scoreboard Scripts Work

FinishLynx can output race data to external scoreboards, displays, and software via **LSS (Lynx Scoreboard Script)** files.

### LSS File Format:

LSS files are **text-based script files** that define:
1. What data to send (place, name, time, splits, etc.)
2. How to format it (layout, delimiters, etc.)
3. When to send it (initialization, time updates, results, etc.)
4. Communication settings (serial port, baud rate, etc.)

### Communication Methods:

**Serial Port (RS-232):**
- Most common for hardware scoreboards
- Settings: `9600,8,N,1` (baud rate, data bits, parity, stop bits)

**TCP/IP (Network):**
- Modern approach for software integrations
- Settings: `-1,0.0.0.0,1024` (port number)
- Can broadcast to multiple receivers on the same network

---

## LSS Script Structure

### Section Headers (preceded by `;;`):

- **;;Initialization** - Sent once when script starts
- **;;TimeRunning** - Sent while timer is running
- **;;TimeStopped** - Sent when timer stops
- **;;ResultsHeader** - Sent before results
- **;;Result** - Sent for each result line (place, name, time, etc.)
- **;;ResultsTrailer** - Sent after results
- **;;Message** - Sent for custom messages

### Group Codes (first byte after `;`):

- `\10` - Initialize
- `\11` - Time
- `\12` - Wind
- `\13` - Results Header/Trailer
- `\14` - Result (individual athlete data)
- `\15` - Message Header/Trailer
- `\16` - Message

### Variable Codes (second byte):

**For Time (`\11`):**
- `\00` - No variable
- `\01` - Formatted time (e.g., "10:23.45")
- `\02` - Binary time (milliseconds)

**For Results (`\14`):**
- `\01` - Place (1st, 2nd, 3rd)
- `\02` - Lane
- `\03` - Id (bib number)
- `\04` - Name
- `\05` - Affiliation (team)
- `\06` - Time
- `\07` - Delta Time (difference from leader)
- `\08` - Cumulative Split Time
- `\09` - Last Split Time
- `\0c` - Reaction Time

### Example LSS Line:

```
\14\01%s\05
```

Breakdown:
- `\14` = Result group code
- `\01` = Variable code (Place)
- `%s` = Printf format specifier (where the variable goes)
- `\05` = Line terminator (ASCII ENQ character)

---

## How to Create a Swimnerd LSS Script

### Goal:
Output race results from FinishLynx to Swimnerd Live scoreboard software.

### Approach:

**Option 1: Network/TCP Output (Recommended)**

FinishLynx → LSS Script → TCP Socket → Swimnerd Live

1. Create custom `swimnerd.lss` file
2. Configure FinishLynx to use TCP/IP output
3. Swimnerd Live listens on TCP port (e.g., 1024)
4. Parse incoming data and update scoreboard

**Option 2: Serial Port Output**

FinishLynx → LSS Script → Serial Port → Swimnerd Hardware

- Useful if you have dedicated Swimnerd timing hardware
- Requires serial cable connection

---

## Sample Swimnerd LSS Script

Here's a starter script for Swimnerd integration:

### File: `swimnerd.lss`

```lss
; Swimnerd FinishLynx Integration Script
; Copyright (c) 2026 Swimnerd
; Network settings: -1,0.0.0.0,1024
;
; This script sends race results from FinishLynx to Swimnerd Live software

;;Initialization
; Sent once when script starts
\10\00SWIMNERD_INIT\0d\0a

;;ResultsHeader
; Sent before results
\13\00START_RESULTS\0d\0a
\13\02EVENT:%s\0d\0a
\13\04EVENT_NUM:%s\0d\0a
\13\06HEAT:%s\0d\0a
\13\08PARTICIPANTS:%s\0d\0a

;;Result
; Sent for each finisher
; Format: RESULT|Place|Lane|Name|Team|Time
\14\00RESULT|
\14\01%s|
\14\02%s|
\14\04%s|
\14\05%s|
\14\06%s\0d\0a

;;ResultsTrailer
; Sent after all results
\13\00END_RESULTS\0d\0a

;;TimeRunning
; Sent while race is in progress
\11\00RUNNING_TIME:
\11\01%s\0d\0a

;;TimeStopped
; Sent when timer stops
\11\00STOPPED_TIME:
\11\01%s\0d\0a

;;Message
; Sent for custom messages (e.g., "OFFICIAL RESULTS")
\16\00MESSAGE:
\16\01%s\0d\0a
```

### Output Example:

When a race finishes, FinishLynx would send:

```
SWIMNERD_INIT
START_RESULTS
EVENT:100 Meter Dash
EVENT_NUM:5
HEAT:1
PARTICIPANTS:8
RESULT|1|4|John Smith|Team A|10.23
RESULT|2|6|Jane Doe|Team B|10.45
RESULT|3|2|Bob Johnson|Team C|10.67
RESULT|4|8|Sally Lee|Team A|10.89
RESULT|5|3|Mike Brown|Team D|11.12
RESULT|6|1|Lisa White|Team B|11.34
RESULT|7|7|Tom Green|Team C|11.56
RESULT|8|5|Amy Black|Team D|11.78
END_RESULTS
```

---

## Integration Steps for Swimnerd

### 1. Create the LSS Script

Save the script above as `swimnerd.lss` in the FinishLynx directory:
- Windows: `C:\Lynx\swimnerd.lss`
- Mac: `/Applications/FinishLynx/swimnerd.lss`

### 2. Configure FinishLynx

In FinishLynx software:
1. Go to **File → Options → Hardware**
2. Select **Scoreboard** tab
3. Click **Add** to add a new scoreboard
4. Settings:
   - **Script:** `swimnerd.lss`
   - **Port:** `-1` (TCP/IP)
   - **IP:** `0.0.0.0` (broadcast to all on network)
   - **Port number:** `1024` (or whatever Swimnerd listens on)
5. Click **OK**

### 3. Build Swimnerd Receiver

Create a TCP listener in Swimnerd Live software:

**Python Example:**

```python
import socket

def listen_for_finishlynx():
    host = '0.0.0.0'
    port = 1024
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Listening for FinishLynx on port {port}...")
        
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    message = data.decode('utf-8')
                    print(f"Received: {message}")
                    parse_finishlynx_data(message)

def parse_finishlynx_data(message):
    if message.startswith("RESULT|"):
        parts = message.strip().split('|')
        place = parts[1]
        lane = parts[2]
        name = parts[3]
        team = parts[4]
        time = parts[5]
        
        # Update Swimnerd scoreboard
        update_scoreboard(place, lane, name, team, time)
    
    elif message.startswith("EVENT:"):
        event_name = message.split(':', 1)[1].strip()
        set_event_name(event_name)
    
    # ... handle other message types

if __name__ == '__main__':
    listen_for_finishlynx()
```

**JavaScript (Node.js) Example:**

```javascript
const net = require('net');

const server = net.createServer((socket) => {
  console.log('FinishLynx connected');
  
  socket.on('data', (data) => {
    const message = data.toString();
    console.log('Received:', message);
    parseFinishLynxData(message);
  });
  
  socket.on('end', () => {
    console.log('FinishLynx disconnected');
  });
});

server.listen(1024, '0.0.0.0', () => {
  console.log('Listening for FinishLynx on port 1024...');
});

function parseFinishLynxData(message) {
  if (message.startsWith('RESULT|')) {
    const parts = message.trim().split('|');
    const [_, place, lane, name, team, time] = parts;
    
    // Update Swimnerd scoreboard
    updateScoreboard(place, lane, name, team, time);
  } else if (message.startsWith('EVENT:')) {
    const eventName = message.split(':')[1].trim();
    setEventName(eventName);
  }
  // ... handle other message types
}
```

### 4. Test the Integration

1. Start Swimnerd receiver (listening on port 1024)
2. Open FinishLynx
3. Load a test race or run a live event
4. When results are finalized, FinishLynx will send data to Swimnerd
5. Verify Swimnerd displays the results correctly

---

## Advanced Customization

### Custom Data Format

Want JSON output instead? Modify the LSS script:

```lss
;;Result
; JSON format
\14\00{"place":
\14\01"%s",
\14\02"lane":"%s",
\14\04"name":"%s",
\14\05"team":"%s",
\14\06"time":"%s"}\0d\0a
```

Output:
```json
{"place":"1","lane":"4","name":"John Smith","team":"Team A","time":"10.23"}
```

### Multiple Scoreboards

FinishLynx can send to multiple scoreboards simultaneously. Create multiple entries in the Hardware settings, each with a different LSS script and port.

---

## Troubleshooting

### Not Receiving Data?

1. **Firewall:** Ensure port 1024 is open
2. **Network:** Both machines must be on the same network
3. **FinishLynx Settings:** Verify scoreboard is enabled
4. **Test with Telnet:**
   ```bash
   telnet localhost 1024
   ```

### Garbled Data?

- Check baud rate/serial settings if using RS-232
- Verify line terminators (`\0d\0a` = CRLF)
- Check encoding (should be ASCII/UTF-8)

### FinishLynx Not Sending?

- Results must be **finalized** (not draft)
- Scoreboard must be **enabled** in Hardware settings
- Check FinishLynx logs for errors

---

## Swimming-Specific Considerations

### Track vs. Swim Timing

**FinishLynx is designed for track**, but some swim meets use it for:
- **Open water swimming** (finish line crossing)
- **Triathlon swim exits**
- **Backup timing** for pool events

**For pool swimming**, you typically use:
- **Touchpads** (Omega, Daktronics, Colorado)
- **Timing consoles** (HyTek, Meet Manager)
- **Swimnerd Live** (your existing system)

### Why Integrate FinishLynx?

If you're running a **multi-sport event** (track + swim) or **open water races**, having FinishLynx compatibility means:
- Venues already using FinishLynx can add Swimnerd displays
- One system for both track and swim events
- Broader market reach

---

## Next Steps

1. **Download sample LSS files** from FinishLynx website
2. **Study existing scripts** (ResulTV.lss, Daktronics.lss)
3. **Create swimnerd.lss** with custom format
4. **Build TCP receiver** in Swimnerd Live software
5. **Test with FinishLynx** (contact local track clubs for test data)
6. **Deploy** and gather feedback

---

## Resources

- **FinishLynx Downloads:** https://finishlynx.com/support/display-and-scoreboard-scripts/
- **LSS Script Library:** All scripts available for reference
- **FinishLynx Manual:** https://finishlynx.com/wp-content/uploads/2022/06/finishlynx_version_4.pdf
- **Support:** Contact FinishLynx technical support for custom script help

---

## Summary

**TL;DR:**
1. FinishLynx = photo-finish cameras for track & field
2. LSS scripts = text files that format race data for scoreboards
3. Create `swimnerd.lss` to output results in Swimnerd-friendly format
4. Swimnerd listens on TCP port 1024, parses data, updates scoreboard
5. Test with FinishLynx software or contact local track clubs

**Benefit:** Makes Swimnerd compatible with track & field timing systems, expanding your market beyond just swimming.

---

**File saved:** `/Users/tim/.openclaw/workspace/swimnerd/FINISHLYNX_INTEGRATION.md`
