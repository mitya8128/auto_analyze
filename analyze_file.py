import argparse
from assert_inserter import process_file


if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Analyze Python file.")
    parser.add_argument('py_file', type=str, help="file to to analyze")

    # Parse arguments
    args = parser.parse_args()

    # Analyze the specific file
    process_file(args.py_file)
