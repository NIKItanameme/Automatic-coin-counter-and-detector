// DOM Elements
const tabWebcam = document.getElementById('tab-webcam');
const tabUpload = document.getElementById('tab-upload');
const webcamVideo = document.getElementById('webcam-video');
const uploadBox = document.getElementById('upload-box');
const uploadLabel = uploadBox.querySelector('.upload-label');
const coinInput = document.getElementById('coin-input');
const previewImg = document.getElementById('preview-img');
const upiInput = document.getElementById('upi-input');
const upiDisplay = document.getElementById('upi-display');
const savingsSlider = document.getElementById('savings-slider');
const savingsValueDisplay = document.getElementById('savings-value-display');
const manualInput = document.getElementById('manual-input');
const scanBtn = document.getElementById('scan-btn');
const viewfinderBox = document.getElementById('viewfinder-box');

// Stats metrics
const totalCoinsVal = document.getElementById('total-coins-val');
const totalVal = document.getElementById('total-val');
const goldVal = document.getElementById('gold-val');
const creditVal = document.getElementById('credit-val');

// Compliance & status
const statusBadge = document.getElementById('status-badge');
const oxidationVal = document.getElementById('oxidation-val');
const oxidationBarFill = document.getElementById('oxidation-bar-fill');
const statusMessage = document.getElementById('status-message');
const statusText = document.getElementById('status-text');

// Tables
const denomEmpty = document.getElementById('denom-empty-placeholder');
const denomTable = document.getElementById('denom-table');
const denomTableBody = document.getElementById('denom-table-body');

const savingsEmpty = document.getElementById('savings-empty-placeholder');
const savingsTable = document.getElementById('savings-table');
const savingsTableBody = document.getElementById('savings-table-body');

// State Variables
let activeMode = 'webcam';
let webcamStream = null;

// Initialize Live Webcam Stream
async function startWebcam() {
    if (webcamStream) return;
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment', width: { ideal: 640 }, height: { ideal: 480 } }
        });
        webcamStream = stream;
        webcamVideo.srcObject = stream;
        webcamVideo.style.display = 'block';
    } catch (err) {
        console.error("Camera access failed:", err);
        // Fallback to upload mode if camera is blocked/unavailable
        switchToUploadMode();
        alert("Unable to access the webcam. Defaulting to File Upload mode.");
    }
}

function stopWebcam() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
        webcamVideo.srcObject = null;
        webcamVideo.style.display = 'none';
    }
}

// Tab Switching
function switchToWebcamMode() {
    activeMode = 'webcam';
    tabWebcam.classList.add('active');
    tabUpload.classList.remove('active');
    uploadBox.style.style = 'none';
    uploadBox.style.display = 'none';
    startWebcam();
}

function switchToUploadMode() {
    activeMode = 'upload';
    tabUpload.classList.add('active');
    tabWebcam.classList.remove('active');
    stopWebcam();
    uploadBox.style.display = 'flex';
}

tabWebcam.addEventListener('click', switchToWebcamMode);
tabUpload.addEventListener('click', switchToUploadMode);

// File upload preview
coinInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const url = URL.createObjectURL(file);
        previewImg.src = url;
        previewImg.style.display = 'block';
        uploadLabel.style.display = 'none';
    } else {
        previewImg.style.display = 'none';
        uploadLabel.style.display = 'flex';
    }
});

// Dynamic values sync
upiInput.addEventListener('input', (e) => {
    upiDisplay.innerText = e.target.value || 'resident@rbi';
});

savingsSlider.addEventListener('input', (e) => {
    savingsValueDisplay.innerText = `${e.target.value}%`;
});

// Execute audit scan
scanBtn.addEventListener('click', async () => {
    let imageBlob = null;
    let fileName = 'scan.jpg';

    // 1. Collect Image Data based on active mode
    if (activeMode === 'webcam') {
        if (!webcamStream) {
            alert("Webcam is not running. Please start camera or upload a file.");
            return;
        }
        
        // Capture frame from video element
        const canvas = document.createElement('canvas');
        canvas.width = webcamVideo.videoWidth || 640;
        canvas.height = webcamVideo.videoHeight || 480;
        const ctx = canvas.getContext('2d');
        
        // Mirror back if drawing webcam
        ctx.translate(canvas.width, 0);
        ctx.scale(-1, 1);
        ctx.drawImage(webcamVideo, 0, 0, canvas.width, canvas.height);
        
        // Convert to blob
        imageBlob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.9));
        fileName = 'webcam-scan.jpg';
    } else {
        const file = coinInput.files[0];
        if (!file) {
            alert("Please choose a coin photo to upload first.");
            return;
        }
        imageBlob = file;
        fileName = file.name;
    }

    // 2. Build FormData parameters
    const formData = new FormData();
    formData.append('file', imageBlob, fileName);
    formData.append('savings_split', parseFloat(savingsSlider.value));
    formData.append('manual_total', parseFloat(manualInput.value) || 0);

    // 3. UI Scanning State
    scanBtn.disabled = true;
    scanBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing Audit...';
    viewfinderBox.classList.add('scanning');
    statusMessage.style.display = 'none';

    try {
        // Send request to backend
        const response = await fetch('/audit', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        // 4. Update UI Dashboard with Results
        renderResults(data);

    } catch (err) {
        console.error("Audit execution failed:", err);
        showStatusMessage(`Error executing deposit: ${err.message}`, true);
    } finally {
        scanBtn.disabled = false;
        scanBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Execute Smart Deposit';
        viewfinderBox.classList.remove('scanning');
    }
});

function renderResults(data) {
    // Basic metrics
    totalCoinsVal.innerText = data.count || 0;
    totalVal.innerText = `₹${(data.total || 0).toFixed(2)}`;
    goldVal.innerText = `₹${(data.savings || 0).toFixed(2)}`;
    creditVal.innerText = `₹${(data.upi_credit || 0).toFixed(2)}`;

    // Compliance Badge status
    const auditStatus = data.summary?.audit_status || 'FIT ✅';
    statusBadge.innerText = auditStatus;
    if (auditStatus.includes('FIT') && !auditStatus.includes('UNFIT')) {
        statusBadge.className = 'audit-badge fit';
        statusBadge.innerHTML = '<i class="fa-solid fa-circle-check"></i> ' + auditStatus;
    } else {
        statusBadge.className = 'audit-badge unfit';
        statusBadge.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> ' + auditStatus;
    }

    // Oxidation progress bar
    const oxStr = data.summary?.oxidation || '0.0%';
    const oxPercent = parseFloat(oxStr) || 0;
    oxidationVal.innerText = oxStr;
    oxidationBarFill.style.width = `${Math.min(oxPercent, 100)}%`;

    // Denomination Table
    if (data.denominations && Object.keys(data.denominations).length > 0) {
        denomEmpty.style.display = 'none';
        denomTable.style.display = 'table';
        denomTableBody.innerHTML = '';

        // Sort keys (denominations) descending
        const sortedDenoms = Object.keys(data.denominations).map(Number).sort((a, b) => b - a);
        sortedDenoms.forEach(denom => {
            const qty = data.denominations[denom];
            const subtotal = denom * qty;
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>₹${denom} Coin</td>
                <td class="mono-text">${qty}</td>
                <td class="mono-text" style="text-align: right; font-weight: 600;">₹${subtotal.toFixed(2)}</td>
            `;
            denomTableBody.appendChild(tr);
        });
    } else {
        denomEmpty.style.display = 'flex';
        denomTable.style.display = 'none';
    }

    // Savings Asset Distribution Table
    if (data.distribution) {
        savingsEmpty.style.display = 'none';
        savingsTable.style.display = 'table';
        savingsTableBody.innerHTML = '';

        const dist = data.distribution;
        const rows = [
            { label: 'UPI Wallet Credit', value: dist.upi_wallet, icon: 'fa-wallet', class: '' },
            { label: 'Digital Gold (SIP)', value: dist.digital_gold, icon: 'fa-coins', class: 'text-amber-400' },
            { label: 'Impact Fund (Charity 5%)', value: dist.impact_fund || 0, icon: 'fa-heart', class: 'text-red-400' },
            { label: 'Mint Condition Bonus', value: dist.mint_bonus || 0, icon: 'fa-gift', class: 'text-emerald-400' },
            { label: 'Net Transaction Value', value: dist.net_credit, icon: 'fa-file-invoice-dollar', class: 'font-weight: 700;' }
        ];

        rows.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="${row.class}"><i class="fa-solid ${row.icon}" style="margin-right: 0.5rem; opacity: 0.85;"></i> ${row.label}</td>
                <td class="mono-text ${row.class}" style="text-align: right; font-weight: 600;">₹${(row.value || 0).toFixed(2)}</td>
            `;
            savingsTableBody.appendChild(tr);
        });
    } else {
        savingsEmpty.style.display = 'flex';
        savingsTable.style.display = 'none';
    }

    // Success Status Notification
    showStatusMessage(`Verified Deposit: ₹${(data.total || 0).toFixed(2)} successfully credited.`, false);
}

function showStatusMessage(text, isError = false) {
    statusText.innerText = text;
    if (isError) {
        statusMessage.className = 'status-panel error';
        statusMessage.querySelector('i').className = 'fa-solid fa-circle-xmark';
    } else {
        statusMessage.className = 'status-panel';
        statusMessage.querySelector('i').className = 'fa-solid fa-circle-check';
    }
    statusMessage.style.display = 'flex';
}

// Auto-start webcam on load
window.addEventListener('DOMContentLoaded', () => {
    startWebcam();
});