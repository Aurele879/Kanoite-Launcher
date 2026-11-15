import random
import webbrowser
from tkinter import Label, PhotoImage
import customtkinter
from PIL import Image

"""
GUI CONFIGURATION
"""
customtkinter.set_default_color_theme("assets/theme.json")


"""
LAUNCHER GUI CLASS
"""
class Gui:
    def __init__(self):
#Initialize launcher window, assets, state, and widgets
        self.root = customtkinter.CTk()
        self.root.geometry("1000x550")
        self.root.title("Kanoite Launcher")
        self.root.resizable(False, False)
        self.root.iconbitmap("assets/icon.ico")
        self.root.configure(fg_color="#1C1C1C")

        self.background_image = PhotoImage(file="assets/background2.png")
        self.background_label = Label(self.root, image=self.background_image)

        self.play_image = Image.open("assets/play.png")
        self.settings_image = Image.open("assets/settings.png")
        self.block_image = Image.open("assets/block_logo.png")
        self.logo_image = Image.open("assets/logo.png")

        self.current_verification_uri = "https://www.microsoft.com/link"
        self.setup_widgets()

    def setup_widgets(self):
#Initialize and configure all GUI widgets
        self.play_button = customtkinter.CTkButton(
            self.root,
            text="PLAY ",
            width=200,
            height=50,
            corner_radius=20,
            image=customtkinter.CTkImage(self.play_image, size=(30, 30)),
            compound="right",
            font=("Arial", 25, "bold")
        )

        self.settings_button = customtkinter.CTkButton(
            self.root,
            text="",
            width=50,
            height=50,
            corner_radius=20,
            image=customtkinter.CTkImage(self.settings_image, size=(30, 30))
        )

        self.add_profile_button = customtkinter.CTkButton(
            self.root,
            text="+",
            width=46,
            height=28,
            corner_radius=100
        )

        self.profiles_combobox_variable = customtkinter.StringVar()
        self.profiles_combobox = customtkinter.CTkComboBox(
            self.root,
            variable=self.profiles_combobox_variable,
            state="readonly",
            corner_radius=15,
            width=150
        )

        self.edit_profile_button = customtkinter.CTkButton(
            self.root,
            text="EDIT PROFILE",
            height=26,
            corner_radius=15,
            width=200
        )

        self.loading_bar = customtkinter.CTkProgressBar(
            self.root,
            mode="indeterminate",
            width=900,
            height=20,
            corner_radius=100
        )

        self.loading_label = customtkinter.CTkLabel(
            self.root,
            text="Downloading files ...",
            font=("Arial", 15, "bold")
        )

        self.back_button = customtkinter.CTkButton(
            self.root,
            fg_color="#972626",
            hover_color="#751F1F",
            text="CANCEL",
            width=200,
            height=50,
            corner_radius=20,
            font=("Arial", 25, "bold")
        )

        self.create_profile_button = customtkinter.CTkButton(
            self.root,
            fg_color="#28A33C",
            hover_color="#1B6D28",
            text="CREATE",
            width=200,
            height=50,
            corner_radius=20,
            font=("Arial", 25, "bold")
        )

        self.save_edited_profile_button = customtkinter.CTkButton(
            self.root,
            fg_color="#28A33C",
            hover_color="#1B6D28",
            text="SAVE",
            width=200,
            height=50,
            corner_radius=20,
            font=("Arial", 25, "bold")
        )

        self.delete_profile_button = customtkinter.CTkButton(
            self.root,
            text="DELETE PROFILE",
            width=500,
            height=50,
            corner_radius=20
        )

        self.profile_name_entry = customtkinter.CTkEntry(
            self.root,
            height=50,
            placeholder_text="*profile name",
            corner_radius=15,
            width=500
        )

        self.profile_edition_label = customtkinter.CTkLabel(
            self.root,
            text="Profile Editor",
            font=("Arial", 50, "bold")
        )

        self.profile_creation_label = customtkinter.CTkLabel(
            self.root,
            text="New Profile",
            font=("Arial", 50, "bold")
        )

        self.block_preview = customtkinter.CTkImage(
            light_image=self.block_image,
            dark_image=self.block_image,
            size=(200, 200)
        )
        self.block = customtkinter.CTkLabel(self.root, image=self.block_preview, text="")

        self.versions_combobox_variable = customtkinter.StringVar()
        self.versions_combobox = customtkinter.CTkComboBox(
            self.root,
            variable=self.versions_combobox_variable,
            state="readonly",
            height=50,
            corner_radius=15,
            width=500
        )

        self.add_loader_button = customtkinter.CTkButton(
            self.root,
            bg_color="#1C1C1C",
            text="+",
            width=50,
            height=50,
            corner_radius=15,
            font=("Arial", 30, "bold")
        )

        self.profile_dir_button = customtkinter.CTkButton(
            self.root,
            text="OPEN DIRECTORY",
            width=500,
            height=50,
            corner_radius=20
        )

        self.settings_label_title = customtkinter.CTkLabel(
            self.root,
            text="Settings",
            font=("Arial", 50, "bold")
        )

        self.ram_slider = customtkinter.CTkSlider(
            self.root,
            width=500,
            command=self.update_ram_label,
            from_=2
        )

        self.ram_value_label = customtkinter.CTkLabel(
            self.root,
            text="Allocated RAM: 2 GB",
            font=("Arial", 25, "bold")
        )

        self.save_settings_button = customtkinter.CTkButton(
            self.root,
            fg_color="#28A33C",
            hover_color="#1B6D28",
            text="SAVE",
            width=200,
            height=50,
            corner_radius=20,
            font=("Arial", 25, "bold")
        )

        self.ms_login_title = customtkinter.CTkLabel(
            self.root,
            text="Microsoft Login",
            font=("Arial", 46, "bold")
        )

        self.ms_login_subtitle = customtkinter.CTkLabel(
            self.root,
            text="Connect with your official Microsoft account to play Minecraft",
            font=("Arial", 15),
            text_color="#AAAAAA"
        )

        self.launcher_logo_ctk = customtkinter.CTkImage(
            light_image=self.logo_image,
            dark_image=self.logo_image,
            size=(150, 150)
        )
        self.login_logo = customtkinter.CTkLabel(self.root, image=self.launcher_logo_ctk, text="")

        self.ms_login_button = customtkinter.CTkButton(
            self.root,
            text="SIGN IN WITH MICROSOFT",
            width=450,
            height=52,
            corner_radius=20,
            font=("Arial", 18, "bold"),
            fg_color="#0067B8",
            hover_color="#005DA6"
        )

        self.ms_code_title = customtkinter.CTkLabel(
            self.root,
            text="Microsoft Authentication",
            font=("Arial", 38, "bold")
        )

        self.ms_code_frame = customtkinter.CTkFrame(
            self.root,
            width=600,
            height=260,
            corner_radius=20,
            fg_color="#232323",
            border_width=1,
            border_color="#363636"
        )

        self.ms_code_instruction = customtkinter.CTkLabel(
            self.root,
            text="Enter the following code on the Microsoft page:",
            font=("Arial", 15),
            text_color="#D5D5D5"
        )

        self.ms_code_display = customtkinter.CTkLabel(
            self.root,
            text="XXXX-XXXX",
            font=("Arial", 36, "bold"),
            text_color="#00D26A"
        )

        self.ms_copy_button = customtkinter.CTkButton(
            self.root,
            text="COPY CODE",
            width=180,
            height=40,
            corner_radius=14,
            font=("Arial", 13, "bold"),
            fg_color="#28A33C",
            hover_color="#1B6D28",
            command=self.copy_current_code
        )

        self.ms_browser_button = customtkinter.CTkButton(
            self.root,
            text="OPEN BROWSER",
            width=180,
            height=40,
            corner_radius=14,
            font=("Arial", 13, "bold"),
            fg_color="#0067B8",
            hover_color="#005DA6",
            command=self.open_browser_url
        )

        self.ms_auth_progress = customtkinter.CTkProgressBar(
            self.root,
            mode="indeterminate",
            width=440,
            height=10,
            corner_radius=6
        )

        self.ms_status_label = customtkinter.CTkLabel(
            self.root,
            text="",
            font=("Arial", 13),
            text_color="#8E8E8E"
        )

        self.ms_cancel_button = customtkinter.CTkButton(
            self.root,
            text="CANCEL",
            width=150,
            height=36,
            corner_radius=14,
            font=("Arial", 13, "bold"),
            fg_color="#972626",
            hover_color="#751F1F"
        )

        self.account_badge = customtkinter.CTkLabel(
            self.root,
            text="● Player",
            font=("Arial", 13, "bold"),
            text_color="#FFFFFF",
            fg_color="#222222",
            corner_radius=10,
            padx=12,
            pady=6
        )

        self.logout_button = customtkinter.CTkButton(
            self.root,
            text="LOGOUT",
            width=85,
            height=30,
            corner_radius=10,
            font=("Arial", 11, "bold"),
            fg_color="#972626",
            hover_color="#751F1F"
        )

        self.widgets = [
            self.play_button,
            self.settings_button,
            self.add_profile_button,
            self.profiles_combobox,
            self.edit_profile_button,
            self.loading_bar,
            self.back_button,
            self.create_profile_button,
            self.save_edited_profile_button,
            self.delete_profile_button,
            self.profile_dir_button,
            self.profile_name_entry,
            self.profile_edition_label,
            self.versions_combobox,
            self.add_loader_button,
            self.profile_creation_label,
            self.block,
            self.loading_label,
            self.settings_label_title,
            self.ram_slider,
            self.ram_value_label,
            self.save_settings_button,
            self.ms_login_title,
            self.ms_login_subtitle,
            self.login_logo,
            self.ms_login_button,
            self.ms_code_title,
            self.ms_code_frame,
            self.ms_code_instruction,
            self.ms_code_display,
            self.ms_copy_button,
            self.ms_browser_button,
            self.ms_auth_progress,
            self.ms_status_label,
            self.ms_cancel_button,
            self.account_badge,
            self.logout_button
        ]

    def clear_ui(self):
#Clear all active widgets from the window
        for widget in self.widgets:
            widget.place_forget()
        try:
            self.ms_auth_progress.stop()
        except Exception:
            pass

    def loading_page(self, text):
#Display the loading screen with a progress bar and status text
        self.clear_ui()
        self.background_label.pack()
        self.loading_bar.place(relx=0.05, rely=0.882)
        self.loading_label.place(relx=0.05, rely=0.92)
        self.loading_label.configure(text=text)
        self.loading_bar.start()

    def ms_login_page(self):
#Display the Microsoft login landing page
        self.clear_ui()
        self.background_label.pack_forget()
        self.ms_login_button.configure(state="normal", text="SIGN IN WITH MICROSOFT")
        self.ms_status_label.configure(text="")

        self.ms_login_title.place(relx=0.5, rely=0.12, anchor="center")
        self.ms_login_subtitle.place(relx=0.5, rely=0.20, anchor="center")
        self.login_logo.place(relx=0.5, rely=0.45, anchor="center")
        self.ms_login_button.place(relx=0.5, rely=0.74, anchor="center")
        self.ms_status_label.place(relx=0.5, rely=0.84, anchor="center")

    def ms_code_page(self, user_code, verification_uri):
#Display the Microsoft device code and authentication instructions
        self.clear_ui()
        self.background_label.pack_forget()
        self.current_verification_uri = verification_uri
        self.ms_code_display.configure(text=user_code)
        self.ms_status_label.configure(text="Waiting for authentication in browser...")
        self.ms_copy_button.configure(text="COPY CODE", fg_color="#28A33C")

        self.ms_code_title.place(relx=0.5, rely=0.10, anchor="center")
        self.ms_code_frame.place(relx=0.5, rely=0.48, anchor="center")

        self.ms_code_instruction.place(relx=0.5, rely=0.31, anchor="center")
        self.ms_code_display.place(relx=0.5, rely=0.41, anchor="center")
        self.ms_copy_button.place(relx=0.39, rely=0.52, anchor="center")
        self.ms_browser_button.place(relx=0.61, rely=0.52, anchor="center")

        self.ms_auth_progress.place(relx=0.5, rely=0.60, anchor="center")
        self.ms_auth_progress.start()

        self.ms_status_label.place(relx=0.5, rely=0.66, anchor="center")
        self.ms_cancel_button.place(relx=0.5, rely=0.86, anchor="center")

    def update_ms_status(self, text):
#Update the status message on the Microsoft authentication screen
        self.ms_status_label.configure(text=text)

    def copy_current_code(self):
#Copy the currently displayed verification code to clipboard
        code = self.ms_code_display.cget("text")
        self.copy_to_clipboard(code)

    def copy_to_clipboard(self, text):
#Copy given text to system clipboard with temporary button feedback
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            self.ms_copy_button.configure(text="COPIED !", fg_color="#1B6D28")
            self.root.after(2000, lambda: self.ms_copy_button.configure(text="COPY CODE", fg_color="#28A33C"))
        except Exception:
            pass

    def open_browser_url(self):
#Open the verification website in the default web browser
        try:
            webbrowser.open(self.current_verification_uri)
        except Exception:
            pass

    def set_account_display(self, username):
#Update the username badge on the main page
        self.account_badge.configure(text=f"● {username}")

    def main_page(self):
#Display the main launcher page
        self.clear_ui()
        self.background_label.pack()
        self.profiles_combobox.place(relx=0.05, rely=0.836)
        self.add_profile_button.place(relx=0.204, rely=0.836)
        self.edit_profile_button.place(relx=0.05, rely=0.91)
        self.settings_button.place(relx=0.66, rely=0.855)
        self.play_button.place(relx=0.75, rely=0.855)

        self.logout_button.place(relx=0.96, rely=0.05, anchor="ne")
        self.account_badge.place(relx=0.86, rely=0.05, anchor="ne")

    def settings_page(self):
#Display the launcher settings page
        self.clear_ui()
        self.background_label.pack_forget()

        self.settings_label_title.place(relx=0.5, rely=0.1, anchor="center")
        self.ram_value_label.place(relx=0.5, rely=0.4, anchor="center")
        self.ram_slider.place(relx=0.5, rely=0.5, anchor="center")

        self.back_button.place(relx=0.75, rely=0.855)
        self.save_settings_button.place(relx=0.525, rely=0.855)

    def edit_profile_page(self):
#Display the profile edition page
        self.clear_ui()
        self.background_label.pack_forget()

        self.back_button.place(relx=0.75, rely=0.855)
        self.save_edited_profile_button.place(relx=0.525, rely=0.855)
        self.delete_profile_button.place(relx=0.5, rely=0.72, anchor="center")
        self.profile_dir_button.place(relx=0.5, rely=0.60, anchor="center")
        self.profile_name_entry.place(relx=0.5, rely=0.36, anchor="center")
        self.profile_edition_label.place(relx=0.5, rely=0.1, anchor="center")

        self.versions_combobox.configure(width=442)
        self.versions_combobox.place(relx=0.25, rely=0.48, anchor="w")
        self.add_loader_button.place(relx=0.7, rely=0.48, anchor="w")

    def create_profile_page(self):
#Display the profile creation page
        self.clear_ui()
        self.background_label.pack_forget()

        self.profile_name_entry.place(relx=0.5, rely=0.58, anchor="center")
        self.back_button.place(relx=0.75, rely=0.855)
        self.create_profile_button.place(relx=0.525, rely=0.855)
        self.profile_creation_label.place(relx=0.5, rely=0.1, anchor="center")
        self.block.place(relx=0.5, rely=0.33, anchor="center")

        self.versions_combobox.configure(width=500)
        self.versions_combobox.place(relx=0.5, rely=0.70, anchor="center")

    def display(self, start_callback=None):
#Start the launcher GUI main loop
        if start_callback:
            self.root.after(100, start_callback)
        else:
            self.ms_login_page()
        self.root.mainloop()

    def fill_profiles_combobox(self, profiles_list):
#Populate the profiles dropdown menu with profile names
        self.profiles_combobox.configure(values=profiles_list)

    def fill_versions_combobox(self, versions_list):
#Populate the versions dropdown menu with game versions
        self.versions_combobox.configure(values=versions_list)

    def update_ram_label(self, value):
#Update the allocated RAM label according to the slider value
        self.ram_value_label.configure(text=f"Allocated RAM: {int(float(value))} GB")
