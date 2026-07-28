"""
Login and Registration Authentication Window.
Provides user registration and login interface.
"""

import customtkinter as ctk
from typing import Callable, Dict, Any
from gui.theme import Theme
from models.user import UserModel


class LoginWindow(ctk.CTk):
    """User Registration & Login window."""

    def __init__(self, on_login_success: Callable[[Dict[str, Any]], None]):
        super().__init__()
        self.on_login_success = on_login_success

        self.title("Medicine Reminder System - Login & Authentication")
        self.geometry("450x560")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_DARK)

        # Center window on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.winfo_screenheight() // 2) - (560 // 2)
        self.geometry(f"+{x}+{y}")

        self._build_ui()

    def _build_ui(self) -> None:
        """Constructs layout."""
        # Header banner
        header = ctk.CTkFrame(self, fg_color=Theme.SIDEBAR_BG, height=110, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        icon_lbl = ctk.CTkLabel(header, text="💊", font=("Segoe UI", 36))
        icon_lbl.pack(pady=(12, 0))

        title_lbl = ctk.CTkLabel(
            header,
            text="Medicine Reminder System",
            font=Theme.FONT_SUBTITLE,
            text_color=Theme.ACCENT
        )
        title_lbl.pack()

        # Tabview for Login and Register
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=Theme.CARD_BG,
            segmented_button_fg_color=Theme.CARD_HOVER,
            segmented_button_selected_color=Theme.PRIMARY,
            segmented_button_selected_hover_color=Theme.PRIMARY_HOVER,
            corner_radius=12
        )
        self.tabview.pack(fill="both", expand=True, padx=25, pady=20)

        self.tab_login = self.tabview.add("Login")
        self.tab_register = self.tabview.add("Register Account")

        self._build_login_tab()
        self._build_register_tab()

    def _build_login_tab(self) -> None:
        """Builds login tab form."""
        ctk.CTkLabel(self.tab_login, text="Username", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(anchor="w", padx=15, pady=(20, 2))
        self.login_user = ctk.CTkEntry(self.tab_login, placeholder_text="Enter username", font=Theme.FONT_BODY)
        self.login_user.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(self.tab_login, text="Password", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(anchor="w", padx=15, pady=(0, 2))
        self.login_pass = ctk.CTkEntry(self.tab_login, placeholder_text="Enter password", show="•", font=Theme.FONT_BODY)
        self.login_pass.pack(fill="x", padx=15, pady=(0, 15))
        self.login_pass.bind("<Return>", lambda e: self._handle_login())

        self.lbl_login_err = ctk.CTkLabel(self.tab_login, text="", font=Theme.FONT_BODY, text_color=Theme.COLOR_MISSED)
        self.lbl_login_err.pack(pady=5)

        btn_login = ctk.CTkButton(
            self.tab_login,
            text="🔐 Login to Account",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            height=40,
            command=self._handle_login
        )
        btn_login.pack(fill="x", padx=15, pady=(10, 10))

    def _build_register_tab(self) -> None:
        """Builds registration tab form."""
        scroll = ctk.CTkScrollableFrame(self.tab_register, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="Full Name", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(anchor="w", padx=5, pady=(10, 2))
        self.reg_fullname = ctk.CTkEntry(scroll, placeholder_text="e.g. John Doe", font=Theme.FONT_BODY)
        self.reg_fullname.pack(fill="x", padx=5, pady=(0, 10))

        ctk.CTkLabel(scroll, text="Username *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(anchor="w", padx=5, pady=(0, 2))
        self.reg_user = ctk.CTkEntry(scroll, placeholder_text="Choose username", font=Theme.FONT_BODY)
        self.reg_user.pack(fill="x", padx=5, pady=(0, 10))

        ctk.CTkLabel(scroll, text="Password *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(anchor="w", padx=5, pady=(0, 2))
        self.reg_pass = ctk.CTkEntry(scroll, placeholder_text="At least 6 characters", show="•", font=Theme.FONT_BODY)
        self.reg_pass.pack(fill="x", padx=5, pady=(0, 10))

        ctk.CTkLabel(scroll, text="Confirm Password *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_MAIN).pack(anchor="w", padx=5, pady=(0, 2))
        self.reg_confirm = ctk.CTkEntry(scroll, placeholder_text="Re-enter password", show="•", font=Theme.FONT_BODY)
        self.reg_confirm.pack(fill="x", padx=5, pady=(0, 10))

        self.lbl_reg_msg = ctk.CTkLabel(scroll, text="", font=Theme.FONT_BODY, text_color=Theme.COLOR_MISSED)
        self.lbl_reg_msg.pack(pady=5)

        btn_reg = ctk.CTkButton(
            scroll,
            text="✨ Create Account",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            height=40,
            command=self._handle_register
        )
        btn_reg.pack(fill="x", padx=5, pady=(5, 10))

    def _handle_login(self) -> None:
        """Processes login."""
        u = self.login_user.get().strip()
        p = self.login_pass.get().strip()

        user_data = UserModel.authenticate(u, p)
        if user_data:
            self.on_login_success(user_data)
            self.destroy()
        else:
            self.lbl_login_err.configure(text="Invalid username or password.")

    def _handle_register(self) -> None:
        """Processes registration."""
        fn = self.reg_fullname.get().strip()
        u = self.reg_user.get().strip()
        p = self.reg_pass.get().strip()
        cp = self.reg_confirm.get().strip()

        if p != cp:
            self.lbl_reg_msg.configure(text="Passwords do not match.", text_color=Theme.COLOR_MISSED)
            return

        success, msg = UserModel.register(u, p, fn)
        if success:
            self.lbl_reg_msg.configure(text=msg, text_color=Theme.COLOR_TAKEN)
            # Switch to login tab after brief delay
            self.after(1200, lambda: self.tabview.set("Login"))
        else:
            self.lbl_reg_msg.configure(text=msg, text_color=Theme.COLOR_MISSED)
