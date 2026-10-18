import argparse
import hashlib
import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class FileState:
    path: str
    hash: str
    size: int
    mod_time: float

def get_file_hash(filepath: Path) -> str:
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return ""

def scan_directory(dir_path: Path) -> dict:
    state = {}
    for filepath in dir_path.rglob('*'):
        if filepath.is_file():
            rel_path = str(filepath.relative_to(dir_path))
            stat = filepath.stat()
            file_hash = get_file_hash(filepath)
            state[rel_path] = asdict(FileState(rel_path, file_hash, stat.st_size, stat.st_mtime))
    return state

def main():
    parser = argparse.ArgumentParser(description="File Integrity Monitor")
    parser.add_argument("--dir", required=True, type=str, help="Directory to monitor")
    parser.add_argument("--baseline", required=True, type=str, help="Path to baseline JSON")
    parser.add_argument("--mode", choices=["generate", "check"], required=True, help="Mode: generate or check")
    parser.add_argument("--log-file", type=str, default="fim_audit.log", help="Log file path")
    
    args = parser.parse_args()
    logging.basicConfig(filename=args.log_file, level=logging.WARNING, format='[%(levelname)s] %(message)s')
    
    target_dir = Path(args.dir)
    baseline_file = Path(args.baseline)

    if not target_dir.exists() or not target_dir.is_dir():
        print(f"Error: Directory {args.dir} does not exist.")
        return

    print(f"[INFO] Scanning directory: {args.dir}")
    current_state = scan_directory(target_dir)

    if args.mode == "generate":
        with open(baseline_file, 'w', encoding='utf-8') as f:
            json.dump(current_state, f, indent=4)
        print(f"[INFO] Baseline generated at {args.baseline}")

    elif args.mode == "check":
        if not baseline_file.exists():
            print("Error: Baseline file not found.")
            return
        
        with open(baseline_file, 'r', encoding='utf-8') as f:
            baseline_state = json.load(f)

        created = set(current_state.keys()) - set(baseline_state.keys())
        deleted = set(baseline_state.keys()) - set(current_state.keys())
        modified = [p for p in set(current_state.keys()).intersection(set(baseline_state.keys())) 
                    if current_state[p]["hash"] != baseline_state[p]["hash"]]

        print("\n=== File Integrity Inspection Summary ===")
        print(f"Total monitored files : {len(baseline_state)}")
        print(f"Created files         : {len(created)}")
        print(f"Deleted files         : {len(deleted)}")
        print(f"Modified files        : {len(modified)}\n")

        if created or deleted or modified:
            print("=== Detected Anomalies ===")
            for path in created:
                print(f"[CREATED] {path} (Size: {current_state[path]['size']} B)")
                logging.warning(f"File created: {path}")
            for path in deleted:
                print(f"[DELETED] {path}")
                logging.warning(f"File deleted: {path}")
            for path in modified:
                print(f"[MODIFIED] {path}")
                print(f"  Expected SHA-256 : {baseline_state[path]['hash']}")
                print(f"  Actual SHA-256   : {current_state[path]['hash']}")
                logging.warning(f"File modified: {path}")
            print(f"\n[WARNING] Security alerts detected! Check audit log at {args.log_file}")
        else:
            print("[INFO] No anomalies detected.")

if __name__ == "__main__":
    main()