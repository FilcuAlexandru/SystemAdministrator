#!/usr/bin/env python3
# -*- coding: utf-8 -*-

######################################################################
# A Python script for monitoring hardware on any Linux distribution  #
# Fetches hardware information from /proc and /sys filesystems       #
# Processes the fetched data for further analysis                    #
# Author: Alexandru Filcu                                            #
# License: MIT                                                       #
# Version: 0.0.1                                                     #
######################################################################

######################
# IMPORT HANDY TOOLS #
######################

import sys
import argparse
import json
import csv
from collections import OrderedDict
import re
import os

# Define ANSI color codes for styled terminal output
class Colors:
    HEADER = '\033[95m'     # Purple color for headers
    OKBLUE = '\033[94m'     # Blue color for information
    OKGREEN = '\033[92m'    # Green color for success
    WARNING = '\033[93m'    # Yellow color for warnings
    FAIL = '\033[91m'       # Red color for errors
    ENDC = '\033[0m'        # Reset color
    BOLD = '\033[1m'        # Bold text

def color_text(text, color):
    """Apply specified ANSI color to text for terminal output"""
    return color + str(text) + Colors.ENDC

def print_main_header(title):
    """Display main header with fancy formatting"""
    border = '=' * 80
    print(color_text('\n' + border, Colors.HEADER))
    print(color_text(title.center(80), Colors.HEADER))
    print(color_text(border + '\n', Colors.HEADER))

def print_section_header(title):
    """Display a section header with hashes"""
    border = '#' * 80
    padding = (80 - len(title) - 8) // 2
    centered_title = '### ' + (' ' * padding) + title + (' ' * padding) + ' ###'
    print(color_text(border, Colors.HEADER))
    print(color_text(centered_title, Colors.HEADER))
    print(color_text(border + '\n', Colors.HEADER))

def strip_ansi(text):
    """Remove ANSI color codes from text for width calculation"""
    ansi_escape = re.compile(r'\033\[[0-9;]*m')
    return ansi_escape.sub('', str(text))

def print_table(data):
    """Print a beautifully formatted table with separators between rows"""
    if not data:
        print(color_text("No data available", Colors.WARNING))
        return

    # Fixed column widths
    col1_width = 28
    col2_width = 48
    
    # Top border
    top_border = '+' + '=' * col1_width + '+' + '=' * col2_width + '+'
    print(color_text(top_border, Colors.OKBLUE))

    # Data rows with separators
    for idx, row in enumerate(data):
        if len(row) >= 2:
            col1_text = str(row[0])
            col2_text = str(row[1])
            
            # Strip ANSI codes for width calculation
            col1_clean = strip_ansi(col1_text)
            col2_clean = strip_ansi(col2_text)
            
            # Truncate if too long with ellipsis
            if len(col1_clean) > col1_width - 3:
                col1_clean = col1_clean[:col1_width - 6] + '...'
            if len(col2_clean) > col2_width - 3:
                col2_clean = col2_clean[:col2_width - 6] + '...'
            
            # Pad to width
            col1_padded = col1_clean.ljust(col1_width - 2)
            col2_padded = col2_clean.ljust(col2_width - 2)
            
            # Print row
            print('| ' + col1_padded + ' | ' + col2_padded + ' |')
            
            # Add separator after each row (except the last one)
            if idx < len(data) - 1:
                separator = '+' + '-' * col1_width + '+' + '-' * col2_width + '+'
                print(color_text(separator, Colors.OKBLUE))

    # Bottom border
    bottom_border = '+' + '=' * col1_width + '+' + '=' * col2_width + '+'
    print(color_text(bottom_border + '\n', Colors.OKBLUE))

def read_file(filepath):
    """Read file safely and return content"""
    try:
        with open(filepath, 'r') as f:
            return f.read().strip()
    except:
        return None

def read_proc_cpuinfo():
    """Parse /proc/cpuinfo"""
    data = {}
    cpuinfo = read_file('/proc/cpuinfo')
    if not cpuinfo:
        return data
    
    for line in cpuinfo.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            if key not in data:
                data[key] = value
    
    return data

def get_cpu_components(verbosity):
    """Retrieve CPU hardware components from /proc/cpuinfo and /sys"""
    data = OrderedDict()
    
    try:
        cpuinfo = read_proc_cpuinfo()
        if not cpuinfo:
            data['Status'] = 'N/A - /proc/cpuinfo not readable'
            return data
        
        # LEVEL 1: Basic CPU info
        processor_count = len([l for l in read_file('/proc/cpuinfo').split('\n') if l.startswith('processor')])
        data['Physical CPU Count'] = str(processor_count)
        
        data['CPU Model'] = cpuinfo.get('model name', 'N/A')
        data['CPU Vendor'] = cpuinfo.get('vendor_id', 'N/A')
        data['Total CPU Cores'] = cpuinfo.get('cpu cores', 'N/A')
        
        if verbosity >= 2:
            # LEVEL 2: Extended CPU info
            data['CPU Stepping'] = cpuinfo.get('stepping', 'N/A')
            data['CPU Family'] = cpuinfo.get('cpu family', 'N/A')
            data['CPU Model Number'] = cpuinfo.get('model', 'N/A')
            data['L3 Cache Size'] = cpuinfo.get('cache size', 'N/A')
            data['Cores Per Socket'] = cpuinfo.get('cpu cores', 'N/A')
            data['Threads (Siblings)'] = cpuinfo.get('siblings', 'N/A')
            
            # Read frequency from /sys
            freq_file = '/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq'
            if os.path.exists(freq_file):
                freq_khz = read_file(freq_file)
                if freq_khz:
                    freq_mhz = str(int(freq_khz) // 1000)
                    data['Current Frequency (MHz)'] = freq_mhz
            
            max_freq_file = '/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq'
            if os.path.exists(max_freq_file):
                max_freq = read_file(max_freq_file)
                if max_freq:
                    data['Max Frequency (MHz)'] = str(int(max_freq) // 1000)
            
            min_freq_file = '/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq'
            if os.path.exists(min_freq_file):
                min_freq = read_file(min_freq_file)
                if min_freq:
                    data['Min Frequency (MHz)'] = str(int(min_freq) // 1000)
        
        if verbosity >= 3:
            # LEVEL 3: Deep CPU analysis
            flags = cpuinfo.get('flags', '')
            if flags:
                flags_list = flags.split()
                data['CPU Extensions (Count)'] = str(len(flags_list))
                data['All CPU Flags'] = flags[:100] + ('...' if len(flags) > 100 else '')
                
                important_flags = ['vmx', 'svm', 'avx', 'avx2', 'sse4_2', 'aes', 'rdrand']
                found_flags = [f for f in important_flags if f in flags_list]
                data['Important Extensions'] = ', '.join(found_flags) if found_flags else 'None'
            
            data['Microcode'] = cpuinfo.get('microcode', 'N/A')
            data['APIC ID'] = cpuinfo.get('apicid', 'N/A')
            data['Physical ID'] = cpuinfo.get('physical id', 'N/A')
            data['Core ID'] = cpuinfo.get('core id', 'N/A')
            data['FPU Present'] = cpuinfo.get('fpu', 'N/A')
            
            bugs_file = '/proc/cpuinfo'
            cpuinfo_full = read_file(bugs_file)
            if cpuinfo_full and 'bugs' in cpuinfo_full:
                for line in cpuinfo_full.split('\n'):
                    if line.startswith('bugs'):
                        data['Known CPU Bugs'] = line.split(':', 1)[1].strip()[:80]
                        break
    
    except Exception as e:
        data['Error'] = str(e)
    
    return data

def get_ram_components(verbosity):
    """Retrieve RAM information from /proc/meminfo and /sys"""
    data = OrderedDict()
    
    try:
        meminfo = read_file('/proc/meminfo')
        if not meminfo:
            data['Status'] = 'N/A - /proc/meminfo not readable'
            return data
        
        # LEVEL 1: Basic RAM
        for line in meminfo.split('\n'):
            if line.startswith('MemTotal:'):
                kb = int(line.split()[1])
                gb = kb // (1024 * 1024)
                data['Total RAM'] = str(gb) + ' GB'
                break
        
        # Try to read from DMI if available
        dmi_path = '/sys/devices/virtual/dmi/id/'
        if os.path.exists(dmi_path):
            if verbosity >= 2:
                # LEVEL 2: Extended info from /sys/devices/virtual/dmi/id/
                board_vendor = read_file(dmi_path + 'board_vendor')
                if board_vendor:
                    data['Board Vendor'] = board_vendor
                
                board_name = read_file(dmi_path + 'board_name')
                if board_name:
                    data['Board Name'] = board_name
            
            if verbosity >= 3:
                # LEVEL 3: Deep info
                board_serial = read_file(dmi_path + 'board_serial')
                if board_serial:
                    data['Board Serial'] = board_serial
        
        # Additional memory info
        for line in meminfo.split('\n'):
            if line.startswith('MemAvailable:'):
                kb = int(line.split()[1])
                gb = kb // (1024 * 1024)
                data['Available RAM'] = str(gb) + ' GB'
            elif line.startswith('Cached:'):
                kb = int(line.split()[1])
                mb = kb // 1024
                data['Cached Memory'] = str(mb) + ' MB'
    
    except Exception as e:
        data['Error'] = str(e)
    
    return data

def get_motherboard_info(verbosity):
    """Retrieve motherboard information from /sys/devices/virtual/dmi/id/"""
    data = OrderedDict()
    
    try:
        dmi_path = '/sys/devices/virtual/dmi/id/'
        
        if not os.path.exists(dmi_path):
            data['Status'] = 'N/A - DMI not available'
            return data
        
        # LEVEL 1: Basic info
        sys_manufacturer = read_file(dmi_path + 'sys_vendor')
        if sys_manufacturer:
            data['System Manufacturer'] = sys_manufacturer
        
        sys_product = read_file(dmi_path + 'product_name')
        if sys_product:
            data['System Product'] = sys_product
        
        board_vendor = read_file(dmi_path + 'board_vendor')
        if board_vendor:
            data['Motherboard Vendor'] = board_vendor
        
        board_name = read_file(dmi_path + 'board_name')
        if board_name:
            data['Motherboard Model'] = board_name
        
        if verbosity >= 2:
            # LEVEL 2: Extended info
            bios_vendor = read_file(dmi_path + 'bios_vendor')
            if bios_vendor:
                data['BIOS Vendor'] = bios_vendor
            
            bios_version = read_file(dmi_path + 'bios_version')
            if bios_version:
                data['BIOS Version'] = bios_version
            
            bios_date = read_file(dmi_path + 'bios_date')
            if bios_date:
                data['BIOS Date'] = bios_date
            
            chassis_type = read_file(dmi_path + 'chassis_type')
            if chassis_type:
                data['Chassis Type'] = chassis_type
        
        if verbosity >= 3:
            # LEVEL 3: Deep info
            board_serial = read_file(dmi_path + 'board_serial')
            if board_serial:
                data['Board Serial'] = board_serial
            
            sys_serial = read_file(dmi_path + 'product_serial')
            if sys_serial:
                data['System Serial'] = sys_serial
            
            chassis_serial = read_file(dmi_path + 'chassis_serial')
            if chassis_serial:
                data['Chassis Serial'] = chassis_serial
            
            chassis_asset = read_file(dmi_path + 'chassis_asset_tag')
            if chassis_asset:
                data['Chassis Asset Tag'] = chassis_asset
    
    except Exception as e:
        data['Error'] = str(e)
    
    return data

def get_storage_components(verbosity):
    """Retrieve storage information from /sys/block/"""
    data = []
    
    try:
        sys_block_path = '/sys/block/'
        
        if not os.path.exists(sys_block_path):
            return data
        
        for device in sorted(os.listdir(sys_block_path)):
            if device.startswith('loop') or device.startswith('dm'):
                continue
            
            device_path = os.path.join(sys_block_path, device)
            
            # Get device size
            size_file = os.path.join(device_path, 'size')
            size_kb = 0
            if os.path.exists(size_file):
                size_str = read_file(size_file)
                if size_str:
                    size_kb = int(size_str) // 2  # Convert 512-byte sectors to KB
            
            # Convert to human readable
            if size_kb > 1024 * 1024:
                size_display = str(size_kb // (1024 * 1024)) + ' GB'
            elif size_kb > 1024:
                size_display = str(size_kb // 1024) + ' MB'
            else:
                size_display = str(size_kb) + ' KB'
            
            # Check if SSD or HDD
            rota_file = os.path.join(device_path, 'queue', 'rotational')
            disk_type = 'UNKNOWN'
            if os.path.exists(rota_file):
                rota = read_file(rota_file)
                if rota == '0':
                    disk_type = 'SSD'
                elif rota == '1':
                    disk_type = 'HDD'
            
            # Get model (if exists)
            model = 'Virtual'
            model_file = os.path.join(device_path, 'device', 'model')
            if os.path.exists(model_file):
                model = read_file(model_file)
            
            device_info = size_display + ' [' + disk_type + '] ' + model
            data.append(['/dev/' + device, device_info])
        
        # Add partition info if verbosity >= 2
        if verbosity >= 2:
            for device in sorted(os.listdir(sys_block_path)):
                device_path = os.path.join(sys_block_path, device)
                
                # Look for partitions
                for entry in os.listdir(device_path):
                    if entry.startswith(device) and entry != device:
                        part_path = os.path.join(device_path, entry)
                        size_file = os.path.join(part_path, 'size')
                        if os.path.exists(size_file):
                            size_str = read_file(size_file)
                            if size_str:
                                size_kb = int(size_str) // 2
                                if size_kb > 1024:
                                    size_display = str(size_kb // 1024) + ' MB'
                                else:
                                    size_display = str(size_kb) + ' KB'
                                data.append(['   └─ ' + entry, size_display + ' partition'])
    
    except Exception as e:
        pass
    
    return data

def get_pci_devices(verbosity):
    """Retrieve PCI devices from /sys/bus/pci/devices/"""
    data = []
    
    try:
        pci_path = '/sys/bus/pci/devices/'
        
        if not os.path.exists(pci_path):
            return data
        
        for device_dir in sorted(os.listdir(pci_path)):
            device_path = os.path.join(pci_path, device_dir)
            
            # Read vendor and device ID
            vendor_file = os.path.join(device_path, 'vendor')
            device_file = os.path.join(device_path, 'device')
            
            if os.path.exists(vendor_file) and os.path.exists(device_file):
                vendor_id = read_file(vendor_file)
                device_id = read_file(device_file)
                
                if vendor_id and device_id:
                    pci_id = device_dir
                    info = vendor_id + ':' + device_id
                    data.append([pci_id, info])
    
    except Exception as e:
        pass
    
    return data

def get_gpu_info(verbosity):
    """Retrieve GPU information from /sys/bus/pci/"""
    data = []
    
    try:
        pci_path = '/sys/bus/pci/devices/'
        
        if not os.path.exists(pci_path):
            return data
        
        for device_dir in sorted(os.listdir(pci_path)):
            device_path = os.path.join(pci_path, device_dir)
            class_file = os.path.join(device_path, 'class')
            
            if os.path.exists(class_file):
                class_id = read_file(class_file)
                if class_id:
                    # Check for VGA (0x030000) or 3D (0x030100)
                    if class_id.startswith('0x030'):
                        vendor_file = os.path.join(device_path, 'vendor')
                        device_file = os.path.join(device_path, 'device')
                        
                        if os.path.exists(vendor_file) and os.path.exists(device_file):
                            vendor_id = read_file(vendor_file)
                            device_id = read_file(device_file)
                            data.append([device_dir, 'VGA: ' + vendor_id + ':' + device_id])
    
    except Exception as e:
        pass
    
    return data

def export_to_json(all_data, filename='hardware_info.json'):
    """Export hardware information to JSON format"""
    try:
        with open(filename, 'w') as f:
            json.dump(all_data, f, indent=2)
        print(color_text('[+] Data exported to: ' + filename, Colors.OKGREEN))
    except Exception as e:
        print(color_text('[-] Error exporting to JSON: ' + str(e), Colors.FAIL))

def export_to_csv(all_data, filename='hardware_info.csv'):
    """Export hardware information to CSV format"""
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            for section, items in all_data.items():
                writer.writerow([section])
                if isinstance(items, dict):
                    for key, value in items.items():
                        writer.writerow([key, value])
                elif isinstance(items, list):
                    for row in items:
                        writer.writerow(row)
                writer.writerow([])
        print(color_text('[+] Data exported to: ' + filename, Colors.OKGREEN))
    except Exception as e:
        print(color_text('[-] Error exporting to CSV: ' + str(e), Colors.FAIL))

def export_to_txt(all_data, filename='hardware_info.txt'):
    """Export hardware information to TXT format"""
    try:
        with open(filename, 'w') as f:
            for section, items in all_data.items():
                f.write('\n' + '='*80 + '\n')
                f.write(section + '\n')
                f.write('='*80 + '\n\n')
                if isinstance(items, dict):
                    for key, value in items.items():
                        f.write('{}: {}\n'.format(key, value))
                elif isinstance(items, list):
                    for row in items:
                        f.write(' | '.join(str(x) for x in row) + '\n')
                f.write('\n')
        print(color_text('[+] Data exported to: ' + filename, Colors.OKGREEN))
    except Exception as e:
        print(color_text('[-] Error exporting to TXT: ' + str(e), Colors.FAIL))

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Hardware Fetcher - VM Hardware Analysis from /proc and /sys',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''VERBOSITY LEVELS:
  -v     (Level 1): Basic hardware overview
  -vv    (Level 2): Extended information with detailed specs
  -vvv   (Level 3): Deep analysis with all identifiers

EXPORT OPTIONS:
  --export=json    Export data to JSON format
  --export=csv     Export data to CSV format
  --export=txt     Export data to TXT format

EXAMPLES:
  python3 hardware_fetcher.py -v
  python3 hardware_fetcher.py -vv --export=json
  python3 hardware_fetcher.py -vvv --export=csv --dry-run=false
        '''
    )
    
    parser.add_argument('--dry-run', 
                       type=lambda x: x.lower() == 'true',
                       default=False,
                       help='Run in dry-run mode without exporting (default: false)')
    
    parser.add_argument('-v', '--verbose', 
                       action='count', 
                       default=1,
                       help='Increase verbosity: -v (basic), -vv (extended), -vvv (deep)')
    
    parser.add_argument('--export', 
                       choices=['json', 'csv', 'txt'],
                       default=None,
                       help='Export format: json, csv, or txt')
    
    args = parser.parse_args()
    
    # Validate verbosity
    if args.verbose > 3:
        args.verbose = 3
    
    # Main header
    print_main_header('VM HARDWARE COMPONENTS FETCHER')
    
    all_data = OrderedDict()
    
    # 1. CPU COMPONENTS
    print_section_header('CPU HARDWARE COMPONENTS')
    cpu_data = get_cpu_components(args.verbose)
    all_data['CPU Components'] = cpu_data
    cpu_table = [[k, v] for k, v in cpu_data.items()]
    print_table(cpu_table)
    
    # 2. RAM COMPONENTS
    print_section_header('RAM HARDWARE COMPONENTS')
    ram_data = get_ram_components(args.verbose)
    all_data['RAM Components'] = ram_data
    ram_table = [[k, v] for k, v in ram_data.items()]
    print_table(ram_table)
    
    # 3. MOTHERBOARD COMPONENTS
    print_section_header('MOTHERBOARD HARDWARE')
    mobo_data = get_motherboard_info(args.verbose)
    all_data['Motherboard'] = mobo_data
    mobo_table = [[k, v] for k, v in mobo_data.items()]
    print_table(mobo_table)
    
    # 4. STORAGE COMPONENTS
    print_section_header('STORAGE HARDWARE COMPONENTS')
    storage_data = get_storage_components(args.verbose)
    all_data['Storage Devices'] = storage_data
    if storage_data:
        print_table(storage_data)
    else:
        print(color_text('No storage devices found\n', Colors.WARNING))
    
    # 5. GPU COMPONENTS
    print_section_header('GPU HARDWARE COMPONENTS')
    gpu_data = get_gpu_info(args.verbose)
    all_data['GPU Devices'] = gpu_data
    if gpu_data:
        print_table(gpu_data)
    else:
        print(color_text('No GPU devices detected\n', Colors.WARNING))
    
    # 6. PCI DEVICES
    if args.verbose >= 2:
        print_section_header('PCI HARDWARE DEVICES')
        pci_data = get_pci_devices(args.verbose)
        all_data['PCI Devices'] = pci_data
        if pci_data:
            print_table(pci_data)
        else:
            print(color_text('No PCI devices found\n', Colors.WARNING))
    
    # Export data if not in dry-run mode
    if not args.dry_run:
        if args.export == 'json':
            export_to_json(all_data)
        elif args.export == 'csv':
            export_to_csv(all_data)
        elif args.export == 'txt':
            export_to_txt(all_data)
    
    print(color_text('=' * 80 + '\n', Colors.HEADER))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(color_text('\n\n[-] Script interrupted by user', Colors.FAIL))
        sys.exit(1)
    except Exception as e:
        print(color_text('\n[-] Error: ' + str(e), Colors.FAIL))
        sys.exit(1)
