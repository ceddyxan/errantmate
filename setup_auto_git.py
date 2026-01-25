import os
import sys
import subprocess
import platform

def create_task_scheduler():
    """Create a Windows Task Scheduler task for auto Git pushes."""
    
    if platform.system() != "Windows":
        print("❌ This script is designed for Windows only")
        return False
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = sys.executable
    daemon_script = os.path.join(project_dir, "auto_git_daemon.py")
    
    # Create a batch file for the task
    batch_content = f"""@echo off
cd /d "{project_dir}"
"{python_exe}" "{daemon_script}" 300
"""
    
    batch_file = os.path.join(project_dir, "run_auto_git.bat")
    with open(batch_file, 'w') as f:
        f.write(batch_content)
    
    print(f"📝 Created batch file: {batch_file}")
    
    # Create the task using PowerShell
    powershell_script = f'''
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c""{batch_file}""" 
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "ErrantMate Auto Git" -Description "Automatic Git pushes for ErrantMate project" -Action $action -Trigger $trigger -Settings $settings -Force
'''
    
    try:
        result = subprocess.run(
            ["powershell", "-Command", powershell_script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Task Scheduler task created successfully!")
            print("📅 Task will run daily at 9:00 AM")
            print("💡 You can modify the trigger in Task Scheduler if needed")
            return True
        else:
            print(f"❌ Failed to create task: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating task: {e}")
        return False

def show_manual_instructions():
    """Show manual setup instructions."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("\n📋 Manual Setup Instructions:")
    print("=" * 50)
    print("\n1️⃣  One-time Push (Immediate):")
    print(f"   cd \"{project_dir}\"")
    print("   python auto_git_push.py")
    
    print("\n2️⃣  Continuous Monitoring (Background):")
    print(f"   cd \"{project_dir}\"")
    print("   python auto_git_daemon.py")
    print("   💡 This will check every 5 minutes and auto-push changes")
    
    print("\n3️⃣  Custom Interval:")
    print("   python auto_git_daemon.py 600  # Check every 10 minutes")
    
    print("\n4️⃣  Quick Batch File:")
    print(f"   Double-click: {project_dir}\\auto_git_push.bat")
    
    print("\n5️⃣  Windows Task Scheduler (Advanced):")
    print("   Run: python setup_auto_git.py")
    print("   Or manually create a task in Windows Task Scheduler")

def main():
    print("🚀 ErrantMate Auto Git Setup")
    print("=" * 40)
    
    choice = input("\nChoose setup option:\n"
                  "1. Create Windows Task Scheduler task\n"
                  "2. Show manual instructions\n"
                  "3. Run one-time push now\n"
                  "4. Start continuous monitoring\n"
                  "Enter choice (1-4): ").strip()
    
    if choice == "1":
        create_task_scheduler()
    elif choice == "2":
        show_manual_instructions()
    elif choice == "3":
        from auto_git_push import auto_git_push
        auto_git_push()
    elif choice == "4":
        import sys
        interval = input("Check interval in seconds (default 300): ").strip()
        try:
            interval = int(interval) if interval else 300
            if interval < 60:
                print("Minimum interval is 60 seconds")
                interval = 60
        except:
            interval = 300
        
        sys.argv = [sys.argv[0], str(interval)]
        from auto_git_daemon import main as daemon_main
        daemon_main()
    else:
        print("❌ Invalid choice")
        show_manual_instructions()

if __name__ == "__main__":
    main()
