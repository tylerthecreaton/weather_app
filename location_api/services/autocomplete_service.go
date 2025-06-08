package services

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
)

// GeoEntry matches the structure of objects in geography.json
type GeoEntry struct {
	ID                int    `json:"id"`
	ProvinceCode      int    `json:"provinceCode"`
	ProvinceNameEn    string `json:"provinceNameEn"`
	ProvinceNameTh    string `json:"provinceNameTh"`
	DistrictCode      int    `json:"districtCode"`
	DistrictNameEn    string `json:"districtNameEn"`
	DistrictNameTh    string `json:"districtNameTh"`
	SubdistrictCode   int    `json:"subdistrictCode"`
	SubdistrictNameEn string `json:"subdistrictNameEn"`
	SubdistrictNameTh string `json:"subdistrictNameTh"`
	PostalCode        int    `json:"postalCode"`
}

// LocationSuggestion is the format for autocomplete results, styled similarly to OpenWeatherMap.
type LocationSuggestion struct {
	ID                int               `json:"id"`                            // Original ID from geography.json
	Name              string            `json:"name"`                          // Primary name (e.g., most specific name in English)
	LocalNames        map[string]string `json:"local_names,omitempty"`       // Language-specific names for the primary 'Name'
	Country           string            `json:"country"`                       // Country code (e.g., "TH")
	State             string            `json:"state"`                         // Province name in English
	District          string            `json:"district,omitempty"`            // District name in English
	Subdistrict       string            `json:"subdistrict,omitempty"`         // Subdistrict name in English
	FullDisplayName   string            `json:"full_display_name"`           // Combined: "Subdistrict, District, Province" (English)
	FullDisplayNameTh string            `json:"full_display_name_th"`        // Combined: "ตำบล, อำเภอ, จังหวัด" (Thai)
	PostalCode        int               `json:"postal_code,omitempty"`       // Postal code

	// Lat and Lon are typically present in OpenWeatherMap data but are missing from geography.json.
	// Lat float64 `json:"lat,omitempty"`
	// Lon float64 `json:"lon,omitempty"`

	originalData GeoEntry `json:"-"` // Internal field, not part of JSON output
}

// AutocompleteService handles location data and autocomplete functionality.
type AutocompleteService struct {
	allSuggestions []LocationSuggestion // Stores all possible suggestions, pre-processed.
}

// buildDisplayName safely combines parts of a name, separated by commas.
func buildDisplayName(parts ...string) string {
	var validParts []string
	for _, p := range parts {
		if strings.TrimSpace(p) != "" {
			validParts = append(validParts, strings.TrimSpace(p))
		}
	}
	return strings.Join(validParts, ", ")
}

// NewAutocompleteService creates and initializes a new AutocompleteService.
// dataFilePath should be the absolute path to geography.json.
func NewAutocompleteService(dataFilePath string) (*AutocompleteService, error) {
	absPath, err := filepath.Abs(dataFilePath)
	if err != nil {
		return nil, fmt.Errorf("failed to get absolute path for '%s': %w", dataFilePath, err)
	}
	log.Printf("Attempting to load geography data from: %s", absPath)

	data, err := os.ReadFile(absPath) // Changed from ioutil.ReadFile
	if err != nil {
		return nil, fmt.Errorf("failed to read data file '%s': %w", absPath, err)
	}

	var geoEntries []GeoEntry
	if err := json.Unmarshal(data, &geoEntries); err != nil {
		return nil, fmt.Errorf("failed to unmarshal geo data from '%s': %w", absPath, err)
	}
	log.Printf("Successfully unmarshalled %d entries from geography.json", len(geoEntries))

	suggestions := make([]LocationSuggestion, len(geoEntries))
	for i, entry := range geoEntries {
		// Determine the primary English and Thai names (most specific available)
		var finalNameEn, finalNameTh string
		if entry.SubdistrictNameEn != "" || entry.SubdistrictNameTh != "" {
			finalNameEn = entry.SubdistrictNameEn
			finalNameTh = entry.SubdistrictNameTh
		} else if entry.DistrictNameEn != "" || entry.DistrictNameTh != "" {
			finalNameEn = entry.DistrictNameEn
			finalNameTh = entry.DistrictNameTh
		} else {
			finalNameEn = entry.ProvinceNameEn
			finalNameTh = entry.ProvinceNameTh
		}

		localNames := make(map[string]string)
		if finalNameEn != "" {
			localNames["en"] = finalNameEn
		}
		if finalNameTh != "" {
			localNames["th"] = finalNameTh
		}

		suggestions[i] = LocationSuggestion{
			ID:                entry.ID,
			Name:              finalNameEn, // The primary name, often English for OpenWeatherMap
			LocalNames:        localNames,
			Country:           "TH",
			State:             entry.ProvinceNameEn, // Province
			District:          entry.DistrictNameEn,
			Subdistrict:       entry.SubdistrictNameEn,
			FullDisplayName:   buildDisplayName(entry.SubdistrictNameEn, entry.DistrictNameEn, entry.ProvinceNameEn),
			FullDisplayNameTh: buildDisplayName(entry.SubdistrictNameTh, entry.DistrictNameTh, entry.ProvinceNameTh),
			PostalCode:        entry.PostalCode,
			originalData:      entry,
		}
	}

	return &AutocompleteService{
		allSuggestions: suggestions,
	}, nil
}

// Search performs autocomplete based on the query string.
// It searches in English and Thai names of subdistrict, district, and province from the original data,
// as well as the pre-formatted full display names.
func (s *AutocompleteService) Search(query string) []LocationSuggestion {
	trimmedQuery := strings.TrimSpace(query)
	if trimmedQuery == "" {
		return []LocationSuggestion{}
	}

	lowerQuery := strings.ToLower(trimmedQuery) // For case-insensitive English search
	var matchedSuggestions []LocationSuggestion
	addedSuggestions := make(map[int]bool) // Key is LocationSuggestion.ID (original GeoEntry.ID)

	for _, suggestion := range s.allSuggestions {
		entry := suggestion.originalData // Access original fields for more precise searching

		matched := false
		// Search English fields (case-insensitive)
		if strings.Contains(strings.ToLower(entry.SubdistrictNameEn), lowerQuery) ||
			strings.Contains(strings.ToLower(entry.DistrictNameEn), lowerQuery) ||
			strings.Contains(strings.ToLower(entry.ProvinceNameEn), lowerQuery) {
			matched = true
		}

		// Search Thai fields (case-sensitive using original trimmed query for better accuracy with Thai)
		if !matched {
			if strings.Contains(entry.SubdistrictNameTh, trimmedQuery) ||
				strings.Contains(entry.DistrictNameTh, trimmedQuery) ||
				strings.Contains(entry.ProvinceNameTh, trimmedQuery) {
				matched = true
			}
		}
		
		// Also search the pre-formatted full display names
		if !matched {
		    if strings.Contains(strings.ToLower(suggestion.FullDisplayName), lowerQuery) || // English full name
		        strings.Contains(suggestion.FullDisplayNameTh, trimmedQuery) { // Thai full name
		        matched = true
		    }
		}

		if matched && !addedSuggestions[suggestion.ID] {
			matchedSuggestions = append(matchedSuggestions, suggestion)
			addedSuggestions[suggestion.ID] = true
		}

		// Limit results to avoid overly large responses
		if len(matchedSuggestions) >= 20 {
			break
		}
	}
	return matchedSuggestions
}
