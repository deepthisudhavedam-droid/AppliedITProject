document.addEventListener('DOMContentLoaded', () => {

    // DOM Elements
    const tryItNowBtn = document.getElementById('tryItNowBtn');
    const generatorSection = document.getElementById('generator');

    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const previewContainer = document.getElementById('previewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const removeImageBtn = document.getElementById('removeImageBtn');

    const generateBtn = document.getElementById('generateBtn');
    const btnText = generateBtn.querySelector('.btn-text');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorContainer = document.getElementById('errorContainer');

    const resultsSection = document.getElementById('resultsSection');
    const categoryTag = document.getElementById('categoryTag');
    const colorTag = document.getElementById('colorTag');
    const styleTag = document.getElementById('styleTag');

    const patternTag = document.getElementById('patternTag');
    const genderTag = document.getElementById('genderTag');
    const fitTag = document.getElementById('fitTag');

    const resultsGrid = document.getElementById('resultsGrid');
    const regenerateBtn = document.getElementById('regenerateBtn');

    let selectedFile = null;

    // Smooth scroll
    tryItNowBtn.addEventListener('click', () => {
        generatorSection.scrollIntoView({ behavior: 'smooth' });
    });

    regenerateBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        resetUpload();
        resultsSection.classList.add('hidden');
    });

    // Drag & Drop
    const preventDefaults = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const file = e.dataTransfer.files[0];
        handleFile(file);
    });

    uploadPlaceholder.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    removeImageBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetUpload();
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            showError('Please upload a valid image file (JPG, PNG).');
            return;
        }

        selectedFile = file;
        hideError();

        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            uploadPlaceholder.classList.add('hidden');
            previewContainer.classList.remove('hidden');
            generateBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }

    function resetUpload() {
        selectedFile = null;
        fileInput.value = '';
        imagePreview.src = '';
        uploadPlaceholder.classList.remove('hidden');
        previewContainer.classList.add('hidden');
        generateBtn.disabled = true;
    }

    function showError(msg) {
        errorContainer.textContent = msg;
        errorContainer.classList.remove('hidden');
    }

    function hideError() {
        errorContainer.classList.add('hidden');
        errorContainer.textContent = '';
    }

    // MAIN FLOW
    generateBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        hideError();

        // Loading UI
        btnText.classList.add('hidden');
        loadingSpinner.classList.remove('hidden');
        generateBtn.disabled = true;

        try {
            // STEP 1 — Analyze image
            const formData = new FormData();
            formData.append('file', selectedFile);

            const analyzeRes = await fetch("http://127.0.0.1:8000/analyze-image", {
                method: "POST",
                body: formData
            });

            if (!analyzeRes.ok) {
                const errorData = await analyzeRes.json();
                throw new Error(errorData.detail || "Analyze endpoint failed");
            }

            const detected = await analyzeRes.json();

            // Update tags
            categoryTag.textContent = `Category: ${detected.category}`;
            colorTag.textContent = `Color: ${detected.color}`;
            styleTag.textContent = `Style: ${detected.style}`;

            if (patternTag) patternTag.textContent = `Pattern: ${detected.pattern}`;
            if (genderTag) genderTag.textContent = `Gender: ${detected.gender}`;
            if (fitTag) fitTag.textContent = `Fit: ${detected.fit}`;

            // STEP 2 — Generate outfits
            const outfitRes = await fetch("http://127.0.0.1:8000/generate-outfits", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(detected)
            });

            if (!outfitRes.ok) {
                const errorData = await outfitRes.json();
                throw new Error(errorData.detail || "Outfit endpoint failed");
            }

            const outfitData = await outfitRes.json();

            renderOutfitCards(outfitData.suggestions);

            resultsSection.classList.remove('hidden');
            resultsSection.scrollIntoView({ behavior: 'smooth' });

        } catch (err) {
            console.error(err);
            showError(err.message || "Something went wrong. Check backend connection.");
        } finally {
            btnText.classList.remove('hidden');
            loadingSpinner.classList.add('hidden');
            generateBtn.disabled = false;
        }
    });

    function renderOutfitCards(suggestions) {
        resultsGrid.innerHTML = "";

        suggestions.forEach((s, index) => {
            const card = document.createElement("div");
            card.className = "card";
            card.style.animationDelay = `${index * 0.1}s`;

            card.innerHTML = `
                <div class="card-content">
                    <h4 class="card-title">${s.title}</h4>
                    <p class="card-tip">${s.description}</p>

                    <div class="card-footer">
                        <span class="card-score">${s.match_percentage}% Match</span>
                        <span class="card-occasion">${s.best_occasion}</span>
                    </div>

                    <p class="card-reason">${s.reasoning}</p>

                    <ul class="card-items">
                        ${s.suggested_items.map(i => `<li>${i}</li>`).join("")}
                    </ul>
                </div>
            `;

            resultsGrid.appendChild(card);
        });
    }

});
