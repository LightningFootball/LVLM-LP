#!/usr/bin/env python3
"""
Script to download, setup and truncate VizWiz dataset.
Downloads VizWiz dataset, extracts files, and truncates to specified ratio.

Usage:
    # Basic usage - download, extract and truncate to 10%
    python truncate_vizwiz_dataset.py --data-dir /data --ratio 0.1

    # Only download and extract, skip truncation
    python truncate_vizwiz_dataset.py --data-dir /data --download-only

    # Only truncate existing dataset (skip download)
    python truncate_vizwiz_dataset.py --data-dir /data --truncate-only --ratio 0.1

    # Truncate specific datasets
    python truncate_vizwiz_dataset.py --data-dir /data --datasets val train --ratio 0.2

    # Skip dependency installation (if already installed)
    python truncate_vizwiz_dataset.py --data-dir /data --skip-install

Features:
    - Preserves downloaded zip files for reuse
    - Creates 'original' backup of extracted files
    - Skips download/extraction if already completed
    - Parallel downloading for faster speed
    - Supports multiple truncation ratios
"""

import json
import shutil
import argparse
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def install_dependencies():
    """
    Install system dependencies: aria2c and unzip
    """
    print("Installing system dependencies...")
    try:
        subprocess.run(['apt', 'update'], check=True)
        subprocess.run(['apt', 'install', '-y', 'aria2', 'unzip'], check=True)
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        print("Please install aria2 and unzip manually")
        sys.exit(1)

def download_file(url, output_dir):
    """
    Download a single file using aria2c with multi-threading
    """
    filename = url.split('/')[-1]
    output_path = output_dir / filename

    print(f"Downloading {filename}...")
    try:
        subprocess.run([
            'aria2c',
            '-x', '16',  # 16 connections per server
            '-s', '16',  # split into 16 segments
            '-d', str(output_dir),
            '-o', filename,
            url
        ], check=True)
        print(f"Successfully downloaded {filename}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error downloading {filename}: {e}")
        return None

def download_vizwiz_dataset(data_dir):
    """
    Download all VizWiz dataset files in parallel (skip if already exists)
    """
    vizwiz_dir = data_dir / "VizWiz"
    vizwiz_dir.mkdir(parents=True, exist_ok=True)

    urls = [
        "https://vizwiz.cs.colorado.edu/VizWiz_final/images/train.zip",
        "https://vizwiz.cs.colorado.edu/VizWiz_final/images/val.zip",
        "https://vizwiz.cs.colorado.edu/VizWiz_final/images/test.zip",
        "https://vizwiz.cs.colorado.edu/VizWiz_final/vqa_data/Annotations.zip"
    ]

    # Check if all files already exist
    all_files_exist = True
    expected_files = []
    for url in urls:
        filename = url.split('/')[-1]
        file_path = vizwiz_dir / filename
        expected_files.append(file_path)
        if not file_path.exists():
            all_files_exist = False
            break

    if all_files_exist:
        print("All zip files already downloaded, skipping download...")
        return expected_files, vizwiz_dir

    print(f"Downloading VizWiz dataset to {vizwiz_dir}")
    print("Starting parallel downloads...")

    # Download files in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(download_file, url, vizwiz_dir): url for url in urls}

        downloaded_files = []
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                if result:
                    downloaded_files.append(result)
            except Exception as exc:
                print(f"Download generated an exception for {url}: {exc}")

    return downloaded_files, vizwiz_dir

def extract_files(downloaded_files, vizwiz_dir):
    """
    Extract all downloaded zip files and create original backup
    """
    print("Extracting downloaded files...")

    # Create original backup directory
    original_dir = vizwiz_dir / "original"
    original_dir.mkdir(exist_ok=True)

    for file_path in downloaded_files:
        if file_path and file_path.suffix == '.zip':
            print(f"Extracting {file_path.name}...")
            try:
                # Extract to original directory first
                subprocess.run(['unzip', '-o', str(file_path), '-d', str(original_dir)], check=True)
                print(f"Successfully extracted {file_path.name} to original/")
                # Do NOT remove zip file - keep for reuse
            except subprocess.CalledProcessError as e:
                print(f"Error extracting {file_path.name}: {e}")

    # Move annotation files to the correct location in original
    annotations_dir = original_dir / "Annotations"
    if annotations_dir.exists():
        for json_file in annotations_dir.glob("*.json"):
            shutil.move(str(json_file), str(original_dir / json_file.name))
        # Remove empty annotations directory
        if annotations_dir.exists() and not any(annotations_dir.iterdir()):
            annotations_dir.rmdir()

    # Copy original files to working directory
    copy_original_to_working(vizwiz_dir)

def copy_original_to_working(vizwiz_dir):
    """
    Copy files from original backup to working directory
    """
    original_dir = vizwiz_dir / "original"
    if not original_dir.exists():
        print("Original backup directory not found!")
        return

    print("Copying original files to working directory...")

    # Copy all directories and files from original to working
    for item in original_dir.iterdir():
        dest_path = vizwiz_dir / item.name
        if item.is_dir():
            if dest_path.exists():
                shutil.rmtree(dest_path)
            shutil.copytree(item, dest_path)
        else:
            if dest_path.exists():
                dest_path.unlink()
            shutil.copy2(item, dest_path)

    print("Files copied from original backup")

def truncate_dataset(dataset_dir, dataset_name, truncate_ratio=0.1):
    """
    Truncate a dataset to specified ratio.

    Args:
        dataset_dir: Path to dataset directory
        dataset_name: Name of dataset (e.g., 'val', 'train', 'test')
        truncate_ratio: Ratio to keep (default 0.1 for 10%)
    """

    json_file = Path(dataset_dir) / f"{dataset_name}.json"
    image_dir = Path(dataset_dir) / dataset_name

    # Use original names for output (no backup needed)
    output_json = json_file
    output_dir = image_dir

    if not json_file.exists():
        print(f"JSON file {json_file} not found!")
        return

    if not image_dir.exists():
        print(f"Image directory {image_dir} not found!")
        return

    print(f"Processing {dataset_name} dataset...")

    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    original_count = len(data)
    target_count = int(original_count * truncate_ratio)

    print(f"Original data count: {original_count}")
    print(f"Target count ({truncate_ratio*100}%): {target_count}")

    # Truncate data
    truncated_data = data[:target_count]

    # Save truncated JSON (overwrite original)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(truncated_data, f, ensure_ascii=False, indent=2)

    print(f"Updated {output_json} with truncated data")

    # Get list of images to keep
    images_to_keep = set()
    for item in truncated_data:
        image_name = item.get('image', '')
        if image_name:
            images_to_keep.add(image_name)

    # Remove unwanted images from original directory
    removed_count = 0
    missing_images = []

    for image_file in list(image_dir.glob('*')):
        if image_file.is_file() and image_file.name not in images_to_keep:
            image_file.unlink()
            removed_count += 1

    # Check for missing images
    for image_name in images_to_keep:
        if not (image_dir / image_name).exists():
            missing_images.append(image_name)

    print(f"Kept {len(images_to_keep)} images, removed {removed_count} images from: {output_dir}")

    if missing_images:
        print(f"Warning: {len(missing_images)} images were missing:")
        for img in missing_images[:5]:  # Show first 5 missing
            print(f"  - {img}")
        if len(missing_images) > 5:
            print(f"  ... and {len(missing_images) - 5} more")

def main():
    parser = argparse.ArgumentParser(description='Download, setup and truncate VizWiz dataset')
    parser.add_argument('--data-dir', default='/data',
                        help='Path to data directory (default: /data)')
    parser.add_argument('--datasets', nargs='+', default=['val', 'train', 'test'],
                        help='Dataset names to process for truncation')
    parser.add_argument('--ratio', type=float, default=0.1,
                        help='Truncation ratio (default: 0.1 for 10%)')
    parser.add_argument('--download-only', action='store_true',
                        help='Only download and extract, skip truncation')
    parser.add_argument('--skip-install', action='store_true',
                        help='Skip system dependencies installation')
    parser.add_argument('--truncate-only', action='store_true',
                        help='Only truncate existing dataset, skip download')

    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    print(f"Data directory: {data_dir}")
    print(f"Truncation ratio: {args.ratio} ({args.ratio*100}%)")
    print("=" * 60)

    # Step 1: Install dependencies (unless skipped)
    if not args.truncate_only and not args.skip_install:
        install_dependencies()
        print("=" * 60)

    # Step 2: Download and extract dataset (unless truncate-only)
    if not args.truncate_only:
        downloaded_files, vizwiz_dir = download_vizwiz_dataset(data_dir)

        # Check if original backup already exists
        original_dir = vizwiz_dir / "original"
        if original_dir.exists() and any(original_dir.iterdir()):
            print("Original backup already exists, skipping extraction...")
            # Still copy to working directory
            copy_original_to_working(vizwiz_dir)
        elif downloaded_files:
            extract_files(downloaded_files, vizwiz_dir)
            print("Dataset download and extraction completed!")
        else:
            print("No files were downloaded successfully!")
            return
        print("=" * 60)

        if args.download_only:
            print("Download-only mode: Skipping truncation")
            return

    # Step 3: Truncate dataset
    vizwiz_dir = data_dir / "VizWiz"
    if not vizwiz_dir.exists():
        print(f"VizWiz directory not found at {vizwiz_dir}")
        print("Please run without --truncate-only first to download the dataset")
        return

    # If truncate-only, make sure to copy from original backup first
    if args.truncate_only:
        original_dir = vizwiz_dir / "original"
        if original_dir.exists() and any(original_dir.iterdir()):
            print("Restoring files from original backup before truncation...")
            copy_original_to_working(vizwiz_dir)
        else:
            print("Warning: Original backup not found. Truncating existing files.")

    print("Starting dataset truncation...")
    print(f"Processing datasets: {args.datasets}")
    print("-" * 50)

    for dataset_name in args.datasets:
        try:
            truncate_dataset(vizwiz_dir, dataset_name, args.ratio)
            print("-" * 50)
        except Exception as e:
            print(f"Error processing {dataset_name}: {e}")
            continue

    print("All operations completed successfully!")

if __name__ == "__main__":
    main()