import git
import os

def sync_to_github():
    try:
        repo = git.Repo(".") # Points to your current folder
        
        print("🔍 Checking for changes...")
        # 1. Add everything (picks up the new DB and deleted CSVs)
        repo.git.add(A=True) 
        
        # 2. Specifically ensure cache is cleared if files were deleted
        # GitPython's add(A=True) handles this, but we can be explicit:
        if repo.is_dirty() or repo.untracked_files:
            repo.index.commit("Auto-sync: Database rebuilt & old CSVs archived/removed")
            
            print("🚀 Pushing to GitHub...")
            origin = repo.remote(name='origin')
            origin.push()
            print("✅ Remote repository is now in sync.")
        else:
            print("ℹ️ No changes to commit.")
            
    except Exception as e:
        print(f"❌ Git Sync Error: {e}")

if __name__ == "__main__":
    sync_to_github()