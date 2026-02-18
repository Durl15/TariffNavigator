const API_BASE_URL = 'http://localhost:8000/api/v1';

async function calculateTariff() {
    const hsCode = document.getElementById('calcHSCode').value;
    const origin = document.getElementById('calcOrigin').value;
    const destination = document.getElementById('calcDestination').value;
    const value = document.getElementById('calcValue').value;
    const resultsDiv = document.getElementById('calcResults');
    
    if (!hsCode || !value) {
        resultsDiv.innerHTML = '<div style=\"color: red;\">Please fill in all fields</div>';
        return;
    }
    
    resultsDiv.innerHTML = '<div>Calculating...</div>';
    
    try {
        const response = await fetch(API_BASE_URL + '/tariffs/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                hs_code: hsCode,
                origin: origin,
                destination: destination,
                value: parseFloat(value)
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Calculation failed');
        }
        
        let html = '<h3>Results:</h3>';
        
        data.applicable_rates.forEach((rate) => {
            const isBest = data.best_rate && rate.rate_type === data.best_rate.rate_type;
            const dutyAmount = (value * rate.duty_rate / 100).toFixed(2);
            
            html += '<div style=\"border: 1px solid #ccc; padding: 15px; margin: 10px 0; border-radius: 5px; background: ' + (isBest ? '#e8f5e9' : '#f5f5f5') + '\">';
            html += '<h4>' + rate.rate_type + (isBest ? ' (BEST)' : '') + '</h4>';
            html += '<p><strong>Rate:</strong> ' + rate.duty_rate + '%</p>';
            html += '<p><strong>Duty:</strong> $' + dutyAmount + ' USD</p>';
            html += '</div>';
        });
        
        if (data.estimated_duty) {
            html += '<div style=\"background: #667eea; color: white; padding: 20px; border-radius: 5px; margin-top: 20px; text-align: center;\">';
            html += '<h3>Estimated Total Duty</h3>';
            html += '<p style=\"font-size: 2em; margin: 10px 0;\">$' + data.estimated_duty.toFixed(2) + ' USD</p>';
            html += '</div>';
        }
        
        resultsDiv.innerHTML = html;
    } catch (error) {
        resultsDiv.innerHTML = '<div style=\"color: red;\">Error: ' + error.message + '</div>';
    }
}

function searchHS() {
    alert('Search clicked! HS Code: ' + document.getElementById('hsSearch').value);
}
