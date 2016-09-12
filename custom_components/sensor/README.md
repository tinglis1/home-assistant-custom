# Sensors

- place the file in the "custom_components\sensor directory" under your ".homeassistant" home directory or "config" directory

## Bureau of Meteorology (BOM) current conditions

- Gets the current weather conditions for a specific weather station from BOM
- each sensor will be give the device_id of bom_[optionalname_]friendlyname_units
- get the station id for your local BOM sation from BOM > State > Observations > Latest Observations > Choose the station > read the url
- the url will look like "http://www.bom.gov.au/products/IDS60801/IDS60801.94675.shtml". This is for Adelaide.
- The url is read as:    "http://www.bom.gov.au/products/[zone_id]/[zone_id].[wmo_id].shtml"


### Example config
```yaml
sensor:
  platform: weather_bom
  # name: "optional name"
  zone_id: IDS60801
  wmo_id: 94675
  monitored_conditions:
    - wmo
    - name
    - history_product
    - local_date_time
    - local_date_time_full
    - aifstime_utc
    - lat
    - lon
    - apparent_t
    - cloud
    - cloud_base_m
    - cloud_oktas
    - cloud_type_id
    - cloud_type
    - delta_t
    - gust_kmh
    - gust_kt
    - air_temp
    - dewpt
    - press
    - press_qnh
    - press_msl
    - press_tend
    - rain_trace
    - rel_hum
    - sea_state
    - swell_dir_worded
    - swell_height
    - swell_period
    - vis_km
    - weather
    - wind_dir
    - wind_spd_kmh
    - wind_spd_kt
```

