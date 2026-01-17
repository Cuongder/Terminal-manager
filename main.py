#!/usr/bin/env python3
"""Terminal Manager - Entry point."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import TerminalManagerApp


def main():
    """Run the application."""
    app = TerminalManagerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
