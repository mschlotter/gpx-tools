# GPX Tools

A collection of Python utilities for processing and analyzing GPX (GPS Exchange Format) files. 

## Scripts

- **GPX_MAXPATH** - Find the longest path with X straight edges in GPX tracks
- **GPX_RDP** - Reduce GPX file size using the Ramer-Douglas-Peucker algorithm

## Installation

### Prerequisites

- Python 3.13+
- UV package manager ([install UV](https://github.com/astral-sh/uv))

### Clone Repository

```bash
git clone https://github.com/yourusername/gpx-tools.git
cd gpx-tools
```

### Install Dependencies and Build Package

```bash
uv sync
```

## Usage

### GPX_MAXPATH - Find Longest Path

Finds the longest path with X straight edges in GPX tracks and filters based on distance threshold.

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
