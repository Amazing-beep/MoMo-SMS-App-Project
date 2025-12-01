let transactionsData = [];

async function fetchData() {
    try {
        const response = await fetch('/data/processed/dashboard.json');
        transactionsData = await response.json();
        updateDashboard(transactionsData);
    } catch (err) {
        console.error("Error fetching data:", err);
    }
}

function updateDashboard(data) {
    renderTable(data);
    renderChart(data);
    updateSummary(data);
}

function renderTable(data) {
    const tbody = document.querySelector('#transactionsTable tbody');
    tbody.innerHTML = '';
    data.forEach(tx => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${tx.id}</td>
            <td>${tx.date}</td>
            <td>${tx.phone}</td>
            <td>${tx.type}</td>
            <td>${tx.amount.toFixed(2)}</td>
            <td>${tx.category}</td>
        `;
        tbody.appendChild(tr);
    });
}

function renderChart(data) {
    const categories = ['High Value', 'Medium Value', 'Low Value'];
    const totals = categories.map(cat => 
        data.filter(tx => tx.category === cat)
            .reduce((sum, tx) => sum + tx.amount, 0)
    );

    const ctx = document.getElementById('transactionChart').getContext('2d');
    if (window.transactionChartInstance) window.transactionChartInstance.destroy();

    window.transactionChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categories,
            datasets: [{
                data: totals,
                backgroundColor: ['#e74c3c', '#f1c40f', '#2ecc71']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

function updateSummary(data) {
    const totalTransactions = data.length;
    const totalAmount = data.reduce((sum, tx) => sum + tx.amount, 0).toFixed(2);

    document.getElementById('totalTransactions').textContent = `Total Transactions: ${totalTransactions}`;
    document.getElementById('totalAmount').textContent = `Total Amount: ${totalAmount}`;
}

// Apply filters
document.getElementById('applyFilter').addEventListener('click', () => {
    const category = document.getElementById('categoryFilter').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    let filtered = transactionsData;

    if (category !== 'all') {
        filtered = filtered.filter(tx => tx.category === category);
    }
    if (startDate) {
        filtered = filtered.filter(tx => new Date(tx.date) >= new Date(startDate));
    }
    if (endDate) {
        filtered = filtered.filter(tx => new Date(tx.date) <= new Date(endDate));
    }

    updateDashboard(filtered);
});

fetchData();