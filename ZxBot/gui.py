import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import asyncio
from bot import DiscordBot
from config import TOKEN, DEFAULT_CHANNEL_ID, DEFAULT_LANGUAGE
from translations import TRANSLATIONS

class BotGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.current_language = DEFAULT_LANGUAGE
        self.root.title(self._('window_title'))
        self.root.geometry("500x400")
        
        self.bot = DiscordBot()
        self.bot_thread = None
        self.setup_gui()
        
    def _(self, key):
        """Translate a key to the current language"""
        return TRANSLATIONS[self.current_language].get(key, key)
        
    def change_language(self, event=None):
        """Change the interface language"""
        self.current_language = self.language_var.get()
        self.update_interface_texts()
        
    def update_interface_texts(self):
        """Update all interface texts with the current language"""
        self.root.title(self._('window_title'))
        
        # Update tabs
        self.notebook.tab(0, text=self._('tab_messages'))
        self.notebook.tab(1, text=self._('tab_settings'))
        
        # Update channel frame
        self.channel_frame.config(text=self._('channel_settings'))
        self.channel_label.config(text=self._('channel_id'))
        
        # Update message frame
        self.message_frame.config(text=self._('message'))
        
        # Update image frame
        self.image_frame.config(text=self._('image'))
        self.browse_image_btn.config(text=self._('browse'))
        
        # Update control buttons
        self.bot_control_frame.config(text=self._('bot_control'))
        self.start_stop_btn.config(text=self._('start_bot') if not self.bot.is_running() else self._('stop_bot'))
        self.force_stop_btn.config(text=self._('force_stop'))
        self.send_btn.config(text=self._('send_message'))
        self.send_image_btn.config(text=self._('send_image'))
        self.cleanup_btn.config(text=self._('clean_messages'))
        
        # Update settings tab
        self.avatar_frame.config(text=self._('avatar_settings'))
        self.browse_avatar_btn.config(text=self._('browse'))
        self.change_avatar_btn.config(text=self._('change_avatar'))
        
        self.status_frame.config(text=self._('status_settings'))
        self.status_label.config(text=self._('status'))
        self.activity_label.config(text=self._('activity'))
        self.update_presence_btn.config(text=self._('update_presence'))
        
    def setup_gui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create tabs
        self.message_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.message_tab, text=self._('tab_messages'))
        self.notebook.add(self.settings_tab, text=self._('tab_settings'))
        
        # Language selector in settings tab
        language_frame = ttk.LabelFrame(self.settings_tab, text=self._('language'), padding=10)
        language_frame.pack(fill="x", padx=10, pady=5)
        
        self.language_var = tk.StringVar(value=self.current_language)
        language_combo = ttk.Combobox(
            language_frame,
            textvariable=self.language_var,
            values=["fr", "en"],
            state="readonly",
            width=5
        )
        language_combo.pack(side="left", padx=5)
        language_combo.bind('<<ComboboxSelected>>', self.change_language)
        
        self.setup_message_tab()
        self.setup_settings_tab()
        
        # Create custom styles
        style = ttk.Style()
        style.configure("Danger.TButton", foreground="red")
        style.configure("Warning.TButton", foreground="orange")
        
        self.update_interface_texts()
        
    def setup_message_tab(self):
        # Channel ID Frame
        self.channel_frame = ttk.LabelFrame(self.message_tab, text=self._('channel_settings'), padding=10)
        self.channel_frame.pack(fill="x", padx=10, pady=5)
        
        self.channel_label = ttk.Label(self.channel_frame, text=self._('channel_id'))
        self.channel_label.pack(side="left")
        
        self.channel_id = ttk.Entry(self.channel_frame)
        self.channel_id.pack(side="left", fill="x", expand=True, padx=5)
        if DEFAULT_CHANNEL_ID:
            self.channel_id.insert(0, str(DEFAULT_CHANNEL_ID))
            
        # Messages Cleanup Frame
        cleanup_frame = ttk.Frame(self.channel_frame)
        cleanup_frame.pack(side="left", padx=5)
        
        self.cleanup_limit = ttk.Spinbox(
            cleanup_frame,
            from_=1,
            to=1000,
            width=5,
            state="readonly"
        )
        self.cleanup_limit.set(100)
        self.cleanup_limit.pack(side="left", padx=2)
        
        self.cleanup_btn = ttk.Button(
            cleanup_frame,
            text=self._('clean_messages'),
            command=self.delete_messages,
            style="Warning.TButton"
        )
        self.cleanup_btn.pack(side="left", padx=2)
        self.cleanup_btn.config(state="disabled")
        
        # Message Frame
        self.message_frame = ttk.LabelFrame(self.message_tab, text=self._('message'), padding=10)
        self.message_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.message_text = tk.Text(self.message_frame, height=8)
        self.message_text.pack(fill="both", expand=True)
        
        # Image Frame
        self.image_frame = ttk.LabelFrame(self.message_tab, text=self._('image'), padding=10)
        self.image_frame.pack(fill="x", padx=10, pady=5)
        
        self.image_path = tk.StringVar()
        image_entry = ttk.Entry(self.image_frame, textvariable=self.image_path, state="readonly")
        image_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        self.browse_image_btn = ttk.Button(
            self.image_frame,
            text=self._('browse'),
            command=self.browse_image
        )
        self.browse_image_btn.pack(side="left", padx=5)
        
        # Control Frame
        control_frame = ttk.Frame(self.message_tab, padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # Bot Control Buttons Frame
        self.bot_control_frame = ttk.LabelFrame(control_frame, text=self._('bot_control'), padding=5)
        self.bot_control_frame.pack(side="left", padx=5)
        
        self.start_stop_btn = ttk.Button(
            self.bot_control_frame,
            text=self._('start_bot'),
            command=self.toggle_bot
        )
        self.start_stop_btn.pack(side="left", padx=5)
        
        self.force_stop_btn = ttk.Button(
            self.bot_control_frame,
            text=self._('force_stop'),
            command=self.force_stop_bot,
            style="Danger.TButton"
        )
        self.force_stop_btn.pack(side="left", padx=5)
        self.force_stop_btn.config(state="disabled")
        
        # Message Control Buttons Frame
        message_control_frame = ttk.Frame(control_frame)
        message_control_frame.pack(side="left", padx=5)
        
        self.send_btn = ttk.Button(
            message_control_frame,
            text=self._('send_message'),
            command=self.send_message
        )
        self.send_btn.pack(side="left", padx=5)
        self.send_btn.config(state="disabled")
        
        self.send_image_btn = ttk.Button(
            message_control_frame,
            text=self._('send_image'),
            command=self.send_image
        )
        self.send_image_btn.pack(side="left", padx=5)
        self.send_image_btn.config(state="disabled")
        
    def setup_settings_tab(self):
        # Avatar Frame
        self.avatar_frame = ttk.LabelFrame(self.settings_tab, text=self._('avatar_settings'), padding=10)
        self.avatar_frame.pack(fill="x", padx=10, pady=5)
        
        self.avatar_path = tk.StringVar()
        avatar_entry = ttk.Entry(self.avatar_frame, textvariable=self.avatar_path, state="readonly")
        avatar_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        self.browse_avatar_btn = ttk.Button(
            self.avatar_frame,
            text=self._('browse'),
            command=self.browse_avatar
        )
        self.browse_avatar_btn.pack(side="left", padx=5)
        
        self.change_avatar_btn = ttk.Button(
            self.avatar_frame,
            text=self._('change_avatar'),
            command=self.change_avatar
        )
        self.change_avatar_btn.pack(side="left", padx=5)
        
        # Status Frame
        self.status_frame = ttk.LabelFrame(self.settings_tab, text=self._('status_settings'), padding=10)
        self.status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_label = ttk.Label(self.status_frame, text=self._('status'))
        self.status_label.pack(side="left", padx=5)
        
        self.status_var = tk.StringVar(value="online")
        status_combo = ttk.Combobox(
            self.status_frame,
            textvariable=self.status_var,
            values=["online", "idle", "dnd", "invisible"],
            state="readonly",
            width=10
        )
        status_combo.pack(side="left", padx=5)
        
        self.activity_label = ttk.Label(self.status_frame, text=self._('activity'))
        self.activity_label.pack(side="left", padx=5)
        
        self.activity_var = tk.StringVar()
        activity_entry = ttk.Entry(self.status_frame, textvariable=self.activity_var)
        activity_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        self.update_presence_btn = ttk.Button(
            self.status_frame,
            text=self._('update_presence'),
            command=self.update_presence
        )
        self.update_presence_btn.pack(side="left", padx=5)
        
    def browse_avatar(self):
        file_path = filedialog.askopenfilename(
            title=self._('select_avatar'),
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.gif"),
                ("Tous les fichiers", "*.*")
            ]
        )
        if file_path:
            self.avatar_path.set(file_path)
            
    def change_avatar(self):
        if not self.bot.is_running():
            messagebox.showerror(self._('error'), self._('bot_must_run'))
            return
            
        avatar_path = self.avatar_path.get()
        if not avatar_path:
            messagebox.showerror(self._('error'), self._('select_image'))
            return
            
        asyncio.run_coroutine_threadsafe(
            self.bot.change_avatar(avatar_path),
            self.bot.bot.loop
        )
        messagebox.showinfo(self._('success'), self._('avatar_changed'))
        
    def browse_image(self):
        file_path = filedialog.askopenfilename(
            title=self._('select_image'),
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.gif"),
                ("Tous les fichiers", "*.*")
            ]
        )
        if file_path:
            self.image_path.set(file_path)
            
    def toggle_bot(self):
        if not self.bot.is_running():
            self.start_bot()
        else:
            self.stop_bot()
            
    def start_bot(self):
        self.bot_thread = threading.Thread(target=self.run_bot_async)
        self.bot_thread.start()
        self.start_stop_btn.config(text=self._('stop_bot'))
        self.send_btn.config(state="normal")
        self.send_image_btn.config(state="normal")
        self.force_stop_btn.config(state="normal")
        self.cleanup_btn.config(state="normal")
        
    def stop_bot(self):
        if self.bot_thread and self.bot.is_running():
            asyncio.run(self.bot.stop_bot())
            self.bot_thread.join()
            self.start_stop_btn.config(text=self._('start_bot'))
            self.send_btn.config(state="disabled")
            self.send_image_btn.config(state="disabled")
            self.force_stop_btn.config(state="disabled")
            self.cleanup_btn.config(state="disabled")
            
    def force_stop_bot(self):
        if not self.bot.is_running():
            return
            
        if messagebox.askyesno(self._('confirmation'), self._('confirm_force_stop')):
            asyncio.run_coroutine_threadsafe(
                self.bot.force_stop_bot(),
                self.bot.bot.loop
            )
            if self.bot_thread:
                self.bot_thread.join(timeout=2)  # Wait for up to 2 seconds
            self.start_stop_btn.config(text=self._('start_bot'))
            self.send_btn.config(state="disabled")
            self.send_image_btn.config(state="disabled")
            self.force_stop_btn.config(state="disabled")
            self.cleanup_btn.config(state="disabled")
            messagebox.showinfo(self._('success'), self._('bot_force_stopped'))
        
    def run_bot_async(self):
        asyncio.run(self.bot.start_bot(TOKEN))
        
    def send_message(self):
        channel_id = self.channel_id.get().strip()
        message = self.message_text.get("1.0", tk.END).strip()
        
        if not channel_id:
            messagebox.showerror(self._('error'), self._('enter_channel_id'))
            return
            
        if not message:
            messagebox.showerror(self._('error'), self._('enter_message'))
            return
            
        asyncio.run_coroutine_threadsafe(
            self.bot.send_message(channel_id, message),
            self.bot.bot.loop
        )
        
    def send_image(self):
        if not self.bot.is_running():
            messagebox.showerror(self._('error'), self._('bot_must_run'))
            return
            
        channel_id = self.channel_id.get().strip()
        if not channel_id:
            messagebox.showerror(self._('error'), self._('enter_channel_id'))
            return
            
        image_path = self.image_path.get()
        if not image_path:
            messagebox.showerror(self._('error'), self._('select_image'))
            return
            
        message = self.message_text.get("1.0", tk.END).strip()
        
        asyncio.run_coroutine_threadsafe(
            self.bot.send_image(channel_id, image_path, message if message else None),
            self.bot.bot.loop
        )
        
    def update_presence(self):
        if not self.bot.is_running():
            messagebox.showerror(self._('error'), self._('bot_must_run'))
            return
            
        status = self.status_var.get()
        activity = self.activity_var.get().strip()
        
        asyncio.run_coroutine_threadsafe(
            self.bot.change_presence(status, activity),
            self.bot.bot.loop
        )
        messagebox.showinfo(self._('success'), self._('presence_updated'))
        
    def delete_messages(self):
        if not self.bot.is_running():
            messagebox.showerror(self._('error'), self._('bot_must_run'))
            return
            
        channel_id = self.channel_id.get().strip()
        if not channel_id:
            messagebox.showerror(self._('error'), self._('enter_channel_id'))
            return
            
        try:
            limit = int(self.cleanup_limit.get())
        except ValueError:
            messagebox.showerror(self._('error'), self._('invalid_limit'))
            return
            
        if messagebox.askyesno(self._('confirmation'), self._('confirm_delete').format(limit)):
            async def delete_and_show_result():
                deleted = await self.bot.delete_bot_messages(channel_id, limit)
                messagebox.showinfo(self._('success'), self._('messages_deleted').format(deleted))
                
            asyncio.run_coroutine_threadsafe(
                delete_and_show_result(),
                self.bot.bot.loop
            )
        
    def run(self):
        self.root.mainloop()
        if self.bot.is_running():
            self.stop_bot()