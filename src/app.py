"""Main application window for Terminal Manager."""

import customtkinter as ctk
from tkinter import filedialog
import os

from .terminal import TabbedTerminalWidget
from .commands import COMMANDS, CATEGORY_ICONS
from .config import add_recent_project, get_recent_projects, get_custom_commands, add_custom_command, remove_custom_command
from .git_helper import get_git_branch, is_git_repo, get_commit_command
from .process_helper import kill_port, check_port_in_use


# Commands that should open in new tabs (long-running processes)
NEW_TAB_COMMANDS = [
    "npm run dev",
    "npm run worker", 
    "npm run start",
    "npx prisma studio",
    "npm run build:watch",
]

# Ports associated with commands
COMMAND_PORTS = {
    "npm run dev": 3000,
    "npx prisma studio": 5555,
}


class TerminalManagerApp(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.title("Terminal Manager")
        self.geometry("1200x750")
        self.minsize(1000, 600)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.current_project = None
        self.command_buttons = []
        
        self._setup_ui()
        self._load_recent_projects()
    
    def _setup_ui(self):
        """Setup the main UI layout."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left sidebar
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # App title
        self.title_label = ctk.CTkLabel(
            self.sidebar,
            text="🖥️ Terminal Manager",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.pack(pady=(20, 10))
        
        # Project selector section
        self.project_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.project_frame.pack(fill="x", padx=15, pady=(10, 5))
        self.project_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.project_frame,
            text="📁 Project",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        
        # Project dropdown
        self.project_var = ctk.StringVar(value="Select project...")
        self.project_dropdown = ctk.CTkOptionMenu(
            self.project_frame,
            variable=self.project_var,
            values=["Select project..."],
            command=self._on_project_select,
            width=240,
            dynamic_resizing=False
        )
        self.project_dropdown.grid(row=1, column=0, sticky="ew", pady=(5, 5))
        
        # Browse button
        self.browse_btn = ctk.CTkButton(
            self.project_frame,
            text="📂 Browse Folder...",
            command=self._browse_folder,
            height=32
        )
        self.browse_btn.grid(row=2, column=0, sticky="ew")
        
        # Current path display
        self.path_label = ctk.CTkLabel(
            self.project_frame,
            text="No project selected",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            wraplength=240
        )
        self.path_label.grid(row=3, column=0, sticky="w", pady=(5, 0))
        
        # Git branch display
        self.git_label = ctk.CTkLabel(
            self.project_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#4CAF50"
        )
        # Initially hidden
        # self.git_label.grid(row=4, column=0, sticky="w")
        
        # Info about new tabs
        self.info_label = ctk.CTkLabel(
            self.project_frame,
            text="💡 Dev/Worker mở tab riêng",
            font=ctk.CTkFont(size=10),
            text_color="#888"
        )
        self.info_label.grid(row=5, column=0, sticky="w", pady=(5, 0))
        
        # Scrollable command buttons area
        self.command_scroll = ctk.CTkScrollableFrame(
            self.sidebar,
            label_text="Commands",
            label_font=ctk.CTkFont(size=13, weight="bold")
        )
        self.command_scroll.pack(fill="both", expand=True, padx=10, pady=(2, 10))
        
        self._create_command_buttons()
        
        # Add custom command button
        self.add_cmd_btn = ctk.CTkButton(
            self.sidebar,
            text="➕ Add Custom Command",
            command=self._add_custom_command,
            height=32,
            fg_color="transparent",
            border_width=1
        )
        self.add_cmd_btn.pack(fill="x", padx=15, pady=(0, 15))
        
        # Right side - Tabbed Terminal
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Tabbed terminal widget
        self.terminal = TabbedTerminalWidget(self.main_frame)
        self.terminal.grid(row=0, column=0, sticky="nsew")
        
        # Bottom control bar
        self.control_bar = ctk.CTkFrame(self.main_frame, height=50)
        self.control_bar.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        
        # Command input
        self.cmd_entry = ctk.CTkEntry(
            self.control_bar,
            placeholder_text="Enter command and press Enter...",
            height=35
        )
        self.cmd_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.cmd_entry.bind("<Return>", self._run_custom_entry)
        
        self.run_btn = ctk.CTkButton(
            self.control_bar,
            text="▶️ Run",
            command=self._run_custom_entry,
            width=80,
            height=35
        )
        self.run_btn.pack(side="left", padx=5)
        
        self.run_new_tab_btn = ctk.CTkButton(
            self.control_bar,
            text="📑 New Tab",
            command=lambda: self._run_custom_entry(new_tab=True),
            width=90,
            height=35,
            fg_color=("#3a7ebf", "#1f538d")
        )
        self.run_new_tab_btn.pack(side="right", padx=5)
    
    def _create_command_buttons(self):
        """Create command buttons for each category."""
        # Clear existing buttons
        for widget in self.command_scroll.winfo_children():
            widget.destroy()
        self.command_buttons.clear()
        
        # Add preset command categories
        for category, commands in COMMANDS.items():
            if not commands and category != "Custom":
                continue
                
            # Category label
            icon = CATEGORY_ICONS.get(category, "📌")
            ctk.CTkLabel(
                self.command_scroll,
                text=f"{icon} {category}",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(anchor="w", pady=(10, 5))
            
            # Command buttons
            for label, cmd in commands:
                # Check if this is a long-running command
                is_new_tab = any(ntc in cmd for ntc in NEW_TAB_COMMANDS)
                
                btn_text = f"📑 {label}" if is_new_tab else label
                
                btn = ctk.CTkButton(
                    self.command_scroll,
                    text=btn_text,
                    command=lambda c=cmd, nt=is_new_tab, l=label: self._run_command(c, new_tab=nt, name=l),
                    height=32,
                    anchor="w",
                    fg_color=("#3a7ebf", "#1f538d") if is_new_tab else ("gray75", "gray25"),
                    hover_color=("#325882", "#14375e") if is_new_tab else ("gray65", "gray35")
                )
                btn.pack(fill="x", pady=2)
                self.command_buttons.append(btn)
        
        # Add custom commands
        custom_cmds = get_custom_commands()
        if custom_cmds:
            ctk.CTkLabel(
                self.command_scroll,
                text="⚡ Custom",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(anchor="w", pady=(10, 5))
            
            for i, item in enumerate(custom_cmds):
                # Frame for row
                frame = ctk.CTkFrame(self.command_scroll, fg_color="transparent")
                frame.pack(fill="x", pady=2)
                
                # Command button
                btn = ctk.CTkButton(
                    frame,
                    text=f"⚡ {item['label']}",
                    command=lambda c=item['command']: self._run_command(c),
                    height=32,
                    anchor="w",
                    fg_color=("gray75", "gray25"),
                    hover_color=("gray65", "gray35")
                )
                btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
                
                # Delete button
                del_btn = ctk.CTkButton(
                    frame,
                    text="❌",
                    command=lambda idx=i: self._delete_custom_command(idx),
                    width=32,
                    height=32,
                    fg_color="transparent",
                    text_color="red",
                    hover_color=("gray85", "gray20")
                )
                del_btn.pack(side="right")
                
                self.command_buttons.append(btn)
    
    def _load_recent_projects(self):
        """Load recent projects into dropdown."""
        recent = get_recent_projects()
        if recent:
            values = [os.path.basename(p) for p in recent]
            values.insert(0, "Select project...")
            self.project_dropdown.configure(values=values)
            self._recent_paths = recent
        else:
            self._recent_paths = []
    
    def _browse_folder(self):
        """Open folder browser dialog."""
        folder = filedialog.askdirectory(title="Select Project Folder")
        if folder:
            self._set_project(folder)
    
    def _on_project_select(self, choice):
        """Handle project selection from dropdown."""
        if choice == "Select project...":
            return
        
        # Find full path from recent
        for path in self._recent_paths:
            if os.path.basename(path) == choice:
                self._set_project(path)
                break
    
    def _set_project(self, path: str):
        """Set the current project directory."""
        self.current_project = path
        self.terminal.set_project(path)
        add_recent_project(path)
        self._load_recent_projects()
        
        # Update UI
        self.project_var.set(os.path.basename(path))
        self.path_label.configure(text=path)
        
        # Check for git
        if is_git_repo(path):
            branch = get_git_branch(path)
            self.git_label.configure(text=f"🔀 {branch}")
            self.git_label.grid(row=4, column=0, sticky="w", pady=(2, 0))
        else:
            self.git_label.configure(text="")
            self.git_label.grid_remove()
    
    def _run_command(self, command: str, new_tab: bool = False, name: str = None):
        """Execute a command."""
        if not self.current_project:
            tab = self.terminal.get_current_tab()
            if tab:
                tab._append_text("\n⚠️ Please select a project folder first!\n")
            return
        
        # Handle special commands
        if command == "GIT_COMMIT":
            self._git_commit_dialog()
            return

        # Auto-kill port if command uses one
        port = COMMAND_PORTS.get(command)
        if port:
            if kill_port(port):
                tab = self.terminal.get_current_tab()
                if tab:
                    tab._append_text(f"\n⚡ Auto-killed process on port {port}\n")
        
        if new_tab:
            # Run in new dedicated tab
            self.terminal.run_command_in_new_tab(
                command, 
                name=name or command[:15],
                cwd=self.current_project
            )
        else:
            # Run in current tab
            self.terminal.run_command(command, cwd=self.current_project)
    
    def _run_custom_entry(self, event=None, new_tab: bool = False):
        """Run command from entry field."""
        cmd = self.cmd_entry.get().strip()
        if cmd:
            self._run_command(cmd, new_tab=new_tab)
            self.cmd_entry.delete(0, "end")
    
    def _git_commit_dialog(self):
        """Show dialog for git commit message."""
        dialog = ctk.CTkInputDialog(
            text="Enter commit message:",
            title="Git Commit"
        )
        message = dialog.get_input()
        
        if message:
            cmd = get_commit_command(message)
            self.terminal.run_command(cmd, cwd=self.current_project)
    
    def _add_custom_command(self):
        """Show dialog to add a custom command."""
        try:
            # Label dialog
            label_dialog = ctk.CTkInputDialog(
                text="Enter button label:",
                title="Add Custom Command"
            )
            self._center_window(label_dialog)
            label = label_dialog.get_input()
            
            if not label:
                return
            
            # Command dialog
            cmd_dialog = ctk.CTkInputDialog(
                text="Enter command:",
                title="Add Custom Command"
            )
            self._center_window(cmd_dialog)
            cmd = cmd_dialog.get_input()
            
            if cmd:
                add_custom_command(label, cmd)
                self._create_command_buttons()
                
                # Feedback
                tab = self.terminal.get_current_tab()
                if tab:
                    tab._append_text(f"\n✅ Added custom command: '{label}' -> '{cmd}'\n")

        except Exception as e:
            print(f"Error adding custom command: {e}")
            tab = self.terminal.get_current_tab()
            if tab:
                tab._append_text(f"\n❌ Error adding custom command: {e}\n")

    def _center_window(self, window, width=300, height=200):
        """Center a window on the screen."""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def _delete_custom_command(self, index: int):
        """Delete a custom command."""
        remove_custom_command(index)
        self._create_command_buttons()

