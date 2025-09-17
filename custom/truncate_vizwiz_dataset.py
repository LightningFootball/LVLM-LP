#!/usr/bin/env python3
"""
Script to truncate VizWiz dataset to 10% of original size.
Processes JSON files and corresponding image directories.
"""

import json
import os
import shutil
import argparse
from pathlib import Path

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

    # Create output directories
    output_json = Path(dataset_dir) / f"{dataset_name}_10percent.json"
    output_dir = Path(dataset_dir) / f"{dataset_name}_10percent"

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
    print(f"Target count (10%): {target_count}")

    # Truncate data
    truncated_data = data[:target_count]

    # Save truncated JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(truncated_data, f, ensure_ascii=False, indent=2)

    print(f"Saved truncated JSON to: {output_json}")

    # Create output image directory
    output_dir.mkdir(exist_ok=True)

    # Copy corresponding images
    copied_count = 0
    missing_images = []

    for item in truncated_data:
        image_name = item.get('image', '')
        if image_name:
            src_path = image_dir / image_name
            dst_path = output_dir / image_name

            if src_path.exists():
                shutil.copy2(src_path, dst_path)
                copied_count += 1
            else:
                missing_images.append(image_name)

    print(f"Copied {copied_count} images to: {output_dir}")

    if missing_images:
        print(f"Warning: {len(missing_images)} images were missing:")
        for img in missing_images[:5]:  # Show first 5 missing
            print(f"  - {img}")
        if len(missing_images) > 5:
            print(f"  ... and {len(missing_images) - 5} more")

def main():
    parser = argparse.ArgumentParser(description='Truncate VizWiz dataset to 10%')
    parser.add_argument('--dataset-dir', default='/Volumes/Relax/download/Compressed/dataset/',
                        help='Path to dataset directory')
    parser.add_argument('--datasets', nargs='+', default=['val', 'train', 'test'],
                        help='Dataset names to process')
    parser.add_argument('--ratio', type=float, default=0.1,
                        help='Truncation ratio (default: 0.1 for 10%)')

    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir)

    if not dataset_dir.exists():
        print(f"Dataset directory {dataset_dir} not found!")
        return

    print(f"Dataset directory: {dataset_dir}")
    print(f"Processing datasets: {args.datasets}")
    print(f"Truncation ratio: {args.ratio} ({args.ratio*100}%)")
    print("-" * 50)

    for dataset_name in args.datasets:
        try:
            truncate_dataset(dataset_dir, dataset_name, args.ratio)
            print("-" * 50)
        except Exception as e:
            print(f"Error processing {dataset_name}: {e}")
            continue

if __name__ == "__main__":
    main()