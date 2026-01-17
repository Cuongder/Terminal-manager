
import customtkinter as ctk

def test_focus():
    app = ctk.CTk()
    try:
        dialog = ctk.CTkInputDialog(text="T", title="T")
        if hasattr(dialog, 'focus_force'):
            print("SUCCESS: dialog has 'focus_force'")
        else:
            print("ERROR: dialog has NO 'focus_force'")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_focus()
