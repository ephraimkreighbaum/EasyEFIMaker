import os
import requests
from tkinter import *
from tkinter import ttk
from zipfile import ZipFile
from PIL import Image, ImageTk
import subprocess

class EasyEFIMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Easy EFI Maker v0.0.1-alpha")

        self.main_frame = ttk.Frame(root)
        self.main_frame.pack()

        self.required_frame = ttk.Frame(self.main_frame)
        self.required_frame.pack(side=LEFT, padx=10, pady=10)

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

        # optional items
        self.optional_frame = ttk.Frame(self.main_frame)
        self.optional_frame.pack(side=RIGHT, padx=10, pady=10)

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

        # Build efi button
        self.build_efi_button = ttk.Button(root, text="Build EFI", command=self.build_efi, state=DISABLED)
        self.build_efi_button.pack()

        # Download OpenCore button
        self.opencore_button = ttk.Button(self.required_frame, text="Download OpenCore", command=self.download_opencore)
        self.opencore_button.pack(side=LEFT)

        # Download ProperTree button
        self.propertree_button = ttk.Button(self.required_frame, text="Download ProperTree", command=self.download_propertree)
        self.propertree_button.pack(side=LEFT)

        # Console box broken lol
        self.console_box = Text(root, height=10, width=50, state=DISABLED)
        self.console_box.pack()

        self.opencore_folder = "./opencore-files"
        os.makedirs(self.opencore_folder, exist_ok=True)

        self.tools_folder = "./tools"
        os.makedirs(self.tools_folder, exist_ok=True)

    def check_bluetooth(self):
        if self.bluetooth_var.get():
            self.bluetooth_dropdown["state"] = "readonly"
        else:
            self.bluetooth_dropdown["state"] = "disabled"

    def check_wifi(self):
        if self.wifi_var.get():
            self.wifi_dropdown["state"] = "readonly"
        else:
            self.wifi_dropdown["state"] = "disabled"

    def get_latest_version(self, repo_name):
        api_url = f"https://api.github.com/repos/acidanthera/{repo_name}/releases/latest"
        response = requests.get(api_url)
        data = response.json()
        latest_version = data["tag_name"]
        return latest_version

    def download_file(self, url, folder, filename):
        response = requests.get(url)
        filepath = os.path.join(folder, filename)
        with open(filepath, "wb") as file:
            file.write(response.content)
        return filepath

    def build_efi(self):
        self.console_box.config(state=NORMAL)
        self.console_box.delete(1.0, END)

        # VirtualSMC
        virtual_smc_version = self.get_latest_version("VirtualSMC")
        virtual_smc_url = f"https://github.com/acidanthera/VirtualSMC/releases/download/{virtual_smc_version}/VirtualSMC-{virtual_smc_version}.zip"
        virtual_smc_filepath = self.download_file(virtual_smc_url, self.opencore_folder, f"VirtualSMC-{virtual_smc_version}.zip")
        self.console_box.insert(END, f"Downloaded VirtualSMC from {virtual_smc_url} (Version: {virtual_smc_version})\n")

        # USBInjectAll
        usb_inject_all_url = "https://bitbucket.org/RehabMan/os-x-usb-inject-all/downloads/RehabMan-USBInjectAll-2018-1108.zip"
        usb_inject_all_filepath = self.download_file(usb_inject_all_url, self.opencore_folder, "RehabMan-USBInjectAll-2018-1108.zip")
        self.console_box.insert(END, f"Downloaded USBInjectAll from {usb_inject_all_url}\n")

        # Lilu
        lilu_version = self.get_latest_version("Lilu")
        lilu_url = f"https://github.com/acidanthera/Lilu/releases/download/{lilu_version}/Lilu-{lilu_version}.zip"
        lilu_filepath = self.download_file(lilu_url, self.opencore_folder, f"Lilu-{lilu_version}.zip")
        self.console_box.insert(END, f"Downloaded Lilu.kext from {lilu_url} (Version: {lilu_version})\n")

        # WhateverGreen
        whatevergreen_version = self.get_latest_version("WhateverGreen")
        whatevergreen_url = f"https://github.com/acidanthera/WhateverGreen/releases/download/{whatevergreen_version}/WhateverGreen-{whatevergreen_version}.zip"
        whatevergreen_filepath = self.download_file(whatevergreen_url, self.opencore_folder, f"WhateverGreen-{whatevergreen_version}.zip")
        self.console_box.insert(END, f"Downloaded WhateverGreen from {whatevergreen_url} (Version: {whatevergreen_version})\n")

        # Enable build EFI button
        self.build_efi_button["state"] = NORMAL

        self.console_box.config(state=DISABLED)

    def download_opencore(self):
        latest_version_opencore = self.get_latest_version("OpenCorePkg")

        opencore_url = f"https://github.com/acidanthera/OpenCorePkg/releases/download/{latest_version_opencore}/OpenCore-{latest_version_opencore}-RELEASE.zip"

        response = requests.get(opencore_url)
        zip_filename = f"OpenCore-{latest_version_opencore}-RELEASE.zip"

        with open(os.path.join(self.opencore_folder, zip_filename), "wb") as zip_file:
            zip_file.write(response.content)

        with ZipFile(os.path.join(self.opencore_folder, zip_filename), "r") as zip_ref:
            zip_ref.extractall(self.opencore_folder)

        os.remove(os.path.join(self.opencore_folder, zip_filename))

        # Show the checkmark after successful download broken lol
        self.opencore_button["state"] = "disabled"
        self.console_box.insert(END, f"Downloaded OpenCore version: {latest_version_opencore}\n")

    def download_propertree(self):
        # Download ProperTree
        propertree_url = "https://github.com/corpnewt/ProperTree/archive/refs/heads/master.zip"
        propertree_filepath = self.download_file(propertree_url, self.tools_folder, "ProperTree-master.zip")

        # Extract ProperTree
        with ZipFile(propertree_filepath, "r") as zip_ref:
            zip_ref.extractall(os.path.join(self.tools_folder, "propertree"))
        os.remove(propertree_filepath)

        # Show the checkmark after successful download broken lol
        self.propertree_button["state"] = "disabled"
        self.console_box.insert(END, f"Downloaded and extracted ProperTree to {os.path.join(self.tools_folder, 'propertree')}\n")

        # Enable "Edit config.plist" button
        self.propertree_button.config(text="Edit config.plist", command=self.edit_config_plist)

        # Enable build EFI button
        self.build_efi_button["state"] = NORMAL

        # Disable console editing
        self.console_box.config(state=DISABLED)

    def edit_config_plist(self):
        self.console_box.config(state=NORMAL)
        self.console_box.delete(1.0, END)

        # Download ProperTree
        self.download_propertree()

        config_plist_path = os.path.join(self.opencore_folder, "X64", "EFI", "OC", "config.plist")

        # Create config.plist if not exists
        if not os.path.exists(config_plist_path):
            with open(config_plist_path, "w") as file:
                file.write("")

        propertree_folder = os.path.join(self.tools_folder, "propertree")
        propertree_path = os.path.join(propertree_folder, "ProperTree.py")

        subprocess.run(["python", propertree_path, config_plist_path])

        self.console_box.config(state=DISABLED)

if __name__ == "__main__":
    root = Tk()
    app = EasyEFIMaker(root)
    root.mainloop()
