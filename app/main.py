import configparser
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.gui import Gui
from core.profile import Profile
from core import auth
import pickle
import shutil
from tkinter import messagebox
import minecraft_launcher_lib
import json
import threading
import uuid
import ctypes
import time
import subprocess
from pypresence import Presence

"""
GLOBAL VARIABLES
"""
ui = Gui()
current_account = None
config = configparser.ConfigParser()
profile_list = []
ram = "2"
stop_auth_event = threading.Event()


"""
DISCORD RICH PRESENCE
"""
presence = Presence("1495473776043757819")


def discord_presence_worker():
#Set up and maintain connection with the Discord Rich Presence API
    try:
        presence.connect()
        presence.update(
            state="Idle",
            large_text="Kanoite Launcher",
            small_image="block"
        )
        while True:
            time.sleep(15)
    except Exception:
        pass


def update_discord_presence(state):
#Update current user activity on Discord
    try:
        presence.update(state=state)
    except Exception:
        pass


thread = threading.Thread(target=discord_presence_worker, daemon=True)
thread.start()


"""
BACKEND
"""
def get_options():
#Generate launch options including username, UUID, token, and RAM
    global current_account
    if current_account is None:
        current_account = auth.load_account()

    if current_account:
        player_name = current_account.get("name", "Player")
        player_uuid = current_account.get("id", str(uuid.uuid4()))
        player_token = current_account.get("access_token", "")
    else:
        player_name = "Player"
        player_uuid = str(uuid.uuid4())
        player_token = ""

    options = {
        "username": player_name,
        "uuid": player_uuid,
        "token": player_token,
        "jvmArguments": [f"-Xmx{ram}G", f"-Xms{ram}G"],
        "launcherName": "Kanoite Launcher",
        "launcherVersion": "2.0"
    }
    return options


def get_profiles_list():
#Load stored profiles list from disk
    profiles_filename = "data/profiles.dat"
    if not os.path.exists(profiles_filename) or os.path.getsize(profiles_filename) == 0:
        return []
    with open(profiles_filename, "rb") as file:
        return pickle.load(file)


def get_profile_list_by_name():
#Return a list containing all profile names
    profile_names = []
    for profile in get_profiles_list():
        profile_names.append(profile.name)
    return profile_names


def get_profile_from_name(name):
#Find and return a profile matching the given name
    for profile in get_profiles_list():
        if profile.name == name:
            return profile


def get_last_used_profile():
#Retrieve the last used profile name from configuration
    return config.get('GUI', 'last_used_profile', fallback='none')


def save_last_used_profile():
#Save the currently selected profile name in configuration
    config.set('GUI', 'last_used_profile', ui.profiles_combobox_variable.get())
    with open("data/config.ini", 'w') as configfile:
        config.write(configfile)


def save_profiles():
#Save the current list of profiles to disk
    with open("data/profiles.dat", "wb") as file:
        pickle.dump(profile_list, file)


def create_profile():
#Validate input and create a new isolated Minecraft profile
    profile_name = ui.profile_name_entry.get()
    selected_version = ui.versions_combobox.get()

    if not verify_str(profile_name) or profile_name in get_profile_list_by_name():
        messagebox.showerror("Error", "Invalid Name.")
        return

    try:
        instance_directory = f"game/{profile_name}"
        os.mkdir(instance_directory)
        create_dummy_launcher_config(instance_directory, selected_version)
        profile_list.append(Profile(profile_name, selected_version))
        save_profiles()
        ui.profiles_combobox_variable.set(profile_name)
        save_last_used_profile()
        go_to_main()
    except Exception as error:
        messagebox.showerror("Error", f"Unable to create profile:\n{str(error)}")


def edit_profile():
#Modify an existing profile name and game version
    old_name = ui.profiles_combobox.get()
    new_name = ui.profile_name_entry.get()
    new_version = ui.versions_combobox.get()

    if (new_name != old_name and new_name in get_profile_list_by_name()) or not verify_str(new_name):
        messagebox.showerror("Error", "Invalid Name.")
        return

    target_index = -1
    for index, profile in enumerate(profile_list):
        if profile.name == old_name:
            target_index = index
            break

    if target_index != -1:
        try:
            old_profile = profile_list[target_index]
            old_directory = old_profile.profile_directory
            new_directory = os.path.join("game", new_name)
            create_dummy_launcher_config(old_directory, new_version)
            os.rename(old_directory, new_directory)
            profile_list[target_index] = Profile(new_name, new_version)

            save_profiles()
            ui.profiles_combobox_variable.set(new_name)
            save_last_used_profile()
            go_to_main()
        except Exception as error:
            messagebox.showerror("Error", f"Unable to edit profile:\n{str(error)}")


def delete_profile():
#Remove an existing profile and delete its instance directory
    profile_name = ui.profiles_combobox.get()
    if not messagebox.askyesno("Profile Removal", f"Are you sure you want to delete '{profile_name}' and all its data?"):
        return

    target_index = -1
    for index, profile in enumerate(profile_list):
        if profile.name == profile_name:
            target_index = index
            break

    if target_index != -1:
        try:
            profile_to_delete = profile_list[target_index]
            shutil.rmtree(profile_to_delete.profile_directory)
            profile_list.pop(target_index)
            save_profiles()

            remaining_profiles = get_profile_list_by_name()
            if len(remaining_profiles) > 0:
                ui.profiles_combobox_variable.set(remaining_profiles[0])
            else:
                ui.profiles_combobox_variable.set("none")
            save_last_used_profile()

            go_to_main()
            messagebox.showinfo("Profile Removal", f"Profile '{profile_name}' has been deleted.")
        except Exception as error:
            messagebox.showerror("Error", f"Unable to delete profile:\n{str(error)}")


def open_directory():
#Open the current profile folder in the system file explorer
    try:
        profile_name = ui.profiles_combobox.get()
        profile = get_profile_from_name(profile_name)
        absolute_path = os.path.abspath(profile.profile_directory)
        os.startfile(absolute_path)
    except Exception as error:
        messagebox.showerror("Error", f"Unable to open profile directory:\n{str(error)}")


def get_available_versions():
#Retrieve all official release versions from Mojang servers
    version_list = []
    try:
        for version in minecraft_launcher_lib.utils.get_version_list():
            if version["type"] == "release":
                version_list.append(version["id"])
    except Exception:
        pass
    return version_list


def get_installed_and_available_versions(selected_profile):
#Retrieve installed versions and official releases for a profile
    version_list = []
    for version in minecraft_launcher_lib.utils.get_available_versions(selected_profile.profile_directory):
        if version["type"] in ["release", "forge", "neoforge", "fabric"]:
            version_list.append(version["id"])
    return version_list


def verify_str(name_to_verify):
#Verify that a profile name contains only allowed characters
    allowed_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    if name_to_verify == "" or name_to_verify == "none":
        return False
    for char in name_to_verify:
        if char not in allowed_characters:
            return False
    return True


def get_system_ram():
#Detect and return total physical system RAM in gigabytes
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
    memory_status = MEMORYSTATUSEX()
    memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))
    total_ram_gb = round(memory_status.ullTotalPhys / (1024 ** 3))
    if total_ram_gb < 2:
        total_ram_gb = 2
    return total_ram_gb


def create_dummy_launcher_config(profile_directory, version):
#Create a standard launcher_profiles JSON file in the profile directory
    configuration_data = {
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
    config_file_path = os.path.join(profile_directory, "launcher_profiles.json")
    if os.path.exists(config_file_path):
        os.remove(config_file_path)
    os.makedirs(profile_directory, exist_ok=True)
    with open(config_file_path, "w", encoding="utf-8") as file:
        json.dump(configuration_data, file, indent=4)


def download_game_files(profile):
#Download missing Minecraft game files and start the game process
    is_version_installed = False
    for installed_version in minecraft_launcher_lib.utils.get_installed_versions(profile.profile_directory):
        if installed_version["id"] == profile.version:
            is_version_installed = True
            break
    try:
        if not is_version_installed:
            minecraft_launcher_lib.install.install_minecraft_version(profile.version, profile.profile_directory)

        command = minecraft_launcher_lib.command.get_minecraft_command(profile.version, profile.profile_directory, profile.options)
        process = subprocess.Popen(command, creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP)

        ui.root.withdraw()
        update_discord_presence(f"Playing Minecraft {profile.version}")

        wait_thread = threading.Thread(target=wait_minecraft_close, args=(process,), daemon=True)
        wait_thread.start()
    except Exception as error:
        messagebox.showerror("Error", f"An error occurred while launching the game: {str(error)}")
        ui.root.deiconify()
        go_to_main()
        update_discord_presence("Idle")


def wait_minecraft_close(process):
#Wait for the Minecraft process to terminate and restore the launcher window
    process.wait()
    time.sleep(1)
    ui.root.deiconify()
    go_to_main()
    update_discord_presence("Idle")


def start_game():
#Validate account and profile before starting game installation and launch
    global current_account
    selected_profile_name = ui.profiles_combobox_variable.get()
    if selected_profile_name == "none" or not selected_profile_name:
        messagebox.showerror("Error", "Create a profile first !")
        return

    if not current_account:
        current_account = auth.load_account()
        if not current_account:
            messagebox.showerror("Authentication Required", "Please connect to your Microsoft account first.")
            ui.ms_login_page()
            return

    ui.loading_page(text='Downloading game files ...')
    selected_profile = get_profile_from_name(selected_profile_name)
    save_last_used_profile()
    selected_profile.set_options(get_options())
    download_thread = threading.Thread(target=lambda: download_game_files(selected_profile), daemon=True)
    download_thread.start()


"""
MICROSOFT AUTHENTICATION
"""
def start_microsoft_login():
#Initiate the Microsoft authentication process in a background thread
    global stop_auth_event
    stop_auth_event.set()
    stop_auth_event = threading.Event()
    ui.ms_login_button.configure(state="disabled")
    ui.update_ms_status("Connecting to Microsoft services...")

    login_thread = threading.Thread(target=microsoft_login_worker, daemon=True)
    login_thread.start()


def microsoft_login_worker():
#Execute the complete Microsoft and Xbox Live login pipeline
    global current_account, stop_auth_event
    try:
        device_data = auth.request_device_code()
        if stop_auth_event.is_set():
            return

        user_code = device_data["user_code"]
        device_code = device_data["device_code"]
        verification_uri = device_data.get("verification_uri", "https://www.microsoft.com/link")
        interval = device_data.get("interval", 5)
        expires_in = device_data.get("expires_in", 900)

        def display_code():
            ui.ms_code_page(user_code, verification_uri)

        ui.root.after(0, display_code)

        token_data = auth.poll_device_token(
            device_code=device_code,
            interval=interval,
            expires_in=expires_in,
            stop_event=stop_auth_event,
            status_callback=lambda message: ui.root.after(0, lambda msg=message: ui.update_ms_status(msg))
        )

        if stop_auth_event.is_set() or token_data is None:
            return

        account = auth.complete_login_with_token(
            ms_access_token=token_data["access_token"],
            ms_refresh_token=token_data.get("refresh_token", ""),
            status_callback=lambda message: ui.root.after(0, lambda msg=message: ui.update_ms_status(msg))
        )

        auth.save_account(account)
        current_account = account

        def on_success():
            ui.set_account_display(account["name"])
            messagebox.showinfo("Success", f"Welcome, {account['name']}!\nSuccessfully connected with Microsoft.")
            go_to_main()

        ui.root.after(0, on_success)

    except Exception as error:
        if not stop_auth_event.is_set():
            error_text = str(error)
            def on_error(msg=error_text):
                ui.ms_login_page()
                messagebox.showerror("Authentication Error", msg)
            ui.root.after(0, on_error)


def cancel_microsoft_login():
#Cancel the active Microsoft authentication polling request
    global stop_auth_event
    stop_auth_event.set()
    ui.ms_login_page()


def logout():
#Sign out of the current Microsoft account and return to login screen
    global current_account
    player_name = current_account.get("name", "Player") if current_account else "Player"
    if not messagebox.askyesno("Logout", f"Are you sure you want to sign out from '{player_name}'?"):
        return
    auth.remove_account()
    current_account = None
    ui.ms_login_page()


def try_auto_login():
#Attempt automatic sign-in with cached credentials or open login screen
    global current_account
    account = auth.load_account()
    if account:
        current_account = account
        ui.set_account_display(account.get("name", "Player"))

        def silent_refresh():
            global current_account
            try:
                refreshed_account = auth.refresh_account_token(account.get("refresh_token", ""))
                current_account = refreshed_account
                ui.root.after(0, lambda: ui.set_account_display(current_account.get("name", "Player")))
            except Exception:
                pass

        refresh_thread = threading.Thread(target=silent_refresh, daemon=True)
        refresh_thread.start()
        go_to_main()
    else:
        ui.ms_login_page()


"""
FRONTEND INTERACTIONS
"""
def go_to_settings():
#Load settings configuration and display the settings page
    max_ram = get_system_ram()
    ui.ram_slider.configure(from_=1, to=max_ram - 1, number_of_steps=int(max_ram - 1))
    saved_ram = int(config.get('GUI', 'ram_allocation', fallback='2'))
    ui.ram_slider.set(saved_ram)
    ui.update_ram_label(saved_ram)
    ui.settings_page()


def save_settings():
#Save modified settings to configuration and return to main page
    global ram
    ram = str(int(ui.ram_slider.get()))
    config.set('GUI', 'ram_allocation', ram)
    with open("data/config.ini", 'w') as configfile:
        config.write(configfile)
    go_to_main()


def go_to_main():
#Refresh profiles list and display the main launcher screen
    ui.versions_combobox.set("")
    ui.profile_name_entry.delete(0, 'end')
    ui.profiles_combobox_variable.set(get_last_used_profile())
    ui.fill_profiles_combobox(get_profile_list_by_name())
    if current_account:
        ui.set_account_display(current_account.get("name", "Player"))
    ui.main_page()


def go_to_new_profile():
#Populate versions list and display the profile creation screen
    version_list = get_available_versions()
    ui.fill_versions_combobox(version_list)
    if version_list:
        ui.versions_combobox.set(version_list[0])
    else:
        ui.versions_combobox.set("")
        messagebox.showwarning("Warning", "Unable to fetch Minecraft versions. Please check your internet connection.")
    ui.create_profile_page()


def go_to_edit_profile():
#Populate selected profile data and display the profile editor screen
    selected_name = ui.profiles_combobox_variable.get()
    if selected_name == "none" or not selected_name:
        messagebox.showerror("Error", "Select a profile first !")
        return

    current_profile = get_profile_from_name(selected_name)
    if current_profile is None:
        messagebox.showerror("Error", "Select a profile first !")
        return

    ui.versions_combobox.set(current_profile.version)
    ui.fill_versions_combobox(get_installed_and_available_versions(current_profile))
    ui.profile_name_entry.delete(0, 'end')
    ui.profile_name_entry.insert(0, current_profile.name)
    ui.edit_profile_page()

def installeur(vanilla_version, loader, directory):
    try:
        modloader = minecraft_launcher_lib.mod_loader.get_mod_loader(loader)
        minecraft_directory = directory
        installed_version = modloader.install(vanilla_version, minecraft_directory, callback={"setStatus": print})
        
        return installed_version
    except Exception as e:
        messagebox.showerror("Error", "An error occurred: " + str(e))
        return 0

def run():
#Bind all GUI buttons to their handlers and start the launcher
    ui.create_profile_button.configure(command=create_profile)
    ui.settings_button.configure(command=go_to_settings)
    ui.edit_profile_button.configure(command=go_to_edit_profile)
    ui.play_button.configure(command=start_game)
    ui.add_profile_button.configure(command=go_to_new_profile)
    ui.back_button.configure(command=go_to_main)
    ui.save_settings_button.configure(command=save_settings)
    ui.save_edited_profile_button.configure(command=edit_profile)
    ui.delete_profile_button.configure(command=delete_profile)
    ui.profile_dir_button.configure(command=open_directory)
    ui.add_loader_button.configure(command=lambda: messagebox.showinfo("Info", "ModLoader selection feature not implemented yet."))

    ui.ms_login_button.configure(command=start_microsoft_login)
    ui.ms_cancel_button.configure(command=cancel_microsoft_login)
    ui.logout_button.configure(command=logout)

    ui.display(start_callback=try_auto_login)


"""
APPLICATION ENTRY POINT
"""
if __name__ == "__main__":
    if not os.path.exists("data"):
        os.mkdir("data")
    if not os.path.exists("game"):
        os.mkdir("game")

    if not os.path.exists("data/config.ini"):
        config['GUI'] = {
            'last_used_profile': 'none',
            'ram_allocation': '2'
        }
        with open("data/config.ini", 'w') as configfile:
            config.write(configfile)
    else:
        config.read('data/config.ini')

    ram = config.get('GUI', 'ram_allocation', fallback='2')
    profile_list = get_profiles_list()

    run()
