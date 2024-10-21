function updateFileName() {
    const fileInput = document.getElementById("file-upload");
    const fileName = document.getElementById("file-name");
    console.log("File selected:", fileInput.files[0].name);  // Check if the file name is updated
    fileName.textContent = fileInput.files.length ? fileInput.files[0].name : "No file chosen";
}

export function showSpinner() {
    document.getElementById("loading-spinner").style.display = "block";
}