#!/usr/bin/env python3
"""
FinishLynx to Swimnerd Clock Bridge
Converts ASCII time strings to binary protocol for Swimnerd clock

Usage:
    python3 finishlynx_to_swimnerd_bridge.py --finishlynx-port 1024 --clock-port COM5

Flow:
    FinishLynx → TCP 1024 (ASCII) → This script → Bluetooth COM5 (Binary) → Clock
"""

import socket
import serial
import argparse
import struct
from datetime import datetime

class FinishLynxBridge:
    def __init__(self, tcp_port=1024, serial_port='COM5', baud=9600):
        self.tcp_port = tcp_port
        self.serial_port = serial_port
        self.baud = baud
        self.ser = None
        self.sock = None
        
    def start(self):
        """Start bridge server"""
        # Open serial port to clock
        self.ser = serial.Serial(self.serial_port, self.baud, timeout=1)
        print(f"[{self.ts()}] Connected to Swimnerd clock on {self.serial_port}")
        
        # Initialize clock
        self.send_binary_time(0, 0, 0)
        
        # Listen for FinishLynx
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', self.tcp_port))
        self.sock.listen()
        
        print(f"[{self.ts()}] Listening for FinishLynx on port {self.tcp_port}")
        print(f"[{self.ts()}] Configure FinishLynx to send to localhost:{self.tcp_port}\n")
        
        try:
            while True:
                conn, addr = self.sock.accept()
                self.handle_connection(conn, addr)
        except KeyboardInterrupt:
            print(f"\n[{self.ts()}] Shutting down...")
        finally:
            if self.ser:
                self.ser.close()
            if self.sock:
                self.sock.close()
    
    def handle_connection(self, conn, addr):
        """Handle FinishLynx connection"""
        print(f"[{self.ts()}] FinishLynx connected from {addr[0]}:{addr[1]}")
        
        try:
            buffer = ""
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                
                buffer += data.decode('utf-8', errors='ignore')
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if line:
                        self.process_message(line)
        
        except Exception as e:
            print(f"[{self.ts()}] Error: {e}")
        
        finally:
            conn.close()
            print(f"[{self.ts()}] FinishLynx disconnected\n")
    
    def process_message(self, message):
        """Parse ASCII message and send binary to clock"""
        print(f"[{self.ts()}] RX: {message}")
        
        # Check for commands
        if message == "CLR":
            self.send_binary_time(0, 0, 0)
            return
        
        # Parse time: "MM:SS.HH" or "M:SS.HH"
        try:
            parts = message.replace('.', ':').split(':')
            if len(parts) >= 3:
                minutes = int(parts[0])
                seconds = int(parts[1])
                hundredths = int(parts[2])
                
                self.send_binary_time(minutes, seconds, hundredths)
        
        except ValueError:
            print(f"[{self.ts()}] Warning: Could not parse time: {message}")
    
    def send_binary_time(self, minutes, seconds, hundredths):
        """Send time to clock in binary format"""
        
        # TODO: ADJUST THIS BASED ON YOUR CLOCK'S PROTOCOL
        # Choose one of the formats below:
        
        # Format 1: Packed BCD (most common)
        # Each byte = hex value (e.g., 23 seconds = 0x23)
        data = bytes([minutes, seconds, hundredths])
        
        # Format 2: Raw binary values
        # data = struct.pack('BBB', minutes, seconds, hundredths)
        
        # Format 3: With header/footer
        # HEADER = 0xFF, FOOTER = 0xFE
        # data = bytes([0xFF, minutes, seconds, hundredths, 0xFE])
        
        # Format 4: 32-bit milliseconds (little-endian)
        # total_ms = (minutes * 60 * 1000) + (seconds * 1000) + (hundredths * 10)
        # data = struct.pack('<I', total_ms)
        
        # Send to clock
        self.ser.write(data)
        
        print(f"[{self.ts()}] TX: {minutes:02d}:{seconds:02d}.{hundredths:02d} → {data.hex().upper()}")
    
    def ts(self):
        """Timestamp for logging"""
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def main():
    parser = argparse.ArgumentParser(description='FinishLynx to Swimnerd Clock Bridge')
    parser.add_argument('--finishlynx-port', type=int, default=1024,
                        help='TCP port to receive from FinishLynx (default: 1024)')
    parser.add_argument('--clock-port', default='COM5',
                        help='Serial port for Swimnerd clock (default: COM5)')
    parser.add_argument('--baud', type=int, default=9600,
                        help='Serial baud rate (default: 9600)')
    args = parser.parse_args()
    
    bridge = FinishLynxBridge(
        tcp_port=args.finishlynx_port,
        serial_port=args.clock_port,
        baud=args.baud
    )
    bridge.start()


if __name__ == '__main__':
    main()
