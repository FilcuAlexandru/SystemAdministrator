#!/usr/bin/env python3
# -*- coding: utf-8 -*-

######################################################################
#                  HARDWARE FETCHER v1.0.0                           #
# Advanced Hardware Detection and Analysis for Linux Systems         #
#                                                                    #
# A professional-grade Python module for comprehensive hardware      #
# information gathering on any Linux distribution. Combines kernel   #
# interfaces (/proc, /sys) with system commands for maximum          #
# compatibility and detailed hardware reporting.                     #
#                                                                    #
# FEATURES:                                                          #
#  • CPU detection: cores, model, frequency, microcode, flags        #
#  • RAM analysis: capacity, modules, speed, ECC support             #
#  • Storage devices: HDDs/SSDs, partitions, SMART status            #
#  • Motherboard info: BIOS version, chassis type, serial numbers    #
#  • GPU enumeration: VGA and 3D graphics controllers                #
#  • PCI device listing: Complete hardware inventory                 #
#  • Multiple export formats: JSON, CSV, TXT                         #
#  • Verbosity levels: Basic (--v), Extended (--vv), Deep (--vvv)    #
#  • Dry-run mode: Compatibility testing without file operations     #
#                                                                    #
# USAGE:                                                             #
#  Standalone: python3 hardware_fetcher.py --vvv --dry-run=false     #
#  As Module: from hardware_fetcher import HardwareFetcher           #
#                                                                    #
# HYBRID APPROACH:                                                   #
#  Tries system commands first (lsblk, lspci, dmidecode, smartctl)   #
#  Falls back to /proc and /sys kernel interfaces for compatibility  #
#  Ensures functionality on minimal systems without external tools   #
#                                                                    #
# Author: Alexandru Filcu                                            #
# License: MIT                                                       #
# Version: 1.0.0                                                     #
# Repository: https://github.com/yourusername/hardware-fetcher       #
######################################################################

######################
# IMPORT HANDY TOOLS #
######################

import sys
import argparse
import json
import csv
import subprocess
from collections import OrderedDict
import re
import os
from datetime import datetime

class Colors:
    """ANSI color codes for terminal output styling"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class HardwareFetcher:
    """
    Comprehensive hardware information gatherer for Linux systems.
    
    Collects detailed information about CPU, RAM, motherboard, storage devices,
    GPUs, and PCI devices using both system commands and kernel interfaces.
    Supports multiple verbosity levels and export formats.
    
    Attributes:
        verbosity (int): Detail level (1-3)
        dry_run (bool): Test mode without file operations
        export_dir (str): Directory for export files
    """
    
    def __init__(self, verbosity=1, dry_run=False, export_directory='.'):
        """
        Initialize HardwareFetcher with configuration parameters.
        
        Args:
            verbosity (int): Detail level - 1=basic, 2=extended, 3=deep (default: 1)
            dry_run (bool): If True, run in test mode without file writes (default: False)
            export_directory (str): Directory path for exported files (default: current)
        """
        self.verbosity = min(verbosity, 3)
        self.dry_run = dry_run
        self.export_dir = export_directory
        self.hardware_data = OrderedDict()

    @staticmethod
    def color_text(text, color):
        """
        Apply ANSI color codes to text for terminal output.
        
        Args:
            text (str): Text to colorize
            color (str): ANSI color code from Colors class
            
        Returns:
            str: Colored text string
        """
        return color + str(text) + Colors.ENDC

    @staticmethod
    def strip_ansi(text):
        """
        Remove ANSI color codes from text for width calculations.
        
        Args:
            text (str): Text possibly containing ANSI codes
            
        Returns:
            str: Text without ANSI codes
        """
        ansi_escape = re.compile(r'\033\[[0-9;]*m')
        return ansi_escape.sub('', str(text))

    @staticmethod
    def run_command(command):
        """
        Execute shell command safely and return output.
        
        Args:
            command (str): Shell command to execute
            
        Returns:
            str or None: Command output if successful, None on failure
        """
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, universal_newlines=True)
            return result.strip()
        except:
            return None

    @staticmethod
    def command_exists(command):
        """
        Check if a command exists in system PATH.
        
        Args:
            command (str): Command name to check
            
        Returns:
            bool: True if command exists, False otherwise
        """
        return HardwareFetcher.run_command('which ' + command) is not None

    @staticmethod
    def read_file(filepath):
        """
        Read file content safely with error handling.
        
        Args:
            filepath (str): Path to file to read
            
        Returns:
            str or None: File content if readable, None on error
        """
        try:
            with open(filepath, 'r') as f:
                return f.read().strip()
        except:
            return None

    @staticmethod
    def get_value(cmd, fallback_file=None):
        """
        Get value from command with automatic fallback to file.
        
        Attempts to execute command first, then falls back to reading file.
        Useful for hybrid approach combining commands and kernel interfaces.
        
        Args:
            cmd (str or None): Shell command to execute
            fallback_file (str or None): File path to read if command fails
            
        Returns:
            str: Value from command or file, 'N/A' if both fail
        """
        if cmd:
            result = HardwareFetcher.run_command(cmd)
            if result:
                return result
        if fallback_file:
            result = HardwareFetcher.read_file(fallback_file)
            if result:
                return result
        return 'N/A'

    def print_header(self, title):
        """
        Display formatted section header with hash borders.
        
        Args:
            title (str): Section title to display
        """
        border = '#' * 80
        padding = (80 - len(title) - 8) // 2
        centered = '### ' + (' ' * padding) + title + (' ' * padding) + ' ###'
        print(self.color_text(border, Colors.HEADER))
        print(self.color_text(centered, Colors.HEADER))
        print(self.color_text(border + '\n', Colors.HEADER))

    def print_table(self, data):
        """
        Print formatted table with aligned columns and separators.
        
        Creates a professional-looking table with automatic column sizing,
        text truncation for long values, and horizontal separators between rows.
        
        Args:
            data (list): List of [key, value] pairs to display
        """
        if not data:
            print(self.color_text("No data available\n", Colors.WARNING))
            return

        col1_width = 28
        col2_width = 48
        
        top_border = '+' + '=' * col1_width + '+' + '=' * col2_width + '+'
        print(self.color_text(top_border, Colors.OKBLUE))

        for idx, row in enumerate(data):
            if len(row) >= 2:
                col1_text = str(row[0])
                col2_text = str(row[1])
                
                col1_clean = self.strip_ansi(col1_text)
                col2_clean = self.strip_ansi(col2_text)
                
                if len(col1_clean) > col1_width - 3:
                    col1_clean = col1_clean[:col1_width - 6] + '...'
                if len(col2_clean) > col2_width - 3:
                    col2_clean = col2_clean[:col2_width - 6] + '...'
                
                col1_padded = col1_clean.ljust(col1_width - 2)
                col2_padded = col2_clean.ljust(col2_width - 2)
                
                print('| ' + col1_padded + ' | ' + col2_padded + ' |')
                
                if idx < len(data) - 1:
                    separator = '+' + '-' * col1_width + '+' + '-' * col2_width + '+'
                    print(self.color_text(separator, Colors.OKBLUE))

        bottom_border = '+' + '=' * col1_width + '+' + '=' * col2_width + '+'
        print(self.color_text(bottom_border + '\n', Colors.OKBLUE))

    def check_system_compatibility(self):
        """
        Check system compatibility for hardware detection.
        
        Verifies presence of required kernel interfaces and tools.
        
        Returns:
            dict: Compatibility status for each required component
        """
        checks = {
            'procfs': os.path.exists('/proc/cpuinfo'),
            'sysfs': os.path.exists('/sys/devices/system/cpu/'),
            'dmidecode': self.command_exists('dmidecode'),
            'lsblk': self.command_exists('lsblk'),
            'lspci': self.command_exists('lspci'),
            'smartctl': self.command_exists('smartctl'),
        }
        return checks

    def print_compatibility_check(self):
        """
        Display system compatibility check results in formatted table.
        
        Shows availability of each hardware detection tool/interface.
        
        Returns:
            bool: True if system is compatible (has /proc/cpuinfo), False otherwise
        """
        checks = self.check_system_compatibility()
        self.print_header('SYSTEM COMPATIBILITY CHECK')
        
        for check_name, result in checks.items():
            status = self.color_text('✓ OK', Colors.OKGREEN) if result else self.color_text('✗ MISSING', Colors.WARNING)
            print(f'{check_name.ljust(20)} : {status}')
        
        print()
        
        if not checks['procfs']:
            print(self.color_text('ERROR: /proc/cpuinfo not found. System not compatible!\n', Colors.FAIL))
            return False
        
        print(self.color_text('[+] System is ABLE TO RUN - Required components detected!\n', Colors.OKGREEN))
        return True

    def get_cpu_components(self):
        """
        Retrieve detailed CPU hardware information from /proc and system commands.
        
        Gathers: CPU count, model, vendor, cache, frequency, microcode,
        CPU flags (instruction set extensions), and known vulnerabilities.
        
        Returns:
            OrderedDict: CPU hardware specifications
        """
        data = OrderedDict()
        
        try:
            # Level 1: Basic CPU information
            cpu_count = self.get_value("grep -c '^processor' /proc/cpuinfo")
            if cpu_count != 'N/A':
                data['Physical CPU Count'] = cpu_count.split('\n')[0]
            else:
                data['Physical CPU Count'] = 'N/A'
            
            data['CPU Model'] = self.get_value("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2 | xargs")
            data['CPU Vendor'] = self.get_value("grep -m 1 'vendor_id' /proc/cpuinfo | cut -d: -f2 | xargs")
            data['Total CPU Cores'] = self.get_value("nproc")
            
            if self.verbosity >= 2:
                # Level 2: Extended CPU details
                data['CPU Stepping'] = self.get_value("grep -m 1 'stepping' /proc/cpuinfo | cut -d: -f2 | xargs")
                data['CPU Family'] = self.get_value("grep -m 1 'cpu family' /proc/cpuinfo | cut -d: -f2 | xargs")
                data['CPU Model Number'] = self.get_value("grep -m 1 '^model' /proc/cpuinfo | grep -v 'model name' | cut -d: -f2 | xargs")
                data['L3 Cache Size'] = self.get_value("grep -m 1 'cache size' /proc/cpuinfo | cut -d: -f2 | xargs")
                data['Cores Per Socket'] = self.get_value("grep -m 1 'cpu cores' /proc/cpuinfo | cut -d: -f2 | xargs")
                data['Threads (Siblings)'] = self.get_value("grep -m 1 'siblings' /proc/cpuinfo | cut -d: -f2 | xargs")
                data['Current Frequency (MHz)'] = self.get_value("grep -m 1 'cpu MHz' /proc/cpuinfo | cut -d: -f2 | xargs")
                data['Max Frequency (MHz)'] = self.get_value(None, '/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq')
                data['Min Frequency (MHz)'] = self.get_value(None, '/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq')
                
                # Virtualization support
                data['VMX Support (Intel)'] = 'Yes' if 'vmx' in self.get_value("grep -m 1 'flags' /proc/cpuinfo | cut -d: -f2 | xargs") else 'No'
                data['SVM Support (AMD)'] = 'Yes' if 'svm' in self.get_value("grep -m 1 'flags' /proc/cpuinfo | cut -d: -f2 | xargs") else 'No'
            
            if self.verbosity >= 3:
                # Level 3: Deep CPU analysis
                flags = self.get_value("grep -m 1 'flags' /proc/cpuinfo | cut -d: -f2 | xargs")
                if flags != 'N/A':
                    flags_list = flags.split()
                    data['CPU Extensions (Count)'] = str(len(flags_list))
                    data['All CPU Flags'] = flags[:100] + ('...' if len(flags) > 100 else '')
                    
                    important = ['vmx', 'svm', 'avx', 'avx2', 'sse4_2', 'aes', 'rdrand', 'tsx']
                    found = [f for f in important if f in flags_list]
                    data['Important Extensions'] = ', '.join(found) if found else 'None'
                
                data['Microcode'] = self.get_value("grep -m 1 'microcode' /proc/cpuinfo | cut -d: -f2 | xargs")
                data['APIC ID'] = self.get_value("grep -m 1 'apicid' /proc/cpuinfo | cut -d: -f2 | xargs")
                data['Physical ID'] = self.get_value("grep -m 1 'physical id' /proc/cpuinfo | cut -d: -f2 | xargs")
                data['Core ID'] = self.get_value("grep -m 1 'core id' /proc/cpuinfo | cut -d: -f2 | xargs")
                data['FPU Present'] = self.get_value("grep -m 1 'fpu[^_]' /proc/cpuinfo | cut -d: -f2 | xargs")
                
                bugs = self.get_value("grep 'bugs' /proc/cpuinfo | head -1 | cut -d: -f2 | xargs")
                if bugs != 'N/A':
                    data['Known CPU Bugs'] = bugs[:80] + ('...' if len(bugs) > 80 else '')
        
        except Exception as e:
            data['Error'] = str(e)
        
        return data

    def get_ram_components(self):
        """
        Retrieve detailed RAM hardware information from /proc and DMI.
        
        Gathers: Total RAM, available RAM, RAM modules, speed, type, ECC support,
        manufacturer info, and memory timing details.
        
        Returns:
            OrderedDict: RAM hardware specifications
        """
        data = OrderedDict()
        
        try:
            meminfo = self.read_file('/proc/meminfo')
            if meminfo:
                for line in meminfo.split('\n'):
                    if line.startswith('MemTotal:'):
                        kb = int(line.split()[1])
                        data['Total RAM'] = str(kb // (1024 * 1024)) + ' GB'
                        break
            
            if self.command_exists('dmidecode'):
                ram_modules = self.get_value("dmidecode -t memory | grep -c 'Memory Device'")
                data['Physical RAM Modules'] = ram_modules
                
                if self.verbosity >= 2:
                    data['RAM Speed'] = self.get_value("dmidecode -t memory | grep -m 1 'Speed' | cut -d: -f2 | xargs")
                    data['RAM Type'] = self.get_value("dmidecode -t memory | grep -m 1 'Type:' | cut -d: -f2 | xargs")
                    data['Form Factor'] = self.get_value("dmidecode -t memory | grep -m 1 'Form Factor' | cut -d: -f2 | xargs")
                    data['Data Width'] = self.get_value("dmidecode -t memory | grep -m 1 'Data Width' | cut -d: -f2 | xargs")
                    data['Voltage'] = self.get_value("dmidecode -t memory | grep -m 1 'Voltage' | cut -d: -f2 | xargs")
                    data['Error Correction'] = self.get_value("dmidecode -t memory | grep -m 1 'Error Correction Type' | cut -d: -f2 | xargs")
                
                if self.verbosity >= 3:
                    data['Manufacturer'] = self.get_value("dmidecode -t memory | grep -m 1 'Manufacturer' | cut -d: -f2 | xargs")
                    data['Module Serial'] = self.get_value("dmidecode -t memory | grep -m 1 'Serial Number' | cut -d: -f2 | xargs")
                    data['Part Number'] = self.get_value("dmidecode -t memory | grep -m 1 'Part Number' | cut -d: -f2 | xargs")
                    data['Configured Speed'] = self.get_value("dmidecode -t memory | grep -m 1 'Configured Clock Speed' | cut -d: -f2 | xargs")
            
            # Available memory info
            if meminfo:
                for line in meminfo.split('\n'):
                    if line.startswith('MemAvailable:'):
                        kb = int(line.split()[1])
                        data['Available RAM'] = str(kb // (1024 * 1024)) + ' GB'
                    elif line.startswith('Cached:'):
                        kb = int(line.split()[1])
                        data['Cached Memory'] = str(kb // 1024) + ' MB'
        
        except Exception as e:
            data['Error'] = str(e)
        
        return data

    def get_motherboard_info(self):
        """
        Retrieve motherboard and system information from DMI and kernel interfaces.
        
        Gathers: Motherboard manufacturer/model, BIOS vendor/version/date, 
        system product, chassis type, serial numbers, and SKU information.
        
        Returns:
            OrderedDict: Motherboard hardware specifications
        """
        data = OrderedDict()
        
        try:
            if self.command_exists('dmidecode'):
                data['Motherboard Manufacturer'] = self.get_value("dmidecode -t baseboard | grep Manufacturer | head -1 | cut -d: -f2 | xargs")
                data['Motherboard Model'] = self.get_value("dmidecode -t baseboard | grep 'Product Name' | head -1 | cut -d: -f2 | xargs")
                data['System Manufacturer'] = self.get_value("dmidecode -t system | grep Manufacturer | head -1 | cut -d: -f2 | xargs")
                
                if self.verbosity >= 2:
                    data['BIOS Vendor'] = self.get_value("dmidecode -t bios | grep Vendor | head -1 | cut -d: -f2 | xargs")
                    data['BIOS Version'] = self.get_value("dmidecode -t bios | grep Version | head -1 | cut -d: -f2 | xargs")
                    data['BIOS Release Date'] = self.get_value("dmidecode -t bios | grep 'Release Date' | cut -d: -f2 | xargs")
                    data['Chassis Type'] = self.get_value("dmidecode -t chassis | grep Type | head -1 | cut -d: -f2 | xargs")
                    data['System Product'] = self.get_value("dmidecode -t system | grep 'Product Name' | head -1 | cut -d: -f2 | xargs")
                
                if self.verbosity >= 3:
                    data['System Serial'] = self.get_value("dmidecode -t system | grep 'Serial Number' | head -1 | cut -d: -f2 | xargs")
                    data['Motherboard Serial'] = self.get_value("dmidecode -t baseboard | grep 'Serial Number' | head -1 | cut -d: -f2 | xargs")
                    data['Chassis Serial'] = self.get_value("dmidecode -t chassis | grep 'Serial Number' | head -1 | cut -d: -f2 | xargs")
                    data['System SKU'] = self.get_value("dmidecode -t system | grep SKU | cut -d: -f2 | xargs")
                    data['BIOS ROM Size'] = self.get_value("dmidecode -t bios | grep 'ROM Size' | cut -d: -f2 | xargs")
            else:
                dmi_path = '/sys/devices/virtual/dmi/id/'
                if os.path.exists(dmi_path):
                    data['System Manufacturer'] = self.read_file(dmi_path + 'sys_vendor') or 'N/A'
                    data['System Product'] = self.read_file(dmi_path + 'product_name') or 'N/A'
                    data['Motherboard Vendor'] = self.read_file(dmi_path + 'board_vendor') or 'N/A'
                    data['Motherboard Model'] = self.read_file(dmi_path + 'board_name') or 'N/A'
        
        except Exception as e:
            data['Error'] = str(e)
        
        return data

    def get_storage_components(self):
        """
        Retrieve storage device information from /sys/block and lsblk.
        
        Gathers: Storage devices (HDDs/SSDs), sizes, types, partitions,
        and SMART health status if available.
        
        Returns:
            list: List of [device_name, device_info] pairs
        """
        data = []
        
        try:
            block_output = self.get_value("lsblk -d -o NAME,SIZE,TYPE,ROTA,MODEL 2>/dev/null")
            
            if block_output and block_output != 'N/A':
                lines = block_output.split('\n')
                for i, line in enumerate(lines):
                    if i > 0 and line.strip():
                        parts = line.split(None, 4)
                        if len(parts) >= 2:
                            name = parts[0]
                            size = parts[1]
                            rota = parts[3] if len(parts) > 3 else 'N/A'
                            model = parts[4] if len(parts) > 4 else 'Virtual'
                            
                            disk_type = 'SSD' if rota == '0' else 'HDD' if rota == '1' else 'UNKNOWN'
                            disk_info = size + ' [' + disk_type + '] ' + model
                            data.append(['/dev/' + name, disk_info])
            
            # Fallback to /sys/block/
            if not data:
                sys_block = '/sys/block/'
                if os.path.exists(sys_block):
                    for device in sorted(os.listdir(sys_block)):
                        if not device.startswith('loop'):
                            device_path = os.path.join(sys_block, device)
                            size_file = os.path.join(device_path, 'size')
                            if os.path.exists(size_file):
                                size_kb = int(self.read_file(size_file) or '0') // 2
                                if size_kb > 1024:
                                    size_str = str(size_kb // 1024) + ' MB'
                                else:
                                    size_str = str(size_kb) + ' KB'
                                data.append(['/dev/' + device, size_str])
            
            # Partitions if verbosity >= 2
            if self.verbosity >= 2:
                part_output = self.get_value("lsblk 2>/dev/null | grep 'part'")
                if part_output and part_output != 'N/A':
                    for line in part_output.split('\n'):
                        if line.strip():
                            data.append(['   └─ PARTITION', line.strip()[:42]])
            
            # SMART info if verbosity >= 3
            if self.verbosity >= 3 and self.command_exists('smartctl'):
                disks = self.get_value("lsblk -d -o NAME 2>/dev/null | grep -v NAME | head -2")
                if disks and disks != 'N/A':
                    for disk in disks.split('\n'):
                        if disk.strip():
                            health = self.get_value(f"smartctl -H /dev/{disk.strip()} 2>/dev/null | grep 'SMART overall'")
                            if health != 'N/A':
                                status = health.split()[-1] if health else 'N/A'
                                data.append([f"   └─ {disk.strip()} [SMART]", f"Status: {status}"])
        
        except Exception as e:
            pass
        
        return data

    def get_pci_devices(self):
        """
        Retrieve PCI device information from lspci and /sys/bus/pci.
        
        Gathers: All PCI devices with vendor and device IDs.
        
        Returns:
            list: List of [pci_slot, device_info] pairs
        """
        data = []
        
        try:
            pci_output = self.get_value("lspci 2>/dev/null")
            
            if pci_output and pci_output != 'N/A':
                for line in pci_output.split('\n'):
                    if line.strip():
                        match = re.match(r'^([0-9a-f:.]+)\s+(.*)', line)
                        if match:
                            data.append([match.group(1), match.group(2)])
            
            # Fallback to /sys/bus/pci/
            if not data:
                pci_path = '/sys/bus/pci/devices/'
                if os.path.exists(pci_path):
                    for device in sorted(os.listdir(pci_path)):
                        vendor_file = os.path.join(pci_path, device, 'vendor')
                        device_file = os.path.join(pci_path, device, 'device')
                        if os.path.exists(vendor_file) and os.path.exists(device_file):
                            vendor = self.read_file(vendor_file)
                            dev_id = self.read_file(device_file)
                            data.append([device, vendor + ':' + dev_id])
        
        except Exception as e:
            pass
        
        return data

    def get_gpu_info(self):
        """
        Retrieve GPU device information from lspci.
        
        Identifies VGA and 3D graphics controllers on the system.
        
        Returns:
            list: List of [gpu_slot, gpu_info] pairs
        """
        data = []
        
        try:
            gpu_output = self.get_value("lspci 2>/dev/null | grep -i 'vga\\|3d\\|display\\|graphics'")
            
            if gpu_output and gpu_output != 'N/A':
                for line in gpu_output.split('\n'):
                    if line.strip():
                        match = re.match(r'^([0-9a-f:.]+)\s+(.*)', line)
                        if match:
                            data.append([match.group(1), match.group(2)])
        
        except Exception as e:
            pass
        
        return data

    def export_to_json(self, filepath):
        """
        Export collected hardware data to JSON file.
        
        Creates formatted JSON output with proper indentation.
        In dry-run mode, displays what would be exported without writing.
        
        Args:
            filepath (str): Target file path for JSON export
            
        Returns:
            bool: True if successful, False on error
        """
        try:
            if self.dry_run:
                print(self.color_text(f'[DRY-RUN] Would export JSON to: {filepath}', Colors.OKBLUE))
                return True
            
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(self.hardware_data, f, indent=2)
            print(self.color_text('[+] Data exported to: ' + filepath, Colors.OKGREEN))
            return True
        except Exception as e:
            print(self.color_text('[-] Error exporting: ' + str(e), Colors.FAIL))
            return False

    def export_to_csv(self, filepath):
        """
        Export collected hardware data to CSV file.
        
        Creates structured CSV output suitable for spreadsheet applications.
        In dry-run mode, displays what would be exported without writing.
        
        Args:
            filepath (str): Target file path for CSV export
            
        Returns:
            bool: True if successful, False on error
        """
        try:
            if self.dry_run:
                print(self.color_text(f'[DRY-RUN] Would export CSV to: {filepath}', Colors.OKBLUE))
                return True
            
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                for section, items in self.hardware_data.items():
                    writer.writerow([section])
                    if isinstance(items, dict):
                        for key, value in items.items():
                            writer.writerow([key, value])
                    elif isinstance(items, list):
                        for row in items:
                            writer.writerow(row)
                    writer.writerow([])
            print(self.color_text('[+] Data exported to: ' + filepath, Colors.OKGREEN))
            return True
        except Exception as e:
            print(self.color_text('[-] Error exporting: ' + str(e), Colors.FAIL))
            return False

    def export_to_txt(self, filepath):
        """
        Export collected hardware data to TXT file.
        
        Creates human-readable text output with formatted sections.
        In dry-run mode, displays what would be exported without writing.
        
        Args:
            filepath (str): Target file path for TXT export
            
        Returns:
            bool: True if successful, False on error
        """
        try:
            if self.dry_run:
                print(self.color_text(f'[DRY-RUN] Would export TXT to: {filepath}', Colors.OKBLUE))
                return True
            
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
            with open(filepath, 'w') as f:
                f.write('HARDWARE REPORT - ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
                f.write('=' * 80 + '\n\n')
                for section, items in self.hardware_data.items():
                    f.write('\n' + '=' * 80 + '\n')
                    f.write(section + '\n')
                    f.write('=' * 80 + '\n\n')
                    if isinstance(items, dict):
                        for key, value in items.items():
                            f.write('{}: {}\n'.format(key, value))
                    elif isinstance(items, list):
                        for row in items:
                            f.write(' | '.join(str(x) for x in row) + '\n')
                    f.write('\n')
            print(self.color_text('[+] Data exported to: ' + filepath, Colors.OKGREEN))
            return True
        except Exception as e:
            print(self.color_text('[-] Error exporting: ' + str(e), Colors.FAIL))
            return False

    def collect_all_data(self):
        """
        Collect all hardware information from all sources.
        
        Executes all hardware detection methods and stores results.
        Should be called before exporting or displaying data.
        """
        self.hardware_data['CPU Components'] = self.get_cpu_components()
        self.hardware_data['RAM Components'] = self.get_ram_components()
        self.hardware_data['Motherboard'] = self.get_motherboard_info()
        self.hardware_data['Storage Devices'] = self.get_storage_components()
        self.hardware_data['GPU Devices'] = self.get_gpu_info()
        if self.verbosity >= 2:
            self.hardware_data['PCI Devices'] = self.get_pci_devices()

    def display_all_data(self):
        """
        Display all collected hardware information in formatted tables.
        
        Prints data to console with proper formatting and colors.
        """
        print(self.color_text('\n' + '=' * 80, Colors.HEADER))
        print(self.color_text('VM HARDWARE COMPONENTS FETCHER'.center(80), Colors.HEADER))
        print(self.color_text('=' * 80 + '\n', Colors.HEADER))
        
        # CPU
        self.print_header('CPU HARDWARE COMPONENTS')
        self.print_table([[k, v] for k, v in self.hardware_data.get('CPU Components', {}).items()])
        
        # RAM
        self.print_header('RAM HARDWARE COMPONENTS')
        self.print_table([[k, v] for k, v in self.hardware_data.get('RAM Components', {}).items()])
        
        # Motherboard
        self.print_header('MOTHERBOARD HARDWARE')
        self.print_table([[k, v] for k, v in self.hardware_data.get('Motherboard', {}).items()])
        
        # Storage
        self.print_header('STORAGE HARDWARE COMPONENTS')
        storage_data = self.hardware_data.get('Storage Devices', [])
        if storage_data:
            self.print_table(storage_data)
        else:
            print(self.color_text('No storage devices found\n', Colors.WARNING))
        
        # GPU
        self.print_header('GPU HARDWARE COMPONENTS')
        gpu_data = self.hardware_data.get('GPU Devices', [])
        if gpu_data:
            self.print_table(gpu_data)
        else:
            print(self.color_text('No GPU devices detected\n', Colors.WARNING))
        
        # PCI
        if self.verbosity >= 2:
            self.print_header('PCI HARDWARE DEVICES')
            pci_data = self.hardware_data.get('PCI Devices', [])
            if pci_data:
                self.print_table(pci_data)
            else:
                print(self.color_text('No PCI devices found\n', Colors.WARNING))
        
        print(self.color_text('=' * 80 + '\n', Colors.HEADER))

    def export(self, export_format):
        """
        Export collected hardware data in specified format.
        
        Args:
            export_format (str): Export format - 'json', 'csv', or 'txt'
            
        Returns:
            bool: True if export successful, False otherwise
        """
        if not self.hardware_data:
            print(self.color_text('No data to export. Call collect_all_data() first.', Colors.WARNING))
            return False
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if export_format == 'json':
            filepath = os.path.join(self.export_dir, f'hardware_info_{timestamp}.json')
            return self.export_to_json(filepath)
        elif export_format == 'csv':
            filepath = os.path.join(self.export_dir, f'hardware_info_{timestamp}.csv')
            return self.export_to_csv(filepath)
        elif export_format == 'txt':
            filepath = os.path.join(self.export_dir, f'hardware_info_{timestamp}.txt')
            return self.export_to_txt(filepath)
        
        return False

    def run(self, export_format=None):
        """
        Execute full hardware detection workflow.
        
        Performs compatibility check, collects data, displays it,
        and optionally exports to file.
        
        Args:
            export_format (str or None): Export format if needed
            
        Returns:
            bool: True if run successful, False otherwise
        """
        # Compatibility check for dry-run
        if self.dry_run:
            is_compatible = self.print_compatibility_check()
            return is_compatible
        
        # Full execution - collect data first
        self.collect_all_data()
        
        # Only display if no export, otherwise just export
        if not export_format:
            self.display_all_data()
            return True
        else:
            return self.export(export_format)


def main():
    """
    Command-line interface for HardwareFetcher.
    
    Parses arguments and executes hardware detection workflow.
    Can be run standalone or imported as module class.
    """
    parser = argparse.ArgumentParser(
        description='Hardware Fetcher - Advanced VM Hardware Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''VERBOSITY LEVELS:
  --v         (Level 1): Basic hardware overview
  --vv        (Level 2): Extended information
  --vvv       (Level 3): Deep analysis with all details

EXPORT OPTIONS:
  --export-format=json             Export to JSON
  --export-format=csv              Export to CSV
  --export-format=txt              Export to TXT
  --export-directory=/path         Save exports to specific directory

DRY-RUN MODES:
  --dry-run=true                   Test mode (compatibility check only)
  --dry-run=false                  Normal mode (full execution) [REQUIRED]

EXAMPLES:
  python3 hardware_fetcher.py --vvv --dry-run=true
  python3 hardware_fetcher.py --vvv --dry-run=false
  python3 hardware_fetcher.py --vvv --dry-run=false --export-format=json --export-directory=/tmp
  python3 hardware_fetcher.py --vv --dry-run=false --export-format=csv
        '''
    )
    
    parser.add_argument('--v', action='store_true', help='Verbosity level 1')
    parser.add_argument('--vv', action='store_true', help='Verbosity level 2')
    parser.add_argument('--vvv', action='store_true', help='Verbosity level 3')
    parser.add_argument('--export-format', choices=['json', 'csv', 'txt'], default=None,
                       help='Export format: json, csv, or txt')
    parser.add_argument('--export-directory', default='.',
                       help='Directory to save exports (default: current)')
    parser.add_argument('--dry-run', choices=['true', 'false'], required=True,
                       help='Dry-run mode: true=test only, false=full run (REQUIRED)')
    
    args = parser.parse_args()
    
    # Determine verbosity level
    verbosity = 1
    if args.vvv:
        verbosity = 3
    elif args.vv:
        verbosity = 2
    elif args.v:
        verbosity = 1
    
    # Parse dry-run flag
    dry_run_enabled = args.dry_run == 'true'
    
    # Create and run fetcher
    fetcher = HardwareFetcher(
        verbosity=verbosity,
        dry_run=dry_run_enabled,
        export_directory=args.export_directory
    )
    
    success = fetcher.run(export_format=args.export_format)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(Colors.FAIL + '\n\n[-] Script interrupted by user' + Colors.ENDC)
        sys.exit(1)
    except Exception as e:
        print(Colors.FAIL + '\n[-] Error: ' + str(e) + Colors.ENDC)
        sys.exit(1)
