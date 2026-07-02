# FTA Wizard Testing Guide

## Testing Environment
- **Frontend:** http://localhost:3003
- **Backend:** http://localhost:8000
- **Wizard URL:** http://localhost:3003/fta-wizard

## Pre-Testing Setup

### ⚠️ Database Check
The database appears to be empty. Before testing, ensure tariff data is loaded:

```bash
# Check if HS codes exist
curl "http://localhost:8000/api/v1/tariff/autocomplete?query=85&country=US"

# If empty, you may need to:
# 1. Run database migrations
# 2. Seed tariff data
# 3. Load HS codes from CSV/JSON files
```

## Manual Testing Checklist

### Step 1: Trade Route Entry
**URL:** http://localhost:3003/fta-wizard

- [ ] **Visual Check**
  - [ ] Progress bar shows Step 1 as active (indigo)
  - [ ] Steps 2-4 are gray (future state)
  - [ ] Page title: "FTA Wizard"
  - [ ] Step heading: "Trade Route Details"

- [ ] **HS Code Autocomplete**
  - [ ] Type at least 4 characters in HS code field
  - [ ] Dropdown appears with matching suggestions
  - [ ] Click a suggestion - field populates
  - [ ] Selected HS code displays below input
  - [ ] Description shows in blue box

- [ ] **Origin Country**
  - [ ] Dropdown has 7 countries: CN, US, EU, JP, KR, MX, CA
  - [ ] Select "CN" (China)
  - [ ] Selection displays in summary box

- [ ] **Destination Country**
  - [ ] Dropdown has same 7 countries
  - [ ] Select "US" (United States)
  - [ ] Route summary shows: "[HS Code] • CN → US"

- [ ] **Validation**
  - [ ] Click "Next" with empty fields → See error toast
  - [ ] Click "Next" with only HS code → See error toast
  - [ ] Click "Next" with all fields filled → Loading spinner appears

- [ ] **FTA Check API Call**
  - [ ] Loading state shows: "Checking FTA Eligibility..."
  - [ ] API call to `/api/v1/tariff/fta-check`
  - [ ] On success → Advance to Step 2
  - [ ] On error → Show error toast with retry option

**Test Data:**
```
HS Code: 8517120000 (or any valid code in database)
Origin: CN (China)
Destination: US (United States)
Expected: FTA check should return eligibility status
```

---

### Step 2: Documentation Requirements
**Conditional:** This step's content depends on Step 1 FTA check result

#### Scenario A: FTA Eligible ✅

- [ ] **Visual Check**
  - [ ] Progress bar: Step 1 green (✓), Step 2 indigo (active), Steps 3-4 gray
  - [ ] Green banner: "✅ Eligible for [FTA Name]!"
  - [ ] Banner text explains FTA benefits
  - [ ] 3 expandable sections visible

- [ ] **Certificate of Origin Section**
  - [ ] Click to expand → Shows content
  - [ ] ChevronDown icon rotates 180°
  - [ ] Content includes 4 bullet points
  - [ ] Click again to collapse → Content hides

- [ ] **Direct Shipment Rules Section**
  - [ ] Expand/collapse works
  - [ ] Shows CN → US route in content
  - [ ] 4 bullet points about shipment rules

- [ ] **Product-Specific Rules Section**
  - [ ] Expand/collapse works
  - [ ] Shows HS code in content
  - [ ] 4 bullet points about origin rules

- [ ] **Navigation**
  - [ ] "Back" button returns to Step 1 (data persists)
  - [ ] "Calculate Savings" button advances to Step 3

#### Scenario B: FTA Not Eligible ❌

- [ ] **Visual Check**
  - [ ] Yellow warning banner appears
  - [ ] AlertCircle icon (warning)
  - [ ] Message: "No FTA Benefits Available"
  - [ ] Explains no agreement exists for this route

- [ ] **Navigation**
  - [ ] "Back" button returns to Step 1
  - [ ] "Continue to Calculation" button advances to Step 3
  - [ ] No documentation sections shown

---

### Step 3: Cost Savings Projection

- [ ] **Visual Check**
  - [ ] Progress bar: Steps 1-2 green (✓), Step 3 indigo (active), Step 4 gray
  - [ ] Heading: "Cost Savings Projection"
  - [ ] CIF Value input field visible

- [ ] **CIF Value Input**
  - [ ] Default value: $10,000
  - [ ] $ symbol prefix in input
  - [ ] Type different values → Calculations update in real-time
  - [ ] Helper text: "Cost, Insurance, and Freight value..."

- [ ] **Standard Rate Card (Left)**
  - [ ] Gray border and background
  - [ ] Badge: "MFN"
  - [ ] Shows CIF Value: $10,000
  - [ ] Shows Duty Rate: [X]% (from Step 1)
  - [ ] Calculates Customs Duty
  - [ ] Shows Total Cost = CIF + Duty

- [ ] **FTA Rate Card (Right)** - Only if FTA eligible
  - [ ] Green border and background
  - [ ] Badge: "[FTA Name]" (e.g., "USMCA")
  - [ ] Shows CIF Value: $10,000
  - [ ] Shows Duty Rate: [Y]% (preferential rate)
  - [ ] Calculates Customs Duty (lower than standard)
  - [ ] Shows Total Cost = CIF + Duty (lower than standard)

- [ ] **Savings Highlight** - Only if FTA eligible
  - [ ] Green gradient background
  - [ ] DollarSign icon
  - [ ] Large bold savings amount: "Save $[amount]"
  - [ ] Percentage: "[X]% savings with [FTA Name]"

- [ ] **Calculation Accuracy**
  ```
  Example with 10% standard rate, 0% FTA rate:
  CIF: $10,000
  Standard Duty: $10,000 × 0.10 = $1,000
  FTA Duty: $10,000 × 0.00 = $0
  Savings: $1,000 - $0 = $1,000
  Savings %: ($1,000 / $10,000) × 100 = 10%
  ```

- [ ] **Validation**
  - [ ] Enter 0 → Click "Next" → Error toast
  - [ ] Enter negative number → Error toast
  - [ ] Enter 10,000,001 → Error toast: "Cannot exceed $10,000,000"
  - [ ] Enter valid value → "Next" button advances

- [ ] **Navigation**
  - [ ] "Back" button returns to Step 2 (data persists)
  - [ ] "Review Summary" button advances to Step 4

---

### Step 4: Review Summary

- [ ] **Visual Check**
  - [ ] Progress bar: All steps green (✓)
  - [ ] Heading: "Review Summary"
  - [ ] 4 summary cards in 2×2 grid (desktop) or stacked (mobile)

- [ ] **Trade Route Card**
  - [ ] Globe icon (indigo background)
  - [ ] Shows HS Code
  - [ ] Shows Description
  - [ ] Shows Route: "CN → US"

- [ ] **FTA Status Card**
  - [ ] Shield icon
  - [ ] Green background if eligible, gray if not
  - [ ] Shows eligibility: "✅ Yes (USMCA)" or "❌ No"
  - [ ] Shows Standard Rate: [X]%
  - [ ] If eligible: Shows FTA Rate: [Y]%

- [ ] **Cost Summary Card**
  - [ ] DollarSign icon (blue background)
  - [ ] Shows CIF Value: $10,000
  - [ ] Shows Standard Cost: $[amount]
  - [ ] If eligible: Shows FTA Cost: $[lower amount]
  - [ ] If eligible: Shows Savings: $[amount] ([X]%)

- [ ] **Required Documents Card** - Only if FTA eligible
  - [ ] FileText icon (amber background)
  - [ ] 3 checklist items with green checkmarks:
    - [ ] Certificate of Origin
    - [ ] Direct Shipment Proof
    - [ ] Rules of Origin Compliance

- [ ] **Action Buttons Section**
  - [ ] Gray background container
  - [ ] Heading: "What would you like to do?"
  - [ ] 3 buttons in grid layout

- [ ] **Save Calculation Button**
  - [ ] Indigo background, Save icon
  - [ ] Click → SaveCalculationModal opens
  - [ ] Modal pre-filled with wizard data:
    - Name: [user enters]
    - Description: [optional]
    - HS Code: [from wizard]
    - Origin/Destination: [from wizard]
    - Tags: [optional]
  - [ ] Click "Save" → Success toast
  - [ ] Check SavedCalculationsSidebar → Calculation appears

- [ ] **Export PDF Button**
  - [ ] Gray background, Download icon
  - [ ] Click → PDF downloads
  - [ ] Filename: `fta-wizard-[HS_CODE]-[TIMESTAMP].pdf`
  - [ ] Open PDF → Verify contains:
    - HS code and description
    - Origin/destination countries
    - Rates (MFN and FTA if applicable)
    - Cost breakdown
    - Total cost
  - [ ] Success toast appears

- [ ] **Start New Button**
  - [ ] White background with border, RefreshCw icon
  - [ ] Click → Wizard resets to Step 1
  - [ ] All fields cleared
  - [ ] State reset to initial values

- [ ] **Back Button** (below action buttons)
  - [ ] Click → Returns to Step 3
  - [ ] All data persists

---

## Browser Compatibility Testing

### Desktop Browsers
- [ ] **Chrome** (latest)
- [ ] **Firefox** (latest)
- [ ] **Safari** (latest)
- [ ] **Edge** (latest)

Test in each browser:
- [ ] All 4 steps render correctly
- [ ] Progress bar displays properly
- [ ] Forms are functional
- [ ] API calls work
- [ ] Modals open/close correctly
- [ ] PDF export downloads

### Mobile Testing
- [ ] **iOS Safari** (iPhone)
  - [ ] Progress bar stacks vertically or displays appropriately
  - [ ] Form inputs accessible with mobile keyboard
  - [ ] Buttons are touch-friendly (min 44px)
  - [ ] Cards stack vertically
  - [ ] Modal fills screen appropriately

- [ ] **Android Chrome**
  - [ ] Same checks as iOS Safari

- [ ] **Responsive Breakpoints**
  - [ ] Desktop (≥1024px): 2×2 card grid
  - [ ] Tablet (768px-1023px): 2×2 or stacked
  - [ ] Mobile (<768px): All cards stack vertically

---

## Edge Cases & Error Handling

### Network Errors
- [ ] **Disconnect internet** → Make API call → Error toast appears
- [ ] Error message is user-friendly
- [ ] Retry option available (user can click "Next" again)

### API Failures
- [ ] **Backend down** → Start wizard → FTA check fails gracefully
- [ ] **Timeout** → Long-running request shows loading state
- [ ] **Invalid response** → Error handled without crash

### Data Validation
- [ ] **Empty HS code** → Cannot proceed
- [ ] **Missing country selection** → Validation error
- [ ] **Invalid CIF value** (0, negative, too large) → Clear error message
- [ ] **Special characters in CIF** → Only numbers accepted

### State Persistence
- [ ] Navigate Step 1 → 2 → 1 → Data persists
- [ ] Navigate Step 1 → 2 → 3 → 2 → Data persists
- [ ] Change CIF value → Back → Forward → CIF value unchanged
- [ ] Browser back button → Wizard state may reset (expected behavior)

### PDF Export Edge Cases
- [ ] **No internet** → PDF export fails gracefully
- [ ] **Large numbers** (millions) → Formatting correct in PDF
- [ ] **Long HS descriptions** → PDF layout not broken

---

## Performance Checks

- [ ] **Page Load Time** → < 2 seconds
- [ ] **API Response Time** → FTA check < 1 second
- [ ] **Form Input Response** → Real-time calculations update instantly
- [ ] **Step Transitions** → Smooth, no lag
- [ ] **PDF Generation** → < 3 seconds

---

## Accessibility Testing

- [ ] **Keyboard Navigation**
  - [ ] Tab through all form fields
  - [ ] Enter key submits forms
  - [ ] Arrow keys work in dropdowns
  - [ ] Escape closes modals

- [ ] **Screen Reader**
  - [ ] Form labels are announced
  - [ ] Error messages are announced
  - [ ] Button purposes are clear
  - [ ] Progress bar state is conveyed

- [ ] **Color Contrast**
  - [ ] Text is readable on all backgrounds
  - [ ] Green/red not only indicators (icons also used)

- [ ] **Focus Indicators**
  - [ ] Visible focus ring on all interactive elements
  - [ ] Focus order is logical

---

## Integration Testing

### SaveCalculationModal Integration
- [ ] Wizard data correctly passed to modal
- [ ] All fields pre-populated
- [ ] Save creates calculation in database
- [ ] Calculation appears in sidebar
- [ ] Loading calculation from sidebar works

### Export Integration
- [ ] PDF export endpoint receives correct data
- [ ] PDF contains all wizard information
- [ ] Currency formatting correct (USD)
- [ ] Number formatting uses locale (commas)

---

## Test Data Examples

### FTA Eligible Route
```
HS Code: 8517120000 (Mobile phones)
Origin: MX (Mexico)
Destination: US (United States)
Expected: USMCA eligible, 0% FTA rate vs 3% MFN
CIF: $50,000
Expected Savings: $1,500 (3%)
```

### FTA Not Eligible Route
```
HS Code: 8517120000 (Mobile phones)
Origin: CN (China)
Destination: EU (European Union)
Expected: No FTA, standard MFN rates apply
```

### High Value Shipment
```
CIF: $5,000,000
Standard Rate: 5%
FTA Rate: 0%
Expected Savings: $250,000
```

---

## Known Issues / Future Enhancements

- [ ] Database needs to be seeded with tariff data
- [ ] FTA eligibility rules may need refinement
- [ ] Documentation templates are hardcoded (future: database-driven)
- [ ] PDF template could be enhanced with FTA-specific formatting
- [ ] Could add "Save Draft" functionality for incomplete wizards
- [ ] Could add comparison across multiple destination countries

---

## Sign-Off Checklist

Before marking testing complete:
- [ ] All 4 steps work end-to-end
- [ ] FTA check API integration works
- [ ] Calculations are mathematically correct
- [ ] Save functionality creates calculation
- [ ] PDF export downloads successfully
- [ ] Mobile responsive design verified
- [ ] No console errors or warnings
- [ ] Browser compatibility confirmed
- [ ] Accessibility guidelines met
- [ ] Performance benchmarks met

---

## Bug Reporting Template

If you find issues, report with:
```
**Step:** [1/2/3/4]
**Action:** [What you did]
**Expected:** [What should happen]
**Actual:** [What actually happened]
**Browser:** [Chrome/Firefox/Safari/etc.]
**Screenshot:** [If applicable]
**Console Errors:** [From browser dev tools]
```
