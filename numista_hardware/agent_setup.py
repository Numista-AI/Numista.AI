"""
agent_setup.py — Numista.AI Desktop Agent First-Run Setup Wizard
================================================================
Displays a tkinter window that collects the user's Numista.AI account
email and an optional device name, then saves them to the config file.

Called by tray_agent.py on first launch (when no config exists) and
from the tray "Settings…" menu item.

Run standalone for testing:
    python agent_setup.py
"""

import sys
import os
import re
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# ── Import config (works both in-source and in PyInstaller bundle) ────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent_config import AgentConfig

# ─── Colour palette (matches Numista.AI brand) ────────────────────────────────
_BG          = "#0B1220"   # deep navy
_CARD        = "#1A2540"   # card surface
_ACCENT      = "#4C8CDA"   # electric blue
_GOLD        = "#C9A84C"   # coin gold
_WHITE       = "#FFFFFF"
_MUTED       = "#94A3B8"
_SUCCESS     = "#00C853"
_ERROR       = "#FF5252"
_FONT_TITLE  = ("Segoe UI", 18, "bold")
_FONT_BODY   = ("Segoe UI", 10)
_FONT_SMALL  = ("Segoe UI", 9)
_FONT_LABEL  = ("Segoe UI", 10, "bold")

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class SetupWizard:
    """
    Modal setup wizard window.

    Parameters
    ----------
    on_complete : callable, optional
        Called with (email, device_name) when the user saves successfully.
    on_cancel : callable, optional
        Called when the user cancels / closes without saving.
    """

    def __init__(self, on_complete=None, on_cancel=None):
        self._on_complete = on_complete
        self._on_cancel   = on_cancel
        self._root = None

    # ─── Public ───────────────────────────────────────────────────────────────

    def run(self):
        """Create and run the Tk main loop (blocks until window closes)."""
        self._root = tk.Tk()
        self._root.title("Numista.AI — Desktop Agent Setup")
        self._root.configure(bg=_BG)
        self._root.resizable(False, False)
        self._root.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Centre on screen
        width, height = 520, 480
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        x  = (sw - width) // 2
        y  = (sh - height) // 2
        self._root.geometry(f"{width}x{height}+{x}+{y}")

        self._build_ui()
        self._root.mainloop()

    # ─── UI Construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        root = self._root

        # ── Header strip ──────────────────────────────────────────────────────
        header = tk.Frame(root, bg=_CARD, pady=20, padx=30)
        header.pack(fill="x")

        tk.Label(header, text="🪙 Numista.AI", font=("Segoe UI", 22, "bold"),
                 bg=_CARD, fg=_GOLD).pack(anchor="w")
        tk.Label(header, text="Desktop Agent Setup", font=("Segoe UI", 13),
                 bg=_CARD, fg=_MUTED).pack(anchor="w")

        # ── Step indicator ────────────────────────────────────────────────────
        steps_frame = tk.Frame(root, bg=_BG, pady=12)
        steps_frame.pack(fill="x", padx=30)
        for i, label in enumerate(["Connect", "Configure", "Done"]):
            dot_color = _ACCENT if i == 0 else _MUTED
            tk.Label(steps_frame, text="●", font=("Segoe UI", 12),
                     bg=_BG, fg=dot_color).pack(side="left")
            tk.Label(steps_frame, text=f" {label}   ", font=_FONT_SMALL,
                     bg=_BG, fg=dot_color).pack(side="left")

        # ── Body card ─────────────────────────────────────────────────────────
        card = tk.Frame(root, bg=_CARD, padx=30, pady=24, relief="flat")
        card.pack(fill="both", expand=True, padx=24, pady=4)

        tk.Label(card,
                 text="Enter your Numista.AI account details",
                 font=_FONT_TITLE, bg=_CARD, fg=_WHITE,
                 wraplength=440, justify="left").pack(anchor="w")

        tk.Label(card,
                 text="Use the same email you sign in with at numista.ai",
                 font=_FONT_SMALL, bg=_CARD, fg=_MUTED).pack(anchor="w", pady=(4, 20))

        # Email field
        tk.Label(card, text="Numista.AI Email *", font=_FONT_LABEL,
                 bg=_CARD, fg=_WHITE).pack(anchor="w")
        self._email_var = tk.StringVar()
        email_entry = tk.Entry(card, textvariable=self._email_var,
                               font=_FONT_BODY, width=42,
                               bg="#263050", fg=_WHITE, insertbackground=_WHITE,
                               relief="flat", bd=8)
        email_entry.pack(fill="x", pady=(4, 2))
        email_entry.focus_set()
        self._email_error = tk.Label(card, text="", font=_FONT_SMALL,
                                     bg=_CARD, fg=_ERROR)
        self._email_error.pack(anchor="w", pady=(0, 12))

        # Device name field
        tk.Label(card, text="Device Name (optional)", font=_FONT_LABEL,
                 bg=_CARD, fg=_WHITE).pack(anchor="w")
        tk.Label(card,
                 text="e.g. 'Main Desktop', 'Coin Room PC'",
                 font=_FONT_SMALL, bg=_CARD, fg=_MUTED).pack(anchor="w", pady=(0, 4))
        self._device_var = tk.StringVar()
        tk.Entry(card, textvariable=self._device_var,
                 font=_FONT_BODY, width=42,
                 bg="#263050", fg=_WHITE, insertbackground=_WHITE,
                 relief="flat", bd=8).pack(fill="x")

        # What this stores note
        tk.Label(card,
                 text="ℹ  Your email is stored locally in %APPDATA%\\NumistaAI\\config.json "
                      "and is never sent to any server during setup.",
                 font=("Segoe UI", 8), bg=_CARD, fg=_MUTED,
                 wraplength=440, justify="left").pack(anchor="w", pady=(16, 0))

        # ── Pre-fill from existing config ─────────────────────────────────────
        cfg = AgentConfig()
        if cfg.is_configured():
            self._email_var.set(cfg.get_user_email())
            self._device_var.set(cfg.get_device_name())

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_frame = tk.Frame(root, bg=_BG, pady=14, padx=24)
        btn_frame.pack(fill="x")

        cancel_btn = tk.Button(btn_frame, text="Cancel",
                               font=_FONT_BODY, bg=_BG, fg=_MUTED,
                               activebackground=_BG, relief="flat", cursor="hand2",
                               command=self._on_window_close)
        cancel_btn.pack(side="right", padx=(8, 0))

        save_btn = tk.Button(btn_frame,
                             text="  Save & Start Agent  ",
                             font=("Segoe UI", 11, "bold"),
                             bg=_ACCENT, fg=_WHITE,
                             activebackground="#3A70C0",
                             relief="flat", cursor="hand2", pady=8,
                             command=self._on_save)
        save_btn.pack(side="right")

        # Bind Enter to save
        root.bind("<Return>", lambda _: self._on_save())

    # ─── Event Handlers ───────────────────────────────────────────────────────

    def _on_save(self):
        email  = self._email_var.get().strip()
        device = self._device_var.get().strip() or "My Computer"

        # Validate
        if not email:
            self._email_error.config(text="Email is required.")
            return
        if not _EMAIL_RE.match(email):
            self._email_error.config(text="Please enter a valid email address.")
            return
        self._email_error.config(text="")

        # Save
        try:
            AgentConfig().set_user(email, device)
        except Exception as e:
            messagebox.showerror("Save Failed",
                                 f"Could not write config:\n{e}\n\n"
                                 "Make sure %APPDATA%\\NumistaAI\\ is writable.")
            return

        # ── Success flash ──────────────────────────────────────────────────
        self._show_success(email, device)

    def _show_success(self, email, device):
        """Replace the window content with a brief success state."""
        for w in self._root.winfo_children():
            w.destroy()

        frame = tk.Frame(self._root, bg=_BG, padx=40, pady=60)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="✓", font=("Segoe UI", 48),
                 bg=_BG, fg=_SUCCESS).pack()
        tk.Label(frame, text="Agent Configured!", font=_FONT_TITLE,
                 bg=_BG, fg=_WHITE).pack(pady=(8, 4))
        tk.Label(frame, text=f"Account: {email}",
                 font=_FONT_BODY, bg=_BG, fg=_MUTED).pack()
        tk.Label(frame, text=f"Device: {device}",
                 font=_FONT_BODY, bg=_BG, fg=_MUTED).pack()
        tk.Label(frame,
                 text="The agent will start monitoring your microscope.\n"
                      "Look for the coin icon in your system tray.",
                 font=_FONT_BODY, bg=_BG, fg=_MUTED,
                 pady=16, justify="center").pack()

        close_btn = tk.Button(frame, text="  Start Agent  ",
                              font=("Segoe UI", 11, "bold"),
                              bg=_SUCCESS, fg=_WHITE, relief="flat",
                              cursor="hand2", pady=8,
                              command=self._close_success)
        close_btn.pack()

        # Auto-close after 3 seconds
        self._root.after(3000, self._close_success)

        if self._on_complete:
            self._on_complete(email, device)

    def _close_success(self):
        if self._root:
            self._root.destroy()
            self._root = None

    def _on_window_close(self):
        if self._on_cancel:
            self._on_cancel()
        if self._root:
            self._root.destroy()
            self._root = None


# ─── Convenience wrappers ─────────────────────────────────────────────────────

def run_setup_wizard(on_complete=None, on_cancel=None):
    """Run the wizard in the current thread (blocks until done)."""
    SetupWizard(on_complete=on_complete, on_cancel=on_cancel).run()


def run_setup_wizard_in_thread(on_complete=None, on_cancel=None):
    """
    Run the wizard in a background thread so the caller stays non-blocking.
    Returns the thread object.
    """
    t = threading.Thread(
        target=run_setup_wizard,
        kwargs={"on_complete": on_complete, "on_cancel": on_cancel},
        daemon=False,  # Keep alive until wizard closes
    )
    t.start()
    return t


# ─── Standalone test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    def _done(email, device):
        print(f"[WIZARD] Saved → email={email!r}  device={device!r}")

    def _cancelled():
        print("[WIZARD] User cancelled.")

    run_setup_wizard(on_complete=_done, on_cancel=_cancelled)
