import os
import hashlib
from collections import defaultdict

def hash_file(filepath, block_size=65536):
    """Generates an MD5 hash for a given file."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read(block_size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(block_size)
    return hasher.hexdigest()

def find_duplicates(directory):
    """
    Finds duplicate files (based on MD5 hash) in the given directory and its subdirectories.
    
    Args:
        directory (str): The path to the directory to scan.

    Returns:
        dict: A dictionary where keys are MD5 hashes and values are lists of file paths
              that share that hash (i.e., duplicates).
    """
    hashes_by_size = defaultdict(list)
    duplicates = defaultdict(list)
    
    # First pass: Group files by size. This is a quick pre-filter to reduce hashing time.
    # Only files of the same size can be exact duplicates.
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath): # Ensure it's a file, not a broken symlink
                try:
                    file_size = os.path.getsize(filepath)
                    hashes_by_size[file_size].append(filepath)
                except OSError as e:
                    print(f"Warning: Could not access file {filepath} - {e}")
                    continue

    # Second pass: For files with the same size, calculate their MD5 hash.
    for file_size, file_paths in hashes_by_size.items():
        if len(file_paths) > 1: # Only proceed if there are multiple files of the same size
            for filepath in file_paths:
                try:
                    file_hash = hash_file(filepath)
                    duplicates[file_hash].append(filepath)
                except OSError as e:
                    print(f"Warning: Could not hash file {filepath} - {e}")
                    continue
    
    # Filter out entries where there are no actual duplicates (hash only has one file)
    actual_duplicates = {hash_val: paths for hash_val, paths in duplicates.items() if len(paths) > 1}
    
    return actual_duplicates

def main():
    # IMPORTANT: Replace this with the actual path to your photo/video album folder
    # where you have the 269 files.
    target_directory = "A:\Drive\Tamannah-07\Tamannah-07\Thumbnails" 
    # Or for macOS/Linux: "/Users/YourUser/Pictures/MyAlbum"

    if not os.path.isdir(target_directory):
        print(f"Error: Directory '{target_directory}' not found.")
        print("Please update 'target_directory' in the script to your actual album path.")
        return

    print(f"Scanning '{target_directory}' for duplicate files...")
    duplicate_files = find_duplicates(target_directory)

    if not duplicate_files:
        print("No duplicate files found based on content.")
    else:
        print("\n--- Duplicate Files Found ---")
        total_duplicates_found = 0
        for md5_hash, file_paths in duplicate_files.items():
            print(f"\nHash: {md5_hash}")
            for path in file_paths:
                print(f"  - {path}")
            total_duplicates_found += (len(file_paths) - 1) # Count extra copies
        print(f"\nTotal unique duplicate sets: {len(duplicate_files)}")
        print(f"Total individual duplicate files (extra copies): {total_duplicates_found}")

        # You can also write the list to a file for easier comparison
        output_filename = "local_duplicates.txt"
        with open(output_filename, 'w') as f:
            f.write("--- Duplicate Files Found ---\n")
            for md5_hash, file_paths in duplicate_files.items():
                f.write(f"\nHash: {md5_hash}\n")
                for path in file_paths:
                    f.write(f"  - {path}\n")
        print(f"\nList of duplicate files also saved to '{output_filename}'")

if __name__ == "__main__":
    main()