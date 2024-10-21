function updateFileName() {
    const fileInput = document.getElementById("file-upload");
    const fileName = document.getElementById("file-name");
    fileName.textContent = fileInput.files.length ? fileInput.files[0].name : "No file chosen";
}

// Show loading spinner when the form is submitted
function showSpinner() {
    document.getElementById("loading-spinner").style.display = "block";
}

// Hide flash message after 5 seconds
function hideFlashMessage() {
    const flashMessage = document.querySelector('.flash-messages');
    if (flashMessage) {
        setTimeout(() => {
            flashMessage.style.opacity = '0';
            flashMessage.style.transition = 'opacity 0.5s ease-out';
            setTimeout(() => {
                flashMessage.remove();
            }, 500);  // Remove from DOM after fading out
        }, 3000); // Adjust the duration here (5000ms = 5 seconds)
    }
}

// Update progress bar dynamically based on the score
function updateProgressBar() {
    const scoreElement = document.getElementById('score-value');
    const scoreValue = parseInt(scoreElement.innerText, 10) || 0;  // Get score from hidden element
    const progressBar = document.querySelector('.progress-bar-fill');
    const progressText = document.querySelector('.progress-text');

    if (progressBar && progressText) {
        progressBar.style.width = scoreValue + '%';  // Update the progress bar width
        progressText.textContent = scoreValue + '/100';  // Update the progress text
    }
}

window.onload = function() {
    hideFlashMessage();
    updateProgressBar();
    createCategoryChart(); // Make sure the chart is created after the page loads
};

function createCategoryChart() {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    // Example data, replace this with dynamic data when ready
    const categoryData = {
        labels: ['Lesser Evil', 'Lack of Accuracy', 'Lack of Transmission into Real Product Features', 'Lack of Evidence', 'Hidden Alternative Costs'],
        datasets: [{
            label: 'Category Frequency',
            data: [5, 8, 3, 7, 2], // Replace with real data dynamically
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