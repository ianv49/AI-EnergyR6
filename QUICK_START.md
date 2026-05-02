# Quick Start - ECharts Data Visualization

## 🚀 Get Started in 30 Seconds

### 1. Open Dashboard
```bash
open /Users/ianvallejo/Documents/GitHub/AI-EnergyR6/index.html
```
Or open the file in your browser.

### 2. Click "Data Charts" Tab
Located at the top of the page (2nd tab after "ML Results")

### 3. Select Visualization
- **Source Data**: NASA, OpenMeteo, MeteoStat, WeatherBit
- **Data Type**: Temperature, Humidity, Irradiance, Wind Power, Solar Energy
- **Date**: January - December 2025
- **Chart Type**: Line, Scatter+Trendline, Box Plot, Histogram, Heatmap

### 4. View Chart
Chart updates automatically as you change selections.

---

## 📊 Chart Types Explained

| Type | What It Shows | Best For |
|------|---------------|----------|
| **Line** | Trend over time | Seeing changes throughout month |
| **Scatter** | Data pattern with best-fit line | Finding linear relationships |
| **Box Plot** | Data spread (quartiles) | Understanding distribution |
| **Histogram** | Frequency distribution | Seeing how often values appear |
| **Heatmap** | Daily patterns by hour | Spotting daily cycles |

---

## 🎯 Common Tasks

### View Temperature Trend (Line Chart)
1. Select: NASA → Temperature → January
2. Chart Type: Line (default)
3. Observe: Temperature trend throughout January

### Compare Data Sources
1. Select: Data Type (e.g., Irradiance) → Month (June)
2. Change Chart Type to any type
3. Switch Source to see different colors (NASA=Cyan, OpenMeteo=Amber, etc.)

### Analyze Wind Pattern
1. Select: Wind Power → January
2. Chart Type: Heatmap
3. Observe: Hour/day grid shows wind distribution

### Check Data Distribution
1. Select: Solar Energy → July
2. Chart Type: Histogram
3. Observe: How often each energy level occurs

---

## 🔍 Understanding the Heatmap

```
        Hour  →  0:00  1:00  2:00 ... 23:00
Day ↓
Day 1:  ░░░░░░░░░░████████░░░░░░░░░░
Day 2:  ░░░░░░░░░░████████░░░░░░░░░░
...
Day 31: ░░░░░░░░░░████████░░░░░░░░░░

Dark (░) = Low values
Light (████) = High values
```

Good for spotting:
- Daily cycles (temperature, solar energy)
- Night vs day patterns
- Unusual days

---

## ⚡ Keyboard Shortcuts (in browser)

| Shortcut | Action |
|----------|--------|
| `F12` | Open developer console (for debugging) |
| `Ctrl/Cmd + R` | Refresh page |
| `Tab` | Move between dropdowns |

---

## 🛠️ Troubleshooting

**Chart not showing?**
- Wait 1-2 seconds for data to load
- Check if file exists: `data/[source]_2025_[month]_[monthname].csv`
- Refresh page (Ctrl+R)

**Wrong data?**
- Verify month selected (01=January, 12=December)
- Check data type matches unit on y-axis
- Confirm source color matches selection

**Slow performance?**
- Close other tabs/apps
- Refresh browser
- Use simpler chart types (Line is fastest)

---

## 📚 Documentation

For detailed info:
- **Features**: `ECHARTS_IMPLEMENTATION.md`
- **Code Details**: `ECHARTS_CODE_ARCHITECTURE.md`
- **Full Testing**: `TEST_GUIDE.md`
- **Status Report**: `FINAL_STATUS_REPORT.md`

---

## ✅ Quick Validation

Run this command to verify everything is installed correctly:

```bash
python3 validate_echarts.py
```

Expected output: All tests PASS ✓

---

## 🎨 Color Legend

| Color | Source |
|-------|--------|
| 🔵 Cyan | NASA |
| 🟠 Amber | OpenMeteo |
| 🟢 Green | MeteoStat |
| 🟣 Purple | WeatherBit |

---

## 💡 Pro Tips

1. **Heatmap heat**: Most useful for finding daily patterns
2. **Scatter + Trendline**: Great for regression analysis
3. **Histogram**: Use for June data (highest variety)
4. **Box Plot**: Compare across months (select same source/type, change month)
5. **Hover for details**: Tooltips show exact values on all charts

---

## 🚀 That's It!

You're ready to explore the data. Start by selecting different combinations and see what patterns emerge.

For detailed testing procedures, see `TEST_GUIDE.md`.
