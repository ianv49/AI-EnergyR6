# ECharts Code Architecture

## File Structure

```
index.html
├── HTML Head
│   ├── Style (CSS Grid 3-column layout)
│   └── Meta tags
├── Body
│   ├── Header (nav to ML pages)
│   ├── Tab Navigation
│   │   ├── ML Results (tab 1)
│   │   ├── Data Charts (tab 2) ← ECharts here
│   │   ├── Raw Data tabs
│   │   └── Simulation tabs
│   ├── ML Results Content
│   │   ├── Table (10 ML models)
│   │   └── CSV Export button
│   ├── Data Charts Content ← ISOLATED SECTION
│   │   ├── Sidebar (250px)
│   │   │   ├── sourceSelect dropdown
│   │   │   ├── dataTypeSelect dropdown
│   │   │   ├── dateRangeSelect dropdown
│   │   │   └── chartTypeSelect dropdown (NEW)
│   │   └── Main Area
│   │       └── id="dataChart" (ECharts container)
│   ├── Other Tabs Content
│   ├── Script (external)
│   │   └── script.js
│   └── ECharts Script (ISOLATED)
│       ├── CDN: echarts@5.4.3
│       ├── Configuration objects
│       ├── Chart rendering functions (5)
│       ├── Utility functions
│       └── Event listeners
```

## JavaScript Code Sections

### 1. Initialization & Constants (Lines 560-600)
```javascript
let echartsInstance = null;  // Global chart instance
const monthNames = {...}     // Month code to name mapping
const dataTypeLabels = {...} // Display labels for data types
const dataTypeUnits = {...}  // Units for y-axis
const colors = {...}         // Color scheme per source
```

### 2. Main Functions

#### loadAndChartData() - Lines 602-625
- Gets user selections from 4 dropdowns
- Constructs CSV filename
- Fetches CSV file
- Parses data
- Calls renderChart()

#### parseCSVData() - Lines 627-651
- Splits CSV by lines
- Extracts column indices
- Loops through data rows
- Returns timestamps and values array

#### renderChart() - Lines 653-675
- Clears previous chart
- Initializes ECharts instance
- Calls appropriate chart function
- Sets chart option
- Adds window resize listener

#### showError() - Lines 677-685
- Disposes previous chart
- Displays error message in container

### 3. Chart Type Functions

#### createLineChart() - Lines 687-718
- Smooth line with area fill
- No point markers
- Y-axis unit display
- Tooltip enabled

**Example Option Structure**:
```javascript
{
  title: { text: "NASA - January 2025 - Temperature (°C)" },
  xAxis: { type: 'category', data: timestamps },
  yAxis: { type: 'value', name: '°C' },
  series: [{
    type: 'line',
    data: values,
    smooth: 0.3,
    lineStyle: { width: 1.5 }
  }]
}
```

#### createScatterChart() - Lines 720-760
- Scatter plot with trendline
- Calls calculateTrendline()
- Two series: scatter + line
- Red dashed trendline

#### createBoxPlot() - Lines 762-809
- Quartile calculation
- IQR method for whiskers
- Outlier detection
- Single series with box + whiskers

#### createHistogram() - Lines 811-856
- Sturges' rule for bin count
- Bin frequency calculation
- Bar chart display
- Rotated labels (45°)

#### createHeatmap() - Lines 858-910
- Creates 24×calendar-day matrix
- Color gradient visualization
- Day-hour cell labels
- Visual map legend

### 4. Utility Functions

#### calculateTrendline() - Lines 912-921
- Linear regression formula
- Calculates slope and intercept
- Returns array of [x, y] points

### 5. Event Listeners & Init - Lines 923-931
```javascript
['sourceSelect', 'dataTypeSelect', 'dateRangeSelect', 'chartTypeSelect']
  .forEach(id => elem.addEventListener('change', loadAndChartData))

window.addEventListener('load', () => {
  setTimeout(loadAndChartData, 500)
})
```

## Data Flow Diagram

```
User Interaction
    ↓
[Dropdown Change Event]
    ↓
loadAndChartData()
    ├→ Get selections from DOM
    ├→ Construct CSV filename
    ├→ fetch(csvFile)
    │   ↓
    │   [CSV File]
    │   ↓
    ├→ parseCSVData()
    │   ├→ Split by newline
    │   ├→ Find column indices
    │   └→ Extract values & timestamps
    │
    ├→ Validate data (length > 0)
    ├→ renderChart()
    │   ├→ Clear old chart
    │   ├→ Create ECharts instance
    │   ├→ Get chart type
    │   │   ├→ createLineChart()
    │   │   ├→ createScatterChart()
    │   │   ├→ createBoxPlot()
    │   │   ├→ createHistogram()
    │   │   └→ createHeatmap()
    │   ├→ setOption() with chart config
    │   └→ Add resize listener
    │
    └→ [Chart Rendered on Screen]
```

## Configuration Pattern

Every chart follows this pattern:
```javascript
function createXXXChart(data, title, unit, source) {
  return {
    title: { /* title config */ },
    tooltip: { /* tooltip config */ },
    xAxis: { /* x-axis config */ },
    yAxis: { /* y-axis config */ },
    series: [ /* series config */ ],
    grid: { /* padding config */ }
  };
}
```

## Isolated Scope

The entire ECharts code is wrapped in:
```html
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<script>
  // ECharts code ONLY
  // Global: echarts library, echartsInstance variable
  // No Chart.js references
  // No conflict with external script.js
</script>
```

## Environment

- **Browser Context**: Client-side execution
- **Data Source**: Local CSV files in `/data/`
- **Async Operations**: fetch() for CSV loading
- **Error Handling**: try/catch with showError()
- **Performance**: One chart instance (reused via clear/setOption)
- **Memory**: Auto-cleanup on new chart (dispose previous)

## Customization Points

To modify behavior:

1. **Colors**: Edit `colors` object (line ~592)
2. **Chart dimensions**: Edit `grid: { left, right, top, bottom }` in each function
3. **Line smoothness**: Edit `smooth: 0.3` in createLineChart()
4. **Histogram bins**: Change Sturges' formula in createHistogram()
5. **Box plot whiskers**: Modify IQR multiplier (1.5) in createBoxPlot()
6. **Heatmap colors**: Change `inRange: { color: [...] }` in createHeatmap()
7. **Tooltips**: Modify `tooltip` config in each function
8. **Axis labels**: Modify `axisLabel` config

## Testing

Run validation:
```bash
python3 validate_echarts.py
```

Expected output:
```
✓ PASS: CSV Files (48 files, all valid)
✓ PASS: HTML Structure (all functions present)
✓ PASS: No Conflicts (isolated ECharts code)
```

Manual testing (browser):
1. Navigate to Data Charts tab
2. Try each chart type
3. Switch sources and data types
4. Verify responsive resizing
5. Check console for errors
