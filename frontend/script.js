const video = document.createElement('video');
const canvas = document.createElement('canvas');
const scanBtn = document.getElementById('scan-btn');
const coinInput = document.getElementById('coin-input');

// Request Webcam Access
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => { video.srcObject = stream; video.play(); })
    .catch(err => console.error("Webcam blocked", err));

scanBtn.onclick = async () => {
    scanBtn.innerText = "🔍 ANALYZING...";
    
    let blob;
    // Use Webcam if no file is selected
    if (coinInput.files[0]) {
        blob = coinInput.files[0];
    } else {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        blob = await new Promise(res => canvas.toBlob(res, 'image/jpeg'));
    }

    const formData = new FormData();
    formData.append("file", blob, "scan.jpg");
    formData.append("savings_split", 20);

    try {
        const response = await fetch("http://127.0.0.1:8000/audit", {
            method: "POST",
            body: formData
        });
        const data = await response.json();

        // Update Dashboard Stats
        document.getElementById('total-val').innerText = `₹${data.summary.final_amount}`;
        document.getElementById('gold-val').innerText = `₹${data.distribution.digital_gold}`;
        document.getElementById('credit-val').innerText = `₹${data.distribution.net_credit}`;
        
        // Update Detail Area
        document.getElementById('display-area').innerHTML = `
            <div class="text-left w-full">
                <p class="text-emerald-400 font-bold mb-2">Audit: ${data.summary.audit_status}</p>
                <p class="text-slate-300 text-sm">Oxidation: ${data.summary.oxidation}</p>
                <hr class="border-slate-700 my-2">
                <p class="text-slate-400 text-xs uppercase tracking-widest">Digital Distribution</p>
                <p class="text-sm">💰 UPI: ₹${data.distribution.upi_wallet}</p>
                <p class="text-sm">✨ Bonus: ₹${data.distribution.mint_bonus}</p>
            </div>
        `;
    } catch (err) {
        alert("Server connection failed!");
    } finally {
        scanBtn.innerText = "EXECUTE AUDIT";
    }
};