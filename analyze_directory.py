import argparse
from assert_inserter import analyze_directory


if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Analyze Python files in a directory and check with CrossHair.")
    parser.add_argument('directory', type=str, help="Directory to analyze")

    # Parse arguments
    args = parser.parse_args()

    # Analyze the specified directory
    analyze_directory(args.directory)
