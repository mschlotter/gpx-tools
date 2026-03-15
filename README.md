# GPX Tools

A collection of file type conversion scripts and Python utilities for processing and analyzing GPX (GPS Exchange Format) files. 

## File Type Conversion Scripts (Bash)
- **IGC2GPX** - Converts IGC files from flight recorders to GPX files using gpsbabel

## Python Scripts

- **GPX_MAXPATH** - Finds the longest path with X straight edges in a GPX track
- **GPX_RDP** - Reduces GPX file size using the Ramer-Douglas-Peucker algorithm

## Installation

### Prerequisites

- Python 3.13+
- UV package manager ([install UV](https://github.com/astral-sh/uv))
- GPSBabel for file type conversions

### Clone Repository

```bash
git clone https://github.com/mschlotter/gpx-tools.git
cd gpx-tools
```

### Install Dependencies and Build Package

```bash
uv sync
```

## Usage

### GPX_MAXPATH - Find Longest Path

Finds the longest path with X straight edges in GPX tracks and filters based on distance threshold. The input files are assumed to be GPX files, converted from IGC files with the igc2gpx.sh script.

It uses dynamic programming to calculate the longest path of n (default: 3) straight
edges. All GPX files from an input directory 'gpx_input' are processed and those whose
n-edge path is longer than the specified threshold (default: 100km) are moved
to the output directory 'gpx_processed', mirroring the original subfolder structure. Only the
first track and its first segment in the input GPX file are processed and
preserved. The route (= declaration) is converted to waypoints, and the four
points corresponding to the n-edge path are stored as route in the output GPX
file.

The output file name is DATE_IGC_REG_LEN.GPX, where DATE is the date of the GPX
file, IGC is the original .IGC file name, REG is the competition number or
registration number of the aircraft, and LEN is the length of the longest n-edge
path in km.

```bash
# Basic usage
uv run gpx_maxpath

# With custom configuration
uv run gpx_maxpath -c my_config.yml
```

#### Command Line Arguments

| Argument | Short | Default | Description |
|------|-------|---------|------------|
| `--config` | `-c` | `gpx_maxpath.yml` | Path to configuration file |
| `--prefix` | `-p` | `.` | Prefix path for directories |
| `--dist` | `-d` | `100` | Minimum distance threshold (km) |
| `--edg` | `-e` | `3` | Number of straight edges |

### GPX_RDP - Reduce GPX Size

Reduces GPX file size by simplifying track points using the RDP algorithm.

It removes all GPX extensions and reduces the number of track points with the
Rahmer-Douglas-Peuker algorithm.

Files from an input directory 'gpx_input' are:
1. copied unmodified to a data store directory 'gpx_original'
2. stripped of the extensions and then placed in a directory 'gpx_purged'
3. simplified with the RDP algorithm and stored in the directory 'gpx_rdp'

```bash
# Basic usage
uv run gpx_rdp

# With custom configuration
uv run gpx_rdp -c my_config.yml
```

#### Command Line Arguments

| Argument | Short | Default | Description |
|------|-------|---------|------------|
| `--config` | `-c` | `gpx_rdp.yml` | Path to configuration file |
| `--prefix` | `-p` | `.` | Prefix path for directories |
| `--epsilon` | `-e` | `1.0` | RDP epsilon threshold (meters) |


## Configuration

Configuration files are YAML-based. Example `gpx_maxpath.yml`:

```yaml
prefix: /path/to/project
dist: 100
edg: 3
```

Example `gpx_rdp.yml`:

```yaml
prefix: /path/to/project
epsilon: 1.0
```

## Known Issues

- Large GPX files may process slowly due to O(n³) algorithm complexity
- No built-in logging module (uses print statements)
- Limited error handling for malformed GPX files

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues and questions, please open an issue on the GitHub repository.

---

**Version:** 0.1.0  
**Last Updated:** March 2026
