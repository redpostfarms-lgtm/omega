# Agriculture Resources - Quick Reference

**Red Post Farms, LLC | Copyright (c) 2025-2026 | All Rights Reserved**

Quick lookup for free agriculture APIs, repositories, and resources.

---

## 🎯 Top 10 Must-Have Resources

### 1. **PlantNet API** - Plant Identification
- **URL:** https://my.plantnet.org
- **Free:** 500 requests/day
- **Use:** Weed/plant identification from photos

### 2. **AG FARM API** - All-in-One Agriculture
- **URL:** https://agfarmapi.com
- **Free:** 1,000 requests/month
- **Use:** Weather, plant database, commodity prices

### 3. **iNaturalist API** - Plant & Animal ID
- **URL:** https://www.inaturalist.org
- **Free:** Unlimited (rate limited)
- **Use:** Animal identification, wildlife tracking

### 4. **USDA FoodData Central API**
- **URL:** https://fdc.nal.usda.gov/api-guide.html
- **Free:** Unlimited (3,600/hour)
- **Use:** Food/nutrient data, plant information

### 5. **OpenWeatherMap API** - Weather
- **URL:** https://openweathermap.org/api
- **Free:** 1M requests/month
- **Use:** Weather forecasts, historical data

### 6. **NOAA Climate Data API**
- **URL:** https://www.ncdc.noaa.gov/cdo-web/webservices/v2
- **Free:** Unlimited (5/second)
- **Use:** Historical climate, agricultural weather

### 7. **FarmOS** - Farm Management
- **URL:** https://farmos.org
- **GitHub:** https://github.com/farmOS/farmOS
- **Use:** Reference implementation, open-source farm management

### 8. **USDA NAL (AGRICOLA)**
- **URL:** https://agricola.nal.usda.gov
- **Free:** Unlimited
- **Use:** 5M+ agricultural research records

### 9. **GBIF API** - Biodiversity
- **URL:** https://www.gbif.org
- **Free:** Unlimited
- **Use:** Global plant/animal occurrence data

### 10. **EOSDA Agriculture API** - Satellite Data
- **URL:** https://eos.com/agriculture-api
- **Free:** Trial available
- **Use:** NDVI, soil moisture, vegetation indices

---

## 📋 Category Quick Links

### Weather APIs
| API | Free Tier | Link |
|-----|-----------|------|
| AG FARM | 1,000/mo | https://agfarmapi.com |
| OpenWeatherMap | 1M/mo | https://openweathermap.org/api |
| NOAA CDO | Unlimited | https://www.ncdc.noaa.gov/cdo-web |
| WeatherAPI.com | 1M/mo | https://www.weatherapi.com |

### Plant Identification
| API | Free Tier | Link |
|-----|-----------|------|
| PlantNet | 500/day | https://my.plantnet.org |
| iNaturalist | Unlimited | https://www.inaturalist.org |
| AG FARM | 1,000/mo | https://agfarmapi.com |
| GBIF | Unlimited | https://www.gbif.org |

### Government APIs (US)
| API | Free Tier | Link |
|-----|-----------|------|
| USDA FoodData | Unlimited | https://fdc.nal.usda.gov/api-guide.html |
| USDA NAL | Unlimited | https://agricola.nal.usda.gov |
| USDA NRCS | Unlimited | https://www.nrcs.usda.gov |
| NOAA CDO | Unlimited | https://www.ncdc.noaa.gov/cdo-web |

### Farm Management (Open-Source)
| System | Language | GitHub |
|--------|----------|--------|
| FarmOS | PHP | https://github.com/farmOS/farmOS |
| LiteFarm | JavaScript | https://github.com/LiteFarmOrg/LiteFarm |
| Tania | Go | https://github.com/Tanibox/tania-core |

### Research Databases
| Database | Records | Link |
|----------|---------|------|
| AGRIS (FAO) | 15M+ | https://agris.fao.org |
| AGRICOLA | 5M+ | https://agricola.nal.usda.gov |
| Ag Data Commons | Various | https://data.nal.usda.gov |
| AgriRxiv | Preprints | https://agrirxiv.org |

---

## 🔧 Integration into The Gatekeeper

### Priority 1: Plant/Weed Identification
```python
# Add to planetary_search.py
- PlantNet API integration
- iNaturalist API integration
- Weed identification database
```

### Priority 2: Weather Data
```python
# Add to knowledge base
- OpenWeatherMap API
- NOAA CDO API
- AG FARM Weather API
```

### Priority 3: Government Data
```python
# Add to planetary_search.py
- USDA FoodData Central
- USDA NAL (AGRICOLA)
- USDA NRCS soil data
```

### Priority 4: Animal Identification
```python
# Add to knowledge base
- iNaturalist API (animals)
- GBIF API (biodiversity)
```

---

## 📦 Install Commands (Python)

```bash
# API Clients (if needed)
pip install requests httpx

# For PlantNet API
pip install requests  # Standard HTTP client

# For iNaturalist API
pip install requests  # Standard HTTP client

# All APIs use standard HTTP (requests library)
# No special SDKs required for most
```

---

## 🔑 API Keys (Free Registration)

1. **OpenWeatherMap** - https://openweathermap.org/api
2. **NOAA CDO** - https://www.ncdc.noaa.gov/cdo-web/webservices/v2
3. **PlantNet** - https://my.plantnet.org (optional, for higher limits)
4. **AG FARM** - https://agfarmapi.com/pricing

**No API Key Required:**
- USDA APIs (rate limited, no auth)
- GBIF API
- iNaturalist API (rate limited)
- Government databases

---

## 📚 Full Documentation

For complete details, see: **AGRICULTURE_COMPREHENSIVE_RESOURCES.md**

---

## 🎓 Learning Resources

### Free Courses
- **Alison:** Agricultural Science course
- **OFRF:** Basics of Organic Farming
- **Oregon State:** Urban Agriculture Overview
- **Elevify:** Hydroponics course
- **Cornell:** Resilience in Agriculture

### Research Databases
- **AGRIS:** 15M+ records (FAO)
- **AGRICOLA:** 5M+ records (USDA)
- **AgriRxiv:** Agricultural preprints
- **AgEcon Search:** Agricultural economics

---

**Red Post Farms, LLC - 2025-2026 | All Rights Reserved**

