import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import threading

URL = "https://pymeet-i66s.vercel.app"

def launch_app():
    # Attempt to open Chrome in app mode
    try:
        # Chrome path for windows
        subprocess.Popen([r"C:\Program Files\Google\Chrome\Application\chrome.exe", f"--app={URL}"])
    except:
        try:
            subprocess.Popen([r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", f"--app={URL}"])
        except:
            # Fallback to default browser
            import webbrowser
            webbrowser.open(URL)

def update_app_task(btn):
    try:
        btn.config(text="Updating...", state=tk.DISABLED)
        # Using git to push changes which will trigger Vercel deployment
        subprocess.run(["git", "add", "."], check=False, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(["git", "commit", "-m", "App Update via Manager"], check=False, creationflags=subprocess.CREATE_NO_WINDOW)
        result = subprocess.run(["git", "push"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        if result.returncode == 0 or "Everything up-to-date" in result.stderr:
            messagebox.showinfo("Success", "Changes have been pushed to Vercel!\nYour live site will update in a few moments.")
        else:
            # If git fails, try using vercel cli as fallback
            try:
                subprocess.run(["vercel", "--prod", "--yes"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                messagebox.showinfo("Success", "Changes deployed via Vercel CLI!\nYour live site will update in a few moments.")
            except:
                messagebox.showerror("Update Failed", "Could not push changes via Git or Vercel CLI. Make sure they are installed.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
    finally:
        btn.config(text="🔄 Update App", state=tk.NORMAL)

def update_app(btn):
    threading.Thread(target=update_app_task, args=(btn,)).start()

def uninstall_app():
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
    shortcut = os.path.join(desktop, "PyMeet.lnk")
    if os.path.exists(shortcut):
        try:
            os.remove(shortcut)
            messagebox.showinfo("Uninstalled", "Desktop shortcut removed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not remove shortcut: {e}")
    else:
        messagebox.showinfo("Info", "Shortcut not found on Desktop.")

def create_gui():
    root = tk.Tk()
    root.title("PyMeet Manager")
    root.geometry("350x250")
    root.configure(bg="#1e1e1e")
    root.eval('tk::PlaceWindow . center')
    
    tk.Label(root, text="PyMeet App", font=("Helvetica", 16, "bold"), bg="#1e1e1e", fg="white").pack(pady=(20,5))
    tk.Label(root, text="Developed by Nishant Panwar", font=("Helvetica", 9), bg="#1e1e1e", fg="#aaaaaa").pack(pady=(0,20))

    btn_launch = tk.Button(root, text="🚀 Launch PyMeet", font=("Helvetica", 11), bg="#4caf50", fg="white", borderwidth=0, cursor="hand2", command=launch_app)
    btn_launch.pack(fill=tk.X, padx=40, pady=5, ipady=5)

    btn_update = tk.Button(root, text="🔄 Update App", font=("Helvetica", 11), bg="#2196f3", fg="white", borderwidth=0, cursor="hand2")
    btn_update.config(command=lambda: update_app(btn_update))
    btn_update.pack(fill=tk.X, padx=40, pady=5, ipady=5)

    btn_uninstall = tk.Button(root, text="🗑️ Uninstall Shortcut", font=("Helvetica", 11), bg="#f44336", fg="white", borderwidth=0, cursor="hand2", command=uninstall_app)
    btn_uninstall.pack(fill=tk.X, padx=40, pady=5, ipady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
