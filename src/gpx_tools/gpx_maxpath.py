"""GXP_MAXPATH finds the longest path with X straight edges in a GPX track.

It uses dynamic programming to calculate the longest path of n (default: 3)
straight edges. All GPX files from an input directory 'gpx_input' are processed
and those whose n-edge path is longer than the specified threshold (default:
100km) are moved to the output directory 'gpx_processed', mirroring the original
subfolder structure. Only the first track and its first segment in the input GPX
file are processed and preserved. The route (= declaration) is converted to
waypoints, and the four points corresponding to the n-edge path are stored as
route in the output GPX file.

The output file name is DATE_IGC_REG_LEN.GPX, where DATE is the date of the GPX
file, IGC is the original .IGC file name, REG is the competition number or
registration number of the aircraft, and LEN is the length of the longest n-edge
path in km.
"""

import argparse
import math
import os
import gpxpy
import numpy as np
from . import gpx_io as io


def parse_arguments():
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        nargs="?",
        default="gpx_maxpath.yml",
        help="path to configuration file (default: gpx_maxpath.yml)",
    )
    parser.add_argument(
        "-p",
        "--prefix",
        type=str,
        nargs="?",
        const=".",
        default=None,
        help="prefix path (default: from config or current directory)",
    )
    parser.add_argument(
        "-d",
        "--dist",
        type=float,
        nargs="?",
        default=100,
        const=100,
        help="min. distance of the n-segment path in km (default: %(default)s)",
    )
    parser.add_argument(
        "-e",
        "--edg",
        type=int,
        nargs="?",
        default=3,
        const=3,
        help="number of straight edges of the path (default: %(default)s)",
    )
    return parser.parse_args()


def haversine_distance(p1, p2):
    """Calculates the great-circle distance between two points on the Earth.

    Args:
        p1 (gpxpy.GPXTrackPoint): first point
        p2 (gpxpy.GPXTrackPoint): second point

    Returns:
        float: The distance between p1 and p2 in kilometers
    """
    lat1, lon1 = p1.latitude, p1.longitude
    lat2, lon2 = p2.latitude, p2.longitude

    # convert decimal degrees to radians for trigonometric functions
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # differences in coordinates
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Haversine formula
    R = 6371  # radius of Earth in kilometers - use 3956 for miles
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c  # distance in kilometers

    return distance


def find_longest_path(segment, edges):
    """Finds the longest path with n straight edges in a track.

    Args:
        segment (gpxpy.GPXTrackSegment): track segment
        edges (int): number of path edges

    Returns:
        tuple: (max_length, list_of_n+1_points)
            - max_length (float): the length of the longest n-edge path in km
            - list_of_n+1_points_coords (list): n+1 vertices of that path
        Returns (0, []) if no such path can be formed (e.g., if N < n+1).
    """
    N = segment.get_points_no()

    # if fewer than n+1 points, no n-edge path exists
    if N < edges + 1:
        print(f"Track has too few points. Cannot form a {edges}-edge path.")
        return 0, []

    # Initialize dynamic programming tables
    # dpX_lengths[j,X] stores the max length of an X-edge path ending at P[j]
    # dpX_parents[j,X] stores the index of the point *before* P[j] in that path
    # init lengths to 0.0, if distances are positive, any found path will be > 0
    # init parent indices to -1 (an invalid index) to indicate no path found yet
    dp_lengths = np.zeros((N, edges), dtype=float)
    dp_parents = np.full((N, edges), -1, dtype=int)

    # calculate longest paths with 1, 2, ..., n-edges iteratively
    # A 1-edge path is P[i] -> P[j], where i < j.
    # It ends at P[j], so j must be at least 1.
    for edge in range(edges):
        for j in range(edge + 1, N):  # P[j] is endpoint of the edge
            for i in range(edge, j):  # P[i] is startpoint of the edge
                if edge == 0:  # path length of first edge
                    path_length = haversine_distance(
                        segment.points[i], segment.points[j]
                    )
                else:  # path length with multiple edges
                    if dp_parents[i, edge - 1] == -1:  # make sure, start is valid
                        continue
                    path_length = dp_lengths[i, edge - 1] + haversine_distance(
                        segment.points[i], segment.points[j]
                    )
                if path_length > dp_lengths[j, edge]:
                    dp_lengths[j, edge] = path_length
                    dp_parents[j, edge] = i  # store P[i] as  parent of P[j]

    # find the maximum length by iterating through all possible endpoints
    max_overall_length = 0.0
    best_final_point_idx = -1
    for idx in range(edges, N):
        if dp_lengths[idx, edges - 1] > max_overall_length:
            max_overall_length = dp_lengths[idx, edges - 1]
            best_final_point_idx = idx  # P[idx] is the current best endpoint

    if best_final_point_idx == -1:  # no path was found
        return 0, []

    # reconstruct path by backtracking using parent pointers
    idx = best_final_point_idx
    path_points_indices = [idx]
    for edge in reversed(range(edges)):
        idx = dp_parents[idx, edge]
        path_points_indices.append(idx)
    path_points_indices.reverse()

    # sanity check: all reconstructed indices should be valid.
    if -1 in path_points_indices:
        print("Error in path reconstruction: one or more parent indices are invalid.")
        return 0, []

    path_points = [segment.points[i] for i in path_points_indices]

    return max_overall_length, path_points


def generate_filename(data, input_filename, max_length):
    """Generates the filename of the output file.

    Args:
        data (gpxpy.GPX): GPX data
        input_filename (str): input file name
        max_length (float): length of the longest n-edge path

    Returns:
        str: the output file name
    """
    # date
    date = data.tracks[0].segments[0].get_time_bounds().start_time.strftime("%Y%m%d")

    # competition_id
    competition_id = ""
    description = data.tracks[0].description
    components = description.split("~")
    for component in components:
        if "HFCIDCOMPETITIONID:" in component:
            competition_id = component.split(":")[1]
            break

    # filename
    filename = (
        date
        + "_"
        + os.path.splitext(input_filename)[0]
        + "_"
        + competition_id
        + "_"
        + str(int(max_length))
        + ".gpx"
    )

    return filename


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
    elif config and "prefix" in config:
        prefix = config["prefix"]
    else:
        prefix = "."
    print(f"Using prefix path: {prefix}")

    # specify the directory paths
    input_directory = os.path.join(prefix, "gpx_input", "")
    output_directory = os.path.join(prefix, "gpx_processed", "")

    # use config values or fall back to command line arguments or defaults
    dist = (
        args.dist
        if args.dist is not None
        else config.get("dist", 100)
        if config
        else 100
    )
    edg = args.edg if args.edg is not None else config.get("edg", 3) if config else 3

    # iterate over all files in the specified input directory
    input_paths = io.list_files(input_directory)
    for input_path in input_paths:
        # open file
        with open(input_path, "r") as input_file:
            data = gpxpy.parse(input_file)
            input_filename = os.path.split(input_path)[1]

        # validate GPX structure before accessing
        if not data.tracks:
            print(f"File {input_filename}: No tracks found - skipping.")
            continue
        if not data.tracks[0].segments:
            print(f"File {input_filename}: No segments in first track - skipping.")
            continue

        # find longest path
        segment = data.tracks[0].segments[0]
        max_length, path_points = find_longest_path(segment, edg)

        # process, if path length is equal or greater than threshold
        if max_length < dist:
            print(
                f"File {input_filename}:"
                f"path length {max_length:.2f} km < threshold {dist} km"
                " - skipping."
            )
            continue
        else:
            print(
                f"File {input_filename}:"
                f"Path length {max_length:.2f} km > threshold {dist} km"
                " - processing."
            )

        # keep first track only
        del data.tracks[1:]

        # copy route (declaration) as waypoints if defined
        data.waypoints.clear()
        if data.routes:
            for rtp in data.routes[0].points:
                data.waypoints.append(
                    gpxpy.gpx.GPXWaypoint(
                        rtp.latitude,
                        rtp.longitude,
                        name=rtp.name,
                        comment=rtp.comment,
                        description=rtp.description,
                    )
                )

        # add path points as route
        data.routes.clear()
        route = gpxpy.gpx.GPXRoute()
        for ptp in path_points:
            route.points.append(
                gpxpy.gpx.GPXWaypoint(
                    ptp.latitude, ptp.longitude, ptp.elevation, ptp.time
                )
            )
        data.routes.append(route)

        # save output, mirroring subfolder structure
        relative_path_dir = os.path.relpath(
            os.path.dirname(input_path), input_directory
        )
        output_subdir = os.path.join(output_directory, relative_path_dir)

        if not os.path.exists(output_subdir):
            os.makedirs(output_subdir)
            print(f"Created output subdirectory: {output_subdir}")

        output_filename = generate_filename(data, input_filename, max_length)
        output_path = os.path.join(output_subdir, output_filename)

        io.check_file(output_path)
        with open(output_path, "w", newline="\n") as output_file:
            output_file.write(data.to_xml())
        print(f"Processed file saved as {output_filename}.")


if __name__ == "__main__":
    main()
