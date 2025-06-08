package handlers

import (
	"encoding/json"
	"net/http"
	"weather_app/location_api/services" // เพิ่ม import สำหรับ AutocompleteService
)

// LocationHandler holds dependencies for location-related handlers
type LocationHandler struct {
	Autocomplete *services.AutocompleteService
}

// NewLocationHandler creates a new LocationHandler with the given AutocompleteService
func NewLocationHandler(autocompleteService *services.AutocompleteService) *LocationHandler {
	return &LocationHandler{
		Autocomplete: autocompleteService,
	}
}

// AutocompleteHandler handles the new autocomplete endpoint (/api/v1/autocomplete/locations)
func (h *LocationHandler) AutocompleteHandler(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("q") // ใช้ "q" เป็น query parameter ตามที่นิยม
	if query == "" {
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "Missing 'q' parameter"})
		return
	}

	suggestions := h.Autocomplete.Search(query)

	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	// CORS headers มักจะถูกจัดการโดย middleware ใน main.go, แต่ถ้าไม่ ก็สามารถใส่ที่นี่ได้
	// w.Header().Set("Access-Control-Allow-Origin", "*") 

	if err := json.NewEncoder(w).Encode(suggestions); err != nil {
		// Log a more detailed error on the server side if needed
		// log.Printf("Error encoding autocomplete response: %v", err)
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{"error": "Failed to encode response"})
	}
}

// SearchLocationsHandler (เดิม) handles the search locations endpoint
// เราจะปรับปรุงให้ใช้ AutocompleteService ด้วย หรือจะลบทิ้งถ้าไม่ต้องการใช้ endpoint นี้แล้ว
// ในที่นี้จะปรับปรุงให้ใช้ AutocompleteService
func (h *LocationHandler) SearchLocationsHandler(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("query")
	if query == "" {
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "Missing 'query' parameter"})
		return
	}

	suggestions := h.Autocomplete.Search(query)

	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	// w.Header().Set("Access-Control-Allow-Origin", "*") // CORS

	if err := json.NewEncoder(w).Encode(suggestions); err != nil {
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{"error": "Failed to encode response"})
	}
}
