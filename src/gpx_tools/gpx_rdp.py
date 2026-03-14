"""GPX_RDP reduces the size of GPX files using the RDP algorithm.

It removes all GPX extensions and reduces the number of track points with the
Rahmer-Douglas-Peuker algorithm.

Files from an input directory are:
1. copied unmodified to a data store directory gpx_original
2. stripped of the extensions and then placed in a directory gpx_purged
3. simplified with the RDP algorithm and stored in the directory gpx_rdp
"""

import argparse
import os
import gpxpy
from . import gpx_io as io


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "-c", "--config", type=str, nargs='?', default="gpx_rdp.yml",
        help="path to configuration file (default: gpx_rdp.yml)")
    parser.add_argument(
        "-p", "--prefix", type=str, nargs='?', const=".", default=None,
        help="prefix path (default: from config or current directory)")
    parser.add_argument(
        "-e", "--epsilon", type=float, nargs='?',
        default=1.0, const=1.0,
        help="RDP epsilon threshold in meters (default: %(default)s)")
    return parser.parse_args()

def main(args=None):
    """Main function to process GPX files.
    
    Args:
       args (argparse.Namespace): command line arguments (optional)
    """
    
    if args is None:
        args = parse_arguments()
    
    # load configuration
    config = io.load_config(args.config)
    
    # use config values or fall back to command line arguments or default
    if args.prefix is not None:
        prefix = args.prefix
    elif config and 'prefix' in config:
        prefix = config['prefix']
    else:
        prefix = '.'
    print(f"Using prefix path: {prefix}")

    # specify the directory paths
    input_directory = os.path.join(prefix, "gpx_input", "")
    original_directory = os.path.join(prefix, "gpx_original", "")
    purged_directory = os.path.join(prefix, "gpx_purged", "")
    rdp_directory = os.path.join(prefix, "gpx_rdp", "")

    # iterate over all files in the specified input directory
    input_paths = io.list_files(input_directory)
    for input_path in input_paths:

        # backup original file
        original_path = os.path.join(original_directory, os.path.split(input_path)[1])
        io.backup_file(input_path, original_path)

        # open file
        with open(input_path,'r') as input_file:
            data = gpxpy.parse(input_file)
        data_points = data.get_points_no()

        # strip extensions
        for track in data.tracks:
            for segment in track.segments:
                for point in segment.points:
                    point.extensions = None
        purged_path = os.path.join(purged_directory, os.path.split(input_path)[1])
        io.check_file(purged_path)
        with open(purged_path, "w", newline='\n') as purged_file:
            purged_file.write(data.to_xml(prettyprint=False))
        print(f"Purged file {purged_path} created with {data_points} data points")
        
        # use config values or fall back to command line arguments or defaults
        epsilon = args.epsilon if args.epsilon is not None else config.get('epsilon', 1.0) if config else 1.0

        # reduce number of points with the RDP algorithm
        data.simplify(epsilon)
        rdp_points = data.get_points_no()
        rdp_path = os.path.join(rdp_directory, os.path.split(input_path)[1])
        io.check_file(rdp_path)
        with open(rdp_path, "w", newline='\n') as rdp_file:
            rdp_file.write(data.to_xml(prettyprint=False))
        print(f"Simplified file {rdp_path} created with {rdp_points} data points.")

if __name__ == "__main__":
    main()
