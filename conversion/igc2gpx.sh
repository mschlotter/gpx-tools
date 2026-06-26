#!/bin/bash

### global variables
PROGRAM="igc2gpx"
AUTHOR="Michael Schlotter"
REVISION="20250518"

DEFAULT_INPUT_DIR="./igc_input"
DEFAULT_OUTPUT_DIR="./gpx_output"
GPSBABEL_CMD="gpsbabel"

### functions
function display_usage {
cat << _EOF_
Usage: $(basename "$0") [--input INPUT_DIRECTORY] [--output OUTPUT_DIRECTORY]

Converts IGC files to GPX files using gpsbabel.

Options:
  --input DIR       Optional. Directory containing .igc files (and subdirectories).
                    Defaults to '$DEFAULT_INPUT_DIR'.
  --output DIR      Optional. Directory where .gpx files will be stored.
                    Defaults to '$DEFAULT_OUTPUT_DIR'.
  -h, --help        Display this help message and exit.

Requires 'gpsbabel' to be installed and in the system PATH.
_EOF_
}

function setup_and_validate_paths {
    # resolve potential relative paths to absolute paths for robustness
    INPUT_DIR=$(realpath "$1")
    OUTPUT_DIR=$(realpath "$2")

    # check if gpsbabel is installed
    if ! command -v "$GPSBABEL_CMD" &> /dev/null; then
        echo "Error: '$GPSBABEL_CMD' command not found." >&2
        echo "Please install gpsbabel." >&2
        return 1
    fi

    # Check if input directory exists
    if [ ! -d "$INPUT_DIR" ]; then
        echo "Error: Input directory '$INPUT_DIR' not found." >&2
        return 1
    fi

    # prevent using the same directory for input and output
    if [ "$INPUT_DIR" == "$OUTPUT_DIR" ]; then
        echo "Error: Input and output dirs cannot be the same ('$INPUT_DIR')." >&2
        return 1
    fi

    # create the base output directory if it doesn't exist
    if ! mkdir -p "$OUTPUT_DIR"; then
        echo "Error: Could not create output directory '$OUTPUT_DIR'." >&2
        return 1
    fi

    echo "Input Directory:  $INPUT_DIR"
    echo "Output Directory: $OUTPUT_DIR"
    return 0
}

function perform_conversion {
    local current_input_dir="$1"
    local current_output_dir="$2"

    echo "Starting conversion..."

    # find all .igc files in the input directory and subdirectories
    # -print0 and read -d $'\0' handle filenames with spaces or special chars
    find "$current_input_dir" -type f -iname '*.igc' -print0 | while IFS= read -r -d $'\0' igc_file; do
        
		# calculate the relative path of the igc file with respect to the INPUT_DIR
        local relative_path="${igc_file#$current_input_dir/}"

        # construct the full path for the output GPX file
        local output_path_base="$current_output_dir/$relative_path"
        local gpx_file="${output_path_base%.*}.gpx" # Use %.* to remove last extension robustly

        local gpx_dir
        gpx_dir=$(dirname "$gpx_file")

        # create the corresponding output subdirectory if it doesn't exist
        if ! mkdir -p "$gpx_dir"; then
            echo "Warning: Could not create subdirectory '$gpx_dir'. Skipping '$igc_file'." >&2
            continue # Skip to the next file
        fi

        echo "Converting '$relative_path' -> '${gpx_file#$current_output_dir/}'"

        # run gpsbabel for conversion
        if ! "$GPSBABEL_CMD" -i igc -f "$igc_file" -o gpx -F "$gpx_file"; then
             echo "Error: Failed to convert '$igc_file'. Check $GPSBABEL_CMD output." >&2
             # optional: remove potentially incomplete/empty output file
             # rm -f "$gpx_file"
        fi
    done

    echo "Conversion process finished."
}

### main
INPUT_DIR=""
OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            display_usage
            exit 0
            ;;
        -i|--input)
            if [[ -n "$2" && ! "$2" =~ ^- ]]; then
                INPUT_DIR="$2"
                shift 2
            else
                echo "Error: -i/--input requires a directory argument." >&2
                exit 1
            fi
            ;;
        -o|--output)
            if [[ -n "$2" && ! "$2" =~ ^- ]]; then
                OUTPUT_DIR="$2"
                shift 2
            else
                echo "Error: -o/--output requires a directory argument." >&2
                exit 1
            fi
            ;;
        *)
            echo "Error: Unknown option '$1'. Use --help for usage." >&2
            exit 1
            ;;
    esac
done

# apply defaults for any unspecified arguments
INPUT_DIR="${INPUT_DIR:-$DEFAULT_INPUT_DIR}"
OUTPUT_DIR="${OUTPUT_DIR:-$DEFAULT_OUTPUT_DIR}"

# perform setup and validation - exit if it fails
if ! setup_and_validate_paths "$INPUT_DIR" "$OUTPUT_DIR"; then
    exit 1
fi

# call the main conversion function with resolved paths
perform_conversion "$INPUT_DIR" "$OUTPUT_DIR"

exit 0