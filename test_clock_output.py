#!/usr/bin/env python3
"""
Test script to simulate FinishLynx output to a 6-digit clock
Use this to test your clock's serial/network input

Usage:
    # For serial port:
    python3 test_clock_output.py --serial /dev/ttyUSB0 --baud 9600
    
    # For network:
    python3 test_clock_output.py --host 192.168.1.100 --port 1024
"""

import argparse
import time
import serial
import socket

def test_serial(port, baud):
    """Test serial output to clock"""
    print(f"Opening serial port {port} at {baud} baud...")
    
    try:
        ser = serial.Serial(port, baud, timeout=1)
        print("Serial port opened successfully")
        
        # Test sequence
        times = ["00:00.00", "00:01.23", "00:05.67", "00:10.00", "01:23.45", "02:00.00"]
        
        for t in times:
            message = f"{t}\r\n"
            print(f"Sending: {message.strip()}")
            ser.write(message.encode('ascii'))
            time.sleep(2)
        
        ser.close()
        print("Test complete")
        
    except Exception as e:
        print(f"Error: {e}")

def test_network(host, port):
    """Test network output to clock"""
    print(f"Connecting to {host}:{port}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print("Connected successfully")
        
        # Test sequence
        times = ["00:00.00", "00:01.23", "00:05.67", "00:10.00", "01:23.45", "02:00.00"]
        
        for t in times:
            message = f"{t}\r\n"
            print(f"Sending: {message.strip()}")
            sock.send(message.encode('ascii'))
            time.sleep(2)
        
        sock.close()
        print("Test complete")
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Test 6-digit clock output')
    parser.add_argument('--serial', help='Serial port (e.g., /dev/ttyUSB0 or COM1)')
    parser.add_argument('--baud', type=int, default=9600, help='Baud rate (default: 9600)')
    parser.add_argument('--host', help='Network host IP')
    parser.add_argument('--port', type=int, help='Network port')
    args = parser.parse_args()
    
    if args.serial:
        test_serial(args.serial, args.baud)
    elif args.host and args.port:
        test_network(args.host, args.port)
    else:
        print("Error: Must specify either --serial or --host/--port")
        parser.print_help()

if __name__ == '__main__':
    main()
