export function createCategoryChart() {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    // Example data
    const categoryData = {
        labels: ['Lesser Evil', 'Lack of Accuracy', 'Lack of Transmission into Real Product Features', 'Lack of Evidence', 'Hidden Alternative Costs'],
        datasets: [{
            label: 'Category Frequency',
            data: [5, 8, 3, 7, 2], // Replace with real 
            backgroundColor: [
                'rgba(0, 102, 255, 0.8)', // Lesser Evil (Blue)
                'rgba(255, 87, 34, 0.8)', // Lack of Accuracy (Orange)
                'rgba(153, 102, 255, 0.8)', // Lack of Real Product Features (Purple)
                'rgba(255, 99, 132, 0.8)', // Lack of Evidence (Red)
                'rgba(128, 128, 128, 0.8)' // Hidden Alternative Costs (Grey)
            ],
            borderColor: [
                'rgba(0, 102, 255, 1)', 
                'rgba(255, 87, 34, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 99, 132, 1)',
                'rgba(128, 128, 128, 1)'
            ],
            borderWidth: 1
        }]
    };

    const categoryChart = new Chart(ctx, {
        type: 'bar',
        data: categoryData,
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Frequency'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Categories'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}