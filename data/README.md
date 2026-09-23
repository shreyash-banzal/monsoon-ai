# MONSOON-AI Data Directory

Place your NetCDF4 observation & NWP dataset here with the filename:
`imd_monsoon_2022_2025.nc`

### Recommended Variables & Coordinates:
- **Dimensions**:
  - `time`: Daily timestamps across the monsoon season (June 1 - September 30, 2022–2025)
  - `lat`: Latitude grid (8.0°N to 36.5°N, 0.25° or 0.5° resolution)
  - `lon`: Longitude grid (68.0°E to 98.0°E, 0.25° or 0.5° resolution)
- **Variables**:
  - `rainfall_obs`: IMD high-resolution gridded daily observed rainfall (mm)
  - `raw_nwp`: Operational numerical weather prediction forecast rainfall (mm)
  - `regime`: Synoptic classification index (0 to 4)
  - `u850`: 850 hPa zonal wind component (m/s)
  - `rh700`: 700 hPa relative humidity (%)
  - `mslp`: Mean sea level pressure (hPa)

If this file is not found, MONSOON-AI seamlessly falls back to high-resolution calibrated representative station and gridded synthetic data so all dashboard features operate smoothly.
