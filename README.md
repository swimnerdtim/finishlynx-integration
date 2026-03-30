# FinishLynx → Swimnerd Integration

**Connect FinishLynx photo-finish cameras to Swimnerd Live scoreboard software**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🏁 What is This?

**FinishLynx** is the industry-standard photo-finish timing system for track & field, used at the Olympics, NCAA championships, and thousands of meets worldwide.

**Swimnerd** is a modern swim meet timing and scoreboard platform.

This integration lets you **send race results from FinishLynx cameras directly to Swimnerd scoreboards** for:
- Track & field meets
- Open water swimming
- Triathlons
- Multi-sport events
- Backup timing systems

---

## ⚡ Quick Start

### 1. Install the LSS Script

Copy `swimnerd.lss` to your FinishLynx directory:

**Windows:**
```
C:\Lynx\swimnerd.lss
```

**Mac:**
```
/Applications/FinishLynx/swimnerd.lss
```

### 2. Configure FinishLynx

1. Open FinishLynx
2. **File → Options → Hardware → Scoreboard**
3. Click **Add**:
   - **Name:** Swimnerd
   - **Script:** `swimnerd.lss`
   - **Port:** `-1` (TCP/IP)
   - **IP:** `0.0.0.0`
   - **Port Number:** `1024`
4. **Enable** the scoreboard

### 3. Test It

```bash
python3 finishlynx_receiver.py
```

Run a race in FinishLynx → see results appear in real-time!

---

## 📦 What's Included

### General Integration
| File | Description |
|------|-------------|
| **`swimnerd.lss`** | FinishLynx scoreboard script (ready to use) |
| **`finishlynx_receiver.py`** | Python TCP receiver (demo/starter code) |
| **`FINISHLYNX_README.md`** | Quick start guide |
| **`FINISHLYNX_INTEGRATION.md`** | Full technical documentation |

### Hardware Clocks
| File | Description |
|------|-------------|
| **`swimnerd_bluetooth_clock.lss`** | LSS script for Bluetooth racing clock |
| **`stm32_bluetooth_clock.ino`** | STM32 firmware (Arduino) |
| **`BLUETOOTH_CLOCK_GUIDE.md`** | Complete build guide for Bluetooth clock |
| **`QUICK_REFERENCE.md`** | Quick setup card (print this!) |
| **`swimnerd_6digit_clock.lss`** | Generic 6-digit clock script |
| **`test_clock_output.py`** | Hardware testing tool |
| **`CLOCK_SETUP.md`** | General clock configuration guide |

---

## 📊 Data Format

Results are sent as pipe-delimited text:

```
RESULT|Place|Lane|Id|Name|Team|Time|Delta|ReacTime
```

Example:
```
RESULT|1|4|123|John Smith|Team A|10.23|-|0.145
RESULT|2|6|456|Jane Doe|Team B|10.45|+0.22|0.132
```

Parse this in your Swimnerd software to update the scoreboard.

---

## 🔥 NEW: Bluetooth Racing Clock (DIY Hardware)

Build your own **wireless 6-digit racing clock** with Bluetooth!

**Hardware:**
- STM32F103 microcontroller ($3)
- HC-08 Bluetooth module ($5)
- 6-digit LED display ($4)
- **Total cost: ~$22**

**Features:**
- ✅ Wireless Bluetooth connection (10m range)
- ✅ Real-time display updates
- ✅ 6-digit precision (MM:SS.HH)
- ✅ Open-source firmware
- ✅ Arduino IDE compatible

**See:** [BLUETOOTH_CLOCK_GUIDE.md](BLUETOOTH_CLOCK_GUIDE.md) for complete build instructions.

---

## 🎯 Use Cases

### Track & Field
Display track results on Swimnerd scoreboards at venues that already use FinishLynx

### Open Water Swimming
FinishLynx cameras at the finish line → Swimnerd displays results

### Triathlons
Coordinate swim exit times with bike/run timing

### Multi-Sport Events
One unified results system for track + swim competitions

---

## 🔧 Integration Options

### Option 1: Standalone Bridge
Run `finishlynx_receiver.py` as a service:
- Receives FinishLynx data on port 1024
- Transforms to Swimnerd format
- Forwards via HTTP/WebSocket

### Option 2: Direct Integration
Add TCP listener to Swimnerd Live software:
```python
import socket

def listen_for_finishlynx():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', 1024))
        s.listen()
        while True:
            conn, addr = s.accept()
            data = conn.recv(1024).decode('utf-8')
            if data.startswith('RESULT|'):
                parts = data.split('|')
                update_scoreboard(parts[1], parts[4], parts[6])
```

### Option 3: Modify LSS Script
Customize `swimnerd.lss` to output JSON, CSV, or any format you need

---

## 🌐 Network Setup

### Same Machine
FinishLynx → `127.0.0.1:1024` → Swimnerd

### Different Machines (LAN)
FinishLynx → `192.168.1.50:1024` → Swimnerd  
*(Ensure port 1024 is open in firewall)*

### Broadcast Mode
FinishLynx → `0.0.0.0:1024` → Multiple Swimnerd displays simultaneously

---

## 📚 Documentation

- **[Quick Start Guide](FINISHLYNX_README.md)** - Setup, troubleshooting, tips
- **[Technical Documentation](FINISHLYNX_INTEGRATION.md)** - LSS format, customization, advanced features

---

## 🛠️ Requirements

### FinishLynx Side
- FinishLynx software (any version with scoreboard script support)
- Network connection or serial port

### Swimnerd Side
- Python 3.6+ (for demo receiver)
- Network connection on port 1024

---

## 🐛 Troubleshooting

### No connection?
- Check firewall (port 1024 must be open)
- Verify FinishLynx scoreboard is **enabled**
- Test with: `telnet localhost 1024`

### No data?
- Results must be **finalized** in FinishLynx (not draft)
- Try manual send: **Scoreboard → Send Results**

### Garbled characters?
- Use UTF-8 encoding
- Check line endings (should be `\r\n`)

See [FINISHLYNX_README.md](FINISHLYNX_README.md) for full troubleshooting guide.

---

## 📝 Example Output

When you run a race, FinishLynx sends:

```
[12:35:10.124] SWIMNERD_INIT|v1.0
[12:35:10.125] START_RESULTS|100 Meter Dash|5|1|8|OFFICIAL
[12:35:10.126] RESULT|1|4|123|John Smith|Team A|10.23|-|0.145
[12:35:10.127] RESULT|2|6|456|Jane Doe|Team B|10.45|+0.22|0.132
[12:35:10.128] RESULT|3|2|789|Bob Johnson|Team C|10.67|+0.44|0.158
[12:35:10.150] END_RESULTS
```

Python receiver displays:

```
[12:35:10.124] >>> Initialized (version: v1.0)
[12:35:10.125] >>> Event: 100 Meter Dash (Heat 1)
[12:35:10.126] >>>   1. Lane 4 - John Smith                  10.23
[12:35:10.127] >>>   2. Lane 6 - Jane Doe                    10.45
[12:35:10.128] >>>   3. Lane 2 - Bob Johnson                 10.67
[12:35:10.150] >>> Results complete (8 finishers)
```

---

## 🤝 Contributing

Pull requests welcome! Areas for improvement:
- WebSocket support
- Additional output formats (JSON, XML, etc.)
- Multi-language support
- Real-time split display
- HyTek file export

---

## 📜 License

MIT License - Free to use, modify, and distribute.

---

## 🌟 About

**Created by:** Swimnerd ([@SwimNerds](https://twitter.com/SwimNerds))  
**Website:** [swimnerd.com](https://swimnerd.com)  
**Support:** support@swimnerd.com

**FinishLynx:** [finishlynx.com](https://finishlynx.com)

---

## 🚀 Get Started

1. Download `swimnerd.lss`
2. Copy to FinishLynx directory
3. Enable in FinishLynx settings
4. Run `python3 finishlynx_receiver.py`
5. See results in real-time!

**Questions?** See [FINISHLYNX_README.md](FINISHLYNX_README.md) or open an issue.

---

**Built with ❤️ for track & field and swimming communities**
