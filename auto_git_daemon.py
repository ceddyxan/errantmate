import os
import time
import subprocess
from datetime import datetime
import threading

# Import the auto_git_push function
from auto_git_push import auto_git_push

class GitAutoDaemon:
    def __init__(self, check_interval=300):  # Default: 5 minutes
        self.check_interval = check_interval
        self.running = False
        self.last_commit_hash = None
        
    def get_current_commit_hash(self):
        """Get the current commit hash."""
        try:
            result = subprocess.run(
                "git rev-parse HEAD", 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=10,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None
    
    def has_changes(self):
        """Check if there are any uncommitted changes."""
        try:
            result = subprocess.run(
                "git status --porcelain", 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=10,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            if result.returncode == 0:
                return bool(result.stdout.strip())
        except:
            pass
        return False
    
    def check_and_push(self):
        """Check for changes and push if needed."""
        print(f"🔍 Checking for changes... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        
        if self.has_changes():
            print("📝 Changes detected, pushing to GitHub...")
            success = auto_git_push()
            if success:
                self.last_commit_hash = self.get_current_commit_hash()
                print("✅ Changes pushed successfully!")
            else:
                print("❌ Failed to push changes")
        else:
            print("✅ No changes detected")
    
    def run(self):
        """Run the daemon."""
        self.running = True
        self.last_commit_hash = self.get_current_commit_hash()
        
        print(f"🚀 Git Auto Daemon Started")
        print(f"⏰ Check interval: {self.check_interval} seconds")
        print(f"📍 Current commit: {self.last_commit_hash}")
        print(f"💡 Press Ctrl+C to stop")
        print("=" * 50)
        
        try:
            while self.running:
                self.check_and_push()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            print("\n🛑 Daemon stopped by user")
            self.running = False
        except Exception as e:
            print(f"\n❌ Daemon error: {e}")
            self.running = False
    
    def stop(self):
        """Stop the daemon."""
        self.running = False

def main():
    import sys
    
    # Parse command line arguments
    interval = 300  # Default 5 minutes
    
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
            if interval < 60:
                print("⚠️  Minimum interval is 60 seconds")
                interval = 60
        except ValueError:
            print("❌ Invalid interval. Using default (300 seconds)")
    
    # Create and run daemon
    daemon = GitAutoDaemon(check_interval=interval)
    daemon.run()

if __name__ == "__main__":
    main()
