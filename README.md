# 🚀 Cacasians Chat Application

A modern, feature-rich chat application built with Python and Tkinter, featuring real-time messaging, file sharing, and a beautiful gradient UI.

## ✨ Features

### 🔐 Authentication
- **User Registration**: Create new accounts with username, email, and password
- **Secure Login**: Password hashing with SHA-256 encryption
- **Input Validation**: Comprehensive form validation and error handling

### 💬 Real-time Chat
- **Live Messaging**: Real-time chat conversations with automatic refresh
- **User Selection**: Browse and select from active users
- **Message History**: Complete chat history storage and retrieval
- **Search Users**: Quick search functionality to find users

### 📝 Message Management
- **Edit Messages**: Right-click to edit your sent messages
- **Delete Messages**: Remove messages with confirmation dialog
- **Message Status**: Visual indicators for edited messages
- **Timestamps**: All messages include time stamps

### 📎 File Sharing
- **Multi-format Support**: Share images, videos, and documents
- **File Types Supported**:
  - Images: PNG, JPG, JPEG, GIF, BMP
  - Videos: MP4, AVI, MOV, WMV
  - Documents: PDF, DOC, DOCX, TXT
- **Secure Storage**: Files are safely stored in attachments directory
- **Visual Indicators**: Different icons for different file types

### 🎨 Modern UI Design
- **Gradient Backgrounds**: Beautiful color gradients throughout the app
- **Smooth Animations**: Hover effects and button animations
- **Emoji Integration**: Emojis and icons for enhanced visual appeal
- **Responsive Design**: Adaptive layout that works on different screen sizes
- **Dark Theme**: Modern dark theme with accent colors

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Install Additional Dependencies for Executable
```bash
pip install cx_Freeze
```

### Step 3: Run the Application
```bash
python enhanced_main.py
```

## 📦 Creating Executable File

To create a standalone .exe file:

```bash
python setup.py build
```

The executable will be created in the `build` directory.

## 🚀 Quick Start Guide

### First Time Setup
1. Run the application
2. Click "✨ Register" to create a new account
3. Fill in your details (username, email, password)
4. Click "🎉 Create Account"

### Using the Chat
1. Login with your credentials
2. Select a user from the "👥 Active Users" list
3. Start typing in the message box
4. Press Enter or click "🚀 Send" to send messages
5. Use the "📎" button to attach files

### Message Management
- **Edit**: Right-click on your messages and select "✏️ Edit Message"
- **Delete**: Right-click on your messages and select "🗑️ Delete Message"

## 📁 Project Structure

```
Cacasians Chat Application/
├── main.py                 # Basic version of the chat app
├── enhanced_main.py        # Enhanced version with better UI
├── setup.py               # Script to build executable
├── requirements.txt       # Python dependencies
├── chat_app.db           # SQLite database (created automatically)
├── attachments/          # Directory for file attachments (created automatically)
└── README.md             # This file
```

## 🗄️ Database Schema

### Users Table
- `id`: Primary key (auto-increment)
- `username`: Unique username
- `password`: Hashed password (SHA-256)
- `email`: User email address
- `created_at`: Account creation timestamp

### Messages Table
- `id`: Primary key (auto-increment)
- `sender_id`: Foreign key to users table
- `receiver_id`: Foreign key to users table
- `message`: Message content
- `file_path`: Path to attached file (if any)
- `file_type`: Type of attached file
- `timestamp`: Message timestamp
- `edited`: Boolean flag for edited messages
- `deleted`: Boolean flag for deleted messages

## 🎯 Key Features Explained

### Real-time Chat Refresh
The application uses a background thread that refreshes the chat every 2 seconds, ensuring you see new messages as they arrive.

### Secure File Handling
All uploaded files are:
- Copied to a secure attachments directory
- Renamed with timestamps to prevent conflicts
- Stored with original filename information

### Message Context Menus
Right-click on your own messages to access:
- Edit functionality (text messages only)
- Delete functionality (all message types)

### User Search
Use the search box in the users panel to quickly find specific users by typing their username.

## 🔧 Customization

### Changing Colors
The application uses a consistent color scheme:
- Primary Background: `#1a1a2e`
- Secondary Background: `#16213e`
- Accent Background: `#0f3460`
- Accent Color: `#e94560`
- Text Color: `#ffffff`

### Adding New Features
The modular design makes it easy to add new features:
- Database operations are centralized in the `init_database()` method
- UI components are separated into different methods
- File handling is abstracted for easy extension

## 🐛 Troubleshooting

### Common Issues

**Database Errors**
- Ensure the application has write permissions in the directory
- Check if `chat_app.db` file is not corrupted

**File Attachment Issues**
- Verify the `attachments` directory exists and is writable
- Check file permissions for uploaded files

**UI Display Problems**
- Ensure all required fonts are available on the system
- Check screen resolution compatibility

### Performance Tips
- The application is optimized for up to 100 concurrent users
- Large file attachments (>50MB) may slow down the interface
- Chat history is loaded entirely - consider pagination for very long conversations

## 🔒 Security Features

- **Password Hashing**: All passwords are hashed using SHA-256
- **SQL Injection Protection**: Parameterized queries prevent SQL injection
- **File Upload Security**: File types are validated and stored securely
- **Session Management**: Proper user session handling

## 🚀 Future Enhancements

Potential features for future versions:
- Group chat functionality
- Voice and video calling
- Message encryption
- Online status indicators
- Push notifications
- Mobile app version
- Cloud synchronization

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📞 Support

For support or questions, please create an issue in the project repository.

---

**Enjoy chatting with Cacasians Chat! 🎉**