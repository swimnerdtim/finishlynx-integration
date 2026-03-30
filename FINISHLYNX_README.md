# FinishLynx Integration for Swimnerd

**Complete integration package for receiving race results from FinishLynx photo-finish cameras into Swimnerd Live scoreboard software.**

---

## 📦 What's Included

1. **`FINISHLYNX_INTEGRATION.md`** - Complete technical documentation
2. **`swimnerd.lss`** - FinishLynx scoreboard script (ready to use)
3. **`finishlynx_receiver.py`** - Python TCP receiver (demo/starter code)

---

## 🚀 Quick Start

### Step 1: Install the LSS Script

Copy `swimnerd.lss` to your FinishLynx directory:

**Windows:**
```
C:\Lynx\swimnerd.lss
```

**Mac:**
```
/Applications/FinishLynx/swimnerd.lss
```

### Step 2: Configure FinishLynx

1. Open FinishLynx software
2. Go to **File → Options → Hardware**
3. Select **Scoreboard** tab
4. Click **Add** to add new scoreboard:
   - **Name:** Swimnerd
   - **Script:** `swimnerd.lss`
   - **Port:** `-1` (TCP/IP mode)
   - **IP Address:** `0.0.0.0` (broadcast)
   - **Port Number:** `1024`
5. Click **OK** and **Enable** the scoreboard

### Step 3: Test the Receiver

Run the Python receiver to verify connection:

```bash
python3 finishlynx_receiver.py
```

You should see:
```
[12:34:56.789] Swimnerd FinishLynx Receiver started
[12:34:56.789] Listening on 0.0.0.0:1024
[12:34:56.789] Waiting for FinishLynx connection...
```

### Step 4: Run a Test Race

In FinishLynx:
1. Load a test race or create a new one
2. Add some test results
3. Click **Send to Scoreboard** (or it will auto-send when finalized)

You should see results appear in the receiver terminal:

```
[12:35:10.123] FinishLynx connected from 192.168.1.100:54321
[12:35:10.124] RX: SWIMNERD_INIT|v1.0
[12:35:10.124] >>> Initialized (version: v1.0)
[12:35:10.125] RX: START_RESULTS|100 Meter Dash|5|1|8|OFFICIAL
[12:35:10.125] >>> Event: 100 Meter Dash (Heat 1)
[12:35:10.125] >>> Status: OFFICIAL
[12:35:10.126] RX: RESULT|1|4|123|John Smith|Team A|10.23|-|0.145
[12:35:10.126] >>>   1. Lane 4 - John Smith                  10.23
[12:35:10.127] RX: RESULT|2|6|456|Jane Doe|Team B|10.45|+0.22|0.132
[12:35:10.127] >>>   2. Lane 6 - Jane Doe                    10.45
...
[12:35:10.150] RX: END_RESULTS
[12:35:10.150] >>> Results complete (8 finishers)
[12:35:10.151] >>> Saved to results_5_20260330_123510.json
```

---

## 📊 Data Format

The LSS script sends pipe-delimited messages:

### Result Format:
```
RESULT|Place|Lane|Id|Name|Team|Time|Delta|ReacTime
```

Example:
```
RESULT|1|4|123|John Smith|Team A|10.23|-|0.145
```

### Event Header Format:
```
START_RESULTS|Event|EventNum|Heat|Participants|Official
```

Example:
```
START_RESULTS|100 Meter Dash|5|1|8|OFFICIAL
```

### Running Time Format:
```
RUNNING|MM:SS.HH
```

Example:
```
RUNNING|01:23.45
```

---

## 🔧 Integration with Swimnerd Live

### Option 1: Replace the Receiver

Modify `finishlynx_receiver.py` to call your Swimnerd API:

```python
def update_result(self, result):
    """Update scoreboard with individual result"""
    # Call Swimnerd Live API
    import requests
    requests.post('http://localhost:3000/api/results', json=result)
```

### Option 2: Use as a Bridge

Run the receiver as a standalone service that:
1. Receives FinishLynx data on port 1024
2. Transforms it to Swimnerd format
3. Forwards to Swimnerd Live via HTTP/WebSocket

### Option 3: Native Integration

Add TCP listener directly to Swimnerd Live software:
- Listen on port 1024
- Parse incoming messages (use `finishlynx_receiver.py` as reference)
- Update scoreboard display in real-time

---

## 🌐 Network Setup

### Same Machine (Localhost)

FinishLynx and Swimnerd on same computer:
- FinishLynx sends to `127.0.0.1:1024`
- Swimnerd listens on `0.0.0.0:1024`

### Different Machines (LAN)

FinishLynx and Swimnerd on separate computers:
- FinishLynx sends to Swimnerd IP (e.g., `192.168.1.50:1024`)
- Swimnerd listens on `0.0.0.0:1024`
- **Firewall:** Ensure port 1024 is open on Swimnerd machine

### Broadcast Mode

FinishLynx sends to all devices on network:
- FinishLynx sends to `0.0.0.0:1024` (broadcast)
- Multiple Swimnerd instances can listen simultaneously
- Useful for backup displays or multiple scoreboards

---

## 🐛 Troubleshooting

### No Connection?

**Check FinishLynx:**
```
File → Options → Hardware → Scoreboard → Enabled ✓
```

**Check Firewall:**
```bash
# Mac
sudo lsof -i :1024

# Linux
sudo netstat -tulpn | grep 1024

# Windows
netstat -ano | findstr 1024
```

**Test with Telnet:**
```bash
telnet localhost 1024
```

### No Data Received?

- Results must be **finalized** in FinishLynx (not draft)
- Check FinishLynx logs: `File → View → Log`
- Verify scoreboard is enabled
- Try manual send: **Scoreboard → Send Results**

### Garbled Characters?

- Encoding issue: Ensure UTF-8 decoding
- Line endings: Should be `\r\n` (CRLF)
- Check for binary data: Use `errors='ignore'` in decode

---

## 📝 Customization

### Change Port

Edit `swimnerd.lss` header comment and update FinishLynx settings:
```
; Network/TCP Settings: -1,0.0.0.0,5000
```

Then in FinishLynx: Hardware → Port Number: `5000`

### Change Data Format

Want JSON instead of pipe-delimited?

Edit `swimnerd.lss`:
```lss
;;Result
; JSON format
\14\00{"place":"
\14\01%s","lane":"
\14\02%s","name":"
\14\04%s","team":"
\14\05%s","time":"
\14\06%s"}\0d\0a
```

### Add Split Times

If FinishLynx has split data:
```lss
;;Result
\14\00RESULT|
\14\01%s|
\14\02%s|
\14\04%s|
\14\06%s|
\14\08%s|      ; Cumulative split
\14\09%s\0d\0a  ; Last split
```

---

## 📚 Documentation

Full technical details in `FINISHLYNX_INTEGRATION.md`:
- LSS script format specification
- All available variables
- Group codes and variable codes
- Advanced customization
- Swimming-specific considerations

---

## 🤝 Support

### FinishLynx Resources

- **Official Site:** https://finishlynx.com
- **LSS Scripts:** https://finishlynx.com/support/display-and-scoreboard-scripts/
- **Manual:** https://finishlynx.com/wp-content/uploads/2022/06/finishlynx_version_4.pdf

### Swimnerd Support

Contact Nate Tschohl:
- **Twitter:** @SwimNerds
- **Email:** support@swimnerd.com
- **Website:** https://swimnerd.com

---

## 📜 License

MIT License - Free to use, modify, and distribute.

---

## 🎯 Use Cases

### Track & Field Meets

- Display track results on Swimnerd scoreboard
- Multi-sport events (track + swim)
- Shared venue with FinishLynx already installed

### Open Water Swimming

- FinishLynx at finish line
- Swimnerd displays results
- Backup timing system

### Triathlons

- Track swim exit times
- Coordinate with bike/run timing
- Unified results display

---

## 🚧 Roadmap

### v1.0 (Current)
- ✅ Basic TCP/IP integration
- ✅ Results output
- ✅ Running time display
- ✅ Python receiver demo

### v2.0 (Future)
- [ ] WebSocket support
- [ ] Real-time split display
- [ ] Heat/event scheduling
- [ ] HyTek file export
- [ ] Web dashboard

### v3.0 (Future)
- [ ] Bidirectional communication
- [ ] Start list import
- [ ] Multi-camera support
- [ ] Cloud sync

---

## 💡 Tips

1. **Test First:** Use FinishLynx demo mode before live events
2. **Backup:** Always have manual backup timing
3. **Network:** Use wired ethernet for reliability
4. **Logs:** Keep logs for troubleshooting
5. **Documentation:** Document your setup for future reference

---

**Ready to integrate? Start with Step 1 above! 🚀**
