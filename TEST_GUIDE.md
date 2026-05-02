# Quick Test Guide - ECharts Implementation

## 🧪 Testing Steps

### Step 1: Open the Page
```bash
open /Users/ianvallejo/Documents/GitHub/AI-EnergyR6/index.html
# Or use your preferred browser
```

### Step 2: Navigate to Data Charts Tab
- Click the **Data Charts** tab (should be 2nd tab after ML Results)
- Page should load and display a line chart by default
- Initial state: NASA, Temperature, January, Line chart

### Step 3: Test Line Chart (Default)
**Expected Behavior:**
- Smooth cyan line
- No point markers
- Tooltip shows on hover
- Y-axis labeled "°C"
- ~744 hourly data points

**Test Actions:**
```
✓ Change Source Data → should update chart color & title
✓ Change Data Type → should update y-axis unit
✓ Change Date Range → should update month and data
```

### Step 4: Test Scatter + Trendline
**Interaction:**
1. Select "Scatter + Trendline" from Chart Type dropdown
2. Chart should update to scatter plot

**Expected Behavior:**
- Light cyan scatter points (4px diameter)
- Red dashed line through middle (trendline)
- X-axis shows time index (0, 100, 200, ...)
- Y-axis shows data values
- Tooltip shows individual point values

**Verify:**
- Trendline slopes match data trend
- Points cluster around trendline
- No console errors

### Step 5: Test Box Plot
**Interaction:**
1. Select "Box Plot (Quartile)" from Chart Type dropdown
2. Chart should update to box plot

**Expected Behavior:**
- Central box showing Q1-Q3 range
- Line through box = median (Q2)
- Whiskers extending to IQR bounds
- No outliers for most datasets

**Test Data:**
- NASA, Temperature, January → Should have compact box (temp range ~10-15°C)
- NASA, Irradiance, June → Should have wide range with outliers

**Verify:**
- Box width represents data spread
- Whiskers don't exceed max/min
- Median line visible inside box

### Step 6: Test Histogram
**Interaction:**
1. Select "Histogram (Distribution)" from Chart Type dropdown
2. Chart should update to bar chart

**Expected Behavior:**
- Bars showing frequency distribution
- X-axis shows value ranges (e.g., "10.5-12.3")
- Y-axis shows frequency (count)
- Bin count = √(data length)

**Examples:**
- Temperature: ~20-25°C range, bell curve shape
- Irradiance: ~0-1000 W/m², skewed distribution
- Humidity: ~30-90% range, multi-modal

**Verify:**
- Bar heights sum to total data points
- Labels readable (rotated 45°)
- Appropriate number of bins

### Step 7: Test Heatmap
**Interaction:**
1. Select "Heatmap (Temporal Pattern)" from Chart Type dropdown
2. Chart should update to heat matrix

**Expected Behavior:**
- Grid of 24 (hours) × ~30 (days)
- Color intensity = data value
- Dark = low values, bright = high values
- Hour labels: 0:00, 1:00, ..., 23:00
- Day labels: Day 1, Day 2, ..., Day 31

**Examples:**
- Temperature: Dark at night, bright during day
- Solar Energy: Bright midday hours, dark evening/night
- Wind Power: Random pattern (no daily cycle)

**Verify:**
- Daily pattern visible (if applicable)
- Color legend shows value range
- Grid is complete (24×month_days)

### Step 8: Test Error Handling
**Interaction 1: Try non-existent file**
```
- This shouldn't happen in normal use
- All files are pre-generated
```

**Interaction 2: Rapid dropdown changes**
```
- Click through multiple dropdowns quickly
- Select different chart types rapidly
- Chart should handle without errors
```

**Expected:**
- No console errors
- Chart updates smoothly
- No memory leaks

### Step 9: Test All Combinations
**Quick Matrix Test:**
```
Sources:     NASA, OpenMeteo, MeteoStat, WeatherBit (4)
Data Types:  Temp, Humidity, Irrad, WindPow, SolarE  (5)
Months:      Jan, Feb, Mar, Apr, May, Jun,
             Jul, Aug, Sep, Oct, Nov, Dec            (12)
Chart Types: Line, Scatter, Box, Hist, Heatmap      (5)

Total combinations: 4×5×12×5 = 1,200
Quick test: 4×5 = 20 combinations per chart type
Expected: All should load within 1-2 seconds
```

**Quick Combo Test:**
```javascript
// In browser console, run:
let passed = 0;
['nasa', 'openmeteo', 'meteostat', 'weatherbit'].forEach(s => {
  document.getElementById('sourceSelect').value = s;
  ['temperature', 'humidity', 'irradiance', 'wind_speed', 'solar_energy_yield'].forEach(d => {
    document.getElementById('dataTypeSelect').value = d;
    // Trigger change event
    document.getElementById('dataTypeSelect').dispatchEvent(new Event('change'));
    // Wait 500ms and check
    setTimeout(() => {
      let chart = document.getElementById('dataChart');
      if (chart && !chart.innerHTML.includes('⚠')) passed++;
    }, 500);
  });
});
```

### Step 10: Verify Other Pages Unaffected
**Test:**
1. Click on "ML Results" tab → Should still show table
2. Click on "NASA Stats" or other raw data tabs → Should still work
3. Open another ML model page (e.g., `ltsm-ml.html`) in new tab → Should not be affected

**Expected:**
- No console errors
- Other pages load normally
- No changes to Chart.js behavior

## 📊 Console Commands (for debugging)

```javascript
// Check if ECharts loaded
console.log(typeof echarts)  // Should be "object"

// Check current data
console.log(echartsInstance.getOption())  // Shows current chart config

// Manual data load
loadAndChartData()  // Refresh chart

// Check data parsing
fetch('data/nasa_2025_01_january.csv')
  .then(r => r.text())
  .then(csv => console.log(csv.split('\n').slice(0, 5)))  // First 5 rows

// Manually select data
document.getElementById('sourceSelect').value = 'nasa'
document.getElementById('dataTypeSelect').value = 'temperature'
document.getElementById('dateRangeSelect').value = '01'
document.getElementById('chartTypeSelect').value = 'line'
loadAndChartData()
```

## ✅ Sign-Off Checklist

- [ ] Data Charts tab loads
- [ ] Default chart displays (Line, NASA, Temp, Jan)
- [ ] All 5 chart types work
- [ ] All 4 sources work
- [ ] All 5 data types work
- [ ] All 12 months work
- [ ] Tooltips show correct data
- [ ] Error handling works (fast dropdowns)
- [ ] No console errors
- [ ] Other pages unaffected
- [ ] Performance acceptable (<1s per chart)
- [ ] Responsive on resize
- [ ] Charts clear between selections

## 🐛 Troubleshooting

**Issue: Blank chart**
- Check browser console (F12 → Console tab)
- Verify CSV file exists: `data/[source]_2025_[MM]_[monthname].csv`
- Check network tab for 404 errors

**Issue: "Unable to load chart data"**
- CSV file not found or network error
- Verify file path in browser Network tab
- Check CORS if running from different origin

**Issue: Chart type doesn't change**
- Check if event listener attached: `document.getElementById('chartTypeSelect')`
- Verify dropdown value matches function names: 'line', 'scatter', 'box', 'histogram', 'heatmap'

**Issue: Data looks wrong**
- Verify CSV has correct columns: timestamp, temperature, humidity, irradiance, wind_speed, solar_energy_yield
- Check for empty rows or malformed data
- Run: `python3 validate_echarts.py`

**Issue: Performance slow**
- Chart initializing twice: Check for multiple event listeners
- Large dataset: Consider data sampling for very large files
- Browser memory: Refresh page if many charts loaded

## 📞 Support

For detailed implementation info, see:
- `ECHARTS_IMPLEMENTATION.md` - Feature overview
- `ECHARTS_CODE_ARCHITECTURE.md` - Code structure
- `validate_echarts.py` - Validation script
