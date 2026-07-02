# Testing Guide - Tier 1 Quick Wins

## Quick Start

**Option 1: Use the startup script**
```bash
# Double-click or run:
start-testing.bat
```

**Option 2: Manual startup**

Terminal 1 (Backend):
```bash
cd C:/Projects/TariffNavigator/backend
pyenv local 3.12.0
uvicorn main:app --reload --port 8000
```

Terminal 2 (Frontend):
```bash
cd C:/Projects/TariffNavigator/frontend
npm run dev
```

Then open: **http://localhost:5173**

---

## Testing Checklist

### ✅ Test 1: Dashboard UI (2 minutes)

**URL:** http://localhost:5173/dashboard

**What to check:**
- [ ] 4 stat cards display with icons
  - Total Calculations: 0
  - This Month: 0
  - Today: 0
  - HS Codes: 9
- [ ] "Popular HS Codes" section visible
- [ ] "Supported Countries" badges: CN, EU, US
- [ ] Two buttons: "New Calculation" and "Export CSV"
- [ ] Page is responsive (try resizing browser)

**Expected behavior:** Stats load within 2 seconds, page looks professional with Tailwind styling

---

### ✅ Test 2: PDF Export (3 minutes)

**URL:** http://localhost:5173/

**Steps:**
1. Enter test data:
   - HS Code: `8517130000`
   - Country: `CN`
   - CIF Value: `10000`
   - Currency: `USD`
2. Click "Calculate in USD"
3. Wait for results
4. Click "Export PDF Report" (blue button)

**What to check:**
- [ ] Button shows loading spinner: "Generating PDF..."
- [ ] Success toast notification appears
- [ ] PDF downloads: `tariff_report_8517130000_YYYY-MM-DD.pdf`
- [ ] PDF opens and shows:
  - Header: "Tariff Calculation Report"
  - HS Code: 8517130000
  - Description: Smartphones
  - Rates table (MFN: 0%, VAT: 13%)
  - Cost calculation table
  - Total: $11,300.00 USD
  - Disclaimer at bottom

**Expected behavior:** PDF generates in <3 seconds, downloads automatically

---

### ✅ Test 3: Search Filters (2 minutes)

**URL:** http://localhost:5173/

**Steps:**
1. Click "Filters" to expand filter panel
2. Click "Electronics" category badge
3. Enter "85" in HS code search
4. Set Min Rate: 0, Max Rate: 10
5. Change Sort to "Duty Rate: Low to High"
6. Click "Clear all"

**What to check:**
- [ ] Filter panel expands/collapses smoothly
- [ ] Category badge turns blue when selected
- [ ] Filter counter shows: "Filters (X active)"
- [ ] Search results update based on filters
- [ ] Sort changes result order
- [ ] Clear all resets everything

**Expected behavior:** Filters apply instantly, UI is responsive

---

### ✅ Test 4: Navigation (1 minute)

**Steps:**
1. Start on calculator page (/)
2. Click "Dashboard" button (top right)
3. Should navigate to /dashboard
4. Click "New Calculation" button
5. Should return to /

**What to check:**
- [ ] Dashboard button visible on calculator
- [ ] Navigation works without page reload
- [ ] URL updates correctly
- [ ] No console errors

---

### ✅ Test 5: Backend API (1 minute)

Open a terminal and test endpoints:

```bash
# Test public stats
curl http://localhost:8000/api/v1/stats/public

# Test enhanced search
curl "http://localhost:8000/api/v1/tariff/search?code=8517&country=CN&sort_by=rate_asc"

# Test PDF generation
curl -o test.pdf http://localhost:8000/api/v1/export/test-pdf

# Test popular HS codes
curl http://localhost:8000/api/v1/stats/public/popular-hs-codes
```

**What to check:**
- [ ] All endpoints return valid JSON (except PDF)
- [ ] No 500 errors
- [ ] Response times < 1 second

---

## Browser Console Check

**Open DevTools (F12) → Console tab**

Should see:
- ✅ No red errors
- ✅ No React warnings
- ⚠️ WeasyPrint warning is OK (using ReportLab fallback)

---

## Known Issues (Expected)

1. **CSV Export Button:** Will fail without authentication (requires JWT token)
   - This is expected - CSV export needs logged-in user
   - Dashboard will show error toast: "Failed to export CSV"

2. **Empty Popular HS Codes:** If no calculations exist yet
   - Expected with fresh database
   - Will show: "No popular HS codes yet"

3. **PDF Styling:** Using ReportLab (simpler than WeasyPrint)
   - Professional but less fancy than WeasyPrint
   - This is expected on Windows without GTK libraries

---

## Success Criteria

**All features PASS if:**
- ✅ Dashboard loads and displays stats
- ✅ PDF export downloads a valid PDF file
- ✅ Search filters expand and categories are clickable
- ✅ Navigation between pages works
- ✅ No critical errors in browser console
- ✅ Backend responds to all API endpoints

**Ready for production if ALL tests pass!**

---

## Troubleshooting

**Backend won't start:**
```bash
# Make sure Python version is set
cd backend
pyenv local 3.12.0
pip install -r requirements.txt
```

**Frontend won't start:**
```bash
# Make sure dependencies are installed
cd frontend
npm install
```

**Port already in use:**
```bash
# Backend - use different port
uvicorn main:app --reload --port 8001

# Frontend - Vite will auto-increment port (5173 → 5174)
```

**PDF generation fails:**
```bash
# Make sure ReportLab is installed
pip install reportlab
```

---

## After Testing

Once all tests pass:
1. Stop both servers (Ctrl+C in terminals)
2. Report results: "working" or describe any issues
3. Ready to push to production!
