import threading
import socket
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox

# --- Connection Parameters ---
host = '127.0.0.1'
port = 1234
address = (host, port)

# Initialize TCP Socket and connect to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(address)

# --- GUI Setup ---
root = tk.Tk()
root.title("Chat Client")

# Prompt for the nickname immediately upon startup
# parent=root ensures the dialog stays on top of the main window
name = simpledialog.askstring("Name", "Enter your client name:", parent=root)

# Display the chosen name as a header label
name_label = tk.Label(root, text=f"Name: {name}", font=("Arial", 14, "bold"))
name_label.pack(pady=(10, 0))

# ScrolledText widget: Provides a scrollable area for chat history
# wrap=tk.WORD ensures words aren't cut off at the edge
chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', width=50, height=20)
chat_area.pack(padx=10, pady=10)

# Entry widget: The input field where the user types their messages
msg_entry = tk.Entry(root, width=40)
msg_entry.pack(side=tk.LEFT, padx=(10, 0), pady=(0, 10))
msg_entry.focus() # Place the cursor in the input field automatically

def send_message():
    """Extracts text from the entry field and sends it to the server."""
    message = msg_entry.get()
    if message:
        # Check if the user is using the 'private:' command
        if message.startswith("private:"):
            client.send(message.encode('ascii'))
        else:
            # Format message with sender's name for public broadcast
            client.send(f"{name}: {message}".encode('ascii'))
        
        # Clear the input box after sending
        msg_entry.delete(0, tk.END)

# Send Button: Triggers the send_message function when clicked
send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(side=tk.LEFT, padx=10, pady=(0, 10))

def receive():
    """
    Continuous loop running in a separate thread.
    Handles incoming data without blocking the GUI responsiveness.
    """
    while True:
        try:
            # Receive data from server (max 1024 bytes)
            message = client.recv(1024).decode('ascii')
            
            # Protocol check: If server asks for identity, send the nickname
            if message == 'NAME':
                client.send(name.encode('ascii'))
            else:
                # Update the UI: Enable editing, insert message, scroll down, then disable
                chat_area.config(state='normal')
                chat_area.insert(tk.END, message + '\n')
                chat_area.yview(tk.END) # Auto-scroll to the newest message
                chat_area.config(state='disabled')
        except Exception as e:
            # If server connection is lost or an error occurs
            messagebox.showerror("Error", f"An error occurred: {e}")
            client.close()
            break

# --- Threading Management ---
# We use a thread so that 'client.recv' doesn't stop the window from responding
receive_thread = threading.Thread(target=receive)
# daemon=True ensures the thread terminates when the GUI window is closed
receive_thread.daemon = True 
receive_thread.start()

def enter_pressed(event):
    """Event handler for the <Return> key to allow sending messages faster."""
    send_message()

# Binding the Enter key to the entry field
msg_entry.bind('<Return>', enter_pressed)

# Start the Tkinter event loop (renders the window and handles clicks)
root.mainloop()