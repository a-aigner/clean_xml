import re
import os
import shutil
import zipfile  # Assuming .aen is a ZIP-like archive
from collections import Counter
import sys


def clean_xml_content(content):
    """Cleans the problematic characters from XML content."""
    problematic_pattern = r'[\x00-\x08\x0B\x0C\x0E-\x1F]'
    problematic_chars = re.findall(problematic_pattern, content)
    char_count = Counter(problematic_chars)
    cleaned_content = re.sub(problematic_pattern, '', content)
    return cleaned_content, char_count


def process_aen_file(aen_path):
    """Processes the .aen file, cleans .xml files, and recreates the .aen archive."""
    print(f"Starting process for: {aen_path}")

    # Create temporary extraction directory
    temp_dir = "temp_aen_extracted"
    if os.path.exists(temp_dir):
        print("Cleaning up old temporary directory...")
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    print(f"Temporary extraction directory created: {temp_dir}")

    # Extract .aen file
    print(f"Extracting .aen file: {aen_path}")
    with zipfile.ZipFile(aen_path, 'r') as archive:
        archive.extractall(temp_dir)
    print("Extraction complete.")

    # Initialize counters for reporting
    total_replacements = 0
    detailed_counts = Counter()

    # Process each .xml file
    print("Scanning for .xml files...")
    for root, _, files in os.walk(temp_dir):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(root, file)
                print(f"Processing XML file: {file_path}")

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Clean the XML content
                cleaned_content, char_count = clean_xml_content(content)
                detailed_counts.update(char_count)
                total_replacements += sum(char_count.values())

                # Write the cleaned content back to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                print(f"Cleaned and updated: {file_path}")

    # Print detailed report
    print("\nDetailed report of problematic characters:")
    for char, count in detailed_counts.items():
        print(f"Character: U+{ord(char):04X} | Count: {count}")
    print(f"\nTotal number of problematic characters found: {total_replacements}")

    # Recreate the .aen archive
    cleaned_aen_path = aen_path.replace('.aen', '_cleaned.aen')
    print(f"Recreating .aen file: {cleaned_aen_path}")
    with zipfile.ZipFile(cleaned_aen_path, 'w') as archive:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                archive_path = os.path.relpath(file_path, temp_dir)
                archive.write(file_path, archive_path)
    print("Recreation of .aen file complete.")

    # Cleanup temporary directory
    print("Cleaning up temporary directory...")
    shutil.rmtree(temp_dir)
    print(f"Temporary directory {temp_dir} removed.")

    print(f"\nProcess complete. Cleaned .aen file saved to: {cleaned_aen_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python clean_aen.py <path_to_aen_file>")
        sys.exit(1)

    aen_file_path = sys.argv[1]
    if not aen_file_path.endswith('.aen'):
        print("Error: The file must have a .aen extension.")
        sys.exit(1)

    if not os.path.exists(aen_file_path):
        print(f"Error: File '{aen_file_path}' does not exist.")
        sys.exit(1)

    process_aen_file(aen_file_path)
