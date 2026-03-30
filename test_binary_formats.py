#!/usr/bin/env python3
"""
Test different binary formats to determine Swimnerd clock protocol

This script sends the time "01:23.45" in various binary formats
to help you identify which format your clock expects.

Usage:
    python3 test_binary_formats.py --port COM5
"""

import serial
import argparse
import time
import struct

def test_formats(port, baud=9600):
    """Test various binary time formats"""
    
    print(f"Opening {port} at {baud} baud...")
    ser = serial.Serial(port, baud, timeout=1)
    print("Connected!\n")
    
    # Test time: 01:23.45
    minutes = 1
    seconds = 23
    hundredths = 45
    
    print("Testing different binary formats for time: 01:23.45")
    print("=" * 60)
    
    # Test 1: Packed BCD (most common)
    print("\nTest 1: Packed BCD")
    print("Description: Each byte is hex (23 seconds = 0x23)")
    data = bytes([0x01, 0x23, 0x45])
    print(f"Sending: {data.hex().upper()} ({len(data)} bytes)")
    ser.write(data)
    time.sleep(3)
    input("Does clock show 01:23.45? (Press Enter to continue)")
    
    # Test 2: Raw binary values
    print("\nTest 2: Raw Binary Values")
    print("Description: Direct integer values")
    data = bytes([1, 23, 45])
    print(f"Sending: {data.hex().upper()} ({len(data)} bytes)")
    ser.write(data)
    time.sleep(3)
    input("Does clock show 01:23.45? (Press Enter to continue)")
    
    # Test 3: With start/stop bytes
    print("\nTest 3: With Header/Footer Markers")
    print("Description: 0xFF [data] 0xFE")
    data = bytes([0xFF, 0x01, 0x23, 0x45, 0xFE])
    print(f"Sending: {data.hex().upper()} ({len(data)} bytes)")
    ser.write(data)
    time.sleep(3)
    input("Does clock show 01:23.45? (Press Enter to continue)")
    
    # Test 4: 16-bit values (little-endian)
    print("\nTest 4: 16-bit Little-Endian")
    print("Description: MM, SS, HH as 16-bit integers")
    data = struct.pack('<HHH', minutes, seconds, hundredths)
    print(f"Sending: {data.hex().upper()} ({len(data)} bytes)")
    ser.write(data)
    time.sleep(3)
    input("Does clock show 01:23.45? (Press Enter to continue)")
    
    # Test 5: 32-bit milliseconds
    print("\nTest 5: Total Milliseconds (32-bit)")
    print("Description: Single 32-bit value = total ms")
    total_ms = (minutes * 60 * 1000) + (seconds * 1000) + (hundredths * 10)
    data = struct.pack('<I', total_ms)  # Little-endian
    print(f"Sending: {data.hex().upper()} ({len(data)} bytes) = {total_ms} ms")
    ser.write(data)
    time.sleep(3)
    input("Does clock show 01:23.45? (Press Enter to continue)")
    
    # Test 6: ASCII with binary header
    print("\nTest 6: Binary Header + ASCII")
    print("Description: 0xAA [ASCII time] 0x0A")
    data = bytes([0xAA]) + b"01:23.45" + bytes([0x0A])
    print(f"Sending: {data.hex().upper()} ({len(data)} bytes)")
    ser.write(data)
    time.sleep(3)
    input("Does clock show 01:23.45? (Press Enter to continue)")
    
    # Test 7: Reversed byte order
    print("\nTest 7: Reversed Order (HH:SS:MM)")
    print("Description: Hundredths first, minutes last")
    data = bytes([0x45, 0x23, 0x01])
    print(f"Sending: {data.hex().upper()} ({len(data)} bytes)")
    ser.write(data)
    time.sleep(3)
    input("Does clock show 01:23.45? (Press Enter to continue)")
    
    # Clear test
    print("\nTest 8: Clear/Reset Command")
    print("Trying common clear patterns...")
    
    patterns = [
        (bytes([0x00, 0x00, 0x00]), "Zeros (00:00.00)"),
        (bytes([0xFF, 0xFF, 0xFF]), "All 0xFF"),
        (bytes([0xCC]), "Single 0xCC byte"),
        (bytes([0xAA, 0x00, 0xBB]), "0xAA 0x00 0xBB")
    ]
    
    for data, desc in patterns:
        print(f"\n  Trying: {desc}")
        print(f"  Sending: {data.hex().upper()}")
        ser.write(data)
        time.sleep(2)
    
    input("\nDid any clear pattern work? (Press Enter to finish)")
    
    ser.close()
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("\nWhich test worked? Tell me the number and I'll")
    print("configure the bridge script with the correct format.")


def main():
    parser = argparse.ArgumentParser(description='Test Swimnerd clock binary formats')
    parser.add_argument('--port', required=True,
                        help='Serial port (e.g., COM5 or /dev/cu.HC-08)')
    parser.add_argument('--baud', type=int, default=9600,
                        help='Baud rate (default: 9600)')
    args = parser.parse_args()
    
    test_formats(args.port, args.baud)


if __name__ == '__main__':
    main()
