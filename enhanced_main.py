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

class ChatApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cacasians Chat Application")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        # Initialize database
        self.init_database()
        
        # Current user
        self.current_user = None
        self.current_chat_partner = None
        
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
        
        # Create messages table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER,
                receiver_id INTEGER,
                message TEXT,
                file_path TEXT,
                file_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                edited BOOLEAN DEFAULT FALSE,
                deleted BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (sender_id) REFERENCES users (id),
                FOREIGN KEY (receiver_id) REFERENCES users (id)
            )
        ''')
        
        self.conn.commit()
    
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
        
        # Logout button with enhanced styling
        logout_btn = tk.Button(top_bar, text="🚪 Logout", font=('Arial', 12, 'bold'), 
                              bg='#e94560', fg='white', command=self.logout,
                              relief='flat', bd=0, pady=8, padx=15)
        logout_btn.pack(side='right', padx=20, pady=20)
        self.animate_button(logout_btn, '#ff6b7a', '#e94560')
        
        # Main content area
        content_frame = tk.Frame(chat_container, bg='#1a1a2e')
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left panel - Users list with enhanced styling
        left_panel = tk.Frame(content_frame, bg='#16213e', width=320, relief='raised', bd=2)
        left_panel.pack(side='left', fill='y', padx=(0, 5))
        left_panel.pack_propagate(False)
        
        # Users list title with icon
        users_title_frame = tk.Frame(left_panel, bg='#16213e')
        users_title_frame.pack(fill='x', pady=15)
        
        tk.Label(users_title_frame, text="👥 Active Users", font=('Arial', 16, 'bold'), 
                fg='white', bg='#16213e').pack()
        
        # Search frame
        search_frame = tk.Frame(left_panel, bg='#16213e')
        search_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Label(search_frame, text="🔍", font=('Arial', 12), 
                fg='white', bg='#16213e').pack(side='left')
        
        self.search_entry = tk.Entry(search_frame, bg='#0f3460', fg='white', 
                                    font=('Arial', 10), insertbackground='white',
                                    relief='flat', bd=5)
        self.search_entry.pack(side='right', fill='x', expand=True, padx=(5, 0))
        self.search_entry.bind('<KeyRelease>', self.filter_users)
        
        # Users listbox with custom styling
        listbox_frame = tk.Frame(left_panel, bg='#16213e')
        listbox_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.users_listbox = tk.Listbox(listbox_frame, bg='#0f3460', fg='white', 
                                       font=('Arial', 12), selectbackground='#e94560',
                                       relief='flat', bd=0, highlightthickness=0)
        users_scrollbar = tk.Scrollbar(listbox_frame, command=self.users_listbox.yview)
        self.users_listbox.configure(yscrollcommand=users_scrollbar.set)
        
        self.users_listbox.pack(side='left', fill='both', expand=True)
        users_scrollbar.pack(side='right', fill='y')
        self.users_listbox.bind('<<ListboxSelect>>', self.select_user)
        
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
        self.load_users()
        self.start_chat_refresh()
    
    def filter_users(self, event=None):
        """Filter users based on search input"""
        search_term = self.search_entry.get().lower()
        self.users_listbox.delete(0, tk.END)
        
        self.cursor.execute("SELECT id, username FROM users WHERE id != ? AND LOWER(username) LIKE ?", 
                           (self.current_user['id'], f'%{search_term}%'))
        users = self.cursor.fetchall()
        
        for user in users:
            self.users_listbox.insert(tk.END, f"👤 {user[1]}")
    
    def load_users(self):
        """Load all users except current user"""
        self.users_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT id, username FROM users WHERE id != ?", (self.current_user['id'],))
        users = self.cursor.fetchall()
        
        for user in users:
            self.users_listbox.insert(tk.END, f"👤 {user[1]}")
            
    def select_user(self, event):
        """Select user to chat with"""
        selection = self.users_listbox.curselection()
        if selection:
            username_with_icon = self.users_listbox.get(selection[0])
            username = username_with_icon.replace("👤 ", "")
            self.cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_id = self.cursor.fetchone()[0]
            self.current_chat_partner = {'id': user_id, 'username': username}
            self.chat_header.config(text=f"💬 Chatting with {username}")
            self.load_chat_history()
    
    def load_chat_history(self):
        """Load chat history with selected user"""
        if not self.current_chat_partner:
            return
        
        self.chat_text.config(state='normal')
        self.chat_text.delete(1.0, tk.END)
        self.message_widgets.clear()
        
        self.cursor.execute("""
            SELECT sender_id, message, file_path, file_type, timestamp, edited, deleted, id
            FROM messages 
            WHERE ((sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?))
            AND deleted = FALSE
            ORDER BY timestamp
        """, (self.current_user['id'], self.current_chat_partner['id'],
              self.current_chat_partner['id'], self.current_user['id']))
        
        messages = self.cursor.fetchall()
        
        for msg in messages:
            sender_id, message, file_path, file_type, timestamp, edited, deleted, msg_id = msg
            sender = "You" if sender_id == self.current_user['id'] else self.current_chat_partner['username']
            
            # Format timestamp
            time_str = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
            
            # Create message display
            if file_path:
                if file_type == 'image':
                    display_text = f"[{time_str}] {sender}: 🖼️ {os.path.basename(file_path)}"
                elif file_type == 'video':
                    display_text = f"[{time_str}] {sender}: 🎥 {os.path.basename(file_path)}"
                else:
                    display_text = f"[{time_str}] {sender}: 📄 {os.path.basename(file_path)}"
            else:
                display_text = f"[{time_str}] {sender}: {message}"
            
            if edited:
                display_text += " ✏️"
            
            # Insert message
            start_pos = self.chat_text.index(tk.END)
            self.chat_text.insert(tk.END, display_text + "\n")
            end_pos = self.chat_text.index(tk.END)
            
            # Add right-click menu for own messages
            if sender_id == self.current_user['id']:
                self.add_message_context_menu(start_pos, end_pos, msg_id, message, file_path)
        
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
        """Send message to selected user"""
        if not self.current_chat_partner:
            messagebox.showwarning("Warning", "Please select a user to chat with!")
            return
        
        message = self.message_entry.get().strip()
        if not message:
            return
        
        try:
            self.cursor.execute("""
                INSERT INTO messages (sender_id, receiver_id, message) 
                VALUES (?, ?, ?)
            """, (self.current_user['id'], self.current_chat_partner['id'], message))
            self.conn.commit()
            
            self.message_entry.delete(0, tk.END)
            self.load_chat_history()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {str(e)}")
    
    def attach_file(self):
        """Attach file to message"""
        if not self.current_chat_partner:
            messagebox.showwarning("Warning", "Please select a user to chat with!")
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
            # Create attachments directory if it doesn't exist
            attachments_dir = "attachments"
            if not os.path.exists(attachments_dir):
                os.makedirs(attachments_dir)
            
            # Copy file to attachments directory
            filename = os.path.basename(file_path)
            new_path = os.path.join(attachments_dir, f"{int(time.time())}_{filename}")
            shutil.copy2(file_path, new_path)
            
            # Determine file type
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                file_type = 'image'
                message_text = f"Sent an image: {filename}"
            elif file_ext in ['.mp4', '.avi', '.mov', '.wmv']:
                file_type = 'video'
                message_text = f"Sent a video: {filename}"
            else:
                file_type = 'document'
                message_text = f"Sent a file: {filename}"
            
            try:
                self.cursor.execute("""
                    INSERT INTO messages (sender_id, receiver_id, message, file_path, file_type) 
                    VALUES (?, ?, ?, ?, ?)
                """, (self.current_user['id'], self.current_chat_partner['id'], 
                      message_text, new_path, file_type))
                self.conn.commit()
                
                self.load_chat_history()
                messagebox.showinfo("Success", f"File attached successfully! 📎")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to attach file: {str(e)}")
    
    def start_chat_refresh(self):
        """Start background thread to refresh chat"""
        if self.chat_refresh_thread is None or not self.chat_refresh_thread.is_alive():
            self.chat_refresh_thread = threading.Thread(target=self.refresh_chat_loop, daemon=True)
            self.chat_refresh_thread.start()
    
    def refresh_chat_loop(self):
        """Background loop to refresh chat every 2 seconds"""
        while self.refresh_chat:
            time.sleep(2)
            if self.current_chat_partner and self.refresh_chat:
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