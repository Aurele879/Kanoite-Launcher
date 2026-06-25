import configparser
from gui import Gui
from profile import Profile
import pickle
import os
import shutil
from tkinter import messagebox
import minecraft_launcher_lib
import json
import threading
import uuid
import hashlib
import ctypes
import time
import subprocess
from pypresence import Presence

"""
Global Variables
"""
ui = Gui()
username = None
config = configparser.ConfigParser()
profile_list = []
ram = "2"

"""
Rich Presence setup
"""
presence = Presence("1495473776043757819")

def discord_presence_worker(): #Function setting up the link with the discord API
    try:
        presence.connect()
        presence.update(
            state="Idle",
            large_text="Astro Launcher 2",
            small_image="block"
        )
        while True:
            time.sleep(15)
    except Exception:
        pass

def update_discord_presence(state): #Function used to update the activity of the user
    try:
        presence.update(state=state)
    except Exception:
        pass

thread = threading.Thread(target=discord_presence_worker, daemon=True)
thread.start()

"""
Backend
"""
def get_options():
    options = {
    "username": username,
    "uuid": str(uuid.UUID(bytes=hashlib.md5(bytes(f"OfflinePlayer:{username}", "utf-8")).digest()[:16])),
    "token": "",
    "jvmArguments": [f"-Xmx{ram}G", f"-Xms{ram}G"]}
    return options

def get_profiles_list(): #Load the stored profiles list
    filename = "profiles.dat"
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        return []
    with open(filename, "rb") as f:
        return pickle.load(f)

def get_profile_list_by_name(): #Returns a list with all the profiles's names
    profile_list_by_name = []
    for element in get_profiles_list():
        profile_list_by_name.append(element.name)
    return profile_list_by_name

def get_profile_from_name(name): #Returns a profile from its name
    for profile in get_profiles_list():
        if profile.name == name:
            return profile
        
def get_last_used_profile(): #Returns the last used profile
    saved_profile = config['GUI']['last_used_profile']
    return saved_profile

def save_last_used_profile(): #Save the last used profile in the config file
    config.set('GUI', 'last_used_profile', ui.profiles_combobox_variable.get())
    with open("config.ini", 'w') as configfile:
        config.write(configfile)

def save_profiles(): #Save a profile
    with open("profiles.dat", "wb") as f:
        pickle.dump(profile_list, f)

def create_profile(): #Create a profile
    if not verify_str(ui.profile_name_entry.get()) or ui.profile_name_entry.get() in get_profile_list_by_name():
        messagebox.showerror("Error", "Invalid Name.")
        return
    try:
        os.mkdir(f"instances/{ui.profile_name_entry.get()}")
        create_dummy_launcher_config(f"instances/{ui.profile_name_entry.get()}", ui.versions_combobox.get())
        profile_list.append(Profile(ui.profile_name_entry.get(), ui.versions_combobox.get()))
        save_profiles()
        ui.profiles_combobox_variable.set(ui.profile_name_entry.get())
        save_last_used_profile()
        go_to_main()
    except Exception as e:
        messagebox.showerror("Error", f"Unable to create profile:\n{str(e)}")

def edit_profile(): #Edit a profile
    old_name = ui.profiles_combobox.get()
    new_name = ui.profile_name_entry.get()
    new_version = ui.versions_combobox.get()

    if (new_name != old_name and new_name in get_profile_list_by_name()) or not verify_str(new_name):
        messagebox.showerror("Error", "Invalid Name.")
        return

    target_index = -1
    for i, p in enumerate(profile_list):
        if p.name == old_name:
            target_index = i
            break

    if target_index != -1:
        try:
            old_profile = profile_list[target_index]
            old_dir = old_profile.profile_directory
            new_dir = os.path.join("instances", new_name)
            create_dummy_launcher_config(old_dir, new_version)
            os.rename(old_dir, new_dir)
            profile_list[target_index] = Profile(new_name, new_version)

            save_profiles()
            ui.profiles_combobox_variable.set(new_name)
            save_last_used_profile()
            go_to_main()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to edit profile:\n{str(e)}")

def delete_profile(): #Delete a profile
    profile_name = ui.profiles_combobox.get()
    if not messagebox.askyesno("Profile Removal", f"Are you sure you want to delete '{profile_name}' and all its data?"):
        return

    target_index = -1
    for i, p in enumerate(profile_list):
        if p.name == profile_name:
            target_index = i
            break

    if target_index != -1:
        try:
            profile_to_delete = profile_list[target_index]
            shutil.rmtree(profile_to_delete.profile_directory)
            profile_list.pop(target_index)
            save_profiles()
            go_to_main()
            messagebox.showinfo("Profile Removal", f"Profile '{profile_name}' has been deleted.")
        except Exception as e:
            messagebox.showerror("Error", f"Unable to delete profile:\n{str(e)}")

def open_directory(): #Opens the profile's directory
    try:
        profile_name = ui.profiles_combobox.get()
        profile = get_profile_from_name(profile_name)
        path = os.path.abspath(profile.profile_directory)
        os.startfile(path)
    except Exception as e:
        messagebox.showerror("Error", f"Unable to open profile directory:\n{str(e)}")

def get_available_versions(): #Returns all the official versions of the game
    versions_list = []
    for version in minecraft_launcher_lib.utils.get_version_list():
        if version["type"] == "release": versions_list.append(version["id"])
    return versions_list
        
def get_installed_and_available_versions(selected_profile): #Returns all the official versions of the game and the ones installed
    versions_list = []
    for version in minecraft_launcher_lib.utils.get_available_versions(selected_profile.profile_directory):
        if version["type"] in ["release", "forge", "neoforge", "fabric"]:
            versions_list.append(version["id"])
    return versions_list

def verify_str(string_to_verify): #Verify if a string is valid for a profile name
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    if string_to_verify == "" or string_to_verify == "none": return False
    for element in string_to_verify:
        if element not in allowed_chars:
            return False
    return True

def get_system_ram(): # Returns system RAM in GB
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]
    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    total_ram_gb = round(stat.ullTotalPhys / (1024 ** 3))
    if total_ram_gb < 2:
        total_ram_gb = 2
    return total_ram_gb

def create_dummy_launcher_config(profile_directory, version): #Create a dummy launcher_profiles.json
    data = {
        "profiles": {
            "Default": {
                "name": "Default",
                "type": "custom",
                "created": "2026-01-01T00:00:00.000Z",
                "lastUsed": "2026-01-01T00:00:00.000Z",
                "icon": "Grass",
                "lastVersionId": version
            }
        },
        "settings": {
            "crashAssistance": True,
            "enableAdvanced": True
        },
        "launcherVersion": {
            "format": 21,
            "name": "2.x",
            "profilesFormat": 3
        }
    }
    if os.path.exists(os.path.join(profile_directory, "launcher_profiles.json")):
        os.remove(os.path.join(profile_directory, "launcher_profiles.json"))
    os.makedirs(profile_directory, exist_ok=True)
    path = os.path.join(profile_directory, "launcher_profiles.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def download_game_files(profile): #Install missing version if needed, then launch
    found = False
    for element in minecraft_launcher_lib.utils.get_installed_versions(profile.profile_directory):
        if element["id"] == profile.version:
            found = True
            break
    try:
        if found == False:
            minecraft_launcher_lib.install.install_minecraft_version(profile.version, profile.profile_directory)
        
        command = minecraft_launcher_lib.command.get_minecraft_command(profile.version, profile.profile_directory, profile.options)
        process = subprocess.Popen(command, creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP)
        
        ui.root.withdraw()
        update_discord_presence(f"Playing Minecraft {profile.version}")
        
        wait_thread = threading.Thread(target=wait_minecraft_close, args=(process,), daemon=True)
        wait_thread.start()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while launching the game: {str(e)}")
        ui.root.deiconify()
        go_to_main()
        update_discord_presence("Idle")

def wait_minecraft_close(process): #Restore launcher UI when game closes
    process.wait()
    time.sleep(1)
    ui.root.deiconify()
    go_to_main()
    update_discord_presence("Idle")

def start_game(): #Start the game files download and launch
    selected_profile_name = ui.profiles_combobox_variable.get()
    if selected_profile_name == "none" or not selected_profile_name:
        messagebox.showerror("Error", "Create a profile first !")
        return
    ui.loading_page(text='Downloading game files ...')
    selected_profile = get_profile_from_name(selected_profile_name)
    save_last_used_profile()
    selected_profile.set_options(get_options())
    thread = threading.Thread(target=lambda: download_game_files(selected_profile), daemon=True)
    thread.start()


"""
Frontend interactions
"""
def connect():
    global username
    username = ui.username_entry.get()
    if len(username) == 0:
        messagebox.showerror("Error", "Username cannot be empty.")
        return
    if not verify_str(username):
        messagebox.showerror("Error", "Username can only contain letters, numbers and underscores.")
        return
    config.set('GUI', 'last_used_nickname', username)
    with open("config.ini", 'w') as configfile:
        config.write(configfile)
    go_to_main()

def go_to_settings():
    max_ram = get_system_ram()
    ui.ram_slider.configure(from_=1, to=max_ram - 1, number_of_steps=int(max_ram - 1))
    saved_ram = int(config.get('GUI', 'ram_allocation', fallback='2'))
    ui.ram_slider.set(saved_ram)
    ui.update_ram_label(saved_ram)
    ui.settings_page()

def save_settings():
    ram = str(int(ui.ram_slider.get()))
    config.set('GUI', 'ram_allocation', ram)
    with open("config.ini", 'w') as configfile:
        config.write(configfile)
    go_to_main()

def go_to_main():
    ui.versions_combobox.set("") 
    ui.profile_name_entry.delete(0, 'end') 
    ui.profiles_combobox_variable.set(get_last_used_profile())
    ui.fill_profiles_combobox(get_profile_list_by_name()) 
    ui.main_page()

def go_to_new_profile():
    version_list = get_available_versions()
    ui.fill_versions_combobox(version_list)
    if version_list:
        ui.versions_combobox.set(version_list[0])
    ui.create_profile_page()

def go_to_edit_profile():
    current_profile = get_profile_from_name(ui.profiles_combobox_variable.get())
    if current_profile is None or ui.profiles_combobox_variable.get() == "none":
        messagebox.showerror("Error", "Select a profile first !")
        return
    ui.versions_combobox.set(current_profile.version) 
    ui.fill_versions_combobox(get_installed_and_available_versions(current_profile)) 
    ui.profile_name_entry.delete(0, 'end')
    ui.profile_name_entry.insert(0, current_profile.name)
    ui.edit_profile_page()

def run():
    ui.create_profile_button.configure(command=lambda: create_profile())
    ui.off_login_button.configure(command=lambda: connect())
    ui.settings_button.configure(command=lambda: go_to_settings())
    ui.edit_profile_button.configure(command=lambda: go_to_edit_profile())
    ui.play_button.configure(command=lambda: start_game())
    ui.add_profile_button.configure(command=lambda: go_to_new_profile())
    ui.back_button.configure(command=lambda: go_to_main())
    
    ui.save_settings_button.configure(command=lambda: save_settings())
    ui.save_edited_profile_button.configure(command=lambda: edit_profile())
    ui.delete_profile_button.configure(command=lambda: delete_profile())
    ui.profile_dir_button.configure(command=lambda: open_directory())
    ui.add_loader_button.configure(command=lambda: messagebox.showinfo("Info", "ModLoader selection feature not implemented yet."))

    saved_username = config.get('GUI', 'last_used_nickname', fallback='Steve')
    if saved_username != "Steve":
        ui.username_entry.insert(0, saved_username)
        
    ui.display()

if __name__ == "__main__":
    if not os.path.exists("config.ini"):
        config['GUI'] = {
            'last_used_profile': 'none',
            'last_used_nickname': 'Steve',
            'ram_allocation': '2'
        }
        with open("config.ini", 'w') as configfile:
            config.write(configfile)
    else:
        config.read('config.ini')

    ram = config.get('GUI', 'ram_allocation', fallback='2')
    profile_list = get_profiles_list()

    if not os.path.exists("instances"):
        os.mkdir("instances")
    run()