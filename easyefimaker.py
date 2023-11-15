import os
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import Text, StringVar, IntVar, DISABLED, END, NORMAL
from urllib.request import urlopen
from zipfile import ZipFile
import json

class EasyEFIMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Easy EFI Maker v0.0.1-alpha")

        self.main_frame = ttk.Frame(root)
        self.main_frame.pack()

        self.required_frame = ttk.Frame(self.main_frame)
        self.required_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.manufacturer_label = ttk.Label(self.required_frame, text="Select Manufacturer:")
        self.manufacturer_label.pack()

        self.manufacturer_var = StringVar(root)
        self.manufacturer_var.set("Select") 
        self.manufacturer_dropdown = ttk.Combobox(self.required_frame, textvariable=self.manufacturer_var, values=["HP", "DELL", "MSI", "GIGABYTE"], state="readonly")
        self.manufacturer_dropdown.pack()

        self.cpu_label = ttk.Label(self.required_frame, text="Select CPU Generation:")
        self.cpu_label.pack()

        self.cpu_var = StringVar(root)
        self.cpu_var.set("Select") 
        self.cpu_dropdown = ttk.Combobox(self.required_frame, textvariable=self.cpu_var, values=["Dummy1", "Dummy2", "Dummy3", "Dummy4", "Dummy5", "Dummy6", "Dummy7", "Dummy8", "Dummy9", "Dummy10"], state="readonly")
        self.cpu_dropdown.pack()

        self.macos_label = ttk.Label(self.required_frame, text="Select macOS Version:")
        self.macos_label.pack()

        self.macos_var = StringVar(root)
        self.macos_var.set("Select") 
        self.macos_dropdown = ttk.Combobox(self.required_frame, textvariable=self.macos_var, values=["macOS 10.15", "macOS 11.0", "macOS 12.0"], state="readonly")
        self.macos_dropdown.pack()

        # Optional items
        self.optional_frame = ttk.Frame(self.main_frame)
        self.optional_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.optional_title_label = ttk.Label(self.optional_frame, text="Optional:")
        self.optional_title_label.pack()

        self.bluetooth_var = IntVar()
        self.bluetooth_checkbox = ttk.Checkbutton(self.optional_frame, text="Bluetooth", variable=self.bluetooth_var, command=self.check_bluetooth)
        self.bluetooth_checkbox.pack()

        self.bluetooth_dropdown = ttk.Combobox(self.optional_frame, values=["Intel", "Broadcom"], state="readonly")
        self.bluetooth_dropdown.pack()

        self.wifi_var = IntVar()
        self.wifi_checkbox = ttk.Checkbutton(self.optional_frame, text="WiFi", variable=self.wifi_var, command=self.check_wifi)
        self.wifi_checkbox.pack()

        self.wifi_dropdown = ttk.Combobox(self.optional_frame, values=["Intel", "Broadcom"], state="readonly")
        self.wifi_dropdown.pack()

        # Build EFI button
        self.build_efi_button = ttk.Button(root, text="Build EFI", command=self.build_efi, state=DISABLED)
        self.build_efi_button.pack()

        # Download OpenCore button
        self.opencore_button = ttk.Button(self.required_frame, text="Download OpenCore", command=self.download_opencore)
        self.opencore_button.pack(side=tk.LEFT)

        # Download ProperTree button
        self.propertree_button = ttk.Button(self.required_frame, text="Download ProperTree", command=self.download_propertree)
        self.propertree_button.pack(side=tk.LEFT)

        # Console box
        self.console_box = Text(root, height=10, width=50, state=DISABLED)
        self.console_box.pack()

        # Initialize folders
        self.opencore_folder = "./opencore-files"
        os.makedirs(self.opencore_folder, exist_ok=True)

        self.tools_folder = "./tools"
        os.makedirs(self.tools_folder, exist_ok=True)

        # Check if ProperTree is already downloaded
        propertree_folder = os.path.join(self.tools_folder, "propertree")
        os.makedirs(propertree_folder, exist_ok=True)  # Create the folder if it doesn't exist
        propertree_button_text = "Edit config.plist" if os.listdir(propertree_folder) else "Download ProperTree"
        self.propertree_button_state = NORMAL if os.path.exists(propertree_folder) else DISABLED

        # Enable "Edit config.plist" button
        self.propertree_button.config(text=propertree_button_text, command=self.edit_config_plist, state=self.propertree_button_state)

    def check_bluetooth(self):
        self.bluetooth_dropdown["state"] = "readonly" if self.bluetooth_var.get() else "disabled"

    def check_wifi(self):
        self.wifi_dropdown["state"] = "readonly" if self.wifi_var.get() else "disabled"

    def get_latest_version(self, repo_name):
        api_url = f"https://api.github.com/repos/acidanthera/{repo_name}/releases/latest"
        response = urlopen(api_url)
        data = response.read()
        data_str = data.decode('utf-8')  
        json_data = json.loads(data_str)  
        latest_version = json_data["tag_name"]
        return latest_version

    def download_file(self, url, folder, filename):
        response = urlopen(url)
        filepath = os.path.join(folder, filename)
        with open(filepath, "wb") as file:
            file.write(response.read())
        return filepath

    def build_efi(self):
        self.console_box.config(state=NORMAL)
        self.console_box.delete(1.0, END)

        components = [
            ("VirtualSMC", "https://github.com/acidanthera/VirtualSMC/releases/latest", "VirtualSMC"),
            ("USBInjectAll", "https://bitbucket.org/RehabMan/os-x-usb-inject-all/downloads", "RehabMan-USBInjectAll-2018-1108"),
            ("Lilu", "https://github.com/acidanthera/Lilu/releases/latest", "Lilu"),
            ("WhateverGreen", "https://github.com/acidanthera/WhateverGreen/releases/latest", "WhateverGreen")
        ]

        for component_name, component_url, component_filename in components:
            component_version = self.get_latest_version(component_name)
            component_download_url = f"{component_url}/{component_filename}-{component_version}.zip"
            component_filepath = self.download_file(component_download_url, self.opencore_folder, f"{component_filename}-{component_version}.zip")
            self.console_box.insert(END, f"Downloaded {component_name} from {component_download_url} (Version: {component_version})\n")

        self.build_efi_button["state"] = NORMAL
        self.console_box.config(state=DISABLED)

    def download_opencore(self):
        latest_version_opencore = self.get_latest_version("OpenCorePkg")

        opencore_url = f"https://github.com/acidanthera/OpenCorePkg/releases/download/{latest_version_opencore}/OpenCore-{latest_version_opencore}-RELEASE.zip"

        response = urlopen(opencore_url)
        zip_filename = f"OpenCore-{latest_version_opencore}-RELEASE.zip"

        with open(os.path.join(self.opencore_folder, zip_filename), "wb") as zip_file:
            zip_file.write(response.read())

        with ZipFile(os.path.join(self.opencore_folder, zip_filename), "r") as zip_ref:
            zip_ref.extractall(self.opencore_folder)

        os.remove(os.path.join(self.opencore_folder, zip_filename))

        self.opencore_button.config(text=f"✔ Downloaded OpenCore {latest_version_opencore}", state="disabled")
        self.console_box.insert(END, f"Downloaded OpenCore version: {latest_version_opencore}\n")

    def download_propertree(self):
        self.console_box.config(state=NORMAL)
        self.console_box.delete(1.0, END)
        self.console_box.insert(END, "Downloading and extracting the latest version of ProperTree...\n")

        propertree_url = "https://github.com/corpnewt/ProperTree/archive/refs/heads/master.zip"
        propertree_filepath = self.download_file(propertree_url, self.tools_folder, "ProperTree-master.zip")

        with ZipFile(propertree_filepath, "r") as zip_ref:
            zip_ref.extractall(os.path.join(self.tools_folder, "propertree"))
        os.remove(propertree_filepath)

        self.propertree_button.config(text="✔ Downloaded ProperTree", state="disabled")
        self.console_box.insert(END, f"Downloaded and extracted ProperTree to {os.path.join(self.tools_folder, 'propertree')}\n")

        self.propertree_button.config(text="Edit config.plist", command=self.edit_config_plist, state=NORMAL)
        self.build_efi_button["state"] = NORMAL
        self.console_box.config(state=DISABLED)

    def edit_config_plist(self):
        self.console_box.config(state=NORMAL)
        self.console_box.delete(1.0, END)

        propertree_folder = os.path.join(self.tools_folder, "propertree")

        if not os.path.exists(propertree_folder):
            self.download_propertree()

        propertree_path = os.path.join(propertree_folder, "ProperTree-master", "ProperTree.py")

        config_plist_path = os.path.join(self.opencore_folder, "X64", "EFI", "OC", "config.plist")

        if not os.path.exists(config_plist_path):
            with open(config_plist_path, "w") as file:
                file.write("")

        try:
            process = subprocess.run(["python", propertree_path, config_plist_path], capture_output=True, text=True, check=True)
            output = process.stdout
            self.console_box.insert(END, f"ProperTree output:\n{output}\n")
        except subprocess.CalledProcessError as e:
            error_output = e.stderr
            self.console_box.insert(END, f"ProperTree encountered an error:\n{error_output}\n")

        self.console_box.config(state=DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = EasyEFIMaker(root)
    root.mainloop()
