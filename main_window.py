"""Main application window for the Weather App."""
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
from typing import Optional, Dict, List, Callable, Any, Tuple
from PIL import Image, ImageTk
import urllib.request
import io
import requests
from datetime import datetime
import logging
import threading

# Assuming config.py and weather_service.py are in the same directory or accessible via PYTHONPATH
from config import Config # Use .config if it's a package
from weather_service import WeatherService, WeatherServiceError # Use .weather_service if it's a package
from theme_manager import ColorPalette # Added import

logger = logging.getLogger(__name__)

# Thai Texts (Simplified for brevity, can be expanded from config.py or a dedicated i18n module)
TEXTS = {
    'th': {
        'app_title': 'แอพพยากรณ์อากาศ',
        'loading': 'กำลังโหลด...',
        'search_placeholder': 'กรอกชื่อเมือง...',
        'search': 'ค้นหา',
        'refresh': 'รีเฟรช',
        'settings': 'ตั้งค่า',
        'current_weather': 'สภาพอากาศปัจจุบัน',
        'forecast_5_day': 'พยากรณ์ 5 วัน',
        'feels_like': 'รู้สึกเหมือน:',
        'humidity': 'ความชื้น:',
        'wind': 'ความเร็วลม:',
        'pressure': 'ความกดอากาศ:',
        'visibility': 'ทัศนวิสัย:',
        'sunrise': 'พระอาทิตย์ขึ้น:',
        'sunset': 'พระอาทิตย์ตก:',
        'last_updated': 'อัปเดตล่าสุด:',
        'api_key_required_title': 'ต้องการ API Key',
        'api_key_required_message': 'กรุณาตั้งค่า OpenWeatherMap API Key ในการตั้งค่า',
        'error_title': 'เกิดข้อผิดพลาด',
        'default_city': 'Bangkok, TH',
        'theme_select_label': 'เลือกธีม:',
        'theme_light': 'สว่าง (Light)',
        'theme_dark': 'มืด (Dark)',
        'theme_auto': 'อัตโนมัติตามอุณหภูมิ (Auto)'
    },
    'en': {
        'app_title': 'Weather App',
        'loading': 'Loading...',
        'search_placeholder': 'Enter city name...',
        'search': 'Search',
        'refresh': 'Refresh',
        'settings': 'Settings',
        'current_weather': 'Current Weather',
        'forecast_5_day': '5-Day Forecast',
        'feels_like': 'Feels like:',
        'humidity': 'Humidity:',
        'wind': 'Wind Speed:',
        'pressure': 'Pressure:',
        'visibility': 'Visibility:',
        'sunrise': 'Sunrise:',
        'sunset': 'Sunset:',
        'last_updated': 'Last updated:',
        'api_key_required_title': 'API Key Required',
        'api_key_required_message': 'Please set your OpenWeatherMap API Key in Settings.',
        'error_title': 'Error',
        'default_city': 'Bangkok, TH',
        'theme_select_label': 'Theme:',
        'theme_light': 'Light',
        'theme_dark': 'Dark',
        'theme_auto': 'Auto by Temperature'
    }
}

class MainWindow(tk.Tk):
    """Main application window."""
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.texts = TEXTS.get(self.config.get_setting('language', 'th'), TEXTS['en'])
        self.weather_service: Optional[WeatherService] = None
        self.weather_icons: Dict[str, ImageTk.PhotoImage] = {}
        self.current_temperature: Optional[float] = None # Added for theme management
        self.current_weather_data: Optional[Dict] = None # Store current weather data
        self.forecast_data: Optional[List[Dict]] = None # Store forecast data

        self.title(self.texts['app_title'])
        self.geometry("450x750")
        self.minsize(400, 700)

        self.setup_styles()
        self.create_widgets()
        self.initialize_weather_service()

        if self.weather_service:
            initial_city = self.config.settings.get('last_location') or self.texts['default_city']
            self.fetch_weather_data(initial_city)
        else:
            self.show_api_key_prompt()

        # เพิ่ม pass เพื่อป้องกัน error expected indented block
        # และจัดระเบียบฟังก์ชันใหม่ให้เหมาะสม

    def apply_theme_and_refresh_ui(self, new_temperature: Optional[float] = None):
        """Applies the current theme and refreshes UI elements."""
        if new_temperature is not None:
            self.current_temperature = new_temperature
        
        self.setup_styles() # Re-apply styles with current_temperature

        # Re-configure existing widgets or recreate them if necessary
        # For now, let's assume setup_styles() handles most of it by reconfiguring the ttk.Style
        # We might need to explicitly update backgrounds of tk.Tk and some frames
        palette = self.config.get_current_palette(self.current_temperature)
        self.configure(background=palette.background)
        
        # Destroy and recreate widgets to ensure theme is fully applied
        # This is a more robust way for Tkinter to handle deep style changes
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets() # Recreate all widgets
        
        # After recreating widgets, if weather data exists, re-populate it
        if self.weather_service and self.weather_service.is_service_ready():
            if self.current_weather_data:
                self.current_weather_card.update_data(self.current_weather_data)
            if self.forecast_data:
                self.forecast_card.update_data(self.forecast_data)
            if self.status_var.get() != self.texts.get('loading', 'Loading...'): # Avoid overwriting loading message
                 last_loc = self.config.get_setting('last_location')
                 if last_loc:
                    self.update_status_bar(f"{self.texts.get('last_updated', 'Last updated:')} {datetime.now().strftime('%H:%M')} - {last_loc}")
                 else:
                    self.update_status_bar(self.texts.get('ready', 'Ready')) 
        else:
            self.show_api_key_prompt()

    def setup_styles(self):
        self.style = ttk.Style(self)
        palette: ColorPalette = self.config.get_current_palette(self.current_temperature)

        # --- Define Base Fonts ---
        try:
            base_font_family = "Segoe UI"
            tkfont.Font(family=base_font_family).actual()
        except tk.TclError:
            base_font_family = "Calibri"
        
        default_font = (base_font_family, 10)
        small_font = (base_font_family, 9)
        medium_font = (base_font_family, 11)
        large_font = (base_font_family, 16, "bold")
        xlarge_font = (base_font_family, 28, "bold")
        header_font = (base_font_family, 18, "bold")
        button_font = (base_font_family, 10, "bold")

        self.style.theme_use('clam')

        # --- General Styles ---
        self.configure(background=palette.background) # Set main window background
        self.style.configure(".", background=palette.background, foreground=palette.text, font=default_font)
        self.style.configure("TFrame", background=palette.background)
        self.style.configure("TLabel", background=palette.background, foreground=palette.text, font=default_font)
        self.style.configure("TButton", padding=(8, 5), font=button_font, relief=tk.FLAT, borderwidth=0)
        self.style.map("TButton",
            background=[('active', palette.accent), ('!disabled', palette.primary)],
            foreground=[('!disabled', palette.button_text)]
        )
        self.style.configure("TEntry", 
                             fieldbackground=palette.card_bg, 
                             foreground=palette.text, 
                             insertcolor=palette.text,
                             font=medium_font,
                             padding=5)
        self.style.map("TEntry", bordercolor=[('focus', palette.primary)])

        # --- Card Styles ---
        self.style.configure("Card.TFrame", 
                             background=palette.card_bg, 
                             relief=tk.SOLID, 
                             borderwidth=1,
                             padding=15)
        self.style.configure("Card.TLabel", background=palette.card_bg, foreground=palette.card_text, font=default_font)
        self.style.configure("Card.Title.TLabel", font=large_font, foreground=palette.primary, background=palette.card_bg)
        self.style.configure("Card.Large.TLabel", font=xlarge_font, foreground=palette.primary, background=palette.card_bg)
        self.style.configure("Card.Small.TLabel", font=small_font, foreground=palette.secondary, background=palette.card_bg)

        # --- Header Styles ---
        self.style.configure("Header.TFrame", background=palette.primary)
        self.style.configure("Header.TLabel", background=palette.primary, foreground=palette.button_text, font=header_font)
        self.style.configure("Header.TButton", 
                             font=(base_font_family, 9, "bold"), 
                             foreground=palette.primary, 
                             background=palette.card_bg, 
                             relief=tk.RAISED,
                             borderwidth=1,
                             padding=(5,3))
        self.style.map("Header.TButton",
            background=[('active', palette.accent), ('!disabled', palette.card_bg)],
            foreground=[('active', palette.button_text), ('!disabled', palette.primary)]
        )

        # --- Search Bar Styles ---
        self.style.configure("Search.TButton", 
                             font=button_font, 
                             padding=(10,5),
                             background=palette.accent, 
                             foreground=palette.button_text)
        self.style.map("Search.TButton",
            background=[('active', palette.primary)]
        )
        self.style.configure("Accent.TButton", # Keep Accent.TButton for other potential uses or specific buttons
                             font=button_font, 
                             padding=(10,5),
                             background=palette.accent, 
                             foreground=palette.button_text)
        self.style.map("Accent.TButton",
            background=[('active', palette.primary)]
        )

        # --- Status Bar Styles ---
        self.style.configure("Status.TLabel", 
                             background=palette.secondary, 
                             foreground=palette.text, 
                             font=small_font, 
                             padding=5)

        # --- Define Base Fonts ---
        try:
            # Attempt to use a more modern font if available
            base_font_family = "Segoe UI" 
            tkfont.Font(family=base_font_family).actual() # Check if font exists
        except tk.TclError:
            base_font_family = "Calibri" # Fallback font
        
        default_font = (base_font_family, 10)
        small_font = (base_font_family, 9)
        medium_font = (base_font_family, 11)
        large_font = (base_font_family, 16, "bold")
        xlarge_font = (base_font_family, 28, "bold")
        header_font = (base_font_family, 18, "bold")
        button_font = (base_font_family, 10, "bold")

        self.style.theme_use('clam') 

        # --- General Styles ---
        self.configure(background=palette.background) # Set main window background
        self.style.configure(".", background=palette.background, foreground=palette.text, font=default_font)
        self.style.configure("TFrame", background=palette.background)
        self.style.configure("TLabel", background=palette.background, foreground=palette.text, font=default_font)
        self.style.configure("TButton", padding=(8, 5), font=button_font, relief=tk.FLAT, borderwidth=0)
        self.style.map("TButton",
            background=[('active', palette.accent), ('!disabled', palette.primary)],
            foreground=[('!disabled', palette.button_text)] # Use button_text for foreground
        )
        self.style.configure("TEntry", 
                             fieldbackground=palette.card_bg, # Use card_bg for entry field
                             foreground=palette.text, 
                             insertcolor=palette.text, # Cursor color
                             font=medium_font,
                             padding=5)
        self.style.map("TEntry", bordercolor=[('focus', palette.primary)])


        # --- Card Styles ---
        self.style.configure("Card.TFrame", 
                             background=palette.card_bg, 
                             relief=tk.SOLID, 
                             borderwidth=1,
                             padding=15)
        self.style.configure("Card.TLabel", background=palette.card_bg, foreground=palette.card_text, font=default_font)
        self.style.configure("Card.Title.TLabel", font=large_font, foreground=palette.primary, background=palette.card_bg)
        self.style.configure("Card.Large.TLabel", font=xlarge_font, foreground=palette.primary, background=palette.card_bg) # For main temp
        self.style.configure("Card.Small.TLabel", font=small_font, foreground=palette.secondary, background=palette.card_bg) # For less important details

        # --- Header Styles ---
        self.style.configure("Header.TFrame", background=palette.primary)
        self.style.configure("Header.TLabel", background=palette.primary, foreground=palette.button_text, font=header_font) # Text on primary bg
        self.style.configure("Header.TButton", 
                             font=(base_font_family, 9, "bold"), 
                             foreground=palette.primary, # Text color for button
                             background=palette.card_bg, # Button background (e.g. white on dark blue header)
                             relief=tk.RAISED,
                             borderwidth=1,
                             padding=(5,3))
        self.style.map("Header.TButton",
            background=[('active', palette.accent), ('!disabled', palette.card_bg)],
            foreground=[('active', palette.button_text), ('!disabled', palette.primary)]
        )


        # --- Search Bar Styles ---
        # Make search button distinct
        self.style.configure("Search.TButton", 
                             font=button_font, 
                             padding=(10,5),
                             background=palette.accent, 
                             foreground=palette.button_text)
        self.style.map("Search.TButton",
            background=[('active', palette.primary)]
        )
        # Special style for the search button if needed, or use Accent.TButton
        self.style.configure("Accent.TButton", 
                             font=button_font, 
                             padding=(10,5),
                             background=palette.accent, 
                             foreground=palette.button_text)
        self.style.map("Accent.TButton",
            background=[('active', palette.primary)]
        )

        # --- Status Bar Styles ---
        self.style.configure("Status.TLabel", 
                             background=palette.secondary, 
                             foreground=palette.text, # Text on secondary bg
                             font=small_font, 
                             padding=5)


    def create_widgets(self):
        """Create all UI widgets for the main window."""
        # Header
        header_frame = ttk.Frame(self, style="Header.TFrame", padding=(10,5))
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text=self.texts['app_title'], style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Button(header_frame, text=self.texts['settings'], command=self.open_settings_dialog, width=8).pack(side=tk.RIGHT, padx=5)
        ttk.Button(header_frame, text=self.texts['refresh'], command=self.refresh_weather, width=8).pack(side=tk.RIGHT)

        # Search Bar
        search_frame = ttk.Frame(self, padding=(10, 5))
        search_frame.pack(fill=tk.X)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=("Helvetica", 12))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.search_entry.bind("<Return>", lambda event: self.search_city())
        self.search_button = ttk.Button(search_frame, text=self.texts['search'], command=self.search_city, style="Search.TButton") # Changed to Search.TButton for consistency
        self.search_button.pack(side=tk.LEFT)

        # Main content area (for weather cards)
        self.content_frame = ttk.Frame(self, padding=(10,0))
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=3)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def initialize_weather_service(self):
        """Initialize the WeatherService with API key from config."""
        api_key = self.config.get_api_key()
        if api_key:
            self.weather_service = WeatherService(api_key, self.config.settings['units'])
            logger.info("Weather service initialized.")
        else:
            logger.warning("API Key not found. Weather service not initialized.")
            self.weather_service = None

    def show_api_key_prompt(self):
        """Inform user that API key is needed and open settings."""
        messagebox.showwarning(
            self.texts.get('api_key_required_title', 'API Key Required'),
            self.texts.get('api_key_required_message', 'Please set your OpenWeatherMap API Key in Settings.')
        )
        self.open_settings_dialog()

    def fetch_weather_data(self, city: str):
        """Fetch and display weather data for the given city."""
        if not self.weather_service:
            self.show_api_key_prompt()
            return

        self.show_loading_indicator(True)
        self.status_var.set(f"{self.texts['loading']} {city}...")
        
        # Use threading to avoid freezing the UI
        threading.Thread(target=self._fetch_weather_thread, args=(city,), daemon=True).start()

    def _fetch_weather_thread(self, city: str):
        try:
            current_weather_data = self.weather_service.get_current_weather(city)
            parsed_current = self.weather_service.parse_weather_data(current_weather_data)
            
            forecast_data = self.weather_service.get_forecast(city)
            parsed_forecast = self.weather_service.parse_forecast_data(forecast_data)

            self.config.settings['last_location'] = city
            self.config.save_settings()
            
            # Schedule UI updates on the main thread
            self.after(0, self.update_ui_with_weather_data, parsed_current, parsed_forecast, city)
        except WeatherServiceError as e:
            logger.error(f"WeatherServiceError for {city}: {e}")
            self.after(0, self.show_error_message, str(e))
        except Exception as e:
            logger.exception(f"Unexpected error fetching weather for {city}: {e}")
            self.after(0, self.show_error_message, f"An unexpected error occurred: {e}")
        finally:
            self.after(0, self.show_loading_indicator, False)

    def update_ui_with_weather_data(self, current_data: Dict, forecast_list: List[Dict], city: str):
        """Update the UI with fetched weather data. Must be called from main thread."""
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Display current weather
        current_weather_card = CurrentWeatherCard(self.content_frame, self.texts, self.config, self.weather_icons, self.weather_service)
        current_weather_card.pack(fill=tk.X, pady=(0, 10))
        current_weather_card.update_data(current_data)

        # Display forecast
        forecast_card = ForecastCard(self.content_frame, self.texts, self.config, self.weather_icons, self.weather_service)
        forecast_card.pack(fill=tk.BOTH, expand=True)
        forecast_card.update_data(forecast_list)

        self.status_var.set(f"Weather for {city} loaded.")
        self.search_var.set(city) # Update search entry with the successfully fetched city name

    def show_loading_indicator(self, show: bool):
        """Show or hide a loading indicator."""
        if show:
            if not hasattr(self, '_loading_frame') or not self._loading_frame.winfo_exists():
                self._loading_frame = ttk.Frame(self.content_frame, style="Card.TFrame")
                self._loading_frame.place(relx=0.5, rely=0.4, anchor=tk.CENTER) # Centered
                ttk.Label(self._loading_frame, text=self.texts['loading'], font=("Helvetica", 14), style="Card.TLabel").pack(pady=10)
                progress = ttk.Progressbar(self._loading_frame, mode='indeterminate', length=200)
                progress.pack(pady=10, padx=20)
                progress.start(10)
        else:
            if hasattr(self, '_loading_frame') and self._loading_frame.winfo_exists():
                self._loading_frame.destroy()

    def show_error_message(self, message: str):
        """Display an error message to the user."""
        messagebox.showerror(self.texts['error_title'], message)
        self.status_var.set(f"{self.texts['error_title']}: {message[:50]}...")
        # Optionally, clear the content frame or show a specific error UI
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        error_label = ttk.Label(self.content_frame, text=f"{self.texts['error_title']}\n{message}", style="Title.TLabel", foreground="red", wraplength=380, justify=tk.CENTER)
        error_label.pack(pady=50, padx=20, fill=tk.BOTH, expand=True)

    def update_status_bar(self, message: str):
        """Update the status bar text."""
        if hasattr(self, 'status_var') and self.status_var:
            self.status_var.set(message)
        else:
            logger.warning("status_var not initialized when trying to update status bar.")

    def search_city(self):
        """Handle city search initiated by user."""
        city = self.search_var.get().strip()
        if city:
            self.fetch_weather_data(city)
        else:
            messagebox.showwarning("Input Error", "Please enter a city name.")

    def refresh_weather(self):
        """Refresh weather for the last searched city."""
        last_city = self.config.settings.get('last_location')
        if last_city:
            self.fetch_weather_data(last_city)
        else:
            # If no last city, try default or prompt
            self.fetch_weather_data(self.texts['default_city'])

    def open_settings_dialog(self):
        """Open the settings dialog window."""
        SettingsDialog(self, title=self.texts['settings'], config_instance=self.config, texts=self.texts, on_close_callback=self.on_settings_closed)

    def on_settings_closed(self):
        """Callback after settings dialog is closed."""
        logger.info("Settings dialog closed. Re-initializing service and refreshing UI.")
        # Re-initialize weather service as API key or units might have changed
        self.initialize_weather_service()
        # Update texts if language changed
        new_lang = self.config.settings.get('language', 'th')
        if new_lang != self.texts.get('lang_code', 'th'): # Add 'lang_code' to your TEXTS dicts
            self.texts = TEXTS.get(new_lang, TEXTS['en'])
            # Recreate UI elements that depend on texts if necessary, or update them
            # For simplicity, a full refresh might be easier if language changes often
            # This might require destroying and recreating parts of the UI.
            # For now, just log and refresh weather which might update some labels.
            logger.info(f"Language changed to {new_lang}. UI text update might be partial.")
        
        self.refresh_weather() # Refresh weather data with new settings


class CurrentWeatherCard(ttk.Frame):
    """Card to display current weather information."""
    def __init__(self, parent, texts: Dict, config: Config, weather_icons: Dict, weather_service: WeatherService): # Added weather_service
        super().__init__(parent, style="Card.TFrame")
        self.texts = texts
        self.config = config
        self.weather_icons = weather_icons
        self.weather_service = weather_service # Store weather_service
        self._create_widgets()

    def _create_widgets(self):
        # Location and Time
        self.location_label = ttk.Label(self, text="--", style="Card.Title.TLabel")
        self.location_label.pack(pady=(5,0))
        self.time_label = ttk.Label(self, text="--", style="Small.TLabel")
        self.time_label.pack()

        # Main weather info (Icon, Temp, Description)
        main_info_frame = ttk.Frame(self, style="Card.TFrame")
        main_info_frame.pack(pady=10)
        self.icon_label = ttk.Label(main_info_frame, style="Card.TLabel") # Placeholder for icon
        self.icon_label.pack(side=tk.LEFT, padx=10)
        self.temp_label = ttk.Label(main_info_frame, text="--°", style="Large.TLabel")
        self.temp_label.pack(side=tk.LEFT, padx=10)
        self.desc_label = ttk.Label(main_info_frame, text="--", style="Title.TLabel", wraplength=150)
        self.desc_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Details Grid
        details_frame = ttk.Frame(self, style="Card.TFrame")
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        details_map = [
            (self.texts['feels_like'], '_feels_like_var'), (self.texts['humidity'], '_humidity_var'),
            (self.texts['wind'], '_wind_var'), (self.texts['pressure'], '_pressure_var'),
            (self.texts['visibility'], '_visibility_var'), (self.texts['sunrise'], '_sunrise_var'),
            (self.texts['sunset'], '_sunset_var'), (self.texts['last_updated'], '_last_updated_var')
        ]
        for i, (text, var_name) in enumerate(details_map):
            setattr(self, var_name, tk.StringVar(value="--"))
            ttk.Label(details_frame, text=text, style="Small.TLabel").grid(row=i//2, column=(i%2)*2, sticky=tk.W, padx=5, pady=2)
            ttk.Label(details_frame, textvariable=getattr(self, var_name), style="Small.TLabel", font=("Helvetica", 9, "bold")).grid(row=i//2, column=(i%2)*2 + 1, sticky=tk.W, padx=5, pady=2)

    def update_data(self, data: Dict):
        units = self.config.settings['units']
        temp_unit = "°C" if units == 'metric' else "°F"
        speed_unit = "m/s" if units == 'metric' else "mph"

        self.location_label.config(text=f"{data.get('city', 'N/A')}, {data.get('country', 'N/A')}")
        self.time_label.config(text=data.get('dt', datetime.now()).strftime("%A, %d %B %Y, %H:%M"))
        self.temp_label.config(text=f"{data.get('temp', '--'):.1f}{temp_unit}")
        self.desc_label.config(text=data.get('description', '--').title())
        
        self._feels_like_var.set(f"{data.get('feels_like', '--'):.1f}{temp_unit}")
        self._humidity_var.set(f"{data.get('humidity', '--')}%" )
        self._wind_var.set(f"{data.get('wind_speed', '--')} {speed_unit}")
        self._pressure_var.set(f"{data.get('pressure', '--')} hPa")
        self._visibility_var.set(f"{data.get('visibility', '--')} km")
        self._sunrise_var.set(data.get('sunrise', datetime.now()).strftime("%H:%M"))
        self._sunset_var.set(data.get('sunset', datetime.now()).strftime("%H:%M"))
        self._last_updated_var.set(data.get('dt', datetime.now()).strftime("%H:%M:%S"))

        self._load_icon(data.get('icon', '01d'))

    def _load_icon(self, icon_code: str):
        if icon_code in self.weather_icons:
            self.icon_label.config(image=self.weather_icons[icon_code])
            return
        
        def _fetch_and_set_icon():
            try:
                icon_url = self.weather_service.get_weather_icon_url(icon_code)
                with urllib.request.urlopen(icon_url) as response:
                    image_data = response.read()
                image = Image.open(io.BytesIO(image_data)).resize((64, 64), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.weather_icons[icon_code] = photo
                self.icon_label.config(image=photo)
            except Exception as e:
                logger.error(f"Failed to load icon {icon_code}: {e}")
                self.icon_label.config(text="IMG") # Fallback text

        threading.Thread(target=_fetch_and_set_icon, daemon=True).start()

class ForecastCard(ttk.Frame):
    """Card to display 5-day weather forecast."""
    def __init__(self, parent, texts: Dict, config: Config, weather_icons: Dict, weather_service: WeatherService): # Added weather_service
        super().__init__(parent, style="Card.TFrame")
        self.texts = texts
        self.config = config
        self.weather_icons = weather_icons
        self.weather_service = weather_service # Store weather_service
        self.forecast_item_frames: List[ttk.Frame] = []
        self._create_widgets()

    def _create_widgets(self):
        ttk.Label(self, text=self.texts['forecast_5_day'], style="Card.Title.TLabel").pack(pady=5)
        self.scrollable_frame = ttk.Frame(self, style="Card.TFrame") # Frame for scrollbar content
        self.scrollable_frame.pack(fill=tk.BOTH, expand=True)

    def update_data(self, forecast_list: List[Dict]):
        for widget in self.scrollable_frame.winfo_children(): # Clear old forecast items
            widget.destroy()
        self.forecast_item_frames.clear()

        # Group forecast by day, taking the noon forecast or first available for the day's icon/temp_max/min
        daily_forecasts = {}
        for item in forecast_list:
            day_str = item['dt'].strftime("%Y-%m-%d")
            if day_str not in daily_forecasts:
                daily_forecasts[day_str] = {'temps': [], 'icons': [], 'descs': [], 'dt': item['dt']}
            daily_forecasts[day_str]['temps'].append(item['temp'])
            daily_forecasts[day_str]['icons'].append(item['icon'])
            daily_forecasts[day_str]['descs'].append(item['description'])

        day_count = 0
        for day_str, data in daily_forecasts.items():
            if day_count >= 5: break
            
            day_frame = ttk.Frame(self.scrollable_frame, style="Card.TFrame", padding=5)
            day_frame.pack(fill=tk.X, pady=2)
            self.forecast_item_frames.append(day_frame)

            dt_obj = data['dt']
            day_name = dt_obj.strftime("%a") # Short day name (e.g., Mon)
            date_info = dt_obj.strftime("%d %b") # Date (e.g., 23 Jul)

            temp_min = min(data['temps'])
            temp_max = max(data['temps'])
            # Choose icon: most frequent or from noon if available
            icon_code = max(set(data['icons']), key=data['icons'].count) if data['icons'] else '01d'
            # desc = max(set(data['descs']), key=data['descs'].count) if data['descs'] else 'N/A'

            ttk.Label(day_frame, text=f"{day_name}\n{date_info}", style="Small.TLabel", justify=tk.LEFT).pack(side=tk.LEFT, padx=5, anchor='n')
            
            icon_label = ttk.Label(day_frame, style="Card.TLabel")
            icon_label.pack(side=tk.LEFT, padx=5)
            self._load_forecast_icon(icon_label, icon_code)

            temp_text = f"{temp_max:.0f}° / {temp_min:.0f}°"
            ttk.Label(day_frame, text=temp_text, style="Small.TLabel", font=("Helvetica", 10, "bold")).pack(side=tk.RIGHT, padx=10)
            day_count += 1

    def _load_forecast_icon(self, label: ttk.Label, icon_code: str):
        if icon_code in self.weather_icons:
            label.config(image=self.weather_icons[icon_code])
            return

        def _fetch_and_set_icon(): # Similar to CurrentWeatherCard's icon loading
            try:
                icon_url = self.weather_service.get_weather_icon_url(icon_code)
                with urllib.request.urlopen(icon_url) as response:
                    image_data = response.read()
                # Smaller icons for forecast
                image = Image.open(io.BytesIO(image_data)).resize((40, 40), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                # Store potentially smaller icons separately if needed, or resize on demand
                # For simplicity, using the main weather_icons dict, ensure keys are unique if sizes differ significantly
                self.weather_icons[icon_code + "_small"] = photo # Store with a different key if size matters
                label.config(image=photo)
            except Exception as e:
                logger.error(f"Failed to load forecast icon {icon_code}: {e}")
                label.config(text="-") # Fallback text
        
        threading.Thread(target=_fetch_and_set_icon, daemon=True).start()

class SettingsDialog(tk.Toplevel):
    """Dialog for application settings."""
    def __init__(self, parent, title: str, config_instance: Config, texts: Dict, on_close_callback: Callable):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.parent_window = parent # Store parent reference
        self.config = config_instance
        self.texts = texts
        self.on_close_callback = on_close_callback
        self.grab_set() # Modal
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.geometry("400x420") # Increased height for theme options
        self.resizable(False, False)

        # Center dialog
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        dialog_width = self.winfo_reqwidth()
        dialog_height = self.winfo_reqheight()
        position_x = parent_x + (parent_width // 2) - (dialog_width // 2)
        position_y = parent_y + (parent_height // 2) - (dialog_height // 2)
        self.geometry(f"+{position_x}+{position_y}")

        self._create_widgets()
        self.wait_window(self)

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # API Key
        ttk.Label(main_frame, text="OpenWeatherMap API Key:", font=("Helvetica", 10, "bold")).pack(anchor=tk.W)
        self.api_key_var = tk.StringVar(value=self.config.get_api_key())
        ttk.Entry(main_frame, textvariable=self.api_key_var, width=50).pack(fill=tk.X, pady=(0,10))

        # Units
        ttk.Label(main_frame, text="Units:", font=("Helvetica", 10, "bold")).pack(anchor=tk.W)
        self.units_var = tk.StringVar(value=self.config.settings.get('units', 'metric'))
        units_frame = ttk.Frame(main_frame)
        units_frame.pack(fill=tk.X, pady=(0,10))
        ttk.Radiobutton(units_frame, text="Celsius (°C, m/s)", variable=self.units_var, value='metric').pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(units_frame, text="Fahrenheit (°F, mph)", variable=self.units_var, value='imperial').pack(side=tk.LEFT, padx=5)

        # Language
        ttk.Label(main_frame, text="Language:", font=("Helvetica", 10, "bold")).pack(anchor=tk.W)
        self.lang_var = tk.StringVar(value=self.config.settings.get('language', 'th'))
        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(fill=tk.X, pady=(0,10))
        ttk.Radiobutton(lang_frame, text="ไทย (Thai)", variable=self.lang_var, value='th').pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(lang_frame, text="English", variable=self.lang_var, value='en').pack(side=tk.LEFT, padx=5)

        # Theme Mode
        ttk.Label(main_frame, text=self.texts.get('theme_select_label', "Theme:"), font=("Helvetica", 10, "bold")).pack(anchor=tk.W, pady=(10,0))
        
        self.theme_options_display_th = {
            self.texts.get('theme_light', "สว่าง (Light)"): "light",
            self.texts.get('theme_dark', "มืด (Dark)"): "dark",
            self.texts.get('theme_auto', "อัตโนมัติตามอุณหภูมิ (Auto)"): "auto_temp"
        }
        self.theme_value_to_display_map = {v: k for k, v in self.theme_options_display_th.items()}
        
        current_theme_mode = self.config.settings.get('theme_mode', 'light')
        current_display_theme = self.theme_value_to_display_map.get(current_theme_mode, list(self.theme_options_display_th.keys())[0])
        
        self.theme_mode_var = tk.StringVar(value=current_display_theme)
        theme_combobox = ttk.Combobox(main_frame, textvariable=self.theme_mode_var, 
                                      values=list(self.theme_options_display_th.keys()), 
                                      state='readonly', width=47)
        theme_combobox.pack(fill=tk.X, pady=(0,10))

        # Save and Cancel buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20,0))
        ttk.Button(button_frame, text="Save", command=self._save_settings, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._on_close).pack(side=tk.RIGHT)

    def _save_settings(self):
        self.config.set_api_key(self.api_key_var.get().strip())
        self.config.settings['units'] = self.units_var.get()
        self.config.settings['language'] = self.lang_var.get()

        # Save theme mode
        selected_display_theme = self.theme_mode_var.get()
        new_theme_mode = self.theme_options_display_th.get(selected_display_theme, 'light') # Default to light if not found
        self.config.settings['theme_mode'] = new_theme_mode

        self.config.save_settings()
        logger.info("Settings saved.")

        # Apply theme and refresh UI if theme or language changed
        # We assume parent_window is MainWindow and has apply_theme_and_refresh_ui
        if hasattr(self.parent_window, 'apply_theme_and_refresh_ui'):
            self.parent_window.apply_theme_and_refresh_ui()
            logger.info("Theme and UI refreshed after settings change.")
        
        self._on_close()

    def _on_close(self):
        self.destroy()
        if self.on_close_callback:
            self.on_close_callback()

# This file (main_window.py) now primarily defines UI classes.
# The actual application startup (if __name__ == "__main__") should be in weather_gui.py or app.py.
