# Hardware Fetcher

Advanced hardware detection and analysis tool for Linux systems. Provides comprehensive CPU, RAM, motherboard, storage, GPU, and PCI device information with hybrid approach combining system commands and kernel interfaces.

## Features

- **Universal Compatibility**: Works on any Linux distribution without external dependencies
- **Hybrid Architecture**: Tries system commands first, falls back to /proc and /sys for maximum compatibility
- **Multiple Verbosity Levels**: Basic (--v), Extended (--vv), Deep Analysis (--vvv)
- **Flexible Export Formats**: JSON, CSV, TXT with automatic timestamps
- **Professional Output**: Color-coded terminal output with formatted tables
- **Dry-Run Mode**: Test compatibility before full execution
- **Class-Based Design**: Easy integration with other Python modules
- **Zero Dependencies**: Uses only Python 3.6+ standard library

## Hardware Information Collected

| Category       | Information                                                                          |
|----------------|--------------------------------------------------------------------------------------|  
| **CPU**        | Model, Vendor, Cores, Frequency, Cache, Microcode, CPU Flags, Virtualization Support |
| **Memory**     | Total/Available RAM, Modules, Speed, Type, ECC Support, Manufacturer                 |
| **Motherboard**| Vendor, Model, BIOS Version/Date, Chassis Type, Serial Numbers, SKU                  |
| **Storage**    | Block Devices, Type (SSD/HDD), Size, Model, Partitions, SMART Status                 |
| **GPU**        | Graphics Controllers, VGA Devices, Device IDs                                        |
| **PCI**        | Complete PCI device listing with vendor and device IDs                               | 

## Requirements

- Python 3.6 or higher
- Linux operating system
- Optional for enhanced features:
  - `dmidecode` - Motherboard and BIOS information
  - `lsblk` - Storage device details
  - `lspci` - PCI device enumeration
  - `smartctl` - Storage SMART status (requires smartmontools)

## Installation

### Download the Script

```bash
wget https://example.com/hardware_fetcher.py
# or
curl -O https://example.com/hardware_fetcher.py
```

### Make it Executable

```bash
chmod +x hardware_fetcher.py
```

### Run the Script

```bash
python3 hardware_fetcher.py --vvv --dry-run=false
```

## Usage

### Command-Line Interface

#### Basic Syntax

```bash
python3 hardware_fetcher.py [OPTIONS]
```

#### Required Arguments

```bash
--dry-run=true|false    Dry-run mode (REQUIRED)
                        true  = Test mode (compatibility check only)
                        false = Normal execution
```

#### Optional Arguments

```bash
--v                     Verbosity level 1 (basic information)
--vv                    Verbosity level 2 (extended information)
--vvv                   Verbosity level 3 (deep analysis)

--export-format=FORMAT  Export format (json, csv, txt)
--export-directory=PATH Save exports to specific directory (default: current)

--help                  Display help information
```

### Usage Examples

#### Test System Compatibility

```bash
# Check if system can run the script
python3 hardware_fetcher.py --vvv --dry-run=true
```

#### Display Hardware Information

```bash
# Basic hardware overview
python3 hardware_fetcher.py --v --dry-run=false

# Extended information
python3 hardware_fetcher.py --vv --dry-run=false

# Complete deep analysis
python3 hardware_fetcher.py --vvv --dry-run=false
```

#### Export Hardware Data

```bash
# Export to JSON
python3 hardware_fetcher.py --vvv --dry-run=false --export-format=json --export-directory=/tmp

# Export to CSV
python3 hardware_fetcher.py --vv --dry-run=false --export-format=csv --export-directory=./reports

# Export to TXT
python3 hardware_fetcher.py --vvv --dry-run=false --export-format=txt
```

#### Display Help

```bash
python3 hardware_fetcher.py --help
```

## Verbosity Levels

### Level 1: Basic (--v)

Essential hardware information:
- Physical CPU count
- CPU model and vendor
- Total CPU cores
- Total RAM
- Available RAM
- Motherboard manufacturer and model
- Storage devices and sizes
- GPU devices
- System compatibility components

### Level 2: Extended (--vv)

All basic information plus:
- CPU stepping, family, model number
- L3 cache size
- Cores per socket, threads per core
- CPU frequency (current, min, max)
- VMX/SVM virtualization support
- RAM speed, type, form factor, voltage
- Error correction support
- BIOS vendor, version, release date
- Chassis type and system product
- Storage partitions
- Complete PCI device listing

### Level 3: Deep Analysis (--vvv)

All extended information plus:
- All CPU instruction set extensions/flags
- Important CPU extensions (AVX, SSE, AES, etc.)
- CPU microcode version
- Known CPU bugs/vulnerabilities
- APIC ID, Physical ID, Core ID
- FPU status, Power management features
- RAM manufacturer, serial, part number
- Configured memory speed
- Motherboard and system serial numbers
- Chassis serial and asset tags
- BIOS ROM size
- SMART disk health status
- Storage power-on hours
- Storage temperatures

## Export Formats

### JSON Format

Structured data ideal for programmatic processing and integration.

**File naming**: `hardware_info_YYYYMMDD_HHMMSS.json`

Example:
```json
{
  "CPU Components": {
    "Physical CPU Count": "4",
    "CPU Model": "Intel(R) Xeon(R) Gold 6242 CPU @ 2.80GHz",
    "Total CPU Cores": "4"
  },
  "RAM Components": {
    "Total RAM": "31 GB"
  }
}
```

### CSV Format

Comma-separated values suitable for spreadsheet applications.

**File naming**: `hardware_info_YYYYMMDD_HHMMSS.csv`

Example:
```csv
CPU Components
Physical CPU Count,4
CPU Model,Intel(R) Xeon(R) Gold 6242 CPU @ 2.80GHz
Total CPU Cores,4

RAM Components
Total RAM,31 GB
```

### TXT Format

Human-readable text with formatted sections and timestamps.

**File naming**: `hardware_info_YYYYMMDD_HHMMSS.txt`

Example:
```
HARDWARE REPORT - 2025-10-10 14:30:00
================================================================================

================================================================================
CPU Components
================================================================================

Physical CPU Count: 4
CPU Model: Intel(R) Xeon(R) Gold 6242 CPU @ 2.80GHz
Total CPU Cores: 4
```

## Output Example

```
================================================================================
                    VM HARDWARE COMPONENTS FETCHER
================================================================================

################################################################################
###                    CPU HARDWARE COMPONENTS                               ###
################################################################################

+============================+================================================+
| Physical CPU Count         | 4                                              |
+----------------------------+------------------------------------------------+
| Total CPU Cores            | 4                                              |
+----------------------------+------------------------------------------------+
| CPU Model                  | Intel(R) Xeon(R) Gold 6242 CPU @ 2.80GHz       |
+----------------------------+------------------------------------------------+
| CPU Vendor                 | GenuineIntel                                   |
+============================+================================================+
```

## System Compatibility Check

When running with `--dry-run=true`, the script checks:

```
procfs     - /proc/cpuinfo kernel interface
sysfs      - /sys/devices/system/cpu kernel interface
dmidecode  - Motherboard and BIOS information tool
lsblk      - Block device listing tool
lspci      - PCI device enumeration tool
smartctl   - Storage SMART status tool
```

## Module Usage

Use as a Python module in other scripts:

```python
from hardware_fetcher import HardwareFetcher

# Create instance
fetcher = HardwareFetcher(verbosity=3, dry_run=False, export_directory='/tmp')

# Collect hardware data
fetcher.collect_all_data()

# Display data
fetcher.display_all_data()

# Export data
fetcher.export('json')

# Or run complete workflow
success = fetcher.run(export_format='json')
```

## Troubleshooting

### Permission Denied Errors

Some hardware information requires elevated privileges:

```bash
sudo python3 hardware_fetcher.py --v --dry-run=false
```

### Missing Compatibility Components

If dmidecode is missing, the script will use /sys kernel interfaces as fallback:

```bash
# Install dmidecode if needed
sudo apt-get install dmidecode  # Debian/Ubuntu
sudo yum install dmidecode      # RHEL/CentOS
```

### No Data in Specific Sections

Virtual machines may not have all hardware information available. The script continues with available data and marks unavailable items as 'N/A'.

### Python Version Issues

Ensure Python 3.6 or higher:

```bash
python3 --version
```

## Use Cases

- **System Administration**: Hardware inventory and monitoring
- **Capacity Planning**: Resource usage tracking over time
- **Troubleshooting**: Quick hardware diagnostics
- **Documentation**: Generate hardware reports
- **Automation**: Integration with monitoring systems
- **Compliance**: Maintain hardware change logs
- **DevOps**: Infrastructure as Code provisioning verification

## Performance

- **Basic (--v)**: <100ms
- **Extended (--vv)**: <200ms
- **Deep (--vvv)**: <500ms (depends on SMART queries)

## Hybrid Architecture Benefits

The script uses a intelligent fallback strategy:

1. **Try system commands first** (faster, more detailed)
   - dmidecode for motherboard info
   - lsblk for storage details
   - lspci for PCI devices
   - smartctl for disk health

2. **Fall back to kernel interfaces** (always available)
   - /proc/cpuinfo for CPU info
   - /proc/meminfo for memory info
   - /sys/devices/virtual/dmi/id/ for system info
   - /sys/block/ for storage devices
   - /sys/bus/pci/devices/ for PCI devices

This ensures the script works on minimal systems without external tools while providing enhanced information when tools are available.

## Examples

### Quick System Check

```bash
python3 hardware_fetcher.py --v --dry-run=false
```

### Detailed Analysis with JSON Export

```bash
python3 hardware_fetcher.py --vv --dry-run=false --export-format=json --export-directory=./reports
```

### Comprehensive Audit

```bash
sudo python3 hardware_fetcher.py --vvv --dry-run=false --export-format=csv --export-directory=/var/log/hardware
```

### Scheduled Monitoring

Add to crontab for regular monitoring:

```bash
# Run daily at 2 AM
0 2 * * * /usr/bin/python3 /opt/hardware_fetcher.py --vv --dry-run=false --export-format=json --export-directory=/var/log/hardware
```

## Contributing

Contributions are welcome! Please:
- Report bugs with detailed information
- Suggest new features
- Improve documentation
- Submit pull requests

## License

MIT License - See LICENSE file for details

```
MIT License

Copyright (c) 2025 Alexandru Filcu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

## Author

**Alexandru Filcu**

## Support

If you find this tool helpful:
- Star the repository
- Report bugs with details
- Suggest features
- Improve documentation
- Share your use cases

## Version History

### Version 1.0.0 (2025-10-10)

- Initial release
- CPU, RAM, Motherboard, Storage, GPU, PCI device detection
- Three verbosity levels (--v, --vv, --vvv)
- Export to JSON, CSV, TXT formats
- Dry-run mode for compatibility testing
- Hybrid approach: commands + kernel interfaces
- Color-coded terminal output
- Class-based design for easy integration
- Zero external Python dependencies
