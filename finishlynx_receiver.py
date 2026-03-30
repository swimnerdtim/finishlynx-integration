#!/usr/bin/env python3
"""
FinishLynx TCP Receiver for Swimnerd
Listens for race results from FinishLynx and updates Swimnerd scoreboard

Usage:
    python3 finishlynx_receiver.py [--port PORT] [--host HOST]

Example:
    python3 finishlynx_receiver.py --port 1024
"""

import socket
import argparse
import json
from datetime import datetime

class FinishLynxReceiver:
    def __init__(self, host='0.0.0.0', port=1024):
        self.host = host
        self.port = port
        self.socket = None
        self.current_event = {}
        self.results = []
        
    def start(self):
        """Start listening for FinishLynx connections"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        
        print(f"[{self.timestamp()}] Swimnerd FinishLynx Receiver started")
        print(f"[{self.timestamp()}] Listening on {self.host}:{self.port}")
        print(f"[{self.timestamp()}] Waiting for FinishLynx connection...\n")
        
        try:
            while True:
                conn, addr = self.socket.accept()
                self.handle_connection(conn, addr)
        except KeyboardInterrupt:
            print(f"\n[{self.timestamp()}] Shutting down...")
        finally:
            if self.socket:
                self.socket.close()
    
    def handle_connection(self, conn, addr):
        """Handle incoming connection from FinishLynx"""
        print(f"[{self.timestamp()}] FinishLynx connected from {addr[0]}:{addr[1]}")
        
        try:
            buffer = ""
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                
                # Decode and add to buffer
                buffer += data.decode('utf-8', errors='ignore')
                
                # Process complete lines
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if line:
                        self.process_message(line)
        
        except Exception as e:
            print(f"[{self.timestamp()}] Error: {e}")
        
        finally:
            conn.close()
            print(f"[{self.timestamp()}] FinishLynx disconnected\n")
    
    def process_message(self, message):
        """Parse and process a message from FinishLynx"""
        print(f"[{self.timestamp()}] RX: {message}")
        
        if message.startswith("SWIMNERD_INIT|"):
            version = message.split('|')[1]
            print(f"[{self.timestamp()}] >>> Initialized (version: {version})")
        
        elif message.startswith("RUNNING|"):
            time_str = message.split('|')[1]
            print(f"[{self.timestamp()}] >>> Clock running: {time_str}")
            self.update_running_time(time_str)
        
        elif message.startswith("STOPPED|"):
            time_str = message.split('|')[1]
            print(f"[{self.timestamp()}] >>> Clock stopped: {time_str}")
            self.update_stopped_time(time_str)
        
        elif message.startswith("UPDATE|"):
            time_str = message.split('|')[1]
            self.update_running_time(time_str)
        
        elif message.startswith("START_RESULTS|"):
            parts = message.split('|')
            self.current_event = {
                'event': parts[1],
                'event_num': parts[2],
                'heat': parts[3],
                'participants': parts[4],
                'official': parts[5]
            }
            self.results = []
            print(f"[{self.timestamp()}] >>> Event: {parts[1]} (Heat {parts[3]})")
            print(f"[{self.timestamp()}] >>> Status: {parts[5]}")
        
        elif message.startswith("RESULT|"):
            parts = message.split('|')
            result = {
                'place': parts[1],
                'lane': parts[2],
                'id': parts[3],
                'name': parts[4],
                'team': parts[5],
                'time': parts[6],
                'delta': parts[7],
                'reac_time': parts[8]
            }
            self.results.append(result)
            print(f"[{self.timestamp()}] >>> {parts[1]:>3}. Lane {parts[2]} - {parts[4]:30} {parts[6]}")
            self.update_result(result)
        
        elif message.startswith("END_RESULTS"):
            print(f"[{self.timestamp()}] >>> Results complete ({len(self.results)} finishers)")
            self.finalize_results()
        
        elif message.startswith("WIND|"):
            wind = message.split('|')[1]
            print(f"[{self.timestamp()}] >>> Wind: {wind}")
            self.update_wind(wind)
        
        elif message.startswith("MESSAGE|"):
            text = message.split('|', 1)[1]
            print(f"[{self.timestamp()}] >>> Message: {text}")
            self.display_message(text)
        
        elif message.startswith("START_LIST|"):
            parts = message.split('|')
            print(f"[{self.timestamp()}] >>> Start List: {parts[1]} (Heat {parts[3]})")
        
        elif message.startswith("ENTRY|"):
            parts = message.split('|')
            print(f"[{self.timestamp()}] >>> Lane {parts[1]} - {parts[3]} ({parts[4]})")
        
        elif message.startswith("END_LIST"):
            print(f"[{self.timestamp()}] >>> Start list complete")
    
    def timestamp(self):
        """Return current timestamp for logging"""
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    # ========================
    # Swimnerd Integration
    # ========================
    # These methods would update your actual Swimnerd scoreboard
    
    def update_running_time(self, time_str):
        """Update scoreboard with running time"""
        # TODO: Send to Swimnerd Live scoreboard display
        pass
    
    def update_stopped_time(self, time_str):
        """Update scoreboard with stopped time"""
        # TODO: Send to Swimnerd Live scoreboard display
        pass
    
    def update_result(self, result):
        """Update scoreboard with individual result"""
        # TODO: Update Swimnerd scoreboard lane display
        # Example: Update lane result, show place, time, name
        pass
    
    def finalize_results(self):
        """Finalize results display"""
        # TODO: Mark results as official, save to database
        # Example: Save results to HyTek/Commit file format
        
        # Save to JSON for debugging
        output = {
            'event': self.current_event,
            'results': self.results,
            'timestamp': datetime.now().isoformat()
        }
        filename = f"results_{self.current_event.get('event_num', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"[{self.timestamp()}] >>> Saved to {filename}")
    
    def update_wind(self, wind):
        """Update scoreboard with wind reading"""
        # TODO: Display wind reading on scoreboard
        pass
    
    def display_message(self, text):
        """Display custom message on scoreboard"""
        # TODO: Show message on scoreboard display
        pass


def main():
    parser = argparse.ArgumentParser(description='FinishLynx TCP Receiver for Swimnerd')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=1024, help='Port to listen on (default: 1024)')
    args = parser.parse_args()
    
    receiver = FinishLynxReceiver(host=args.host, port=args.port)
    receiver.start()


if __name__ == '__main__':
    main()
