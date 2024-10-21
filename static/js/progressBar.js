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