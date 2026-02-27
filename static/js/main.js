// File upload handling
const imageInput = document.getElementById('images');
const jsonInput = document.getElementById('jsons');
const imageList = document.getElementById('imageList');
const jsonList = document.getElementById('jsonList');
const imageUploadArea = document.getElementById('imageUploadArea');
const jsonUploadArea = document.getElementById('jsonUploadArea');
const uploadForm = document.getElementById('uploadForm');
const previewBtn = document.getElementById('previewBtn');
const processBtn = document.getElementById('processBtn');
const clearBtn = document.getElementById('clearBtn');
const previewSection = document.getElementById('previewSection');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');
const projectNameInput = document.getElementById('projectName');

let imageFiles = [];
let jsonFiles = [];

// Display uploaded files
function displayFiles(files, listElement, fileType) {
    listElement.innerHTML = '';
    files.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <span>${file.name}</span>
            <button type="button" onclick="removeFile(${index}, '${fileType}')">✕ Remove</button>
        `;
        listElement.appendChild(fileItem);
    });
}

// Remove file from list
function removeFile(index, fileType) {
    if (fileType === 'image') {
        imageFiles.splice(index, 1);
        displayFiles(imageFiles, imageList, 'image');
    } else {
        jsonFiles.splice(index, 1);
        displayFiles(jsonFiles, jsonList, 'json');
    }
}

// Handle image file selection
imageInput.addEventListener('change', (e) => {
    const newFiles = Array.from(e.target.files);
    imageFiles = [...imageFiles, ...newFiles];
    displayFiles(imageFiles, imageList, 'image');
});

// Handle JSON file selection
jsonInput.addEventListener('change', (e) => {
    const newFiles = Array.from(e.target.files);
    jsonFiles = [...jsonFiles, ...newFiles];
    displayFiles(jsonFiles, jsonList, 'json');
});

// Drag and drop for images
imageUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    imageUploadArea.classList.add('dragover');
});

imageUploadArea.addEventListener('dragleave', () => {
    imageUploadArea.classList.remove('dragover');
});

imageUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    imageUploadArea.classList.remove('dragover');
    const newFiles = Array.from(e.dataTransfer.files);
    imageFiles = [...imageFiles, ...newFiles];
    displayFiles(imageFiles, imageList, 'image');
});

// Drag and drop for JSONs
jsonUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    jsonUploadArea.classList.add('dragover');
});

jsonUploadArea.addEventListener('dragleave', () => {
    jsonUploadArea.classList.remove('dragover');
});

jsonUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    jsonUploadArea.classList.remove('dragover');
    const newFiles = Array.from(e.dataTransfer.files);
    jsonFiles = [...jsonFiles, ...newFiles];
    displayFiles(jsonFiles, jsonList, 'json');
});

// Show error message
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    successMessage.style.display = 'none';
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

// Show success message
function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.style.display = 'block';
    errorMessage.style.display = 'none';
    setTimeout(() => {
        successMessage.style.display = 'none';
    }, 5000);
}

// Preview changes
previewBtn.addEventListener('click', async () => {
    const projectName = document.getElementById('projectName').value.trim();
    
    if (!projectName) {
        showError('Please enter a project name');
        return;
    }
    
    if (imageFiles.length === 0 && jsonFiles.length === 0) {
        showError('Please upload at least one file');
        return;
    }
    
    const formData = new FormData();
    formData.append('project_name', projectName);
    
    imageFiles.forEach(file => {
        formData.append('images', file);
    });
    
    jsonFiles.forEach(file => {
        formData.append('jsons', file);
    });
    
    loading.style.display = 'block';
    previewSection.style.display = 'none';
    
    try {
        const response = await fetch('/preview', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            // Check if response is JSON or HTML
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                throw new Error(data.error || 'Preview failed');
            } else {
                throw new Error(`Server error (${response.status}): ${response.statusText}`);
            }
        }
        
        const data = await response.json();
        displayPreview(data);
        loading.style.display = 'none';
        previewSection.style.display = 'block';
        
    } catch (error) {
        loading.style.display = 'none';
        showError(error.message || 'An error occurred while previewing');
    }
});

// Display preview
function displayPreview(data) {
    const previewImagesList = document.getElementById('previewImagesList');
    const previewJsonsList = document.getElementById('previewJsonsList');
    
    // Display images preview
    if (data.images && data.images.length > 0) {
        previewImagesList.innerHTML = '';
        data.images.forEach(item => {
            const previewItem = document.createElement('div');
            previewItem.className = 'preview-item';
            previewItem.innerHTML = `
                <span class="original-name">${item.original}</span>
                <span class="arrow">→</span>
                <span class="renamed-name">${item.renamed}</span>
            `;
            previewImagesList.appendChild(previewItem);
        });
        document.getElementById('previewImages').style.display = 'block';
    } else {
        document.getElementById('previewImages').style.display = 'none';
    }
    
    // Display JSONs preview
    if (data.jsons && data.jsons.length > 0) {
        previewJsonsList.innerHTML = '';
        data.jsons.forEach(item => {
            const previewItem = document.createElement('div');
            previewItem.className = 'preview-item';
            previewItem.innerHTML = `
                <span class="original-name">${item.original}</span>
                <span class="arrow">→</span>
                <span class="renamed-name">${item.renamed}</span>
            `;
            previewJsonsList.appendChild(previewItem);
        });
        document.getElementById('previewJsons').style.display = 'block';
    } else {
        document.getElementById('previewJsons').style.display = 'none';
    }
}

// Process and download
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const projectName = document.getElementById('projectName').value.trim();
    
    if (!projectName) {
        showError('Please enter a project name');
        return;
    }
    
    if (imageFiles.length === 0 && jsonFiles.length === 0) {
        showError('Please upload at least one file');
        return;
    }
    
    const formData = new FormData();
    formData.append('project_name', projectName);
    
    imageFiles.forEach(file => {
        formData.append('images', file);
    });
    
    jsonFiles.forEach(file => {
        formData.append('jsons', file);
    });
    
    loading.style.display = 'block';
    processBtn.disabled = true;
    
    try {
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            // Check if response is JSON or HTML
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                throw new Error(data.error || 'Processing failed');
            } else {
                // HTML error page or other format
                const text = await response.text();
                throw new Error(`Server error (${response.status}): ${response.statusText}`);
            }
        }
        
        // Download the file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${projectName}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        loading.style.display = 'none';
        processBtn.disabled = false;
        showSuccess('Files processed successfully! Download started.');
        
    } catch (error) {
        loading.style.display = 'none';
        processBtn.disabled = false;
        showError(error.message || 'An error occurred while processing files');
    }
});

// Clear all functionality
clearBtn.addEventListener('click', () => {
    // Clear project name
    projectNameInput.value = '';
    
    // Clear file arrays
    imageFiles = [];
    jsonFiles = [];
    
    // Clear file inputs
    imageInput.value = '';
    jsonInput.value = '';
    
    // Clear file lists
    imageList.innerHTML = '';
    jsonList.innerHTML = '';
    
    // Hide preview section
    previewSection.style.display = 'none';
    
    // Hide messages
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';
    
    // Show success message
    showSuccess('All fields cleared successfully!');
});
