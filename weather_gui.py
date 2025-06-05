import tkinter as tk
import logging
from dotenv import load_dotenv

# Import the new main window and configuration classes
from main_window import MainWindow
from config import Config # Ensure config.py is in the same directory or accessible

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("weather_app.log"),
        logging.StreamHandler() # Also print to console
    ]
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Load environment variables (e.g., for API key if stored in .env initially)
    # The Config class now handles API key storage primarily via config.json,
    # but .env can be a fallback or initial source.
    load_dotenv()

    logger.info("Starting Weather App...")
    
    # Create the main application window using the new MainWindow class
    app = MainWindow()
    
    # Start the Tkinter event loop
    app.mainloop()
    
    logger.info("Weather App closed.")

