"""Terminal output widget and process management."""

import subprocess
import threading
import queue
import os
from typing import Optional, Callable
import customtkinter as ctk


class TerminalTab(ctk.CTkFrame):
    """A single terminal tab with its own process."""
    
    def __init__(self, master, tab_id: str, name: str, on_close: Callable = None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.tab_id = tab_id
        self.tab_name = name
        self.output_queue = queue.Queue()
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.on_close = on_close
        self.on_process_end: Optional[Callable] = None
        
        self._setup_ui()
        self._poll_output()
    
    def _setup_ui(self):
        """Setup the terminal UI components."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Terminal header
        self.header = ctk.CTkFrame(self, fg_color="transparent", height=30)
        self.header.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        
        self.status_label = ctk.CTkLabel(
            self.header,
            text="● Ready",
            text_color="#4CAF50",
            font=("Consolas", 12)
        )
        self.status_label.pack(side="left")
        
        self.action_btn = ctk.CTkButton(
            self.header,
            text="⏹ Stop",
            width=80,
            height=24,
            fg_color="#f44336",
            hover_color="#d32f2f",
            command=self._on_action_click,
            state="disabled"
        )
        self.action_btn.pack(side="right", padx=2)
        
        self.clear_btn = ctk.CTkButton(
            self.header,
            text="Clear",
            width=60,
            height=24,
            command=self.clear
        )
        self.clear_btn.pack(side="right", padx=2)
        
        # Terminal output area
        self.output = ctk.CTkTextbox(
            self,
            font=("Consolas", 11),
            fg_color="#1a1a1a",
            text_color="#e0e0e0",
            wrap="word"
        )
        self.output.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.output.configure(state="disabled")
    
    def _poll_output(self):
        """Poll the output queue and update the display."""
        if not self.winfo_exists():
            return
            
        try:
            while True:
                line = self.output_queue.get_nowait()
                self._append_text(line)
        except queue.Empty:
            pass
        
        # Schedule next poll
        if self.winfo_exists():
            self.after(50, self._poll_output)
    
    def _append_text(self, text: str):
        """Append text to the output widget."""
        if not self.winfo_exists():
            return
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.configure(state="disabled")
    
    def _read_output(self, pipe, is_error=False):
        """Read output from a pipe in a separate thread."""
        try:
            for line in iter(pipe.readline, ''):
                if line:
                    self.output_queue.put(line)
            pipe.close()
        except Exception as e:
            self.output_queue.put(f"\n[Error reading output: {e}]\n")
    
    def _monitor_process(self):
        """Monitor process and update status when it ends."""
        # Capture process in local variable to avoid race conditions
        process = self.process
        if process:
            process.wait()
            exit_code = process.returncode
            
            self.is_running = False
            self.process = None
            
            # Update status on main thread
            try:
                self.after(0, lambda: self._on_process_complete(exit_code))
            except Exception:
                pass
    
    def _on_action_click(self):
        """Handle action button click (Stop/Restart)."""
        if self.is_running:
            self.stop_process()
        else:
            self.restart_process()

    def _on_process_complete(self, exit_code: int):
        """Handle process completion."""
        if not self.winfo_exists():
            return

        # Change button to Restart
        self.action_btn.configure(
            text="🔄 Restart",
            fg_color="#2196F3",
            hover_color="#1976D2",
            state="normal"
        )
        
        if exit_code == 0:
            self.set_status("✓ Completed", "#4CAF50")
            self._append_text(f"\n[Process completed successfully]\n")
        elif exit_code == -15 or exit_code == 1:  # SIGTERM or generic error
            self.set_status("■ Stopped", "#FF9800")
        else:
            self.set_status(f"✗ Exit: {exit_code}", "#f44336")
            self._append_text(f"\n[Process exited with code {exit_code}]\n")
        
        if self.on_process_end:
            self.on_process_end(self.tab_id)
    
    def run_command(self, command: str, cwd: str = None):
        """Run a command and display output."""
        if self.is_running:
            self._append_text("\n[Process already running]\n")
            return False
        
        # Store for restart
        self.last_cmd = command
        self.last_cwd = cwd
        
        self._append_text(f"\n$ {command}\n")
        self._append_text("-" * 50 + "\n")
        self.set_status("● Running...", "#2196F3")
        
        # Change button to Stop
        self.action_btn.configure(
            text="⏹ Stop",
            fg_color="#f44336",
            hover_color="#d32f2f",
            state="normal"
        )
        
        try:
            self.process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',  # Replace invalid characters instead of crashing
                bufsize=1,
                cwd=cwd,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            self.is_running = True
            
            # Start output reader thread
            threading.Thread(
                target=self._read_output,
                args=(self.process.stdout,),
                daemon=True
            ).start()
            
            # Start process monitor thread
            threading.Thread(
                target=self._monitor_process,
                daemon=True
            ).start()
            
            return True
            
        except Exception as e:
            self._append_text(f"\n[Error starting process: {e}]\n")
            self.set_status("✗ Error", "#f44336")
            self.action_btn.configure(state="disabled") # Disable if failed to start
            return False
            
    def restart_process(self):
        """Restart the last command."""
        if hasattr(self, 'last_cmd') and self.last_cmd:
            self.clear()
            self.run_command(self.last_cmd, getattr(self, 'last_cwd', None))

    def stop_process(self):
        """Stop the running process."""
        if self.process and self.is_running:
            try:
                if os.name == 'nt':
                    # Windows: Kill process tree forcefully
                    subprocess.run(
                        f"taskkill /PID {self.process.pid} /T /F", 
                        shell=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    self.process.terminate()
                
                self._append_text("\n[Process terminated by user]\n")
            except Exception as e:
                self._append_text(f"\n[Error stopping process: {e}]\n")
            finally:
                self.is_running = False
                self.process = None
                # Let _monitor_process handle UI update via _on_process_complete
                self.set_status("■ Stopped", "#FF9800")
    
    def set_status(self, text: str, color: str = "#4CAF50"):
        """Update the status label."""
        if self.winfo_exists():
            self.status_label.configure(text=text, text_color=color)
    
    def clear(self):
        """Clear the terminal output."""
        if self.winfo_exists():
            self.output.configure(state="normal")
            self.output.delete("1.0", "end")
            self.output.configure(state="disabled")


class TabbedTerminalWidget(ctk.CTkFrame):
    """Multi-tab terminal widget supporting parallel command execution."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.tabs: dict[str, TerminalTab] = {}
        self.tab_counter = 0
        self.current_project = None
        
        self._setup_ui()
        # Create default main tab
        self._create_tab("Main", select=True)
    
    def _setup_ui(self):
        """Setup the tabbed terminal UI."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Tab bar
        self.tab_bar = ctk.CTkFrame(self, height=35, fg_color="transparent")
        self.tab_bar.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        
        self.tab_buttons_frame = ctk.CTkFrame(self.tab_bar, fg_color="transparent")
        self.tab_buttons_frame.pack(side="left", fill="x", expand=True)
        
        self.add_tab_btn = ctk.CTkButton(
            self.tab_bar,
            text="➕",
            width=30,
            height=28,
            command=self._add_new_tab
        )
        self.add_tab_btn.pack(side="right")
        
        # Tab content area
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        self.current_tab_id = None
        self.tab_buttons: dict[str, ctk.CTkButton] = {}
    
    def _create_tab(self, name: str, select: bool = True) -> str:
        """Create a new terminal tab."""
        self.tab_counter += 1
        tab_id = f"tab_{self.tab_counter}"
        
        # Create terminal tab
        tab = TerminalTab(
            self.content_frame,
            tab_id=tab_id,
            name=name,
            on_close=lambda: self._close_tab(tab_id)
        )
        tab.grid(row=0, column=0, sticky="nsew")
        tab.grid_remove()  # Hide initially
        
        self.tabs[tab_id] = tab
        
        # Create tab button
        btn_frame = ctk.CTkFrame(self.tab_buttons_frame, fg_color="transparent")
        btn_frame.pack(side="left", padx=2)
        
        btn = ctk.CTkButton(
            btn_frame,
            text=name,
            height=28,
            width=100,
            fg_color=("gray70", "gray30"),
            command=lambda tid=tab_id: self._select_tab(tid)
        )
        btn.pack(side="left")
        
        # Close button (except for first tab)
        if self.tab_counter > 1:
            close_btn = ctk.CTkButton(
                btn_frame,
                text="✕",
                width=24,
                height=28,
                fg_color="transparent",
                hover_color="#f44336",
                command=lambda tid=tab_id: self._close_tab(tid)
            )
            close_btn.pack(side="left")
        
        self.tab_buttons[tab_id] = btn_frame
        
        if select:
            self._select_tab(tab_id)
        
        return tab_id
    
    def _select_tab(self, tab_id: str):
        """Select and show a tab."""
        if self.current_tab_id and self.current_tab_id in self.tabs:
            self.tabs[self.current_tab_id].grid_remove()
            # Update button style
            btn_frame = self.tab_buttons.get(self.current_tab_id)
            if btn_frame:
                for child in btn_frame.winfo_children():
                    if isinstance(child, ctk.CTkButton) and child.cget("text") != "✕":
                        child.configure(fg_color=("gray70", "gray30"))
        
        self.current_tab_id = tab_id
        if tab_id in self.tabs:
            self.tabs[tab_id].grid()
            # Update button style
            btn_frame = self.tab_buttons.get(tab_id)
            if btn_frame:
                for child in btn_frame.winfo_children():
                    if isinstance(child, ctk.CTkButton) and child.cget("text") != "✕":
                        child.configure(fg_color=("#3B8ED0", "#1F6AA5"))
    
    def _close_tab(self, tab_id: str):
        """Close a tab."""
        if tab_id not in self.tabs:
            return
        
        # Stop any running process
        tab = self.tabs[tab_id]
        if tab.is_running:
            tab.stop_process()
        
        # Remove tab
        tab.destroy()
        del self.tabs[tab_id]
        
        # Remove button
        if tab_id in self.tab_buttons:
            self.tab_buttons[tab_id].destroy()
            del self.tab_buttons[tab_id]
        
        # Select another tab if needed
        if self.current_tab_id == tab_id:
            if self.tabs:
                self._select_tab(list(self.tabs.keys())[0])
    
    def _add_new_tab(self):
        """Add a new terminal tab."""
        name = f"Terminal {self.tab_counter + 1}"
        self._create_tab(name, select=True)
    
    def run_command_in_new_tab(self, command: str, name: str = None, cwd: str = None):
        """Run a command in a new dedicated tab."""
        tab_name = name or command[:20]
        tab_id = self._create_tab(tab_name, select=True)
        self.tabs[tab_id].run_command(command, cwd=cwd or self.current_project)
        return tab_id
    
    def run_command(self, command: str, cwd: str = None):
        """Run a command in the current tab."""
        if self.current_tab_id and self.current_tab_id in self.tabs:
            self.tabs[self.current_tab_id].run_command(command, cwd=cwd or self.current_project)
    
    def get_current_tab(self) -> Optional[TerminalTab]:
        """Get the currently selected tab."""
        if self.current_tab_id and self.current_tab_id in self.tabs:
            return self.tabs[self.current_tab_id]
        return None
    
    def set_project(self, path: str):
        """Set the current project directory."""
        self.current_project = path
        # Notify current tab
        tab = self.get_current_tab()
        if tab:
            tab.clear()
            tab._append_text(f"📁 Project: {path}\n")
