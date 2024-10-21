export function hideFlashMessage() {
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