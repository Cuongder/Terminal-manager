"""System process helper functions."""

import subprocess
import os
import re

def kill_port(port: int) -> bool:
    """Kill process running on specified port."""
    try:
        if os.name == 'nt':  # Windows
            # Find PID using netstat
            cmd = f'netstat -ano | findstr :{port}'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if not result.stdout:
                return False
                
            # Extract PID (last column)
            lines = result.stdout.strip().split('\n')
            pids = set()
            for line in lines:
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid != '0':
                        pids.add(pid)
            
            if not pids:
                return False
                
            # Kill processes
            for pid in pids:
                subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
            return True
            
        else:  # Linux/Mac
            cmd = f'lsof -t -i:{port}'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(f'kill -9 {pid}', shell=True)
                return True
                
    except Exception as e:
        print(f"Error killing port {port}: {e}")
    return False

def check_port_in_use(port: int) -> bool:
    """Check if a port is in use."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0
