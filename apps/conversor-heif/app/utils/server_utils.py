import os
import socket
import signal
import psutil
from typing import Optional, List, Tuple
from pathlib import Path
import time


class ServerManager:
    """Robust server management with port conflict detection and resolution"""
    
    def __init__(self, default_port: int = 8000):
        self.default_port = default_port
        self.pid_file = Path("temp/server.pid")
        self.pid_file.parent.mkdir(exist_ok=True)
    
    def find_available_port(self, start_port: int = None) -> int:
        """
        Find an available port starting from the given port
        
        Args:
            start_port: Port to start searching from (default: self.default_port)
            
        Returns:
            Available port number
        """
        start_port = start_port or self.default_port
        
        for port in range(start_port, start_port + 100):  # Try 100 ports
            if self.is_port_available(port):
                return port
        
        raise RuntimeError(f"No available ports found starting from {start_port}")
    
    def is_port_available(self, port: int) -> bool:
        """
        Check if a port is available for use
        
        Args:
            port: Port number to check
            
        Returns:
            True if port is available, False otherwise
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                result = sock.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def get_processes_using_port(self, port: int) -> List[Tuple[int, str]]:
        """
        Get list of processes using a specific port
        
        Args:
            port: Port number to check
            
        Returns:
            List of tuples (pid, process_name)
        """
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    connections = proc.info['connections']
                    if connections:
                        for conn in connections:
                            if (hasattr(conn, 'laddr') and 
                                conn.laddr and 
                                conn.laddr.port == port):
                                processes.append((proc.info['pid'], proc.info['name']))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            print(f"Error checking processes: {e}")
        
        return processes
    
    def terminate_processes_on_port(self, port: int, force: bool = False) -> bool:
        """
        Terminate processes using a specific port
        
        Args:
            port: Port number
            force: If True, use SIGKILL instead of SIGTERM
            
        Returns:
            True if successful, False otherwise
        """
        processes = self.get_processes_using_port(port)
        
        if not processes:
            return True
        
        print(f"Found {len(processes)} processes using port {port}")
        
        for pid, name in processes:
            try:
                proc = psutil.Process(pid)
                
                # Don't kill system processes or browsers
                if name.lower() in ['chrome', 'firefox', 'safari', 'edge']:
                    print(f"Skipping browser process: {name} (PID: {pid})")
                    continue
                
                print(f"Terminating {name} (PID: {pid})")
                
                if force:
                    proc.kill()
                else:
                    proc.terminate()
                    
                # Wait for process to terminate
                try:
                    proc.wait(timeout=5)
                    print(f"Process {pid} terminated successfully")
                except psutil.TimeoutExpired:
                    if not force:
                        print(f"Process {pid} didn't terminate, forcing...")
                        proc.kill()
                        proc.wait(timeout=2)
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"Could not terminate process {pid}: {e}")
                continue
        
        # Verify port is now available
        time.sleep(1)
        return self.is_port_available(port)
    
    def save_server_pid(self, pid: int):
        """Save server PID to file for later cleanup"""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(pid))
        except Exception as e:
            print(f"Warning: Could not save PID file: {e}")
    
    def cleanup_previous_server(self) -> bool:
        """
        Clean up any previous server instance
        
        Returns:
            True if cleanup successful or no cleanup needed
        """
        if not self.pid_file.exists():
            return True
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is still running
            try:
                proc = psutil.Process(pid)
                if proc.is_running():
                    print(f"Found previous server process (PID: {pid}), terminating...")
                    proc.terminate()
                    proc.wait(timeout=5)
                    print("Previous server terminated successfully")
                
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                # Process already dead or took too long
                pass
            
            # Remove PID file
            self.pid_file.unlink(missing_ok=True)
            return True
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return False
    
    def prepare_server_start(self, preferred_port: int = None) -> int:
        """
        Prepare for server start: cleanup previous instances and find available port
        
        Args:
            preferred_port: Preferred port to use
            
        Returns:
            Port number to use for the server
        """
        preferred_port = preferred_port or self.default_port
        
        # Step 1: Cleanup any previous server instances
        print("🧹 Cleaning up previous server instances...")
        self.cleanup_previous_server()
        
        # Step 2: Check if preferred port is available
        if self.is_port_available(preferred_port):
            print(f"✅ Port {preferred_port} is available")
            return preferred_port
        
        # Step 3: Try to free the preferred port
        print(f"⚠️  Port {preferred_port} is in use, attempting to free it...")
        if self.terminate_processes_on_port(preferred_port):
            if self.is_port_available(preferred_port):
                print(f"✅ Port {preferred_port} freed successfully")
                return preferred_port
        
        # Step 4: Find alternative port
        print(f"🔍 Finding alternative port...")
        available_port = self.find_available_port(preferred_port + 1)
        print(f"✅ Using port {available_port} instead")
        
        return available_port
    
    def register_cleanup_handlers(self):
        """Register signal handlers for graceful shutdown"""
        def cleanup_handler(signum, frame):
            print("\n🛑 Shutting down server...")
            self.cleanup_previous_server()
            exit(0)
        
        signal.signal(signal.SIGINT, cleanup_handler)
        signal.signal(signal.SIGTERM, cleanup_handler)
