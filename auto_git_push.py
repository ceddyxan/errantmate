import os
import subprocess
from datetime import datetime

def run_git_command(command, cwd=None):
    """Run a git command and return the result."""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def auto_git_push():
    """Automatically add, commit, and push changes to GitHub."""
    
    # Get the current directory (should be the project root)
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"🚀 Auto Git Push - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Project directory: {project_dir}")
    
    # 1. Check if we're in a git repository
    success, _, error = run_git_command("git rev-parse --git-dir", project_dir)
    if not success:
        print("❌ Not a Git repository")
        return False
    
    # 2. Check current status
    success, status_output, _ = run_git_command("git status --porcelain", project_dir)
    if not success:
        print("❌ Failed to check git status")
        return False
    
    if not status_output.strip():
        print("✅ No changes to commit")
        return True
    
    print(f"📝 Changes detected:")
    for line in status_output.strip().split('\n'):
        print(f"   {line}")
    
    # 3. Add all changes
    print("📦 Adding all changes...")
    success, _, error = run_git_command("git add .", project_dir)
    if not success:
        print(f"❌ Failed to add changes: {error}")
        return False
    
    # 4. Check what's staged
    success, staged_output, _ = run_git_command("git diff --cached --name-only", project_dir)
    if success and staged_output.strip():
        print(f"📋 Staged files:")
        for file in staged_output.strip().split('\n'):
            print(f"   - {file}")
    
    # 5. Commit with automatic message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Auto-update - {timestamp}"
    
    print(f"💬 Committing with message: '{commit_message}'")
    success, _, error = run_git_command(f'git commit -m "{commit_message}"', project_dir)
    if not success:
        if "nothing to commit" in error.lower():
            print("✅ Nothing new to commit")
            return True
        print(f"❌ Failed to commit: {error}")
        return False
    
    # 6. Push to GitHub
    print("📤 Pushing to GitHub...")
    success, push_output, error = run_git_command("git push origin master", project_dir)
    if not success:
        print(f"❌ Failed to push: {error}")
        return False
    
    print("✅ Successfully pushed to GitHub!")
    print(f"📊 Push output: {push_output}")
    return True

if __name__ == "__main__":
    auto_git_push()
