#!/usr/bin/env python3
import os
import re
import json
import requests
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def find_wdl_files(directory):
    """Find all WDL files in a directory and its subdirectories."""
    wdl_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.wdl'):
                wdl_files.append(os.path.join(root, file))
    return wdl_files


def extract_container_hashes(wdl_file):
    """Extract container hashes from a WDL file."""
    with open(wdl_file, 'r') as f:
        content = f.read()
    
    # Pattern to match docker container references with SHA256 hashes
    pattern = r'docker:\s*"~\{runtime_attributes\.container_registry\}/([^@]+)@sha256:([a-f0-9]{64})"'
    matches = re.findall(pattern, content)
    
    return [(wdl_file, container, sha) for container, sha in matches]


def get_tag_for_hash(container, sha_hash):
    """Query the quay.io API to find the tag for a SHA256 hash."""
    # Assuming all containers are in the pacbio namespace
    url = f"https://quay.io/api/v1/repository/pacbio/{container}/tag"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        for tag in data.get('tags', []):
            if tag.get('manifest_digest') == f"sha256:{sha_hash}":
                return tag.get('name')
        
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error querying API for {container}: {e}")
        return None


def process_wdl_file(wdl_file, container_tags, dry_run=True):
    """Update a WDL file with the tag format if matches are found."""
    with open(wdl_file, 'r') as f:
        content = f.read()
    
    modified = False
    changes = []
    
    for container, sha_hash in container_tags.keys():
        tag = container_tags[(container, sha_hash)]
        if tag:
            old_format = f'docker: "~{{runtime_attributes.container_registry}}/{container}@sha256:{sha_hash}"'
            new_format = f'docker: "~{{runtime_attributes.container_registry}}/{container}:{tag}"'
            
            if old_format in content:
                if dry_run:
                    changes.append((old_format, new_format))
                content = content.replace(old_format, new_format)
                modified = True
    
    if modified and not dry_run:
        with open(wdl_file, 'w') as f:
            f.write(content)
    
    return modified, changes


def main():
    parser = argparse.ArgumentParser(description='Convert SHA256 container references to tag format in WDL files')
    parser.add_argument('--directory', '-d', required=True, help='Directory containing WDL files')
    parser.add_argument('--output', '-o', help='Output file for the container-tag mapping (JSON)')
    parser.add_argument('--update', '-u', action='store_true', help='Update WDL files with tag format')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Show changes without modifying files')
    parser.add_argument('--threads', '-t', type=int, default=4, help='Number of threads for API requests')
    
    args = parser.parse_args()
    
    print(f"Finding WDL files in {args.directory}...")
    wdl_files = find_wdl_files(args.directory)
    print(f"Found {len(wdl_files)} WDL files")
    
    all_container_hashes = []
    for wdl_file in wdl_files:
        extracted = extract_container_hashes(wdl_file)
        all_container_hashes.extend(extracted)
    
    # Filter out duplicates while maintaining file information
    unique_hashes = {}
    for wdl_file, container, sha in all_container_hashes:
        key = (container, sha)
        if key not in unique_hashes:
            unique_hashes[key] = []
        unique_hashes[key].append(wdl_file)
    
    print(f"Found {len(unique_hashes)} unique container references")
    
    # Look up tags for each container hash
    container_tags = {}
    print("Looking up tags for container hashes...")
    
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_to_key = {
            executor.submit(get_tag_for_hash, container, sha): (container, sha)
            for (container, sha) in unique_hashes.keys()
        }
        
        for future in future_to_key:
            key = future_to_key[future]
            tag = future.result()
            container_tags[key] = tag
            container, sha = key
            if tag:
                print(f"Found tag '{tag}' for {container}@sha256:{sha}")
            else:
                print(f"No tag found for {container}@sha256:{sha}")
    
    # Output the container-tag mapping if requested
    if args.output:
        output_data = {
            f"{container}@sha256:{sha}": tag 
            for (container, sha), tag in container_tags.items() if tag
        }
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"Container-tag mapping written to {args.output}")
    
    # Show changes or update WDL files
    if args.update or args.dry_run:
        dry_run = args.dry_run or not args.update
        action_word = "Would update" if dry_run else "Updating"
        print(f"{action_word} WDL files...")
        
        updated_files = 0
        total_changes = 0
        
        for wdl_file in wdl_files:
            modified, changes = process_wdl_file(wdl_file, container_tags, dry_run=dry_run)
            if modified:
                updated_files += 1
                if dry_run:
                    rel_path = os.path.relpath(wdl_file, args.directory)
                    print(f"\nFile: {rel_path}")
                    for i, (old, new) in enumerate(changes, 1):
                        print(f"  Change {i}:")
                        print(f"    From: {old}")
                        print(f"    To:   {new}")
                    total_changes += len(changes)
        
        if dry_run:
            print(f"\nDry run summary: Would update {updated_files} WDL files with {total_changes} changes")
            print("Use --update to apply these changes")
        else:
            print(f"Updated {updated_files} WDL files")
    else:
        print("No changes made to WDL files")
        print("Use --dry-run to see potential changes")
        print("Use --update to modify the WDL files")


if __name__ == "__main__":
    main()