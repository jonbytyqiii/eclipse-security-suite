#!/usr/bin/env python3
import os
import logging
from PIL import Image
from PIL.ExifTags import TAGS
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class ImageForensicsEngine:
    def __init__(self, core_framework):
        self.core = core_framework

    def convert_to_degrees(self, value):
        """Helper method to parse tuple-based EXIF rational numbers into clean decimal degrees"""
        try:
            d = float(value[0])
            m = float(value[1])
            s = float(value[2])
            return d + (m / 60.0) + (s / 3600.0)
        except:
            return None

    def extract_gps_coordinates(self, exif_data):
        """Extracts and formats raw GPS geolocation tags into actionable telemetry mappings"""
        gps_info = {}
        for tag, value in exif_data.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                # GPSInfo contains sub-tags; map them out
                for sub_tag in value:
                    from PIL.ExifTags import GPSTAGS
                    decoded_sub = GPSTAGS.get(sub_tag, sub_tag)
                    gps_info[decoded_sub] = value[sub_tag]
        
        if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
            lat = self.convert_to_degrees(gps_info["GPSLatitude"])
            lon = self.convert_to_degrees(gps_info["GPSLongitude"])
            
            # Adjust signs based on reference quadrants (South/West require negative values)
            if lat and gps_info.get("GPSLatitudeRef") == "S": lat = -lat
            if lon and gps_info.get("GPSLongitudeRef") == "W": lon = -lon
            
            return lat, lon
        return None

    def run(self, raw_path):
        """Parses target metadata payloads for forensic validation analysis"""
        # Strip trailing or leading quotes added by terminal drag-and-drop actions
        image_path = raw_path.strip("'\"")
        
        if not os.path.exists(image_path):
            console.print(f"[bold red][!] ERROR: Specified target file path does not exist: {image_path}[/bold red]")
            return

        console.print(f"\n[bold magenta][*][/bold magenta] Extracting binary image metadata from: [bold cyan]{os.path.basename(image_path)}[/bold cyan]")
        
        try:
            img = Image.open(image_path)
            exif = img._getexif()
            
            if not exif:
                console.print(Panel("[bold yellow][!] EXIF METADATA EMPTY: No digital metadata footprints embedded within this file.[/bold yellow]", border_style="yellow"))
                return

            # Build data grid table
            table = Table(title="EXIF Metadata Breakdown Matrix", border_style="yellow", header_style="bold yellow", expand=True)
            table.add_column("Hardware/Software Tag", style="white", width=25)
            table.add_column("Extracted Structural Value", style="cyan")

            for tag, value in exif.items():
                decoded_tag = TAGS.get(tag, tag)
                # Filter out messy raw binary blobs to keep the console clean
                if decoded_tag not in ["MakerNote", "PrintImageMatching", "UserComment", "GPSInfo"]:
                    table.add_row(str(decoded_tag), str(value)[:90])

            console.print(table)
            
            # Run GPS extraction checks
            gps_coords = self.extract_gps_coordinates(exif)
            if gps_coords:
                lat, lon = gps_coords
                maps_url = f"https://www.google.com/maps/place/{lat},{lon}"
                
                telemetry_data = (
                    f"[bold green][+] TARGET GEOLOCATION ACQUIRED[/bold green]\n\n"
                    f"[bold white]Latitude Decimal Degrees:[/bold white] {lat}\n"
                    f"[bold white]Longitude Decimal Degrees:[/bold white] {lon}\n"
                    f"[bold white]Active Intel Link:[/bold white] [underline cyan]{maps_url}[/underline cyan]"
                )
                console.print("\n")
                console.print(Panel(telemetry_data, title="🎯 TELEMETRY COORDINATES LOGGED", border_style="green"))
                
                # Log findings out straight to our central database repository
                self.core.log_intel(
                    vector="IMAGE_FORENSICS",
                    email=f"geo-intel@{os.path.basename(image_path)}",
                    business="EXIF Geolocation Coordinates Extracted",
                    url=maps_url,
                    zone=f"Lat: {round(lat,4)}, Lon: {round(lon,4)}"
                )
            else:
                console.print("\n[bold yellow][!] Telemetry Notice: No valid GPS coordinate blocks recovered inside the target file header.[/bold yellow]")

        except Exception as e:
            console.print(f"[bold red][!] Forensic Parsing Failure: {e}[/bold red]")
            logging.error(f"EXIF parsing drop: {e}")