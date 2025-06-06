class WeatherApp {
    constructor() {
        this.currentWeather = null;
        this.forecastData = [];
        this.isLoading = false;
        this.notificationTimeout = null;
        this.searchHistory = [];
        this.MAX_HISTORY_ITEMS = 5;
        this.LOADING_TIMEOUT = 15000; // 15 วินาที

        this.THAI_MONTHS = [
            'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
            'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม'
        ];

        this.WEATHER_ICONS_FA = {
            '01d': 'fas fa-sun', // clear sky day
            '01n': 'fas fa-moon', // clear sky night
            '02d': 'fas fa-cloud-sun', // few clouds day
            '02n': 'fas fa-cloud-moon', // few clouds night
            '03d': 'fas fa-cloud', // scattered clouds day
            '03n': 'fas fa-cloud', // scattered clouds night
            '04d': 'fas fa-cloud-meatball', // broken clouds day (using a similar one)
            '04n': 'fas fa-cloud-meatball', // broken clouds night
            '09d': 'fas fa-cloud-showers-heavy', // shower rain day
            '09n': 'fas fa-cloud-showers-heavy', // shower rain night
            '10d': 'fas fa-cloud-sun-rain', // rain day
            '10n': 'fas fa-cloud-moon-rain', // rain night
            '11d': 'fas fa-bolt', // thunderstorm day
            '11n': 'fas fa-bolt', // thunderstorm night
            '13d': 'fas fa-snowflake', // snow day
            '13n': 'fas fa-snowflake', // snow night
            '50d': 'fas fa-smog', // mist day
            '50n': 'fas fa-smog', // mist night
            'default': 'fas fa-question-circle' // Default icon
        };

        this.initApp();
    }

    initApp() {
        this.loadSearchHistory();

        const searchForm = document.getElementById('searchForm');
        if (searchForm) {
            searchForm.addEventListener('submit', (event) => this.handleSearch(event));
        }

        const locationBtn = document.getElementById('locationBtn');
        if (locationBtn) {
            locationBtn.addEventListener('click', () => this.searchByLocation());
        }
        // Initial call to update UI, maybe with a default city or last search
        // For now, it will show the placeholder for forecast
        this.updateForecast([]); 
    }

    async searchByLocation() {
        if (this.isLoading) return;

        try {
            if (!navigator.geolocation) {
                throw new Error('เบราว์เซอร์ของคุณไม่รองรับการค้นหาตำแหน่ง');
            }
            this.setLoadingState(true, 'กำลังค้นหาตำแหน่งของคุณ...');
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    timeout: this.LOADING_TIMEOUT,
                    maximumAge: 0,
                    enableHighAccuracy: true
                });
            });
            const { latitude, longitude } = position.coords;
            await this.searchWeatherByCoords(latitude, longitude);
        } catch (error) {
            console.error('เกิดข้อผิดพลาดในการค้นหาตำแหน่ง:', error);
            let errorMessage = 'ไม่สามารถระบุตำแหน่งของคุณได้';
            if (error.code) {
                switch (error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage = 'คุณไม่ได้อนุญาตให้เข้าถึงตำแหน่ง';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMessage = 'ไม่สามารถระบุตำแหน่งได้ในขณะนี้';
                        break;
                    case error.TIMEOUT:
                        errorMessage = 'การค้นหาตำแหน่งใช้เวลานานเกินไป';
                        break;
                }
            }
            this.showNotification(errorMessage, 'error');
        } finally {
            this.setLoadingState(false);
        }
    }

    async searchWeatherByCoords(lat, lon) {
        if (this.isLoading) return;
        try {
            this.isLoading = true;
            this.setLoadingState(true, 'กำลังโหลดข้อมูลสภาพอากาศ...');
            const response = await fetch(`/api/weather?lat=${lat}&lon=${lon}`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `เกิดข้อผิดพลาด HTTP ${response.status}`);
            }
            const data = await response.json();
            if (data.error) throw new Error(data.error);
            if (!data || !data.main) throw new Error('ไม่พบข้อมูลสภาพอากาศสำหรับตำแหน่งนี้');

            this.currentWeather = data;
            this.forecastData = data.forecast || [];
            document.getElementById('currentWeather').classList.remove('hidden');
            document.getElementById('currentWeather').classList.add('animate__fadeIn');
            await this.updateCurrentWeather();
            await this.updateForecast(this.forecastData); 
            this.addToSearchHistory(data.name);
            this.showNotification(`โหลดข้อมูลสภาพอากาศสำหรับ ${data.name} เรียบร้อยแล้ว`, 'success');
        } catch (error) {
            console.error('เกิดข้อผิดพลาดในการโหลดข้อมูลสภาพอากาศ:', error);
            this.showError(error.message || 'เกิดข้อผิดพลาดในการโหลดข้อมูลสภาพอากาศ');
            document.getElementById('currentWeather').classList.add('hidden');
            this.updateForecast([]); // Clear forecast on error
        } finally {
            this.isLoading = false;
            this.setLoadingState(false);
        }
    }

    async searchWeather(city) {
        if (this.isLoading) return;
        try {
            this.isLoading = true;
            this.setLoadingState(true, `กำลังค้นหาข้อมูลสำหรับ ${city}...`);
            const response = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `เกิดข้อผิดพลาด HTTP ${response.status}`);
            }
            const data = await response.json();
            if (data.error) throw new Error(data.error);
            if (!data || !data.main) throw new Error('ไม่พบข้อมูลสภาพอากาศสำหรับเมืองนี้');

            this.currentWeather = data;
            this.forecastData = data.forecast || [];
            document.getElementById('currentWeather').classList.remove('hidden');
            document.getElementById('currentWeather').classList.add('animate__fadeIn');
            await this.updateCurrentWeather();
            await this.updateForecast(this.forecastData);
            this.addToSearchHistory(city);
            this.showNotification(`โหลดข้อมูลสภาพอากาศสำหรับ ${data.name} เรียบร้อยแล้ว`, 'success');
        } catch (error) {
            this.showError(error.message || 'ไม่สามารถโหลดข้อมูลสภาพอากาศได้');
            document.getElementById('currentWeather').classList.add('hidden');
            this.updateForecast([]); // Clear forecast on error
        } finally {
            this.isLoading = false;
            this.setLoadingState(false);
        }
    }

    getSearchHistory() {
        try {
            const history = localStorage.getItem('weatherSearchHistory');
            return history ? JSON.parse(history) : [];
        } catch (error) {
            console.error('เกิดข้อผิดพลาดในการโหลดประวัติการค้นหา:', error);
            return [];
        }
    }

    getWindDirection(degrees) {
        const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
        return directions[Math.round(degrees / 22.5) % 16];
    }

    formatTime(timestamp, timezoneOffsetSeconds) {
        const date = new Date((timestamp + timezoneOffsetSeconds) * 1000);
        const hours = date.getUTCHours().toString().padStart(2, '0');
        const minutes = date.getUTCMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes} น.`;
    }

    async updateCurrentWeather() {
        const currentWeatherEl = document.getElementById('currentWeather');
        if (!currentWeatherEl || !this.currentWeather) return;
        try {
            const now = new Date();
            const localDate = new Date(now.getTime() + (this.currentWeather.timezone * 1000));
            const day = localDate.getUTCDate();
            const month = this.THAI_MONTHS[localDate.getUTCMonth()];
            const year = localDate.getUTCFullYear() + 543;
            const formattedDate = `${day} ${month} ${year}`;
            
            const weatherIconCode = this.currentWeather.weather[0].icon;
            const weatherIconClass = this.WEATHER_ICONS_FA[weatherIconCode] || this.WEATHER_ICONS_FA['default'];
            const windDirection = this.getWindDirection(this.currentWeather.wind.deg);
            
            currentWeatherEl.innerHTML = `
                <div class="weather-header">
                    <div class="location">
                        <h2><i class="fas fa-map-marker-alt text-red-500"></i> ${this.currentWeather.name}, ${this.currentWeather.sys.country}</h2>
                        <p class="date">อัปเดตล่าสุด: ${formattedDate}, ${this.formatTime(this.currentWeather.dt, this.currentWeather.timezone)}</p>
                    </div>
                    <div class="weather-main">
                        <div class="temperature">
                            <i class="fas ${weatherIconClass} weather-icon"></i>
                            <span class="temp-value">${Math.round(this.currentWeather.main.temp)}</span>
                            <span class="temp-unit">°C</span>
                        </div>
                        <div class="weather-desc">
                            <p class="description">${this.currentWeather.weather[0].description}</p>
                            <p class="feels-like">รู้สึกเหมือน ${Math.round(this.currentWeather.main.feels_like)}°C</p>
                        </div>
                    </div>
                </div>
                <div class="weather-details">
                    <div class="detail-item">
                        <i class="fas fa-temperature-high"></i>
                        <div>
                            <span class="label">อุณหภูมิสูงสุด</span>
                            <span class="value">${Math.round(this.currentWeather.main.temp_max)}°C</span>
                        </div>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-temperature-low"></i>
                        <div>
                            <span class="label">อุณหภูมิต่ำสุด</span>
                            <span class="value">${Math.round(this.currentWeather.main.temp_min)}°C</span>
                        </div>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-tint"></i>
                        <div>
                            <span class="label">ความชื้น</span>
                            <span class="value">${this.currentWeather.main.humidity}%</span>
                        </div>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-wind"></i>
                        <div>
                            <span class="label">ลม</span>
                            <span class="value">${(this.currentWeather.wind.speed * 3.6).toFixed(1)} กม./ชม. (${windDirection})</span>
                        </div>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-tachometer-alt"></i>
                        <div>
                            <span class="label">ความกดอากาศ</span>
                            <span class="value">${this.currentWeather.main.pressure} hPa</span>
                        </div>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-eye"></i>
                        <div>
                            <span class="label">ทัศนวิสัย</span>
                            <span class="value">${(this.currentWeather.visibility / 1000).toFixed(1)} กม.</span>
                        </div>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-sun text-yellow-500"></i>
                        <div>
                            <span class="label">พระอาทิตย์ขึ้น</span>
                            <span class="value">${this.formatTime(this.currentWeather.sys.sunrise, this.currentWeather.timezone)}</span>
                        </div>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-moon text-gray-700"></i>
                        <div>
                            <span class="label">พระอาทิตย์ตก</span>
                            <span class="value">${this.formatTime(this.currentWeather.sys.sunset, this.currentWeather.timezone)}</span>
                        </div>
                    </div>
                </div>
            `;
            currentWeatherEl.classList.remove('animate__fadeOut');
            currentWeatherEl.classList.add('animate__fadeIn');
        } catch (error) {
            console.error('เกิดข้อผิดพลาดในการอัปเดตข้อมูลสภาพอากาศปัจจุบัน:', error);
            this.showError('ไม่สามารถอัปเดตข้อมูลสภาพอากาศปัจจุบันได้');
        }
    }

        // Ensure WEATHER_ICONS_FA is defined in the class, e.g., in constructor or as a static property
    // constructor() { ... this.WEATHER_ICONS_FA = { '01d': 'fas fa-sun', ... }; ... }

    getWeatherIcon(weatherId, pod = 'd') { // pod: 'd' for day, 'n' for night
        // Basic example, expand with actual OpenWeatherMap ID to Font Awesome mapping
        const OWM_ICON_MAP_FA = {
            // Group 2xx: Thunderstorm
            200: 'fas fa-cloud-bolt', 201: 'fas fa-cloud-bolt', 202: 'fas fa-cloud-bolt',
            210: 'fas fa-cloud-bolt', 211: 'fas fa-cloud-bolt', 212: 'fas fa-cloud-bolt',
            230: 'fas fa-cloud-bolt', 231: 'fas fa-cloud-bolt', 232: 'fas fa-cloud-bolt',
            // Group 3xx: Drizzle
            300: 'fas fa-cloud-drizzle', 301: 'fas fa-cloud-drizzle', 302: 'fas fa-cloud-showers-heavy',
            310: 'fas fa-cloud-drizzle', 311: 'fas fa-cloud-drizzle', 312: 'fas fa-cloud-showers-heavy',
            313: 'fas fa-cloud-drizzle', 314: 'fas fa-cloud-showers-heavy', 321: 'fas fa-cloud-showers-heavy',
            // Group 5xx: Rain
            500: 'fas fa-cloud-rain', 501: 'fas fa-cloud-rain', 502: 'fas fa-cloud-showers-heavy',
            503: 'fas fa-cloud-showers-heavy', 504: 'fas fa-cloud-showers-heavy', 511: 'fas fa-snowflake',
            520: 'fas fa-cloud-showers-heavy', 521: 'fas fa-cloud-showers-heavy', 522: 'fas fa-cloud-showers-heavy', 531: 'fas fa-cloud-showers-heavy',
            // Group 6xx: Snow
            600: 'fas fa-snowflake', 601: 'fas fa-snowflake', 602: 'fas fa-snowflake',
            611: 'fas fa-sleet', 612: 'fas fa-sleet', 613: 'fas fa-sleet',
            615: 'fas fa-sleet', 616: 'fas fa-sleet', 620: 'fas fa-snowflake', 621: 'fas fa-snowflake', 622: 'fas fa-snowflake',
            // Group 7xx: Atmosphere
            701: 'fas fa-smog', // Mist
            711: 'fas fa-smoke', // Smoke
            721: 'fas fa-smog', // Haze
            731: 'fas fa-sun-dust', // Dust whirls
            741: 'fas fa-fog', // Fog
            751: 'fas fa-sun-dust', // Sand
            761: 'fas fa-sun-dust', // Dust
            762: 'fas fa-volcano', // Volcanic ash
            771: 'fas fa-wind', // Squalls
            781: 'fas fa-tornado', // Tornado
            // Group 800: Clear
            800: pod === 'd' ? 'fas fa-sun' : 'fas fa-moon',
            // Group 80x: Clouds
            801: pod === 'd' ? 'fas fa-cloud-sun' : 'fas fa-cloud-moon',
            802: 'fas fa-cloud',
            803: 'fas fa-cloud-sun', // Or fa-clouds if you prefer for more clouds
            804: 'fas fa-cloud',
            // Default
            default: 'fas fa-question-circle'
        };
        return OWM_ICON_MAP_FA[weatherId] || OWM_ICON_MAP_FA['default'];
    }

    getIconColor(weatherIconCode) {
        // Example: '01d' -> 'text-yellow-400', '10d' -> 'text-blue-400'
        if (!weatherIconCode) return 'text-gray-400';
        const firstTwoChars = weatherIconCode.substring(0, 2);
        const dayNight = weatherIconCode.charAt(2);

        switch (firstTwoChars) {
            case '01': return dayNight === 'd' ? 'text-yellow-400' : 'text-indigo-300'; // Sun/Moon
            case '02': return dayNight === 'd' ? 'text-yellow-400' : 'text-indigo-300'; // Few clouds
            case '03': return 'text-gray-400'; // Scattered clouds
            case '04': return 'text-gray-500'; // Broken clouds
            case '09': return 'text-blue-400'; // Shower rain
            case '10': return 'text-blue-500'; // Rain
            case '11': return 'text-yellow-500'; // Thunderstorm
            case '13': return 'text-blue-300'; // Snow
            case '50': return 'text-gray-400'; // Mist
            default: return 'text-gray-400';
        }
    }

    async updateForecast(forecastDataToUpdate) {
        console.log('[WeatherApp] updateForecast called with:', JSON.parse(JSON.stringify(forecastDataToUpdate))); // Log a deep copy for inspection
        const forecastEl = document.getElementById('forecast');
        if (!forecastEl) return;

        forecastEl.innerHTML = ''; // Clear previous forecast
        // Ensure forecastEl is not using grid if it was before, and add spacing for rows
        forecastEl.classList.remove('grid', 'grid-cols-1', 'sm:grid-cols-2', 'md:grid-cols-3', 'lg:grid-cols-4', 'xl:grid-cols-5', 'gap-4');
        forecastEl.classList.add('space-y-4');

                console.log('[WeatherApp] Checking forecastDataToUpdate.list:', forecastDataToUpdate ? forecastDataToUpdate.list : 'forecastDataToUpdate is null/undefined or has no list property');
        if (!Array.isArray(forecastDataToUpdate) || forecastDataToUpdate.length === 0) {
            forecastEl.innerHTML = `
                <div class="text-center py-8 text-gray-500 bg-white bg-opacity-70 rounded-xl shadow-lg">
                    <i class="fas fa-cloud-sun text-5xl mb-3 opacity-50"></i>
                    <p>ค้นหาข้อมูลเพื่อดูพยากรณ์อากาศ 5 วัน</p>
                </div>
            `;
            // Show the forecast section even if it's empty, so the message is visible
            document.getElementById('forecastSection').classList.remove('hidden');
            document.getElementById('forecastSection').classList.add('animate__animated', 'animate__fadeIn');
            return;
        }

        try {
            const groupedForecast = forecastDataToUpdate.reduce((acc, item) => {
                const date = new Date(item.dt * 1000);
                const dayKey = date.toISOString().split('T')[0]; // YYYY-MM-DD

                if (!acc[dayKey]) {
                    acc[dayKey] = {
                        dateObject: date,
                        items: []
                    };
                }
                acc[dayKey].items.push(item);
                return acc;
            }, {});

            let dayIndex = 0;
            for (const dayKey in groupedForecast) {
                if (groupedForecast.hasOwnProperty(dayKey)) {
                    const dayData = groupedForecast[dayKey];

                    const dayRowElement = document.createElement('div');
                    dayRowElement.className = `forecast-day-row bg-white bg-opacity-80 p-4 rounded-xl shadow-lg animate__animated animate__fadeInUp`;
                    dayRowElement.style.animationDelay = `${dayIndex * 100}ms`;

                    const dayHeader = document.createElement('h3');
                    dayHeader.className = 'text-lg md:text-xl font-semibold text-indigo-700 mb-3';
                    dayHeader.textContent = dayData.dateObject.toLocaleDateString('th-TH', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                    });
                    dayRowElement.appendChild(dayHeader);

                    const timeSlotsContainer = document.createElement('div');
                    timeSlotsContainer.className = 'forecast-timeslots-container flex overflow-x-auto space-x-3 pb-2';

                    dayData.items.forEach((item, itemIndex) => {
                        const itemTime = new Date(item.dt * 1000);
                        // Use getWeatherIcon method for consistency if available, otherwise map directly
                        const weatherIconCode = item.weather[0].icon;
                        const weatherIconClass = this.getWeatherIcon(item.weather[0].id, item.sys.pod); // Assuming getWeatherIcon handles mapping
                        const iconColor = this.getIconColor(weatherIconCode); // Assuming getIconColor exists

                        const timeSlotCard = document.createElement('div');
                        timeSlotCard.className = `forecast-timeslot-item flex flex-col items-center p-2.5 bg-indigo-50 hover:bg-indigo-100 rounded-lg shadow-sm transition-colors duration-200 min-w-[90px] md:min-w-[100px] animate__animated animate__zoomIn`;
                        timeSlotCard.style.animationDelay = `${(dayIndex * 100) + (itemIndex * 50)}ms`;

                        timeSlotCard.innerHTML = `
                            <p class="time text-xs sm:text-sm font-medium text-indigo-700">
                                ${itemTime.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit', hour12: false })}
                            </p>
                            <i class="${weatherIconClass} text-2xl sm:text-3xl ${iconColor} my-1.5"></i>
                            <p class="temp text-sm sm:text-base font-semibold text-gray-700">${Math.round(item.main.temp)}°C</p>
                            <p class="description text-xs text-gray-500 capitalize text-center">${item.weather[0].description}</p>
                        `;
                        timeSlotsContainer.appendChild(timeSlotCard);
                    });

                    dayRowElement.appendChild(timeSlotsContainer);
                    forecastEl.appendChild(dayRowElement);
                    dayIndex++;
                }
            }
            // Make forecast section visible
            document.getElementById('forecastSection').classList.remove('hidden');
            document.getElementById('forecastSection').classList.add('animate__animated', 'animate__fadeIn');

        } catch (error) {
            console.error('เกิดข้อผิดพลาดในการอัปเดตพยากรณ์อากาศ:', error);
            forecastEl.innerHTML = '<div class="text-center py-8 text-red-500 bg-white bg-opacity-70 rounded-xl shadow-lg"><p>ไม่สามารถโหลดข้อมูลพยากรณ์อากาศได้</p></div>';
            // Ensure forecast section is visible to show error
            document.getElementById('forecastSection').classList.remove('hidden');
            document.getElementById('forecastSection').classList.add('animate__animated', 'animate__fadeIn');
        }
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    setLoadingState(newIsLoading, message = 'กำลังโหลด...') {
        const loadingOverlay = document.getElementById('loadingOverlay');
        const loadingMessageEl = document.getElementById('loadingMessage');
        const mainContent = document.getElementById('mainContent');
        this.isLoading = newIsLoading;

        if (loadingOverlay && loadingMessageEl && mainContent) {
            if (this.isLoading) {
                loadingMessageEl.textContent = message;
                loadingOverlay.classList.remove('hidden');
                mainContent.classList.add('blur-sm');
            } else {
                loadingOverlay.classList.add('hidden');
                mainContent.classList.remove('blur-sm');
            }
        } else {
            console.warn('ไม่พบองค์ประกอบ UI สำหรับสถานะการโหลด');
        }
    }

    async handleSearch(event) {
        event.preventDefault();
        const cityInput = document.getElementById('cityInput');
        const city = cityInput.value.trim();
        if (city) {
            await this.searchWeather(city);
            // cityInput.value = ''; // Optional: clear input after search
        } else {
            this.showNotification('กรุณาป้อนชื่อเมือง', 'warning');
        }
    }

    addToSearchHistory(city) {
        if (!city) return;
        const normalizedCity = city.toLowerCase().split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
        this.searchHistory = this.searchHistory.filter(item => item.toLowerCase() !== normalizedCity.toLowerCase());
        this.searchHistory.unshift(normalizedCity);
        if (this.searchHistory.length > this.MAX_HISTORY_ITEMS) {
            this.searchHistory = this.searchHistory.slice(0, this.MAX_HISTORY_ITEMS);
        }
        try {
            localStorage.setItem('weatherSearchHistory', JSON.stringify(this.searchHistory));
        } catch (error) {
            console.error('เกิดข้อผิดพลาดในการบันทึกประวัติการค้นหา:', error);
        }
        this.updateSearchHistoryUI();
    }

    clearSearchHistory() {
        this.searchHistory = [];
        try {
            localStorage.removeItem('weatherSearchHistory');
        } catch (error) {
            console.error('เกิดข้อผิดพลาดในการล้างประวัติการค้นหาจาก localStorage:', error);
        }
        this.updateSearchHistoryUI();
        this.showNotification('ล้างประวัติการค้นหาเรียบร้อยแล้ว', 'info');
    }

    loadSearchHistory() {
        this.searchHistory = this.getSearchHistory();
        this.updateSearchHistoryUI();
    }

    showNotification(message, type = 'info', duration = 5000) {
        if (this.notificationTimeout) {
            clearTimeout(this.notificationTimeout);
        }
        
        const notificationsContainer = document.getElementById('notifications');
        if (!notificationsContainer) {
            console.error('Notification container not found');
            return;
        }

        const notification = document.createElement('div');
        notification.className = `notification notification-${type} animate__animated animate__fadeInRight`;
        
        let iconClass = 'fa-info-circle';
        switch(type) {
            case 'success': iconClass = 'fa-check-circle'; break;
            case 'error': iconClass = 'fa-times-circle'; break;
            case 'warning': iconClass = 'fa-exclamation-triangle'; break;
        }

        notification.innerHTML = `
            <i class="fas ${iconClass}"></i>
            <span>${message}</span>
            <button class="close-btn">&times;</button>
        `;
        
        const closeBtn = notification.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                notification.classList.remove('animate__fadeInRight');
                notification.classList.add('animate__fadeOutRight');
                setTimeout(() => notification.remove(), 500); // Match Animate.css duration
            });
        }
        
        notificationsContainer.appendChild(notification);

        if (duration > 0) {
            this.notificationTimeout = setTimeout(() => {
                if (notification.parentNode) { // Check if still in DOM
                    notification.classList.remove('animate__fadeInRight');
                    notification.classList.add('animate__fadeOutRight');
                    setTimeout(() => notification.remove(), 500);
                }
            }, duration);
        }
    }

    updateSearchHistoryUI() {
        try {
            const historyContainer = document.getElementById('searchHistory');
            if (!historyContainer) return;

            if (!this.searchHistory || this.searchHistory.length === 0) {
                historyContainer.innerHTML = '<p class="text-gray-500 text-sm text-center">ยังไม่มีประวัติการค้นหา</p>';
                return;
            }

            const historyItems = this.searchHistory.map(city => `
                <button 
                    class="history-item"
                    onclick="weatherAppInstance.searchWeather('${city.replace(/'/g, "\\'")}')"
                    aria-label="ค้นหา ${city} อีกครั้ง"
                >
                    <i class="fas fa-history"></i>
                    <span>${city}</span>
                </button>
            `).join('');

            historyContainer.innerHTML = `
                <div class="flex justify-between items-center mb-2">
                    <h3 class="text-sm font-medium text-gray-700">ประวัติการค้นหา</h3>
                    <button 
                        id="clearHistoryBtnInternal" 
                        class="text-xs text-red-500 hover:text-red-700 hover:underline"
                        aria-label="ล้างประวัติการค้นหา"
                    >
                        <i class="fas fa-trash-alt"></i> ล้างทั้งหมด
                    </button>
                </div>
                <div class="history-items space-y-1">
                    ${historyItems}
                </div>
            `;
            
            const clearBtn = document.getElementById('clearHistoryBtnInternal');
            if (clearBtn) {
                // Remove old listener if any to prevent multiple bindings
                clearBtn.replaceWith(clearBtn.cloneNode(true));
                document.getElementById('clearHistoryBtnInternal').addEventListener('click', () => this.clearSearchHistory());
            }
        } catch (error) {
            console.error('เกิดข้อผิดพลาดในการอัปเดตประวัติการค้นหา:', error);
        }
    }
}

let weatherAppInstance;
document.addEventListener('DOMContentLoaded', () => {
    weatherAppInstance = new WeatherApp();
});
