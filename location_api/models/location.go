package models

// LocationSuggestion represents a single location suggestion.
// It includes common fields that might be returned by a geo-search API.
// omitempty is used to hide fields from JSON if they are empty.
type LocationSuggestion struct {
	Name         string  `json:"name"`                   // Display name (Thai by default for now), e.g., "เขาสวนกวาง, ขอนแก่น"
	NameEN       string  `json:"nameEn,omitempty"`        // English display name, e.g., "Khao Suan Kwang, Khon Kaen"
	Country      string  `json:"country,omitempty"`       // e.g., "TH"
	AdminArea1   string  `json:"adminArea1,omitempty"`    // Province name (Thai), e.g., "ขอนแก่น"
	AdminArea1EN string  `json:"adminArea1En,omitempty"`  // Province name (English), e.g., "Khon Kaen"
	AdminArea2   string  `json:"adminArea2,omitempty"`    // District name (Thai), e.g., "เขาสวนกวาง"
	AdminArea2EN string  `json:"adminArea2En,omitempty"`  // District name (English), e.g., "Khao Suan Kwang"
	Type         string  `json:"type,omitempty"`          // e.g., "Province", "District"
	Latitude     float64 `json:"latitude,omitempty"`     // Optional: Latitude
	Longitude    float64 `json:"longitude,omitempty"`    // Optional: Longitude
}
