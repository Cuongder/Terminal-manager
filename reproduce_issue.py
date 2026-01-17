
import customtkinter as ctk
import sys

def test_dialog():
    app = ctk.CTk()
    
    print("Creating dialog...")
    try:
        dialog = ctk.CTkInputDialog(
            text="Test Input:",
            title="Test"
        )
        
        # This is the suspicious line
        print("Attempting to call .after() on dialog...")
        dialog.after(100, lambda: print("Focus force called"))
        # dialog.focus_force() # This might also be what they meant
        
        print("Calling get_input()...")
        # We need to simulate user input or close detection if possible, 
        # but get_input blocks. 
        # For reproduction, we just want to see if .after accesses crash causing a popup error 
        # (which might be a python error dialog or crash).
        
        # Since we can't interact, we might just check attributes
        if not hasattr(dialog, 'after'):
             print("ERROR: dialog has no attribute 'after'")
        else:
             print("SUCCESS: dialog has 'after'")

        # We won't actually call get_input() because it blocks forever in this headless-ish env
        # dialog.get_input() 
        
    except Exception as e:
        print(f"CAUGHT EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

    # app.destroy() # Might need to run update to process events
    # app.update()

if __name__ == "__main__":
    try:
        test_dialog()
    except Exception as e:
        print(f"Main crashed: {e}")
