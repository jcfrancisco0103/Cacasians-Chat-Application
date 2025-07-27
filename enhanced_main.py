import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import hashlib
import datetime
import threading
import time
import os
import shutil
from PIL import Image, ImageTk
import json
import urllib.request
import urllib.error
import webbrowser

class ChatApplication:
    VERSION = "1.2.0"
    UPDATE_URL = "https://github.com/jcfrancisco0103/Cacasians-Chat-Application/releases"  # Example URL
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Cacasians Chat Application v{self.VERSION}")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        # Initialize database
        self.init_database()
        
        # Current user
        self.current_user = None
        self.current_chat_partner = None
        self.current_group = None
        
        # Chat mode: 'user' or 'group'
        self.chat_mode = 'user'
        
        # Chat refresh thread
        self.chat_refresh_thread = None
        self.refresh_chat = False
        
        # Message tracking for edit/delete
        self.message_widgets = {}
        
        # Create main container
        self.main_frame = tk.Frame(self.root, bg='#1a1a2e')
        self.main_frame.pack(fill='both', expand=True)
        
        # Show login screen initially
        self.show_login_screen()
        
    def init_database(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect('chat_app.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Create users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create groups table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        # Create group members table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER,
                user_id INTEGER,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (group_id) REFERENCES groups (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(group_id, user_id)
            )
        ''')
        
        # Create messages table (updated for group support)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER,
                receiver_id INTEGER,
                group_id INTEGER,
                message TEXT,
                file_path TEXT,
                file_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                edited BOOLEAN DEFAULT FALSE,
                deleted BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (sender_id) REFERENCES users (id),
                FOREIGN KEY (receiver_id) REFERENCES users (id),
                FOREIGN KEY (group_id) REFERENCES groups (id)
            )
        ''')
        
        self.conn.commit()
    
    def check_for_updates(self):
        """Check for application updates"""
        try:
            # Show checking dialog
            checking_dialog = tk.Toplevel(self.root)
            checking_dialog.title("Checking for Updates")
            checking_dialog.geometry("300x150")
            checking_dialog.configure(bg='#1a1a2e')
            checking_dialog.transient(self.root)
            checking_dialog.grab_set()
            
            # Center the dialog
            checking_dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
            
            tk.Label(checking_dialog, text="🔄 Checking for updates...", 
                    font=('Arial', 14), fg='white', bg='#1a1a2e').pack(pady=50)
            
            def check_update_thread():
                try:
                    # Simulate update check (replace with actual update logic)
                    time.sleep(2)  # Simulate network delay
                    
                    # For demo purposes, we'll simulate different scenarios
                    import random
                    scenario = random.choice(['up_to_date', 'update_available', 'error'])
                    
                    checking_dialog.after(0, lambda: self.show_update_result(checking_dialog, scenario))
                    
                except Exception as e:
                    checking_dialog.after(0, lambda: self.show_update_result(checking_dialog, 'error', str(e)))
            
            # Start update check in background thread
            update_thread = threading.Thread(target=check_update_thread, daemon=True)
            update_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check for updates: {str(e)}")
    
    def show_update_result(self, checking_dialog, result, error_msg=None):
        """Show update check result"""
        checking_dialog.destroy()
        
        if result == 'up_to_date':
            messagebox.showinfo("Updates", f"✅ You're running the latest version!\n\nCurrent version: {self.VERSION}")
        elif result == 'update_available':
            response = messagebox.askyesno("Update Available", 
                                         f"🎉 New version available!\n\nCurrent: {self.VERSION}\nLatest: 1.3.0\n\nWould you like to download the update?")
            if response:
                webbrowser.open("https://github.com/cacasians/chat-app/releases")  # Example URL
        else:
            messagebox.showerror("Update Check Failed", 
                               f"❌ Could not check for updates.\n\n{error_msg if error_msg else 'Please check your internet connection.'}")
    
    def create_group_dialog(self):
        """Show create group dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Group")
        dialog.geometry("400x300")
        dialog.configure(bg='#1a1a2e')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # Title
        tk.Label(dialog, text="👥 Create New Group", font=('Arial', 18, 'bold'), 
                fg='#e94560', bg='#1a1a2e').pack(pady=20)
        
        # Group name
        tk.Label(dialog, text="Group Name:", font=('Arial', 12), 
                fg='white', bg='#1a1a2e').pack(pady=(10, 5))
        name_entry = tk.Entry(dialog, font=('Arial', 12), bg='#0f3460', fg='white', 
                             insertbackground='white', width=30)
        name_entry.pack(pady=5)
        
        # Group description
        tk.Label(dialog, text="Description (optional):", font=('Arial', 12), 
                fg='white', bg='#1a1a2e').pack(pady=(15, 5))
        desc_text = tk.Text(dialog, font=('Arial', 10), bg='#0f3460', fg='white', 
                           insertbackground='white', width=35, height=4)
        desc_text.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#1a1a2e')
        button_frame.pack(pady=20)
        
        def create_group():
            name = name_entry.get().strip()
            description = desc_text.get(1.0, tk.END).strip()
            
            if not name:
                messagebox.showerror("Error", "Group name is required!")
                return
            
            try:
                # Create group
                self.cursor.execute("INSERT INTO groups (name, description, created_by) VALUES (?, ?, ?)",
                                   (name, description, self.current_user['id']))
                group_id = self.cursor.lastrowid
                
                # Add creator as admin
                self.cursor.execute("INSERT INTO group_members (group_id, user_id, is_admin) VALUES (?, ?, TRUE)",
                                   (group_id, self.current_user['id']))
                self.conn.commit()
                
                dialog.destroy()
                messagebox.showinfo("Success", f"Group '{name}' created successfully! 🎉")
                self.load_groups()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create group: {str(e)}")
        
        create_btn = tk.Button(button_frame, text="🎉 Create Group", font=('Arial', 12, 'bold'), 
                              bg='#e94560', fg='white', command=create_group)
        create_btn.pack(side='left', padx=10)
        self.animate_button(create_btn, '#ff6b7a', '#e94560')
        
        cancel_btn = tk.Button(button_frame, text="❌ Cancel", font=('Arial', 12, 'bold'), 
                               bg='#0f3460', fg='white', command=dialog.destroy)
        cancel_btn.pack(side='right', padx=10)
        self.animate_button(cancel_btn)
    
    def clear_frame(self):
        """Clear all widgets from main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def create_gradient_frame(self, parent, color1='#16213e', color2='#0f3460'):
        """Create a frame with gradient background effect"""
        frame = tk.Frame(parent, bg=color1)
        return frame
    
    def animate_button(self, button, enter_color='#e94560', leave_color='#0f3460'):
        """Add hover animation to buttons"""
        def on_enter(e):
            button.configure(bg=enter_color)
            button.configure(relief='raised')
        
        def on_leave(e):
            button.configure(bg=leave_color)
            button.configure(relief='flat')
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def show_login_screen(self):
        """Display login/register screen"""
        self.clear_frame()
        
        # Main container with gradient effect
        container = self.create_gradient_frame(self.main_frame)
        container.pack(fill='both', expand=True)
        
        # Title with animation effect
        title_label = tk.Label(container, text="🚀 Cacasians Chat", 
                              font=('Arial', 36, 'bold'), 
                              fg='#e94560', bg='#1a1a2e')
        title_label.pack(pady=50)
        
        # Subtitle
        subtitle_label = tk.Label(container, text="Connect • Chat • Share", 
                                 font=('Arial', 16), 
                                 fg='#ffffff', bg='#1a1a2e')
        subtitle_label.pack(pady=(0, 30))
        
        # Login form frame with rounded corners effect
        login_frame = tk.Frame(container, bg='#16213e', relief='raised', bd=3)
        login_frame.pack(pady=20, padx=50, fill='x')
        
        # Form title
        form_title = tk.Label(login_frame, text="Sign In", 
                             font=('Arial', 20, 'bold'), 
                             fg='#e94560', bg='#16213e')
        form_title.pack(pady=20)
        
        # Username
        tk.Label(login_frame, text="👤 Username:", font=('Arial', 14), 
                fg='white', bg='#16213e').pack(pady=(10, 5))
        self.username_entry = tk.Entry(login_frame, font=('Arial', 12), 
                                      bg='#0f3460', fg='white', 
                                      insertbackground='white', width=30,
                                      relief='flat', bd=5)
        self.username_entry.pack(pady=5, ipady=5)
        
        # Password
        tk.Label(login_frame, text="🔒 Password:", font=('Arial', 14), 
                fg='white', bg='#16213e').pack(pady=(15, 5))
        self.password_entry = tk.Entry(login_frame, font=('Arial', 12), 
                                      bg='#0f3460', fg='white', 
                                      insertbackground='white', show='*', width=30,
                                      relief='flat', bd=5)
        self.password_entry.pack(pady=5, ipady=5)
        
        # Buttons frame
        buttons_frame = tk.Frame(login_frame, bg='#16213e')
        buttons_frame.pack(pady=30)
        
        # Login button with enhanced styling
        login_btn = tk.Button(buttons_frame, text="🚀 Login", 
                             font=('Arial', 12, 'bold'), 
                             bg='#0f3460', fg='white', 
                             command=self.login, width=15,
                             relief='flat', bd=0, pady=8)
        login_btn.pack(side='left', padx=15)
        self.animate_button(login_btn)
        
        # Register button
        register_btn = tk.Button(buttons_frame, text="✨ Register", 
                                font=('Arial', 12, 'bold'), 
                                bg='#0f3460', fg='white', 
                                command=self.show_register_screen, width=15,
                                relief='flat', bd=0, pady=8)
        register_btn.pack(side='right', padx=15)
        self.animate_button(register_btn)
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda e: self.login())
    
    def show_register_screen(self):
        """Display registration screen"""
        self.clear_frame()
        
        container = self.create_gradient_frame(self.main_frame)
        container.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(container, text="✨ Create Account", 
                              font=('Arial', 32, 'bold'), 
                              fg='#e94560', bg='#1a1a2e')
        title_label.pack(pady=30)
        
        # Register form frame
        register_frame = tk.Frame(container, bg='#16213e', relief='raised', bd=3)
        register_frame.pack(pady=20, padx=50, fill='x')
        
        # Form title
        form_title = tk.Label(register_frame, text="Join the Community", 
                             font=('Arial', 18, 'bold'), 
                             fg='#e94560', bg='#16213e')
        form_title.pack(pady=20)
        
        # Username
        tk.Label(register_frame, text="👤 Username:", font=('Arial', 14), 
                fg='white', bg='#16213e').pack(pady=(10, 5))
        self.reg_username_entry = tk.Entry(register_frame, font=('Arial', 12), 
                                          bg='#0f3460', fg='white', 
                                          insertbackground='white', width=30,
                                          relief='flat', bd=5)
        self.reg_username_entry.pack(pady=5, ipady=5)
        
        # Email
        tk.Label(register_frame, text="📧 Email:", font=('Arial', 14), 
                fg='white', bg='#16213e').pack(pady=(15, 5))
        self.reg_email_entry = tk.Entry(register_frame, font=('Arial', 12), 
                                       bg='#0f3460', fg='white', 
                                       insertbackground='white', width=30,
                                       relief='flat', bd=5)
        self.reg_email_entry.pack(pady=5, ipady=5)
        
        # Password
        tk.Label(register_frame, text="🔒 Password:", font=('Arial', 14), 
                fg='white', bg='#16213e').pack(pady=(15, 5))
        self.reg_password_entry = tk.Entry(register_frame, font=('Arial', 12), 
                                          bg='#0f3460', fg='white', 
                                          insertbackground='white', show='*', width=30,
                                          relief='flat', bd=5)
        self.reg_password_entry.pack(pady=5, ipady=5)
        
        # Confirm Password
        tk.Label(register_frame, text="🔐 Confirm Password:", font=('Arial', 14), 
                fg='white', bg='#16213e').pack(pady=(15, 5))
        self.reg_confirm_entry = tk.Entry(register_frame, font=('Arial', 12), 
                                         bg='#0f3460', fg='white', 
                                         insertbackground='white', show='*', width=30,
                                         relief='flat', bd=5)
        self.reg_confirm_entry.pack(pady=5, ipady=5)
        
        # Buttons frame
        buttons_frame = tk.Frame(register_frame, bg='#16213e')
        buttons_frame.pack(pady=30)
        
        # Register button
        register_btn = tk.Button(buttons_frame, text="🎉 Create Account", 
                                font=('Arial', 12, 'bold'), 
                                bg='#0f3460', fg='white', 
                                command=self.register, width=18,
                                relief='flat', bd=0, pady=8)
        register_btn.pack(side='left', padx=15)
        self.animate_button(register_btn)
        
        # Back button
        back_btn = tk.Button(buttons_frame, text="⬅️ Back to Login", 
                            font=('Arial', 12, 'bold'), 
                            bg='#0f3460', fg='white', 
                            command=self.show_login_screen, width=18,
                            relief='flat', bd=0, pady=8)
        back_btn.pack(side='right', padx=15)
        self.animate_button(back_btn)
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self):
        """Register new user"""
        username = self.reg_username_entry.get().strip()
        email = self.reg_email_entry.get().strip()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required!")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters!")
            return
        
        try:
            hashed_password = self.hash_password(password)
            self.cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                               (username, hashed_password, email))
            self.conn.commit()
            messagebox.showinfo("Success", "Account created successfully! 🎉")
            self.show_login_screen()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")
    
    def login(self):
        """Login user"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password!")
            return
        
        hashed_password = self.hash_password(password)
        self.cursor.execute("SELECT id, username FROM users WHERE username = ? AND password = ?",
                           (username, hashed_password))
        user = self.cursor.fetchone()
        
        if user:
            self.current_user = {'id': user[0], 'username': user[1]}
            messagebox.showinfo("Welcome", f"Welcome back, {username}! 🎉")
            self.show_chat_screen()
        else:
            messagebox.showerror("Error", "Invalid username or password!")
    
    def show_chat_screen(self):
        """Display main chat interface"""
        self.clear_frame()
        self.refresh_chat = True
        
        # Main chat container
        chat_container = tk.Frame(self.main_frame, bg='#1a1a2e')
        chat_container.pack(fill='both', expand=True)
        
        # Top bar with gradient effect
        top_bar = tk.Frame(chat_container, bg='#16213e', height=70)
        top_bar.pack(fill='x', pady=(0, 5))
        top_bar.pack_propagate(False)
        
        # Welcome label with emoji
        welcome_label = tk.Label(top_bar, text=f"👋 Welcome, {self.current_user['username']}!", 
                                font=('Arial', 18, 'bold'), fg='#e94560', bg='#16213e')
        welcome_label.pack(side='left', padx=20, pady=20)
        
        # Status indicator
        status_label = tk.Label(top_bar, text="🟢 Online", 
                               font=('Arial', 12), fg='#4CAF50', bg='#16213e')
        status_label.pack(side='left', padx=(0, 20), pady=20)
        
        # Right side buttons frame
        right_buttons = tk.Frame(top_bar, bg='#16213e')
        right_buttons.pack(side='right', padx=20, pady=20)
        
        # Check for Updates button
        update_btn = tk.Button(right_buttons, text="🔄 Check Updates", font=('Arial', 10, 'bold'), 
                              bg='#0f3460', fg='white', command=self.check_for_updates,
                              relief='flat', bd=0, pady=6, padx=10)
        update_btn.pack(side='left', padx=(0, 10))
        self.animate_button(update_btn)
        
        # Logout button with enhanced styling
        logout_btn = tk.Button(right_buttons, text="🚪 Logout", font=('Arial', 12, 'bold'), 
                              bg='#e94560', fg='white', command=self.logout,
                              relief='flat', bd=0, pady=8, padx=15)
        logout_btn.pack(side='left')
        self.animate_button(logout_btn, '#ff6b7a', '#e94560')
        
        # Main content area
        content_frame = tk.Frame(chat_container, bg='#1a1a2e')
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left panel - Users and Groups list with enhanced styling
        left_panel = tk.Frame(content_frame, bg='#16213e', width=320, relief='raised', bd=2)
        left_panel.pack(side='left', fill='y', padx=(0, 5))
        left_panel.pack_propagate(False)
        
        # Chat mode tabs
        tabs_frame = tk.Frame(left_panel, bg='#16213e')
        tabs_frame.pack(fill='x', pady=10)
        
        self.users_tab_btn = tk.Button(tabs_frame, text="👥 Users", font=('Arial', 12, 'bold'), 
                                      bg='#e94560', fg='white', command=lambda: self.switch_chat_mode('user'),
                                      relief='flat', bd=0, pady=8)
        self.users_tab_btn.pack(side='left', fill='x', expand=True, padx=(10, 5))
        
        self.groups_tab_btn = tk.Button(tabs_frame, text="🏢 Groups", font=('Arial', 12, 'bold'), 
                                       bg='#0f3460', fg='white', command=lambda: self.switch_chat_mode('group'),
                                       relief='flat', bd=0, pady=8)
        self.groups_tab_btn.pack(side='right', fill='x', expand=True, padx=(5, 10))
        
        self.animate_button(self.users_tab_btn, '#ff6b7a', '#e94560')
        self.animate_button(self.groups_tab_btn)
        
        # Search frame
        search_frame = tk.Frame(left_panel, bg='#16213e')
        search_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Label(search_frame, text="🔍", font=('Arial', 12), 
                fg='white', bg='#16213e').pack(side='left')
        
        self.search_entry = tk.Entry(search_frame, bg='#0f3460', fg='white', 
                                    font=('Arial', 10), insertbackground='white',
                                    relief='flat', bd=5)
        self.search_entry.pack(side='right', fill='x', expand=True, padx=(5, 0))
        self.search_entry.bind('<KeyRelease>', self.filter_items)
        
        # Create group button (only visible in group mode)
        self.create_group_frame = tk.Frame(left_panel, bg='#16213e')
        
        create_group_btn = tk.Button(self.create_group_frame, text="➕ Create Group", 
                                    font=('Arial', 11, 'bold'), bg='#e94560', fg='white', 
                                    command=self.create_group_dialog, relief='flat', bd=0, pady=6)
        create_group_btn.pack(fill='x', padx=10, pady=5)
        self.animate_button(create_group_btn, '#ff6b7a', '#e94560')
        
        # List frame
        listbox_frame = tk.Frame(left_panel, bg='#16213e')
        listbox_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.items_listbox = tk.Listbox(listbox_frame, bg='#0f3460', fg='white', 
                                       font=('Arial', 12), selectbackground='#e94560',
                                       relief='flat', bd=0, highlightthickness=0)
        items_scrollbar = tk.Scrollbar(listbox_frame, command=self.items_listbox.yview)
        self.items_listbox.configure(yscrollcommand=items_scrollbar.set)
        
        self.items_listbox.pack(side='left', fill='both', expand=True)
        items_scrollbar.pack(side='right', fill='y')
        self.items_listbox.bind('<<ListboxSelect>>', self.select_item)
        
        # Right panel - Chat area
        right_panel = tk.Frame(content_frame, bg='#16213e', relief='raised', bd=2)
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Chat header with enhanced styling
        chat_header_frame = tk.Frame(right_panel, bg='#0f3460', height=60)
        chat_header_frame.pack(fill='x')
        chat_header_frame.pack_propagate(False)
        
        self.chat_header = tk.Label(chat_header_frame, text="💬 Select a user to start chatting", 
                                   font=('Arial', 16, 'bold'), fg='#e94560', bg='#0f3460')
        self.chat_header.pack(pady=20)
        
        # Chat display area with scrollbar
        chat_display_frame = tk.Frame(right_panel, bg='#16213e')
        chat_display_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.chat_text = tk.Text(chat_display_frame, bg='#0f3460', fg='white', 
                                font=('Arial', 11), wrap='word', state='disabled',
                                relief='flat', bd=0, highlightthickness=0)
        chat_scrollbar = tk.Scrollbar(chat_display_frame, command=self.chat_text.yview)
        self.chat_text.configure(yscrollcommand=chat_scrollbar.set)
        
        self.chat_text.pack(side='left', fill='both', expand=True)
        chat_scrollbar.pack(side='right', fill='y')
        
        # Message input area with enhanced styling
        input_frame = tk.Frame(right_panel, bg='#16213e', height=80)
        input_frame.pack(fill='x', padx=10, pady=10)
        input_frame.pack_propagate(False)
        
        # File attachment button with icon
        attach_btn = tk.Button(input_frame, text="📎", font=('Arial', 14), 
                              bg='#0f3460', fg='white', command=self.attach_file,
                              relief='flat', bd=0, width=3, height=2)
        attach_btn.pack(side='left', padx=(0, 10), pady=10)
        self.animate_button(attach_btn)
        
        # Message entry with enhanced styling
        self.message_entry = tk.Entry(input_frame, bg='#0f3460', fg='white', 
                                     font=('Arial', 12), insertbackground='white',
                                     relief='flat', bd=5)
        self.message_entry.pack(side='left', fill='x', expand=True, padx=5, pady=10, ipady=8)
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        
        # Send button with icon
        send_btn = tk.Button(input_frame, text="🚀 Send", font=('Arial', 12, 'bold'), 
                            bg='#e94560', fg='white', command=self.send_message,
                            relief='flat', bd=0, padx=15, pady=10)
        send_btn.pack(side='right', padx=(10, 0), pady=10)
        self.animate_button(send_btn, '#ff6b7a', '#e94560')
        
        # Load users and start chat refresh
        self.refresh_users()
        self.start_chat_refresh()
    
    def switch_chat_mode(self, mode):
        """Switch between user and group chat modes"""
        self.chat_mode = mode
        
        # Update tab button styles
        if mode == 'user':
            self.users_tab_btn.config(bg='#e94560')
            self.groups_tab_btn.config(bg='#0f3460')
            self.create_group_frame.pack_forget()
        else:
            self.users_tab_btn.config(bg='#0f3460')
            self.groups_tab_btn.config(bg='#e94560')
            self.create_group_frame.pack(fill='x', pady=5)
        
        # Clear current selection and refresh list
        self.current_user = None
        self.current_group = None
        self.current_chat_partner = None
        self.refresh_items()
        self.clear_chat()
    
    def clear_chat(self):
        """Clear the chat display"""
        self.chat_label.config(text="💬 Select a user or group to start chatting")
        self.chat_text.config(state='normal')
        self.chat_text.delete(1.0, tk.END)
        self.chat_text.config(state='disabled')
        self.message_widgets.clear()
    
    def refresh_items(self):
        """Refresh the items list based on current chat mode"""
        if self.chat_mode == 'user':
            self.refresh_users()
        else:
            self.refresh_groups()
    
    def refresh_groups(self):
        """Refresh the groups list"""
        self.items_listbox.delete(0, tk.END)
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT g.id, g.name, g.description, COUNT(gm.user_id) as member_count
            FROM groups g
            LEFT JOIN group_members gm ON g.id = gm.group_id
            INNER JOIN group_members ugm ON g.id = ugm.group_id
            WHERE ugm.user_id = ?
            GROUP BY g.id, g.name, g.description
            ORDER BY g.name
        ''', (self.current_user_id,))
        
        groups = cursor.fetchall()
        for group in groups:
            group_id, name, description, member_count = group
            display_text = f"🏢 {name} ({member_count} members)"
            if description:
                display_text += f" - {description[:30]}..."
            self.items_listbox.insert(tk.END, display_text)
            
    def refresh_users(self):
        """Refresh the users list"""
        self.items_listbox.delete(0, tk.END)
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, username FROM users WHERE id != ?', (self.current_user_id,))
        users = cursor.fetchall()
        
        for user in users:
            user_id, username = user
            # Add online status indicator (simplified - always show as online for demo)
            self.items_listbox.insert(tk.END, f"🟢 {username}")
    
    def select_item(self, event):
        """Handle item selection based on current chat mode"""
        if self.chat_mode == 'user':
            self.select_user(event)
        else:
            self.select_group(event)
    
    def select_group(self, event):
        """Handle group selection"""
        selection = self.items_listbox.curselection()
        if selection:
            selected_text = self.items_listbox.get(selection[0])
            group_name = selected_text.split(' ', 1)[1].split(' (')[0]  # Extract group name
            
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM groups WHERE name = ?', (group_name,))
            result = cursor.fetchone()
            
            if result:
                self.current_group = result[0]
                self.current_user = None  # Clear user selection
                self.current_chat_partner = None
                self.chat_label.config(text=f"💬 Group: {group_name}")
                self.refresh_chat()
    
    def select_user(self, event):
        """Handle user selection for chat"""
        selection = self.items_listbox.curselection()
        if selection:
            selected_text = self.items_listbox.get(selection[0])
            username = selected_text.split(' ', 1)[1]  # Remove the status indicator
            
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            
            if result:
                self.current_user = result[0]
                self.current_group = None
                self.current_chat_partner = {'id': result[0], 'username': username}
                self.chat_label.config(text=f"💬 Chat with {username}")
                self.refresh_chat()
    
    def filter_items(self, event):
        """Filter items based on current chat mode"""
        if self.chat_mode == 'user':
            self.filter_users(event)
        else:
            self.filter_groups(event)
    
    def filter_groups(self, event):
        """Filter groups based on search text"""
        search_text = self.search_entry.get().lower()
        self.items_listbox.delete(0, tk.END)
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT g.id, g.name, g.description, COUNT(gm.user_id) as member_count
            FROM groups g
            LEFT JOIN group_members gm ON g.id = gm.group_id
            INNER JOIN group_members ugm ON g.id = ugm.group_id
            WHERE ugm.user_id = ? AND LOWER(g.name) LIKE ?
            GROUP BY g.id, g.name, g.description
            ORDER BY g.name
        ''', (self.current_user_id, f'%{search_text}%'))
        
        groups = cursor.fetchall()
        for group in groups:
            group_id, name, description, member_count = group
            display_text = f"🏢 {name} ({member_count} members)"
            if description:
                display_text += f" - {description[:30]}..."
            self.items_listbox.insert(tk.END, display_text)
    
    def filter_users(self, event):
        """Filter users based on search text"""
        search_text = self.search_entry.get().lower()
        self.items_listbox.delete(0, tk.END)
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, username FROM users WHERE id != ? AND LOWER(username) LIKE ?', 
                      (self.current_user_id, f'%{search_text}%'))
        users = cursor.fetchall()
        
        for user in users:
            user_id, username = user
            self.items_listbox.insert(tk.END, f"🟢 {username}")
    
    def refresh_chat(self):
        """Refresh the chat display"""
        self.load_chat_history()
    
    def load_chat_history(self):
        """Load chat history with selected user or group"""
        if not self.current_chat_partner and not self.current_group:
            return
        
        self.chat_text.config(state='normal')
        self.chat_text.delete(1.0, tk.END)
        self.message_widgets.clear()
        
        cursor = self.conn.cursor()
        
        if self.current_chat_partner:
            # Load user chat history
            cursor.execute("""
                SELECT sender_id, message, file_path, file_type, timestamp, edited, deleted, id
                FROM messages 
                WHERE ((sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?))
                AND deleted = FALSE AND group_id IS NULL
                ORDER BY timestamp
            """, (self.current_user['id'], self.current_chat_partner['id'],
                  self.current_chat_partner['id'], self.current_user['id']))
        else:
            # Load group chat history
            cursor.execute("""
                SELECT sender_id, message, file_path, file_type, timestamp, edited, deleted, id
                FROM messages 
                WHERE group_id = ? AND deleted = FALSE
                ORDER BY timestamp
            """, (self.current_group,))
        
        messages = cursor.fetchall()
        
        for msg in messages:
            sender_id, message, file_path, file_type, timestamp, edited, deleted, msg_id = msg
            
            # Get sender name
            if sender_id == self.current_user['id']:
                sender = "You"
            elif self.current_chat_partner:
                sender = self.current_chat_partner['username']
            else:
                # For group chats, get the sender's username
                cursor.execute("SELECT username FROM users WHERE id = ?", (sender_id,))
                sender_result = cursor.fetchone()
                sender = sender_result[0] if sender_result else "Unknown"
            
            # Format timestamp
            time_str = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
            
            # Create message frame
            msg_frame = tk.Frame(self.chat_text, bg='#1a1a2e')
            
            # Determine message alignment and color
            is_own_message = sender_id == self.current_user['id']
            bg_color = '#e94560' if is_own_message else '#0f3460'
            align = 'right' if is_own_message else 'left'
            
            # Message content frame
            content_frame = tk.Frame(msg_frame, bg=bg_color, relief='raised', bd=1)
            content_frame.pack(side=align, padx=10, pady=2, fill='x' if not is_own_message else 'none')
            
            # Sender and time info
            info_text = f"{sender} • {time_str}"
            if edited:
                info_text += " (edited)"
            
            info_label = tk.Label(content_frame, text=info_text, font=('Arial', 8), 
                                 fg='#cccccc', bg=bg_color, anchor='w')
            info_label.pack(fill='x', padx=5, pady=(2, 0))
            
            # Message text or file info
            if file_path:
                file_name = os.path.basename(file_path)
                file_icon = self.get_file_icon(file_type)
                display_text = f"{file_icon} {file_name}"
                if message:
                    display_text = f"{message}\n{display_text}"
            else:
                display_text = message
            
            msg_label = tk.Label(content_frame, text=display_text, font=('Arial', 10), 
                               fg='white', bg=bg_color, wraplength=300, justify='left', anchor='w')
            msg_label.pack(fill='x', padx=5, pady=(0, 5))
            
            # Store message widget for context menu
            self.message_widgets[msg_id] = {
                'frame': content_frame,
                'label': msg_label,
                'sender_id': sender_id,
                'message': message,
                'file_path': file_path
            }
            
            # Add context menu for own messages
            if is_own_message:
                self.add_message_context_menu(msg_label, msg_id)
            
            # Add click handler for file messages
            if file_path:
                msg_label.bind("<Button-1>", lambda e, path=file_path: self.open_file(path))
                msg_label.config(cursor="hand2")
            
            # Insert message frame into chat
            self.chat_text.window_create(tk.END, window=msg_frame)
            self.chat_text.insert(tk.END, '\n')
        
        self.chat_text.config(state='disabled')
        self.chat_text.see(tk.END)
    
    def add_message_context_menu(self, start_pos, end_pos, message_id, message_text, file_path):
        """Add context menu for message editing/deletion"""
        def show_context_menu(event):
            context_menu = tk.Menu(self.root, tearoff=0, bg='#16213e', fg='white')
            
            if not file_path:  # Only allow editing text messages
                context_menu.add_command(label="✏️ Edit Message", 
                                       command=lambda: self.edit_message(message_id, message_text))
            
            context_menu.add_command(label="🗑️ Delete Message", 
                                   command=lambda: self.delete_message(message_id))
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        # Bind right-click to the message line
        self.chat_text.tag_add(f"msg_{message_id}", start_pos, end_pos)
        self.chat_text.tag_bind(f"msg_{message_id}", "<Button-3>", show_context_menu)
    
    def edit_message(self, message_id, current_text):
        """Edit a message"""
        new_text = simpledialog.askstring("Edit Message", "Enter new message:", initialvalue=current_text)
        
        if new_text and new_text != current_text:
            try:
                self.cursor.execute("UPDATE messages SET message = ?, edited = TRUE WHERE id = ?",
                                   (new_text, message_id))
                self.conn.commit()
                self.load_chat_history()
                messagebox.showinfo("Success", "Message edited successfully! ✏️")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to edit message: {str(e)}")
    
    def delete_message(self, message_id):
        """Delete a message"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this message?"):
            try:
                self.cursor.execute("UPDATE messages SET deleted = TRUE WHERE id = ?", (message_id,))
                self.conn.commit()
                self.load_chat_history()
                messagebox.showinfo("Success", "Message deleted successfully! 🗑️")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete message: {str(e)}")
    
    def send_message(self):
        """Send message to selected user or group"""
        if not self.current_chat_partner and not self.current_group:
            messagebox.showwarning("Warning", "Please select a user or group to chat with!")
            return
        
        message = self.message_entry.get().strip()
        if not message:
            return
        
        try:
            cursor = self.conn.cursor()
            if self.current_chat_partner:
                # Send to user
                cursor.execute("""
                    INSERT INTO messages (sender_id, receiver_id, message) 
                    VALUES (?, ?, ?)
                """, (self.current_user['id'], self.current_chat_partner['id'], message))
            else:
                # Send to group
                cursor.execute("""
                    INSERT INTO messages (sender_id, group_id, message) 
                    VALUES (?, ?, ?)
                """, (self.current_user['id'], self.current_group, message))
            
            self.conn.commit()
            self.message_entry.delete(0, tk.END)
            self.load_chat_history()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {str(e)}")
    
    def attach_file(self):
        """Attach file to message"""
        if not self.current_chat_partner and not self.current_group:
            messagebox.showwarning("Warning", "Please select a user or group to chat with!")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select file to attach",
            filetypes=[
                ("All files", "*.*"),
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Videos", "*.mp4 *.avi *.mov *.wmv"),
                ("Documents", "*.pdf *.doc *.docx *.txt")
            ]
        )
        
        if file_path:
            # Get file info
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            # Check file size (limit to 50MB)
            if file_size > 50 * 1024 * 1024:
                messagebox.showerror("Error", "File size too large! Maximum size is 50MB.")
                return
            
            # Determine file type
            file_ext = os.path.splitext(file_name)[1].lower()
            if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                file_type = 'image'
            elif file_ext in ['.mp4', '.avi', '.mov', '.wmv']:
                file_type = 'video'
            else:
                file_type = 'document'
            
            # Create attachments directory if it doesn't exist
            attachments_dir = os.path.join(os.path.dirname(__file__), 'attachments')
            os.makedirs(attachments_dir, exist_ok=True)
            
            # Copy file to attachments directory
            new_path = os.path.join(attachments_dir, f"{int(time.time())}_{file_name}")
            shutil.copy2(file_path, new_path)
            
            # Get optional message text
            message_text = self.message_entry.get().strip()
            
            try:
                cursor = self.conn.cursor()
                if self.current_chat_partner:
                    # Send file to user
                    cursor.execute("""
                        INSERT INTO messages (sender_id, receiver_id, message, file_path, file_type) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (self.current_user['id'], self.current_chat_partner['id'], 
                          message_text, new_path, file_type))
                else:
                    # Send file to group
                    cursor.execute("""
                        INSERT INTO messages (sender_id, group_id, message, file_path, file_type) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (self.current_user['id'], self.current_group, 
                          message_text, new_path, file_type))
                
                self.conn.commit()
                
                self.message_entry.delete(0, tk.END)
                self.load_chat_history()
                messagebox.showinfo("Success", f"File '{file_name}' attached successfully!")
                
            except Exception as e:
                # Clean up copied file if database insert fails
                if os.path.exists(new_path):
                    os.remove(new_path)
                messagebox.showerror("Error", f"Failed to attach file: {str(e)}")
    
    def get_file_icon(self, file_type):
        """Get appropriate icon for file type"""
        if file_type == 'image':
            return '🖼️'
        elif file_type == 'video':
            return '🎥'
        else:
            return '📄'
    
    def open_file(self, file_path):
        """Open file with default system application"""
        try:
            if os.path.exists(file_path):
                os.startfile(file_path)  # Windows
            else:
                messagebox.showerror("Error", "File not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def add_message_context_menu(self, widget, msg_id):
        """Add context menu to message widget"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="✏️ Edit", command=lambda: self.edit_message(msg_id))
        context_menu.add_command(label="🗑️ Delete", command=lambda: self.delete_message(msg_id))
        
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        widget.bind("<Button-3>", show_context_menu)  # Right click
    
    def edit_message(self, msg_id):
        """Edit a message"""
        if msg_id not in self.message_widgets:
            return
        
        msg_data = self.message_widgets[msg_id]
        if msg_data['file_path']:
            messagebox.showwarning("Warning", "Cannot edit messages with file attachments!")
            return
        
        # Create edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Message")
        dialog.geometry("400x200")
        dialog.configure(bg='#1a1a2e')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        tk.Label(dialog, text="Edit your message:", font=('Arial', 12, 'bold'), 
                fg='white', bg='#1a1a2e').pack(pady=10)
        
        # Text entry
        text_var = tk.StringVar(value=msg_data['message'])
        entry = tk.Entry(dialog, textvariable=text_var, font=('Arial', 11), 
                        bg='#0f3460', fg='white', insertbackground='white', width=40)
        entry.pack(pady=10, padx=20, fill='x')
        entry.focus()
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#1a1a2e')
        button_frame.pack(pady=20)
        
        def save_edit():
            new_message = text_var.get().strip()
            if new_message and new_message != msg_data['message']:
                try:
                    cursor = self.conn.cursor()
                    cursor.execute("UPDATE messages SET message = ?, edited = TRUE WHERE id = ?", 
                                 (new_message, msg_id))
                    self.conn.commit()
                    dialog.destroy()
                    self.load_chat_history()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to edit message: {str(e)}")
            else:
                dialog.destroy()
        
        save_btn = tk.Button(button_frame, text="💾 Save", font=('Arial', 11, 'bold'), 
                           bg='#e94560', fg='white', command=save_edit)
        save_btn.pack(side='left', padx=10)
        
        cancel_btn = tk.Button(button_frame, text="❌ Cancel", font=('Arial', 11, 'bold'), 
                             bg='#0f3460', fg='white', command=dialog.destroy)
        cancel_btn.pack(side='right', padx=10)
        
        # Bind Enter key to save
        entry.bind('<Return>', lambda e: save_edit())
    
    def delete_message(self, msg_id):
        """Delete a message"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this message?"):
            try:
                cursor = self.conn.cursor()
                cursor.execute("UPDATE messages SET deleted = TRUE WHERE id = ?", (msg_id,))
                self.conn.commit()
                self.load_chat_history()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete message: {str(e)}")
    
    def start_chat_refresh(self):
        """Start background thread to refresh chat"""
        if self.chat_refresh_thread is None or not self.chat_refresh_thread.is_alive():
            self.chat_refresh_thread = threading.Thread(target=self.refresh_chat_loop, daemon=True)
            self.chat_refresh_thread.start()
    
    def refresh_chat_loop(self):
        """Background loop to refresh chat every 2 seconds"""
        while self.refresh_chat:
            time.sleep(2)
            if (self.current_chat_partner or self.current_group) and self.refresh_chat:
                self.root.after(0, self.load_chat_history)
    
    def logout(self):
        """Logout current user"""
        self.refresh_chat = False
        self.current_user = None
        self.current_chat_partner = None
        messagebox.showinfo("Goodbye", "Thanks for using Cacasians Chat! 👋")
        self.show_login_screen()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()
        self.refresh_chat = False
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    app = ChatApplication()
    app.run()