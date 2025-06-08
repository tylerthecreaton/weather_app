package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"

	"weather_app/location_api/handlers"
	"weather_app/location_api/services" // เพิ่ม import สำหรับ services
)

// enableCORS เป็น middleware ที่เพิ่ม header CORS ให้กับทุก response
func enableCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// อนุญาตให้เรียกจากทุก origin (ใน production ควรระบุ origin ที่เฉพาะเจาะจง)
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

		// สำหรับการส่ง request แบบ OPTIONS (preflight)
		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		// เรียก handler ถัดไป
		next.ServeHTTP(w, r)
	})
}

func main() {
	// กำหนด port ที่จะรันเซิร์ฟเวอร์
	port := os.Getenv("PORT")
	if port == "" {
		port = "8082"
	}

	// กำหนด path ไปยัง geography.json (ควรใช้ path ที่ถูกต้อง)
	// อาจจะใช้ relative path หรือ environment variable ใน production
	geoDataPath, err := filepath.Abs("./data/geography.json")
	if err != nil {
		log.Fatalf("Error getting absolute path for geography.json: %v", err)
	}

	// สร้าง AutocompleteService
	autocompleteService, err := services.NewAutocompleteService(geoDataPath)
	if err != nil {
		log.Fatalf("Failed to create autocomplete service: %v", err)
	}

	// สร้าง LocationHandler โดย inject AutocompleteService
	locationAPIHandler := handlers.NewLocationHandler(autocompleteService)

	// สร้าง router ใหม่
	mux := http.NewServeMux()

	// กำหนด route พื้นฐาน
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" {
			http.NotFound(w, r)
			return
		}
		fmt.Fprintf(w, "Location API Service is running")
	})

	// กำหนด route สำหรับค้นหาสถานที่ (เดิม) - แก้ไขให้เรียกผ่าน instance ของ LocationHandler
	mux.HandleFunc("/api/search-locations", locationAPIHandler.SearchLocationsHandler)

	// กำหนด route ใหม่สำหรับ Autocomplete
	mux.HandleFunc("/api/v1/autocomplete/locations", locationAPIHandler.AutocompleteHandler)

	// กำหนด middleware CORS
	cachedHandler := enableCORS(mux)

	// เริ่มต้นเซิร์ฟเวอร์
	server := &http.Server{
		Addr:    ":" + port,
		Handler: cachedHandler, // ใช้ cachedHandler ที่มี CORS
	}

	log.Printf("Server is running on port %s\n", port)
	log.Printf("Legacy Search API Endpoint: http://localhost:%s/api/search-locations\n", port)
	log.Printf("New Autocomplete API Endpoint: http://localhost:%s/api/v1/autocomplete/locations?q=<your_query>\n", port)

	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("Could not start server: %v\n", err)
	}
}
