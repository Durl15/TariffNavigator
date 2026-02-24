# 🌐 TariffNavigator - User Guide & Cheatsheet

**Welcome to TariffNavigator!** Your AI-powered tool for calculating import tariffs and managing international trade.

---

## 🚀 Quick Start

**Access the app**: Open your browser and go to the URL provided (e.g., `http://localhost:3000`)

**First time?** No account needed to use the calculator! Just start calculating.

---

## 📊 Features Overview

### 1. **Tariff Calculator** 🧮
Calculate import duties, VAT, and total landed costs

### 2. **Dashboard** 📈
View your calculation history and statistics

### 3. **Product Catalogs** 📦
Upload CSV files to analyze tariff impact on your entire product catalog

### 4. **Watchlists** 👀
Monitor specific HS codes and countries for tariff changes

### 5. **Notifications** 🔔
Get alerts when tariffs change for items you're watching

---

## 🧮 How to Use the Calculator

### Step 1: Select Destination
Choose where you're importing to:
- **China (CN)** - For imports to China
- **European Union (EU)** - For imports to EU countries

### Step 2: Choose Currency
Select your preferred currency:
- USD ($), CNY (¥), EUR (€), JPY (¥), GBP (£), KRW (₩)

### Step 3: Find Your Product
**Search by keyword or HS code:**
- Type product name: `"passenger car"` → Shows car HS codes
- Type HS code directly: `"8703"` → Shows exact match
- Click on a suggestion from the dropdown

**Popular searches:**
- `"passenger"` - Cars (8703.x)
- `"laptop"` - Computers (8471.30)
- `"phone"` or `"smartphone"` - Mobile phones (8517.12)
- `"footwear"` - Shoes (6402, 6403)
- `"jacket"` - Clothing (6203, 6204)
- `"furniture"` - Furniture (9403)

### Step 4: Enter CIF Value
Enter the **Cost, Insurance, and Freight** value in USD:
- Example: `50000` for a $50,000 shipment
- This is the total value including shipping and insurance

### Step 5: Calculate
Click **"Calculate in [Currency]"** button

### Step 6: View Results
See breakdown of:
- ✅ CIF Value (converted to your currency)
- ✅ Customs Duty (percentage + amount)
- ✅ VAT (percentage + amount)
- ✅ Total Landed Cost

### Step 7: Save (Optional)
- Click the **bookmark icon** (💾) at bottom-right to save your calculation
- Access saved calculations anytime from the sidebar

---

## 🎯 Common Use Cases

### Scenario 1: "I'm importing smartphones to China"
1. Destination: **China (CN)**
2. Search: **"smartphone"**
3. Select: **8517.12 - Mobile phones including smartphones**
4. CIF Value: **100000** (for $100k shipment)
5. Click Calculate
6. **Result**: $100,000 + $0 duty (0%) + $13,000 VAT (13%) = **$113,000 total**

### Scenario 2: "I'm importing cars to EU"
1. Destination: **European Union (EU)**
2. Search: **"passenger"**
3. Select: **8703 - Motor cars and other motor vehicles**
4. CIF Value: **50000** (for $50k shipment)
5. Click Calculate
6. **Result**: $50,000 + $5,000 duty (10%) + $11,000 VAT (20%) = **$66,000 total**

### Scenario 3: "I'm importing laptops to China"
1. Destination: **China (CN)**
2. Search: **"laptop"**
3. Select: **8471.30 - Portable automatic data processing machines**
4. CIF Value: **25000**
5. Click Calculate
6. **Result**: $25,000 + $0 duty (0%) + $3,250 VAT (13%) = **$28,250 total**

---

## 📦 Product Catalog Analyzer

**Upload a CSV of your products to analyze tariff impact across your entire catalog**

### How to use:
1. Go to **Catalogs** page
2. Click **"Upload Catalog"**
3. Prepare your CSV file with columns:
   ```
   SKU, Product Name, HS Code, Origin Country, Unit Cost, Annual Volume
   ```
4. Upload the file
5. View impact analysis:
   - Total tariff costs
   - Highest impact products
   - Cost breakdowns by category

### Example CSV:
```csv
SKU,Product Name,HS Code,Origin Country,Unit Cost,Annual Volume
SKU-001,Laptop Model X,8471.30,CN,800,1000
SKU-002,Smartphone Pro,8517.12,CN,600,2000
SKU-003,Running Shoes,6402,VN,45,5000
```

---

## 👀 Watchlists

**Monitor tariff changes for specific products/countries**

### How to create a watchlist:
1. Go to **Watchlists** page
2. Click **"+ Create Watchlist"**
3. Fill in details:
   - **Name**: "China Electronics" (descriptive name)
   - **HS Codes**: Add codes like `8517`, `8471`, `8528`
   - **Countries**: Add country codes like `CN`, `US`
4. Click **"Create Watchlist"**

### What happens next?
- 🔔 You'll get notified when tariffs change for these HS codes
- 📧 Daily/weekly digest emails (if enabled)
- 📊 Track historical changes

---

## 🔔 Notifications

**Stay informed about tariff changes**

### View notifications:
1. Click **bell icon** (🔔) in navigation bar
2. See all notifications
3. Filter by:
   - **Unread only** - Show only new notifications
   - **Type** - Rate changes, deadlines, new programs

### Notification types:
- **📊 Rate Change** - Tariff rates changed for watched items
- **⏰ Deadline** - Important trade deadline approaching
- **🎉 New Program** - New FTA or trade program available

---

## 📈 Dashboard

**View your calculation statistics**

### What you'll see:
- **Total Calculations** - All-time calculations
- **This Month** - Current month activity
- **Today** - Today's calculations
- **HS Codes** - Unique codes you've calculated
- **Popular HS Codes** - Most frequently calculated codes
- **Export CSV** - Download your calculation history

---

## 💡 Pro Tips

### 1. **Use Filters for Better Search**
Click **"Filters"** to narrow down search by:
- Category (Electronics, Textiles, Vehicles, etc.)
- Duty rate range (e.g., 0-10%)
- Sort by duty rate (high to low)

### 2. **Compare Multiple Scenarios**
- Open calculator in multiple tabs
- Compare different HS codes for same product
- Compare China vs EU duty rates

### 3. **Save Frequently Used Calculations**
- Use the bookmark button to save common calculations
- Quick access from saved calculations sidebar

### 4. **Export Your Data**
- Go to Dashboard → Click **"Export CSV"**
- Get all your calculations in Excel-compatible format

### 5. **Understand the Numbers**
- **MFN Rate** = Most Favored Nation rate (standard duty)
- **CIF Value** = Cost + Insurance + Freight (total value)
- **VAT** = Value Added Tax (calculated on CIF + Duty)

---

## 🌍 Supported Countries

### Currently Available:
- 🇨🇳 **China (CN)** - 24 HS codes
- 🇪🇺 **European Union (EU)** - 27 HS codes

### Coming Soon:
- 🇺🇸 United States
- 🇯🇵 Japan
- 🇬🇧 United Kingdom
- 🇮🇳 India

---

## 📱 Mobile Access

TariffNavigator is mobile-responsive:
- ✅ Works on smartphones
- ✅ Works on tablets
- ✅ Responsive navigation menu
- ✅ Touch-friendly interface

---

## 🆘 Troubleshooting

### "No results found" when searching?
- Try broader terms: "car" instead of "passenger car"
- Try HS code directly: "8703"
- Check if you selected the right country (CN/EU)

### Calculator button disabled?
- Make sure you've selected an HS code
- Make sure you've entered a CIF value
- Both fields must be filled

### Autocomplete not showing?
- Type at least 2 characters
- Wait a moment for results to load
- Check your internet connection

### Results seem wrong?
- Verify you entered CIF value in USD
- Double-check the HS code is correct for your product
- VAT is calculated on (CIF + Duty), not just CIF

---

## 🔑 Keyboard Shortcuts

- **Tab** - Navigate between form fields
- **Enter** - Submit calculation (when in CIF value field)
- **Esc** - Close autocomplete dropdown
- **↑/↓** - Navigate autocomplete suggestions

---

## 📞 Support & Resources

### Need Help?
- Check this guide first
- Review calculation examples above
- Contact the admin if issues persist

### Useful Links:
- **GitHub Repository**: https://github.com/Durl15/TariffNavigator
- **HS Code Database**: https://www.foreign-trade.com/reference/hscode.htm
- **WTO Tariff Database**: https://www.wto.org/english/tratop_e/tariffs_e/tariff_data_e.htm

---

## 🎓 Understanding HS Codes

**HS Code** = Harmonized System Code (international product classification)

### Structure:
- **2 digits** - Chapter (e.g., 87 = Vehicles)
- **4 digits** - Heading (e.g., 8703 = Motor cars)
- **6+ digits** - Subheading (e.g., 8703.21 = Cars, 1000-1500cc)

### Example: 8703.22
- **87** - Vehicles, aircraft, vessels
- **8703** - Motor cars and other motor vehicles
- **8703.22** - Cars with 1500-2000cc spark-ignition engines

### Finding Your HS Code:
1. Know your product details (material, function, size, etc.)
2. Search by product name in calculator
3. Read descriptions carefully
4. Choose the most specific code that matches
5. When in doubt, consult a customs broker

---

## 📊 Sample Calculations Reference

| Product | HS Code | Destination | Duty Rate | VAT Rate | Example |
|---------|---------|-------------|-----------|----------|---------|
| Smartphones | 8517.12 | China | 0% | 13% | $10k → $11.3k |
| Laptops | 8471.30 | China | 0% | 13% | $10k → $11.3k |
| Passenger Cars | 8703 | China | 15% | 13% | $50k → $64.5k |
| Passenger Cars | 8703 | EU | 10% | 20% | $50k → $66k |
| Footwear | 6402 | China | 13% | 13% | $5k → $6.4k |
| T-shirts | 6109 | China | 6% | 13% | $2k → $2.4k |

---

## 🎉 Getting Started Checklist

- [ ] Access the app URL
- [ ] Try a sample calculation (e.g., smartphone to China)
- [ ] Save a calculation for later
- [ ] Create a watchlist for products you frequently import
- [ ] Check the Dashboard to see your stats
- [ ] Bookmark the app for easy access
- [ ] Share with your team!

---

**Happy Calculating! 🚀**

*TariffNavigator - Making international trade calculations simple and transparent.*

---

**Version**: 1.0
**Last Updated**: February 2026
**Powered by**: AI & Real-time Tariff Data
