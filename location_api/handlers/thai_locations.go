package handlers

import (
	"fmt"
	"strings"

	"weather_app/location_api/models"
)

// ThaiDistrict represents a district in Thailand
type ThaiDistrict struct {
	NameTH string `json:"name_th"` // Thai name of the district
	NameEN string `json:"name_en"` // English name of the district
}

// ThaiProvince represents a province in Thailand
type ThaiProvince struct {
	NameTH  string         `json:"name_th"`  // Thai name of the province
	NameEN  string         `json:"name_en"`  // English name of the province
	Amphoes []ThaiDistrict `json:"amphoe"`   // List of districts
}

// thaiProvincesData contains static data of all 77 Thai provinces and their districts
// (ข้อมูลจังหวัดและอำเภอทั้งหมดจะอยู่ที่นี่)
var thaiProvincesData = []ThaiProvince{
	{
		NameTH: "กรุงเทพมหานคร",
		NameEN: "Bangkok",
		Amphoes: []ThaiDistrict{
			{NameTH: "พระนคร", NameEN: "Phra Nakhon"},
			{NameTH: "ดุสิต", NameEN: "Dusit"},
			{NameTH: "หนองจอก", NameEN: "Nong Chok"},
			{NameTH: "บางรัก", NameEN: "Bang Rak"},
			{NameTH: "บางเขน", NameEN: "Bang Khen"},
			{NameTH: "บางกะปิ", NameEN: "Bang Kapi"},
			{NameTH: "ปทุมวัน", NameEN: "Pathum Wan"},
			{NameTH: "ป้อมปราบศัตรูพ่าย", NameEN: "Pom Prap Sattru Phai"},
			{NameTH: "พระโขนง", NameEN: "Phra Khanong"},
			{NameTH: "มีนบุรี", NameEN: "Min Buri"},
			{NameTH: "ลาดกระบัง", NameEN: "Lat Krabang"},
			{NameTH: "ยานนาวา", NameEN: "Yan Nawa"},
			{NameTH: "สัมพันธวงศ์", NameEN: "Samphanthawong"},
			{NameTH: "พญาไท", NameEN: "Phaya Thai"},
			{NameTH: "ธนบุรี", NameEN: "Thon Buri"},
			{NameTH: "บางกอกใหญ่", NameEN: "Bangkok Yai"},
			{NameTH: "ห้วยขวาง", NameEN: "Huai Khwang"},
			{NameTH: "คลองสาน", NameEN: "Khlong San"},
			{NameTH: "ตลิ่งชัน", NameEN: "Taling Chan"},
			{NameTH: "บางกอกน้อย", NameEN: "Bangkok Noi"},
			{NameTH: "บางขุนเทียน", NameEN: "Bang Khun Thian"},
			{NameTH: "ภาษีเจริญ", NameEN: "Phasi Charoen"},
			{NameTH: "หนองแขม", NameEN: "Nong Khaem"},
			{NameTH: "ราษฎร์บูรณะ", NameEN: "Rat Burana"},
			{NameTH: "บางพลัด", NameEN: "Bang Phlat"},
			{NameTH: "ดินแดง", NameEN: "Din Daeng"},
			{NameTH: "บึงกุ่ม", NameEN: "Bung Kum"},
			{NameTH: "สาทร", NameEN: "Sathon"},
			{NameTH: "บางซื่อ", NameEN: "Bang Sue"},
			{NameTH: "จตุจักร", NameEN: "Chatuchak"},
			{NameTH: "บางคอแหลม", NameEN: "Bang Kho Laem"},
			{NameTH: "ประเวศ", NameEN: "Prawet"},
			{NameTH: "คลองเตย", NameEN: "Khlong Toei"},
			{NameTH: "สวนหลวง", NameEN: "Suan Luang"},
			{NameTH: "จอมทอง", NameEN: "Chom Thong"},
			{NameTH: "ดอนเมือง", NameEN: "Don Mueang"},
			{NameTH: "ราชเทวี", NameEN: "Ratchathewi"},
			{NameTH: "ลาดพร้าว", NameEN: "Lat Phrao"},
			{NameTH: "วัฒนา", NameEN: "Watthana"},
			{NameTH: "บางแค", NameEN: "Bang Khae"},
			{NameTH: "หลักสี่", NameEN: "Lak Si"},
			{NameTH: "สายไหม", NameEN: "Sai Mai"},
			{NameTH: "คันนายาว", NameEN: "Khan Na Yao"},
			{NameTH: "สะพานสูง", NameEN: "Saphan Sung"},
			{NameTH: "วังทองหลาง", NameEN: "Wang Thonglang"},
			{NameTH: "คลองสามวา", NameEN: "Khlong Sam Wa"},
			{NameTH: "บางนา", NameEN: "Bang Na"},
			{NameTH: "ทวีวัฒนา", NameEN: "Thawi Watthana"},
			{NameTH: "ทุ่งครุ", NameEN: "Thung Khru"},
			{NameTH: "บางบอน", NameEN: "Bang Bon"},
		},
	},
	{
		NameTH: "สมุทรปราการ",
		NameEN: "Samut Prakan",
		Amphoes: []ThaiDistrict{
			{NameTH: "เมืองสมุทรปราการ", NameEN: "Mueang Samut Prakan"},
			{NameTH: "บางบ่อ", NameEN: "Bang Bo"},
			{NameTH: "บางพลี", NameEN: "Bang Phli"},
			{NameTH: "พระประแดง", NameEN: "Phra Pradaeng"},
			{NameTH: "พระสมุทรเจดีย์", NameEN: "Phra Samut Chedi"},
			{NameTH: "บางเสาธง", NameEN: "Bang Sao Thong"},
		},
	},
	{
		NameTH: "นนทบุรี",
		NameEN: "Nonthaburi",
		Amphoes: []ThaiDistrict{
			{NameTH: "เมืองนนทบุรี", NameEN: "Mueang Nonthaburi"},
			{NameTH: "บางบัวทอง", NameEN: "Bang Bua Thong"},
			{NameTH: "ปากเกร็ด", NameEN: "Pak Kret"},
			{NameTH: "บางกรวย", NameEN: "Bang Kruai"},
			{NameTH: "บางใหญ่", NameEN: "Bang Yai"},
			{NameTH: "ไทรน้อย", NameEN: "Sai Noi"},
		},
	},
	{
		NameTH: "เชียงใหม่",
		NameEN: "Chiang Mai",
		Amphoes: []ThaiDistrict{
			{NameTH: "เมืองเชียงใหม่", NameEN: "Mueang Chiang Mai"},
			{NameTH: "จอมทอง", NameEN: "Chom Thong"},
			{NameTH: "แม่แจ่ม", NameEN: "Mae Chaem"},
			{NameTH: "เชียงดาว", NameEN: "Chiang Dao"},
			{NameTH: "ดอยสะเก็ด", NameEN: "Doi Saket"},
			{NameTH: "แม่แตง", NameEN: "Mae Taeng"},
			{NameTH: "แม่ริม", NameEN: "Mae Rim"},
			{NameTH: "สะเมิง", NameEN: "Samoeng"},
			{NameTH: "ฝาง", NameEN: "Fang"},
			{NameTH: "แม่อาย", NameEN: "Mae Ai"},
			{NameTH: "พร้าว", NameEN: "Phrao"},
			{NameTH: "สันป่าตอง", NameEN: "San Pa Tong"},
			{NameTH: "สันกำแพง", NameEN: "San Kamphaeng"},
			{NameTH: "สันทราย", NameEN: "San Sai"},
			{NameTH: "หางดง", NameEN: "Hang Dong"},
			{NameTH: "ฮอด", NameEN: "Hot"},
			{NameTH: "ดอยเต่า", NameEN: "Doi Tao"},
			{NameTH: "อมก๋อย", NameEN: "Omkoi"},
			{NameTH: "สารภี", NameEN: "Saraphi"},
			{NameTH: "เวียงแหง", NameEN: "Wiang Haeng"},
			{NameTH: "ไชยปราการ", NameEN: "Chai Prakan"},
			{NameTH: "แม่วาง", NameEN: "Mae Wang"},
			{NameTH: "แม่ออน", NameEN: "Mae On"},
			{NameTH: "ดอยหล่อ", NameEN: "Doi Lo"},
			{NameTH: "กัลยาณิวัฒนา", NameEN: "Galayani Vadhana"},
		},
	},
	{
		NameTH: "ขอนแก่น",
		NameEN: "Khon Kaen",
		Amphoes: []ThaiDistrict{
			{NameTH: "เมืองขอนแก่น", NameEN: "Mueang Khon Kaen"},
			{NameTH: "บ้านฝาง", NameEN: "Ban Fang"},
			{NameTH: "พระยืน", NameEN: "Phra Yuen"},
			{NameTH: "หนองเรือ", NameEN: "Nong Ruea"},
			{NameTH: "ชุมแพ", NameEN: "Chum Phae"},
			{NameTH: "สีชมพู", NameEN: "Si Chomphu"},
			{NameTH: "น้ำพอง", NameEN: "Nam Phong"},
			{NameTH: "อุบลรัตน์", NameEN: "Ubolratana"},
			{NameTH: "กระนวน", NameEN: "Kranuan"},
			{NameTH: "บ้านไผ่", NameEN: "Ban Phai"},
			{NameTH: "เปือยน้อย", NameEN: "Pueai Noi"},
			{NameTH: "พล", NameEN: "Phon"},
			{NameTH: "แวงใหญ่", NameEN: "Waeng Yai"},
			{NameTH: "แวงน้อย", NameEN: "Waeng Noi"},
			{NameTH: "หนองสองห้อง", NameEN: "Nong Song Hong"},
			{NameTH: "ภูเวียง", NameEN: "Phu Wiang"},
			{NameTH: "มัญจาคีรี", NameEN: "Mancha Khiri"},
			{NameTH: "ชนบท", NameEN: "Chonnabot"},
			{NameTH: "เขาสวนกวาง", NameEN: "Khao Suan Kwang"},
			{NameTH: "ภูผาม่าน", NameEN: "Phu Pha Man"},
			{NameTH: "ซำสูง", NameEN: "Sam Sung"},
			{NameTH: "โคกโพธิ์ไชย", NameEN: "Khok Pho Chai"},
			{NameTH: "หนองนาคำ", NameEN: "Nong Na Kham"},
			{NameTH: "บ้านแฮด", NameEN: "Ban Haet"},
			{NameTH: "โนนศิลา", NameEN: "Non Sila"},
			{NameTH: "เวียงเก่า", NameEN: "Wiang Kao"},
		},
	},
	// เพิ่มจังหวัดอื่นๆ ตามต้องการ...
}

// searchLocations searches for provinces and districts based on the query.
// This function is intended to be used within the handlers package.
func searchLocations(query string) []models.LocationSuggestion {
	query = strings.TrimSpace(query)
	if query == "" {
		return []models.LocationSuggestion{}
	}

	query = strings.ToLower(normalizeQuery(query)) // Normalize the query
	isThaiQuery := isThaiString(query)
	var suggestions []models.LocationSuggestion
	seenSuggestions := make(map[string]bool) // To avoid duplicate suggestions

	for _, province := range thaiProvincesData {
		provinceNameTH := strings.ToLower(province.NameTH)
		provinceNameEN := strings.ToLower(province.NameEN)

		// Check province match
		if (isThaiQuery && strings.Contains(provinceNameTH, query)) || 
		   (!isThaiQuery && strings.Contains(provinceNameEN, query)) {
			suggestionKey := province.NameTH // Use Thai name as key for uniqueness
			if !seenSuggestions[suggestionKey] {
				suggestions = append(suggestions, models.LocationSuggestion{
					Name:         province.NameTH,
					NameEN:       province.NameEN,
					Country:      "TH",
					AdminArea1:   province.NameTH,
					AdminArea1EN: province.NameEN,
					Type:         "Province",
				})
				seenSuggestions[suggestionKey] = true
			}
		}

		// Check district match
		for _, district := range province.Amphoes {
			districtNameTH := strings.ToLower(district.NameTH)
			districtNameEN := strings.ToLower(district.NameEN)

			// A district match can be triggered by matching the district name OR the province name (if query is broad)
			if (isThaiQuery && (strings.Contains(districtNameTH, query) || strings.Contains(provinceNameTH, query))) || 
			   (!isThaiQuery && (strings.Contains(districtNameEN, query) || strings.Contains(provinceNameEN, query))) {
				
				suggestionName := fmt.Sprintf("%s, %s", district.NameTH, province.NameTH)
				suggestionKey := suggestionName // Use combined name as key

				if !seenSuggestions[suggestionKey] {
					suggestions = append(suggestions, models.LocationSuggestion{
						Name:         suggestionName, // Thai name: "อำเภอ, จังหวัด"
						NameEN:       fmt.Sprintf("%s, %s", district.NameEN, province.NameEN),
						Country:      "TH",
						AdminArea1:   province.NameTH,
						AdminArea1EN: province.NameEN,
						AdminArea2:   district.NameTH,
						AdminArea2EN: district.NameEN,
						Type:         "District",
					})
					seenSuggestions[suggestionKey] = true
				}
			}

			if len(suggestions) >= 10 {
				return suggestions
			}
		}

		if len(suggestions) >= 10 {
			break
		}
	}

	// The Name field is now primarily Thai. NameEN holds the English equivalent.
	// The logic below to switch Name to English if !isThaiQuery might be redundant
	// if the frontend consistently uses Name for display and NameEN/AdminArea1EN for API calls.
	// However, keeping it for now in case Name is directly used by something expecting English on English query.
	if !isThaiQuery {
		for i := range suggestions {
			if suggestions[i].NameEN != "" {
				// If we have a pre-formatted NameEN, use it.
				// This is particularly for district, province combinations.
				suggestions[i].Name = suggestions[i].NameEN
			} else if suggestions[i].AdminArea1EN != "" { 
				// Fallback for provinces if NameEN was not set directly for them
				suggestions[i].Name = suggestions[i].AdminArea1EN
			}
		}
	}

	return suggestions
}

// isThaiString checks if the string contains Thai characters.
// This function is intended to be used within the handlers package.
func isThaiString(s string) bool {
	for _, r := range s {
		if (r >= 'ก' && r <= '๛') || (r >= '๐' && r <= '๙') { // Thai characters and digits range
			return true
		}
	}
	return false
}

// normalizeQuery normalizes the search query by removing common prefixes and trimming spaces.
// This function is intended to be used within the handlers package.
func normalizeQuery(query string) string {
	prefixes := []string{"อำเภอ", "อ.", "ตำบล", "ต.", "จังหวัด", "จ."}
	normalizedQuery := strings.ToLower(strings.TrimSpace(query))
	for _, prefix := range prefixes {
		normalizedQuery = strings.TrimPrefix(normalizedQuery, strings.ToLower(prefix))
	}
	return strings.TrimSpace(normalizedQuery)
}
