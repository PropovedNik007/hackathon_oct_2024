
import { updateFileName, showSpinner } from './fileUploadTemp.js';
import { hideFlashMessage } from './flashMessages.js';
import { updateProgressBar } from './progressBar.js';
import { createCategoryChart } from './chart.js';

window.onload = function() {
    hideFlashMessage();
    updateProgressBar();
    createCategoryChart(); 
};

document.getElementById('file-upload').addEventListener('change', updateFileName);
document.getElementById('upload-form').addEventListener('submit', showSpinner);