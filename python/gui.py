"""Modern Glassy File Encrypter GUI with Poppins/Roboto fonts and glassmorphism effects.

This GUI recreates the beautiful glassy interface design with:
- Modern Poppins/Roboto typography
- Glassmorphism panels with backdrop blur effects
- Smooth animations and hover states
- Dark background with luminous accents
"""

import mmap
import shutil
import tkthread; tkthread.patch()
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import font as tkfont
import os
from multiprocessing import Process, Lock, Pool
# from concurrent.futures import ThreadPoolExecutor
import zipfile
from encryption_backend import encrypt_data, hash_password, generate_salt  # pyright: ignore[reportMissingImports]
import math
from typing import Optional
import threading
import queue

# --- Worker Process (moved outside the class) ---
def encrypt_worker_process(selected_file, chunk_info, hashed_password, finalpath, file_name_base):
    """Worker process to encrypt a single chunk of data."""
    chunk_no, offset, size = chunk_info
    try:
        with open(selected_file, "rb") as f_in:
            f_in.seek(offset)
            chunk_data = f_in.read(size)
        
        encrypted = encrypt_data(chunk_data, hashed_password)
        
        # Write encrypted chunk to file
        chunk_filename = f"{file_name_base}_{chunk_no:04d}.crypt"
        with open(os.path.join(finalpath, chunk_filename), "wb") as f:
            f.write(encrypted)
        
        # Using print for now, a more robust logging/queue system could be used
        # print(f"Process {os.getpid()}: Encrypted chunk {chunk_no}")
        return True
    except Exception as e:
        # print(f"Process {os.getpid()}: Error encrypting chunk {chunk_no}: {e}")
        return False

# Glassmorphism Color Palette - Enhanced
DARK_BG = "#10101a"  # Very dark background
GLASS_PANEL = "#1e1e2899"  # Semi-transparent panel base with alpha
GLASS_OVERLAY = "#3c467859"  # Button overlay with transparency
GLASS_BORDER = "#ffffff1a"  # Subtle white border
ACCENT_BLUE = "#3a8eff"  # Cobalt blue accent
ACCENT_TEAL = "#0099ff"  # Teal for focus states
TEXT_PRIMARY = "#ffffff"  # White text
TEXT_SECONDARY = "#b0b3c1"  # Muted text
SUCCESS_GLOW = "#00ff88"
ERROR_GLOW = "#ff4757"
SHADOW_COLOR = "#28324014"  # Subtle shadow

# Typography - Poppins & Roboto
FONT_HEADING = "Poppins"  # For titles and headings
FONT_BODY = "Roboto"  # For inputs and buttons
FONT_FALLBACK = "Segoe UI"  # System fallback

# Font Sizes (converted from px to pt approximately)
TITLE_SIZE = 18  # ~24px
BUTTON_SIZE = 12  # ~16px
TEXT_SIZE = 11   # ~14px
SMALL_SIZE = 10  # ~13px
CAPTION_SIZE = 9 # ~12px

class GlassyFileEncrypter:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.setup_window()
        self.setup_fonts()
        self.setup_variables()
        self.create_interface()
        self.setup_animations()

    def setup_window(self):
        """Configure the main window with glassy theme"""
        self.root.title("🔐 Secure File Encrypter")
        self.root.configure(bg=DARK_BG)
        # Base geometry in logical units; scale with Tk's DPI scaling so fonts and window match
        base_width, base_height = 600, 720
        try:
            tk_scaling = float(self.root.tk.call('tk', 'scaling'))  # pixels per point (1/72")
        except Exception:
            tk_scaling = 96.0 / 72.0  # Fallback to 100% scale
        base_scaling = 96.0 / 72.0
        ratio = tk_scaling / base_scaling
        width, height = int(base_width * ratio), int(base_height * ratio)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False, False)
        
        # Center window on screen, accounting for taskbar
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2) - 50  # Adjust for typical taskbar height
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_fonts(self):
        """Initialize Poppins and Roboto fonts with fallbacks"""
        # Try to load preferred fonts, fallback to system fonts
        self.fonts = {}
        
        font_configs = [
            ("title", FONT_HEADING, TITLE_SIZE, "bold", "roman"),
            ("button", FONT_BODY, BUTTON_SIZE, "normal", "roman"),
            ("input", FONT_BODY, BUTTON_SIZE, "normal", "roman"),
            ("text", FONT_BODY, TEXT_SIZE, "normal", "roman"),
            ("small", FONT_BODY, SMALL_SIZE, "normal", "italic"),
            ("caption", FONT_BODY, CAPTION_SIZE, "normal", "roman")
        ]
        
        for name, family, size, weight, slant in font_configs:
            try:
                # Use point sizes; Tk will map to pixels using current DPI/scaling
                self.fonts[name] = tkfont.Font(family=family, size=size, weight=weight, slant=slant)
            except tk.TclError:
                # Fallback to system font
                try:
                    self.fonts[name] = tkfont.Font(family=FONT_FALLBACK, size=size, weight=weight, slant=slant)
                except tk.TclError:
                    # Final fallback - just size
                    self.fonts[name] = tkfont.Font(size=size, weight=weight if weight in ["normal", "bold"] else "normal")

    def setup_variables(self):
        """Initialize GUI state variables"""
        self.selected_file = tk.StringVar()
        self.selected_folder = tk.StringVar()
        self.file_name = tk.StringVar()
        self.password_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Select a file to get started")
        self.show_password = tk.BooleanVar(value=False)
        self.is_processing = False
        self.filesize = 0
        self.thread_count = os.cpu_count() or 1  # Use available CPU cores, fallback to 1 if not available
        # UI state tracking
        self.file_selected = False
        self.password_ready = False
        
        # Animation variables
        self.animation_step = 0
        self.hover_states = {}

    def create_interface(self):
        """Build the glassy interface components"""
        # Main container with better padding
        self.main_frame = tk.Frame(self.root, bg=DARK_BG)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)
        
        # Create interface sections in logical order
        self.create_header()
        self.create_file_upload_section()  # File upload first
        self.create_password_section()     # Password second (hidden)
        self.create_action_buttons()       # Actions third (hidden)
        self.create_clear_button_section() # Clear button (hidden)
        self.create_status_section()       # Status last

    def create_header(self):
        """Create the header with title"""
        header_frame = tk.Frame(self.main_frame, bg=DARK_BG)
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Main title
        title_label = tk.Label(
            header_frame, 
            text= "Secure Encrypter",
            font=self.fonts["title"],
            fg=TEXT_PRIMARY,
            bg=DARK_BG
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Military-grade file protection",
            font=self.fonts["small"],
            fg=TEXT_SECONDARY,
            bg=DARK_BG
        )
        subtitle_label.pack(pady=(3, 0))
    def reset_to_initial_state(self):
        """Reset UI to initial state with only file upload visible"""
        # Hide sections
        if hasattr(self, 'password_container'):
            self.password_container.pack_forget()
        if hasattr(self, 'button_frame'):
            self.button_frame.pack_forget()
        if hasattr(self, 'clear_button_frame'):
            self.clear_button_frame.pack_forget()
        
        # Reset state variables
        self.file_selected = False
        self.password_ready = False
        self.selected_file.set("")
        self.password_var.set("")
        
        # Reset upload area to original state
        self.reset_upload_area()
        
        # Reset status
        self.status_var.set("Select a file to get started")

    def reset_upload_area(self):
        """Reset upload area back to original state"""
        # Destroy the selected file frame if it exists
        if hasattr(self, 'selected_file_frame'):
            self.selected_file_frame.destroy()

        # Reset container height
        self.upload_container.configure(height=180)
        
        # Show original widgets
        self.file_icon.pack(pady=(0, 10))
        self.upload_text.pack(pady=(0, 12))
        self.browse_btn.pack(pady=(0, 8))
        self.file_info_label.pack()
        
        # Re-bind events
        for widget in [self.upload_container, self.upload_frame, self.file_icon, self.upload_text]:
            widget.bind("<Button-1>", lambda e: self.browse_file())
            widget.bind("<Enter>", lambda e: self.on_upload_hover(True))
            widget.bind("<Leave>", lambda e: self.on_upload_hover(False))

    def create_password_section(self):
        """Create the glassy password input section"""
        # Password container with glassy effect - initially hidden
        self.password_container = self.create_glass_panel(self.main_frame, height=100)
        # Don't pack initially - will be shown when file is selected
        
        # Password frame
        pwd_frame = tk.Frame(self.password_container, bg="#1e1e28")
        pwd_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=18)
        
        # Password label
        pwd_label = tk.Label(
            pwd_frame,
            text="Enter password:",
            font=self.fonts["text"],
            fg=TEXT_SECONDARY,
            bg="#1e1e28"
        )
        pwd_label.pack(anchor='w', pady=(0, 8))
        
        # Password input with icon and toggle
        input_frame = tk.Frame(pwd_frame, bg="#1e1e28")
        input_frame.pack(fill=tk.X)
        
        # Lock icon
        lock_icon = tk.Label(
            input_frame,
            text="🔒",
            font=self.fonts["button"],
            fg=TEXT_SECONDARY,
            bg="#1e1e28"
        )
        lock_icon.pack(side=tk.LEFT, padx=(0, 12))
        
        # Password entry with enhanced styling
        self.password_entry = tk.Entry(
            input_frame,
            textvariable=self.password_var,
            font=self.fonts["input"],
            bg="#1e1e28",
            fg=TEXT_PRIMARY,
            bd=0,
            relief=tk.FLAT,
            insertbackground=TEXT_PRIMARY,
            show="●",
            highlightthickness=2,
            highlightbackground="#ffff20",
            highlightcolor=ACCENT_TEAL,
            selectborderwidth=0,
            insertwidth=4,
            width=10 # Added width to ensure it doesn't shrink
        )
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6) # Better internal padding
        
        # Add placeholder text
        self.add_placeholder(self.password_entry, "Enter password")
        
        # Bind password entry to check if ready for actions
        self.password_entry.bind('<KeyRelease>', self.check_ready_state)
        
        # Password visibility toggle
        self.eye_button = tk.Button(
            input_frame,
            text="👁",
            font=self.fonts["button"],
            bg="#1e1e28",
            fg=TEXT_SECONDARY,
            bd=0,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.toggle_password_visibility,
            activebackground="#3c4678",
            activeforeground=TEXT_PRIMARY
        )
        self.eye_button.pack(side=tk.RIGHT, padx=(8, 0))

    def create_file_upload_section(self):
        """Create the glassy file upload area"""
        # Upload container - better proportioned height
        self.upload_container = self.create_glass_panel(self.main_frame, height=180)
        self.upload_container.pack(fill=tk.X, pady=(0, 20))
        
        # Upload content
        self.upload_frame = tk.Frame(self.upload_container, bg="#1e1e28")
        self.upload_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # File icon (will change after upload)
        self.file_icon = tk.Label(
            self.upload_frame,
            text="📄",
            font=("Arial", 32),
            fg=TEXT_SECONDARY,
            bg="#1e1e28"
        )
        self.file_icon.pack(pady=(0, 10))
        
        # Upload text (will change after upload)
        self.upload_text = tk.Label(
            self.upload_frame,
            text="Choose file to encrypt/decrypt",
            font=self.fonts["button"],
            fg=TEXT_PRIMARY,
            bg="#1e1e28"
        )
        self.upload_text.pack(pady=(0, 12))
        
        # Browse button (will change after upload)
        self.browse_btn = self.create_glass_button(
            self.upload_frame,
            "📁 Browse Files",
            self.browse_file,
            color="#6b73ff"
        )
        self.browse_btn.pack(pady=(0, 8))
        
        # File selection info
        self.file_info_label = tk.Label(
            self.upload_frame,
            text="No file selected",
            font=self.fonts["small"],
            fg=TEXT_SECONDARY,
            bg="#1e1e28",
            wraplength=450
        )
        self.file_info_label.pack()
        
        # Make the entire upload area clickable
        for widget in [self.upload_container, self.upload_frame, self.file_icon, self.upload_text]:
            widget.bind("<Button-1>", lambda e: self.browse_file())
            widget.bind("<Enter>", lambda e: self.on_upload_hover(True))
            widget.bind("<Leave>", lambda e: self.on_upload_hover(False))

    def create_clear_button_section(self):
        """Create the clear button, initially hidden"""
        self.clear_button_frame = tk.Frame(self.main_frame, bg=DARK_BG)
        # Don't pack initially
        
        self.clear_btn = self.create_glass_button(
            self.clear_button_frame,
            "🔄 Clear and Reset",
            self.reset_to_initial_state,
            color="#ff6b6b",
            small=True
        )
        self.clear_btn.pack(pady=8)

    def create_action_buttons(self):
        """Create the glassy encrypt/decrypt buttons side by side"""
        self.button_frame = tk.Frame(self.main_frame, bg=DARK_BG)
        # Don't pack initially - will be shown when ready
        
        # Create buttons side by side
        # Encrypt button
        self.encrypt_btn = self.create_glass_button(
            self.button_frame, 
            "🔒 Encrypt File", 
            self.encrypt_file,
            color=ACCENT_BLUE
        )
        self.encrypt_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Decrypt button
        self.decrypt_btn = self.create_glass_button(
            self.button_frame,
            "🔓 Decrypt File",
            self.decrypt_file,
            color=ACCENT_TEAL
        )
        self.decrypt_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

    def create_status_section(self):
        """Create the status display area"""
        status_frame = tk.Frame(self.main_frame, bg=DARK_BG)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=self.fonts["small"],
            fg=TEXT_SECONDARY,
            bg=DARK_BG,
            justify=tk.CENTER
        )
        self.status_label.pack()

    def create_glass_panel(self, parent, height=None):
        """Create a glassmorphism panel with enhanced styling"""
        # Glass panel with border simulation
        glass_panel = tk.Frame(
            parent, 
            bg="#1e1e28",  # Using solid color as tkinter doesn't support rgba
            relief=tk.FLAT,
            highlightbackground="#ffffff",
            highlightcolor="#ffffff", 
            highlightthickness=1,
            bd=0
        )
        
        if height:
            glass_panel.configure(height=height)
            glass_panel.pack_propagate(False)  # Maintain the specified height
        
        return glass_panel

    def create_glass_button(self, parent, text, command, color=ACCENT_BLUE, small=False):
        """Create a glassmorphism button with enhanced hover effects"""
        # Adjust padding based on size
        px = 20 if small else 40
        py = 10 if small else 20
        font_key = "small" if small else "button"
        
        button = tk.Button(
            parent,
            text=text,
            font=self.fonts[font_key],
            bg="#3c4678",  # Semi-transparent button background
            fg=TEXT_PRIMARY,
            activebackground=color,
            activeforeground=TEXT_PRIMARY,
            bd=0,
            relief=tk.FLAT,
            padx=px,  # Adjustable padding
            pady=py,  # Adjustable padding
            cursor="hand2",
            command=command,
            highlightthickness=1,
            highlightbackground="#cccccc",
            highlightcolor=color
        )
        
        # Enhanced hover effects with color transitions
        def on_enter(e):
            button.configure(
                bg=color,
                highlightbackground=color,
                relief=tk.RAISED,
                bd=1
            )
            
        def on_leave(e):
            button.configure(
                bg="#3c4678",
                highlightbackground="#cccccc",
                relief=tk.FLAT,
                bd=0
            )
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button

    def add_placeholder(self, entry_widget, placeholder_text):
        """Add placeholder text to entry widget"""
        def on_focus_in(event):
            if entry_widget.get() == placeholder_text:
                entry_widget.delete(0, tk.END)
                entry_widget.configure(fg=TEXT_PRIMARY)
                if hasattr(entry_widget, 'show_option'):
                    entry_widget.configure(show="●")
            # Check ready state when password gets focus
            if hasattr(self, 'check_ready_state'):
                self.check_ready_state()

        def on_focus_out(event):
            if not entry_widget.get():
                entry_widget.insert(0, placeholder_text)
                entry_widget.configure(fg=TEXT_SECONDARY)
                if hasattr(entry_widget, 'show_option'):
                    entry_widget.configure(show="")
            # Check ready state when password loses focus
            if hasattr(self, 'check_ready_state'):
                self.check_ready_state()

        entry_widget.insert(0, placeholder_text)
        entry_widget.configure(fg=TEXT_SECONDARY, show="")
        entry_widget.show_option = True
        entry_widget.bind("<FocusIn>", on_focus_in)
        entry_widget.bind("<FocusOut>", on_focus_out)

    def browse_file(self):
        """Open file dialog to select file"""
        file_path = filedialog.askopenfilename(
            title="Select file to encrypt/decrypt",
            filetypes=[
                ("All Files", "*.*"),
                ("Text Files", "*.txt"),
                ("Documents", "*.pdf;*.doc;*.docx"),
                ("Images", "*.jpg;*.png;*.gif"),
            ]
        )
        
        if file_path:
            self.selected_file.set(file_path)
            self.file_selected = True
            filename = os.path.basename(file_path)
            self.file_size = os.path.getsize(file_path)
            self.file_name.set(filename.split(".")[0])
            size_str = self.format_file_size(self.file_size)

            # Transform the upload area to show selected file
            self.transform_upload_area_after_selection(filename, size_str)
            
            self.status_var.set(f"File selected: {filename}")
            self.selected_folder.set(os.path.dirname(file_path))
            
            # Show password section and clear button
            self.password_container.pack(fill=tk.X, pady=(0, 15))
            self.clear_button_frame.pack(fill=tk.X, pady=8)
            self.password_entry.focus_set()  # Focus on password field
            self.check_ready_state()  # Check if we can show action buttons

    def transform_upload_area_after_selection(self, filename, size_str):
        """Transform upload area to show selected file with compact layout"""
        # Change the upload container to be more compact
        self.upload_container.configure(height=100)  # More compact height
        
        # Hide original upload widgets
        self.file_icon.pack_forget()
        self.upload_text.pack_forget()
        self.browse_btn.pack_forget()
        self.file_info_label.pack_forget()

        # Create new compact layout
        self.selected_file_frame = tk.Frame(self.upload_frame, bg="#1e1e28")
        self.selected_file_frame.pack(fill=tk.BOTH, expand=True)

        icon = tk.Label(self.selected_file_frame, text="✅", font=("Arial", 20), fg=SUCCESS_GLOW, bg="#1e1e28")
        icon.pack(side=tk.LEFT, padx=(0, 12))

        info_frame = tk.Frame(self.selected_file_frame, bg="#1e1e28")
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        filename_label = tk.Label(info_frame, text=filename, font=self.fonts["button"], fg=TEXT_PRIMARY, bg="#1e1e28", anchor="w")
        filename_label.pack(fill=tk.X)

        size_label = tk.Label(info_frame, text=size_str, font=self.fonts["small"], fg=TEXT_SECONDARY, bg="#1e1e28", anchor="w")
        size_label.pack(fill=tk.X)
        
        # Unbind hover events from main container
        for widget in [self.upload_container, self.upload_frame]:
            widget.unbind("<Enter>")
            widget.unbind("<Leave>")

    def check_ready_state(self, event=None):
        """Check if both file and password are ready and show action buttons"""
        has_file = self.file_selected and bool(self.selected_file.get())
        current_password = self.password_var.get()
        has_password = bool(current_password and current_password != "Enter password")
        
        self.password_ready = has_password
        
        if has_file and has_password:
            # Show action buttons when both file and password are available
            self.button_frame.pack(fill=tk.X, pady=(0, 25))
            self.status_var.set("Ready to encrypt or decrypt your file")
        else:
            # Hide action buttons if requirements not met
            self.button_frame.pack_forget()
            if has_file and not has_password:
                self.status_var.set("Enter a password to continue")
            elif not has_file:
                self.status_var.set("Select a file to get started")

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        current_show = self.password_entry.cget("show")
        if current_show:
            self.password_entry.configure(show="")
            self.eye_button.configure(text="🙈")
        else:
            self.password_entry.configure(show="●")
            self.eye_button.configure(text="👁")

    def encrypt_password(self, cost=15, salt=None):
        """Hash the password using the encryption backend."""
        if not self.validate_inputs():
            return
        self.start_processing("Hashing password...")
        current_password = self.password_var.get()
        if salt is None:
            salt = generate_salt(16)
        hashed = hash_password(current_password, cost, salt)
        return hashed, salt, cost

    def encrypt_file(self):
        def encrypt_data(a,b):
            return a
        """Encrypt the selected file (placeholder implementation)"""
        if not self.validate_inputs():
            return
        
        encryption_result = self.encrypt_password()
        if not encryption_result:
            self.finish_processing("❌ Encryption failed", "Password hashing failed.", is_error=True)
            return
        
        hashed_password, salt, cost = encryption_result

        finalpath = os.path.join(self.selected_folder.get(), self.file_name.get())
        os.makedirs(finalpath, exist_ok=True)
        
        data_for_regen = (f"File Name : {os.path.basename(self.selected_file.get())}\nSalt : {salt}\nCost : {cost}").encode('utf-8')
        encrypted_regen_data = encrypt_data(data_for_regen, hashed_password)
        encrypted_regen_data = encrypted_regen_data + b"\n" + encrypted_regen_data
        encrypted_regen_data = encrypt_data(encrypted_regen_data, hashed_password)
        with open(os.path.join(finalpath, "regen.datatxt"), "wb") as f:
            f.write(encrypted_regen_data)
        with open(os.path.join(finalpath, "file.txt"), "wb") as f:
            f.write(data_for_regen)
        self.start_processing("Encrypting file...")

        def encryption_logic():
            try:
                if self.file_size < 1 << 20:
                    # File is small enough for quick encryption
                    with open(self.selected_file.get(), "rb") as f:
                        data = f.read()
                    encrypted = encrypt_data(data, hashed_password)
                    with open(os.path.join(finalpath, self.file_name.get() + ".crypt"), "wb") as f:
                        f.write(encrypted)
                else:
                    # File is large - use multiprocessing Pool for chunked encryption
                    CHUNK_SIZE = 1 << 20  # 1 MB chunks
                    no_of_chunks = (self.file_size + CHUNK_SIZE - 1) // CHUNK_SIZE
                    
                    tasks = []
                    for i in range(no_of_chunks):
                        offset = i * CHUNK_SIZE
                        size = min(CHUNK_SIZE, self.file_size - offset)
                        tasks.append((self.selected_file.get(), (i, offset, size), hashed_password, finalpath, self.file_name.get()))

                    # Use a Pool to manage worker processes, limited to CPU count
                    with Pool(processes=self.thread_count) as pool:
                        results = pool.starmap(encrypt_worker_process, tasks)
                    
                    if all(results):
                        # print(f"All {no_of_chunks} chunks encrypted successfully")
                        pass
                    else:
                        raise Exception("One or more chunks failed to encrypt.")

                final_folder = os.path.join(self.selected_folder.get(), self.file_name.get())
                
                zip_path = finalpath + "_encrypted.zip"

                with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                    for root_dir, _, files in os.walk(final_folder):
                        for fname in files:
                            full_path = os.path.join(root_dir, fname)
                            if os.path.abspath(full_path) == os.path.abspath(zip_path):
                                continue
                            arcname = os.path.relpath(full_path, start=final_folder)
                            zf.write(full_path, arcname)

                if os.path.isdir(finalpath):
                    shutil.rmtree(finalpath, ignore_errors=True)
                
                self.root.after(0, lambda: self.finish_processing(
                    "✅ File encrypted and zipped",
                    f"Archive created at:\n{zip_path}"
                ))
            except Exception as e:
                self.root.after(0, lambda e=e: self.finish_processing("❌ Encryption failed", str(e), is_error=True))

        # Run the encryption logic in a separate thread to not block the GUI
        thread = threading.Thread(target=encryption_logic)
        thread.daemon = True
        thread.start()

        
        
    def decrypt_file(self):
        def decrypt_data(a,b):
            return a
        def encrypt_data(a,b):
            return a
        if not self.validate_inputs():
            return
        finalpath = os.path.join(self.selected_folder.get(), self.file_name.get())
        
    def encrypt_worker_process(self, chunk_info, hashed_password, finalpath, file_name_base):
        """Worker process to encrypt a single chunk of data."""
        chunk_no, offset, size = chunk_info
        try:
            with open(self.selected_file.get(), "rb") as f_in:
                f_in.seek(offset)
                chunk_data = f_in.read(size)
            
            encrypted = encrypt_data(chunk_data, hashed_password)
            
            # Write encrypted chunk to file
            chunk_filename = f"{file_name_base}_{chunk_no:04d}.crypt"
            with open(os.path.join(finalpath, chunk_filename), "wb") as f:
                f.write(encrypted)
            
            # Using print for now, a more robust logging/queue system could be used
            print(f"Process {os.getpid()}: Encrypted chunk {chunk_no}")
            return True
        except Exception as e:
            print(f"Process {os.getpid()}: Error encrypting chunk {chunk_no}: {e}")
            return False

    def validate_inputs(self):
        """Validate user inputs"""
        if not self.selected_file.get():
            self.show_error("Please select a file first")
            return False
            
        password = self.password_var.get()
        if not password or password == "Enter password":
            self.show_error("Please enter a password")
            self.password_entry.focus_set()
            return False
            
        return True

    def start_processing(self, message):
        """Start processing animation"""
        self.is_processing = True
        self.status_var.set(message)
        self.encrypt_btn.configure(state='disabled')
        self.decrypt_btn.configure(state='disabled')

    def finish_processing(self, status_message, detail_message, is_error=False):
        """Finish processing and show result"""
        self.is_processing = False
        self.status_var.set(status_message)
        self.encrypt_btn.configure(state='normal')
        self.decrypt_btn.configure(state='normal')
        
        if is_error:
            messagebox.showerror("Error", detail_message)
        else:
            messagebox.showinfo("Success", detail_message)

    def show_error(self, message):
        """Show error message"""
        self.status_var.set(f"❌ {message}")
        messagebox.showerror("Error", message)

    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"

    def on_upload_hover(self, entering):
        """Handle upload area hover effects"""
        # Placeholder for hover animation
        pass

    def animate_button_hover(self, button, entering):
        """Animate button hover effects"""
        # Placeholder for button hover animation
        pass

    def setup_animations(self):
        """Setup continuous animations"""
        self.animate_glow()

    def animate_glow(self):
        """Animate subtle glow effects"""
        self.animation_step += 1
        # Continue animation loop
        self.root.after(100, self.animate_glow)



def main():
    """Main application entry point"""
    # Make the application DPI-aware on Windows
    try:
        from ctypes import windll
        try:
            # Try per-monitor v2 on Windows 10+
            windll.user32.SetProcessDpiAwarenessContext(-3)  # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
        except Exception:
            # Fallback to system DPI aware
            windll.shcore.SetProcessDpiAwareness(1)
    except (ImportError, AttributeError):
        try: # Fallback for older Windows
            from ctypes import windll
            windll.user32.SetProcessDPIAware()
        except (ImportError, AttributeError):
            pass # Not on Windows or call failed

    root = tk.Tk()
    app = GlassyFileEncrypter(root)
    root.mainloop()


if __name__ == '__main__':
    main()
