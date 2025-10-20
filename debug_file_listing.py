"""
Debug script to check file upload and listing issues
"""
import os
import json

def check_uploads_folder():
    """Check if uploads folder exists and has files"""
    upload_folder = 'shared_files'  # Changed from 'uploads' to match app.py
    if not os.path.exists(upload_folder):
        print(f"❌ Upload folder '{upload_folder}' does NOT exist!")
        return []
    
    files = os.listdir(upload_folder)
    print(f"\n✓ Upload folder exists: {os.path.abspath(upload_folder)}")
    print(f"✓ Total files in folder: {len(files)}")
    
    if files:
        print("\nFiles found:")
        for i, f in enumerate(files[:10], 1):  # Show first 10
            filepath = os.path.join(upload_folder, f)
            size = os.path.getsize(filepath)
            print(f"  {i}. {f} ({size:,} bytes)")
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more files")
    else:
        print("  (No files found)")
    
    return files

def check_file_metadata():
    """Check file metadata database"""
    metadata_file = 'data/file_metadata.json'
    if not os.path.exists(metadata_file):
        print(f"\n❌ Metadata file '{metadata_file}' does NOT exist!")
        return {}
    
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    print(f"\n✓ Metadata file exists: {metadata_file}")
    print(f"✓ Files in metadata: {len(metadata)}")
    
    if metadata:
        print("\nMetadata entries:")
        for i, (filename, data) in enumerate(list(metadata.items())[:5], 1):
            owner = data.get('owner', 'Unknown')
            permission = data.get('permission', 'public')
            print(f"  {i}. {filename}")
            print(f"     Owner: {owner}, Permission: {permission}")
        if len(metadata) > 5:
            print(f"  ... and {len(metadata) - 5} more entries")
    
    return metadata

def check_users():
    """Check users database"""
    users_file = 'data/users.json'
    if not os.path.exists(users_file):
        print(f"\n❌ Users file '{users_file}' does NOT exist!")
        return {}
    
    with open(users_file, 'r') as f:
        users = json.load(f)
    
    print(f"\n✓ Users file exists: {users_file}")
    print(f"✓ Total users: {len(users)}")
    
    if users:
        print("\nRegistered users:")
        for i, username in enumerate(list(users.keys())[:5], 1):
            user_data = users[username]
            role = user_data.get('role', 'user')
            print(f"  {i}. {username} (role: {role})")
    
    return users

def check_sync_issues(files, metadata):
    """Check for sync issues between uploads folder and metadata"""
    print("\n" + "=" * 60)
    print("SYNC CHECK: Upload folder vs Metadata")
    print("=" * 60)
    
    files_set = set(files)
    metadata_set = set(metadata.keys())
    
    # Files in folder but not in metadata
    missing_metadata = files_set - metadata_set
    if missing_metadata:
        print(f"\n⚠️  Files WITHOUT metadata ({len(missing_metadata)}):")
        for f in list(missing_metadata)[:5]:
            print(f"  - {f}")
        if len(missing_metadata) > 5:
            print(f"  ... and {len(missing_metadata) - 5} more")
    else:
        print("\n✓ All files in upload folder have metadata")
    
    # Metadata entries without actual files
    orphaned_metadata = metadata_set - files_set
    if orphaned_metadata:
        print(f"\n⚠️  Metadata WITHOUT actual files ({len(orphaned_metadata)}):")
        for f in list(orphaned_metadata)[:5]:
            print(f"  - {f}")
        if len(orphaned_metadata) > 5:
            print(f"  ... and {len(orphaned_metadata) - 5} more")
    else:
        print("\n✓ All metadata entries have corresponding files")
    
    return missing_metadata, orphaned_metadata

def main():
    print("=" * 60)
    print("FILE UPLOAD & LISTING DEBUG TOOL")
    print("=" * 60)
    
    # Check uploads folder
    files = check_uploads_folder()
    
    # Check metadata
    metadata = check_file_metadata()
    
    # Check users
    users = check_users()
    
    # Check sync issues
    if files or metadata:
        missing_metadata, orphaned_metadata = check_sync_issues(files, metadata)
    
    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSIS")
    print("=" * 60)
    
    issues_found = []
    
    if not os.path.exists('uploads'):
        issues_found.append("❌ Upload folder missing - create it!")
    elif not files:
        issues_found.append("⚠️  No files in upload folder - try uploading a file")
    
    if not os.path.exists('data/file_metadata.json'):
        issues_found.append("❌ Metadata file missing")
    
    if not os.path.exists('data/users.json'):
        issues_found.append("❌ Users file missing - authentication required")
    elif not users:
        issues_found.append("⚠️  No users registered - create an account first")
    
    if files and metadata:
        missing_metadata, orphaned_metadata = check_sync_issues(files, metadata)
        if missing_metadata:
            issues_found.append(f"⚠️  {len(missing_metadata)} files missing metadata")
        if orphaned_metadata:
            issues_found.append(f"⚠️  {len(orphaned_metadata)} orphaned metadata entries")
    
    if not issues_found:
        print("\n✅ Everything looks good!")
        print("\nIf files still don't show in UI:")
        print("  1. Check browser console (F12) for errors")
        print("  2. Check if you're logged in")
        print("  3. Try refreshing the page")
        print("  4. Check Network tab for /files API response")
    else:
        print("\n⚠️  Issues found:")
        for issue in issues_found:
            print(f"  {issue}")
        
        print("\n📋 RECOMMENDED ACTIONS:")
        if "Upload folder missing" in str(issues_found):
            print("  1. Create uploads folder: mkdir uploads")
        if "No users registered" in str(issues_found):
            print("  2. Register a user account via /login")
        if "No files in upload folder" in str(issues_found):
            print("  3. Upload a test file")
        if "files missing metadata" in str(issues_found):
            print("  4. Metadata may be out of sync - files uploaded before auth system")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
