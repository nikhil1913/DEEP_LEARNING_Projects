/**
 * EcoSort AI — Waste Classifier Frontend Logic
 * Handles image upload, camera capture, and API communication
 */

// ─── DOM Elements ────────────────────────────────────────────────────────────
const elements = {
    // Mode
    modeToggle: document.getElementById('modeToggle'),
    btnUploadMode: document.getElementById('btnUploadMode'),
    btnCameraMode: document.getElementById('btnCameraMode'),

    // Upload
    uploadArea: document.getElementById('uploadArea'),
    dropZone: document.getElementById('dropZone'),
    fileInput: document.getElementById('fileInput'),

    // Camera
    cameraArea: document.getElementById('cameraArea'),
    cameraFeed: document.getElementById('cameraFeed'),
    cameraCanvas: document.getElementById('cameraCanvas'),
    captureBtn: document.getElementById('captureBtn'),

    // Preview
    previewArea: document.getElementById('previewArea'),
    previewImage: document.getElementById('previewImage'),
    clearBtn: document.getElementById('clearBtn'),
    predictBtn: document.getElementById('predictBtn'),
    predictBtnText: document.querySelector('.predict-btn-text'),
    predictLoader: document.getElementById('predictLoader'),

    // Results
    resultsSection: document.getElementById('resultsSection'),
    recyclabilityBadge: document.getElementById('recyclabilityBadge'),
    badgeIcon: document.getElementById('badgeIcon'),
    badgeLabel: document.getElementById('badgeLabel'),
    predictedClass: document.getElementById('predictedClass'),
    confidenceValue: document.getElementById('confidenceValue'),
    confidenceFill: document.getElementById('confidenceFill'),
    categoryCard: document.getElementById('categoryCard'),
    categoryIcon: document.getElementById('categoryIcon'),
    categoryTitle: document.getElementById('categoryTitle'),
    categoryDesc: document.getElementById('categoryDesc'),
    disposalTip: document.getElementById('disposalTip'),
    predictionsList: document.getElementById('predictionsList'),
    tryAgainBtn: document.getElementById('tryAgainBtn'),

    // Background
    bgParticles: document.getElementById('bgParticles'),
};

// ─── State ───────────────────────────────────────────────────────────────────
let currentMode = 'upload';
let currentFile = null;
let cameraStream = null;

// ─── Initialize ──────────────────────────────────────────────────────────────
function init() {
    createParticles();
    setupModeToggle();
    setupDropZone();
    setupCamera();
    setupPreview();
    setupResults();
}

// ─── Background Particles ────────────────────────────────────────────────────
function createParticles() {
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        const size = Math.random() * 4 + 2;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDuration = (Math.random() * 15 + 10) + 's';
        particle.style.animationDelay = (Math.random() * 10) + 's';
        elements.bgParticles.appendChild(particle);
    }
}

// ─── Mode Toggle ─────────────────────────────────────────────────────────────
function setupModeToggle() {
    elements.btnUploadMode.addEventListener('click', () => switchMode('upload'));
    elements.btnCameraMode.addEventListener('click', () => switchMode('camera'));
}

function switchMode(mode) {
    currentMode = mode;

    // Update buttons
    elements.btnUploadMode.classList.toggle('active', mode === 'upload');
    elements.btnCameraMode.classList.toggle('active', mode === 'camera');

    // Show/hide areas
    if (mode === 'upload') {
        elements.uploadArea.classList.remove('hidden');
        elements.cameraArea.classList.add('hidden');
        stopCamera();
    } else {
        elements.uploadArea.classList.add('hidden');
        elements.cameraArea.classList.remove('hidden');
        startCamera();
    }

    // Hide preview and results when switching
    clearPreview();
    hideResults();
}

// ─── Drop Zone (Upload) ─────────────────────────────────────────────────────
function setupDropZone() {
    const dropZone = elements.dropZone;

    // Click to browse
    dropZone.addEventListener('click', () => elements.fileInput.click());

    // File selected
    elements.fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // Drag events
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });
}

function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file (JPG, PNG, WEBP)');
        return;
    }

    currentFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        elements.previewImage.src = e.target.result;
        showPreview();
    };
    reader.readAsDataURL(file);
}

// ─── Camera ──────────────────────────────────────────────────────────────────
function setupCamera() {
    elements.captureBtn.addEventListener('click', captureImage);
}

async function startCamera() {
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment', width: { ideal: 640 }, height: { ideal: 480 } }
        });
        elements.cameraFeed.srcObject = cameraStream;
    } catch (err) {
        console.error('Camera error:', err);
        alert('Could not access camera. Please check permissions or try uploading an image.');
        switchMode('upload');
    }
}

function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
        elements.cameraFeed.srcObject = null;
    }
}

function captureImage() {
    const video = elements.cameraFeed;
    const canvas = elements.cameraCanvas;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');
    // Mirror the image to match video display
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0);
    ctx.setTransform(1, 0, 0, 1, 0, 0);

    canvas.toBlob((blob) => {
        currentFile = new File([blob], 'capture.jpg', { type: 'image/jpeg' });
        elements.previewImage.src = canvas.toDataURL('image/jpeg');
        showPreview();
        stopCamera();
    }, 'image/jpeg', 0.9);
}

// ─── Preview ─────────────────────────────────────────────────────────────────
function setupPreview() {
    elements.clearBtn.addEventListener('click', () => {
        clearPreview();
        hideResults();
        if (currentMode === 'camera') {
            startCamera();
        }
    });

    elements.predictBtn.addEventListener('click', classifyImage);
}

function showPreview() {
    elements.uploadArea.classList.add('hidden');
    elements.cameraArea.classList.add('hidden');
    elements.previewArea.classList.remove('hidden');
    hideResults();
}

function clearPreview() {
    elements.previewArea.classList.add('hidden');
    elements.previewImage.src = '';
    currentFile = null;
    elements.fileInput.value = '';

    if (currentMode === 'upload') {
        elements.uploadArea.classList.remove('hidden');
    } else {
        elements.cameraArea.classList.remove('hidden');
    }
}

// ─── Classification ──────────────────────────────────────────────────────────
async function classifyImage() {
    if (!currentFile) return;

    // Show loading
    elements.predictBtnText.classList.add('hidden');
    elements.predictLoader.classList.remove('hidden');
    elements.predictBtn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('file', currentFile);

        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data.prediction);
        } else {
            alert('Prediction failed: ' + (data.error || 'Unknown error'));
        }
    } catch (err) {
        console.error('API error:', err);
        alert('Could not connect to the server. Make sure the backend is running.');
    } finally {
        // Reset button
        elements.predictBtnText.classList.remove('hidden');
        elements.predictLoader.classList.add('hidden');
        elements.predictBtn.disabled = false;
    }
}

// ─── Display Results ─────────────────────────────────────────────────────────
function displayResults(prediction) {
    const isRecyclable = prediction.recyclable;
    const resultsCard = elements.resultsSection.querySelector('.results-card');

    // Reset classes
    resultsCard.classList.remove('recyclable', 'non-recyclable');
    elements.recyclabilityBadge.classList.remove('recyclable', 'non-recyclable');
    elements.categoryCard.classList.remove('recyclable-card', 'non-recyclable-card');

    // Set recyclability badge
    if (isRecyclable) {
        elements.recyclabilityBadge.classList.add('recyclable');
        resultsCard.classList.add('recyclable');
        elements.badgeIcon.textContent = '♻️';
        elements.badgeLabel.textContent = 'Recyclable';
        elements.categoryCard.classList.add('recyclable-card');
        elements.categoryIcon.textContent = '♻️';
        elements.categoryTitle.textContent = 'Recyclable Waste';
        elements.categoryDesc.textContent = 'This item can be recycled. Please dispose in the recycling bin.';
    } else {
        elements.recyclabilityBadge.classList.add('non-recyclable');
        resultsCard.classList.add('non-recyclable');
        elements.badgeIcon.textContent = '🚫';
        elements.badgeLabel.textContent = 'Non-Recyclable';
        elements.categoryCard.classList.add('non-recyclable-card');
        elements.categoryIcon.textContent = '🗑️';
        elements.categoryTitle.textContent = 'Non-Recyclable Waste';
        elements.categoryDesc.textContent = 'This item cannot be recycled. Dispose in general waste.';
    }

    // Set predicted class
    elements.predictedClass.textContent = prediction.display_name;

    // Set confidence
    const confidence = prediction.confidence;
    elements.confidenceValue.textContent = confidence.toFixed(1) + '%';
    elements.confidenceFill.className = 'confidence-fill';
    if (confidence < 40) {
        elements.confidenceFill.classList.add('low');
        elements.confidenceValue.style.color = 'var(--red-400)';
    } else if (confidence < 70) {
        elements.confidenceFill.classList.add('medium');
        elements.confidenceValue.style.color = 'var(--amber-400)';
    } else {
        elements.confidenceValue.style.color = 'var(--green-400)';
    }

    // Animate confidence bar
    setTimeout(() => {
        elements.confidenceFill.style.width = confidence + '%';
    }, 100);

    // Set disposal tip
    elements.disposalTip.textContent = prediction.disposal_tip;

    // Set top 3 predictions
    elements.predictionsList.innerHTML = '';
    prediction.top_3.forEach((pred, index) => {
        const item = document.createElement('div');
        item.classList.add('prediction-item');

        const typeBadgeClass = pred.recyclable ? 'recyclable' : 'non-recyclable';
        const typeBadgeText = pred.recyclable ? 'Recycle' : 'General';

        item.innerHTML = `
            <div class="prediction-rank">${index + 1}</div>
            <span class="prediction-name">${pred.display_name}</span>
            <span class="prediction-type-badge ${typeBadgeClass}">${typeBadgeText}</span>
            <span class="prediction-conf">${pred.confidence.toFixed(1)}%</span>
        `;
        elements.predictionsList.appendChild(item);
    });

    // Show results
    elements.resultsSection.classList.remove('hidden');

    // Scroll to results
    setTimeout(() => {
        elements.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 200);
}

function hideResults() {
    elements.resultsSection.classList.add('hidden');
    elements.confidenceFill.style.width = '0%';
}

// ─── Results Actions ─────────────────────────────────────────────────────────
function setupResults() {
    elements.tryAgainBtn.addEventListener('click', () => {
        clearPreview();
        hideResults();
        if (currentMode === 'camera') {
            startCamera();
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// ─── Start ───────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', init);
