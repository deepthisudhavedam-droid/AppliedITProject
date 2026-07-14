document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('authToken');
    const userStorage = localStorage.getItem('authUser');
    const emailInput = document.getElementById('email');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const profileForm = document.getElementById('profileForm');
    const profileError = document.getElementById('profileError');
    const profileSuccess = document.getElementById('profileSuccess');
    const cancelBtn = document.getElementById('cancelBtn');
    const profileBtn = document.getElementById('profileBtn');
    const profileInitial = document.getElementById('profileInitial');

    const viewWardrobeBtn = document.getElementById('viewWardrobeBtn');
    const addClothesBtn = document.getElementById('addClothesBtn');
    const wardrobeGrid = document.getElementById('wardrobeGrid');
    const wardrobeStatus = document.getElementById('wardrobeStatus');
    const wardrobeModal = document.getElementById('wardrobeModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelUploadBtn = document.getElementById('cancelUploadBtn');
    const uploadWardrobeBtn = document.getElementById('uploadWardrobeBtn');
    const deviceFileInput = document.getElementById('deviceFileInput');
    const takePhotoBtn = document.getElementById('takePhotoBtn');
    const cameraContainer = document.getElementById('cameraContainer');
    const cameraPreview = document.getElementById('cameraPreview');
    const cameraCanvas = document.getElementById('cameraCanvas');
    const capturePhotoBtn = document.getElementById('capturePhotoBtn');
    const cancelCameraBtn = document.getElementById('cancelCameraBtn');
    const uploadPreview = document.getElementById('uploadPreview');
    const uploadPreviewImage = document.getElementById('uploadPreviewImage');
    const replaceImageBtn = document.getElementById('replaceImageBtn');
    const clearImageBtn = document.getElementById('clearImageBtn');
    const wardrobeCategory = document.getElementById('wardrobeCategory');
    const wardrobeColor = document.getElementById('wardrobeColor');
    const wardrobeNotes = document.getElementById('wardrobeNotes');
    const uploadError = document.getElementById('uploadError');
    const uploadSuccess = document.getElementById('uploadSuccess');
    const imageViewerModal = document.getElementById('imageViewerModal');
    const imageViewer = document.getElementById('imageViewer');
    const closeViewerBtn = document.getElementById('closeViewerBtn');

    if (!token || !userStorage) {
        window.location.href = 'login.html';
        return;
    }

    const user = JSON.parse(userStorage);
    usernameInput.value = user.username;
    emailInput.value = user.email;
    if (profileInitial) {
        profileInitial.textContent = (user.username || 'U')[0].toUpperCase();
    }

    let selectedFile = null;
    let selectedPreviewUrl = null;
    let stream = null;
    let activeViewerUrl = null;
    let isUploading = false;

    document.getElementById('logoutBtn')?.addEventListener('click', async () => {
        await window.authenticatedFetch('/logout', {
            method: 'POST',
            responseType: 'json',
        }).catch(() => {});

        window.clearSession();
        window.location.href = 'login.html';
    });

    profileBtn?.addEventListener('click', () => {
        window.location.href = 'profile.html';
    });

    cancelBtn.addEventListener('click', () => {
        window.location.href = 'index.html';
    });

    viewWardrobeBtn?.addEventListener('click', () => {
        loadWardrobe();
    });

    addClothesBtn?.addEventListener('click', () => {
        openUploadModal();
    });

    closeModalBtn?.addEventListener('click', closeUploadModal);
    cancelUploadBtn?.addEventListener('click', closeUploadModal);
    replaceImageBtn?.addEventListener('click', () => deviceFileInput.click());
    clearImageBtn?.addEventListener('click', clearSelectedFile);
    takePhotoBtn?.addEventListener('click', startCamera);
    cancelCameraBtn?.addEventListener('click', stopCamera);
    capturePhotoBtn?.addEventListener('click', captureFromCamera);
    closeViewerBtn?.addEventListener('click', closeViewer);
    imageViewerModal?.addEventListener('click', (event) => {
        if (event.target === imageViewerModal) {
            closeViewer();
        }
    });
    wardrobeModal?.addEventListener('click', (event) => {
        if (event.target === wardrobeModal) {
            closeUploadModal();
        }
    });

    deviceFileInput?.addEventListener('change', (event) => {
        const file = event.target.files?.[0];
        if (file) {
            setSelectedFile(file);
        }
    });

    uploadWardrobeBtn?.addEventListener('click', uploadWardrobeItem);

    profileForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        profileError.classList.add('hidden');
        profileSuccess.classList.add('hidden');

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (!email) {
            showError('Email is required.');
            return;
        }

        if (password && password.length < 6) {
            showError('Password must be at least 6 characters long.');
            return;
        }

        try {
            const { response, data } = await window.authenticatedFetch('/me', {
                method: 'PUT',
                body: JSON.stringify({ email, password: password || undefined }),
                responseType: 'json',
            });

            if (!response.ok) {
                throw new Error(data?.detail || data?.message || 'Unable to update profile.');
            }

            localStorage.setItem('authUser', JSON.stringify(data));
            showSuccess('Profile updated successfully.');
            passwordInput.value = '';
        } catch (error) {
            showError(error.message || 'Unable to update profile.');
        }
    });

    async function loadWardrobe() {
        setWardrobeStatus('Loading wardrobe…');
        wardrobeGrid.innerHTML = '';

        try {
            const { response, data } = await window.authenticatedFetch('/wardrobe/items', {
                method: 'GET',
                responseType: 'json',
            });

            if (!response.ok) {
                throw new Error(data?.detail || data?.message || 'Unable to load wardrobe.');
            }

            if (!Array.isArray(data) || data.length === 0) {
                setWardrobeStatus('Your wardrobe is empty. Add your first piece to get started.');
                wardrobeGrid.innerHTML = '';
                return;
            }

            setWardrobeStatus(`${data.length} ${data.length === 1 ? 'item' : 'items'} in your wardrobe.`);
            data.forEach((item) => renderWardrobeCard(item));
        } catch (error) {
            setWardrobeStatus(error.message || 'Unable to load wardrobe.');
        }
    }

    function renderWardrobeCard(item) {
        const card = document.createElement('article');
        card.className = 'wardrobe-card';

        const thumb = document.createElement('img');
        thumb.className = 'wardrobe-thumb';
        thumb.alt = item.original_filename || 'Wardrobe item';
        thumb.src = '';
        loadThumbnail(thumb, item.id);

        const content = document.createElement('div');
        content.className = 'wardrobe-card-content';

        const title = document.createElement('h3');
        title.textContent = item.category || 'Wardrobe item';

        const meta = document.createElement('p');
        meta.className = 'wardrobe-meta';
        const createdAt = item.created_at ? new Date(item.created_at).toLocaleDateString() : 'Unknown date';
        meta.textContent = `${item.color || 'No color'} • ${createdAt}`;

        const actions = document.createElement('div');
        actions.className = 'wardrobe-actions-row';

        const viewBtn = document.createElement('button');
        viewBtn.type = 'button';
        viewBtn.className = 'secondary-btn wardrobe-action';
        viewBtn.textContent = 'View';
        viewBtn.addEventListener('click', () => openViewer(item.id));

        const deleteBtn = document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.className = 'secondary-btn wardrobe-action danger';
        deleteBtn.textContent = 'Delete';
        deleteBtn.addEventListener('click', () => deleteWardrobeItem(item.id, card));

        actions.append(viewBtn, deleteBtn);
        content.append(title, meta, actions);
        card.append(thumb, content);
        wardrobeGrid.appendChild(card);
    }

    function revokeThumbnailUrl(img) {
        if (img?.dataset.objectUrl) {
            URL.revokeObjectURL(img.dataset.objectUrl);
            delete img.dataset.objectUrl;
        }
    }

    async function loadThumbnail(img, itemId) {
        try {
            const { response, data } = await window.authenticatedFetch(`/wardrobe/items/${itemId}/thumbnail`, {
                method: 'GET',
                responseType: 'blob',
            });

            if (!response.ok) {
                throw new Error('Unable to load thumbnail.');
            }

            revokeThumbnailUrl(img);
            const objectUrl = URL.createObjectURL(data);
            img.dataset.objectUrl = objectUrl;
            img.src = objectUrl;
        } catch (error) {
            img.alt = 'Thumbnail unavailable';
            img.src = '';
        }
    }

    async function deleteWardrobeItem(itemId, card) {
        const confirmed = window.confirm('Delete this wardrobe item?');
        if (!confirmed) {
            return;
        }

        try {
            const { response, data } = await window.authenticatedFetch(`/wardrobe/items/${itemId}`, {
                method: 'DELETE',
                responseType: 'json',
            });

            if (!response.ok) {
                throw new Error(data?.detail || data?.message || 'Unable to delete wardrobe item.');
            }

            card.remove();
            if (!wardrobeGrid.children.length) {
                setWardrobeStatus('Your wardrobe is empty. Add your first piece to get started.');
            }
        } catch (error) {
            setWardrobeStatus(error.message || 'Unable to delete wardrobe item.');
        }
    }

    async function openViewer(itemId) {
        try {
            const { response, data } = await window.authenticatedFetch(`/wardrobe/items/${itemId}/image`, {
                method: 'GET',
                responseType: 'blob',
            });

            if (!response.ok) {
                throw new Error(data?.detail || data?.message || 'Unable to load image.');
            }

            if (activeViewerUrl) {
                URL.revokeObjectURL(activeViewerUrl);
            }
            activeViewerUrl = URL.createObjectURL(data);
            imageViewer.src = activeViewerUrl;
            imageViewerModal.classList.remove('hidden');
        } catch (error) {
            setWardrobeStatus(error.message || 'Unable to load image.');
        }
    }

    function closeViewer() {
        imageViewerModal.classList.add('hidden');
        imageViewer.removeAttribute('src');
        if (activeViewerUrl) {
            URL.revokeObjectURL(activeViewerUrl);
            activeViewerUrl = null;
        }
    }

    function openUploadModal() {
        clearUploadMessages();
        wardrobeModal.classList.remove('hidden');
        deviceFileInput.value = '';
        clearSelectedFile();
    }

    function closeUploadModal() {
        stopCamera();
        clearUploadMessages();
        wardrobeModal.classList.add('hidden');
        clearSelectedFile();
    }

    function setSelectedFile(file) {
        if (!file || !file.type.startsWith('image/')) {
            showUploadError('Please upload a valid image file.');
            return;
        }

        selectedFile = file;
        const previewUrl = URL.createObjectURL(file);
        if (selectedPreviewUrl) {
            URL.revokeObjectURL(selectedPreviewUrl);
        }
        selectedPreviewUrl = previewUrl;
        uploadPreviewImage.src = previewUrl;
        uploadPreview.classList.remove('hidden');
        hideUploadError();
    }

    function clearSelectedFile() {
        selectedFile = null;
        if (selectedPreviewUrl) {
            URL.revokeObjectURL(selectedPreviewUrl);
            selectedPreviewUrl = null;
        }
        uploadPreviewImage.removeAttribute('src');
        uploadPreview.classList.add('hidden');
        if (deviceFileInput) {
            deviceFileInput.value = '';
        }
    }

    async function uploadWardrobeItem() {
        if (isUploading) {
            return;
        }
        if (!selectedFile) {
            showUploadError('Please choose an image first.');
            return;
        }

        clearUploadMessages();
        isUploading = true;
        uploadWardrobeBtn.disabled = true;
        uploadWardrobeBtn.textContent = 'Uploading…';

        const formData = new FormData();
        formData.append('file', selectedFile);
        if (wardrobeCategory.value.trim()) {
            formData.append('category', wardrobeCategory.value.trim());
        }
        if (wardrobeColor.value.trim()) {
            formData.append('color', wardrobeColor.value.trim());
        }
        if (wardrobeNotes.value.trim()) {
            formData.append('notes', wardrobeNotes.value.trim());
        }

        try {
            const { response, data } = await window.authenticatedFetch('/wardrobe/items', {
                method: 'POST',
                body: formData,
                responseType: 'json',
            });

            if (!response.ok) {
                throw new Error(data?.detail || data?.message || 'Upload failed.');
            }

            uploadSuccess.textContent = 'Item uploaded successfully.';
            uploadSuccess.classList.remove('hidden');
            clearSelectedFile();
            wardrobeCategory.value = '';
            wardrobeColor.value = '';
            wardrobeNotes.value = '';
            await loadWardrobe();
            setTimeout(closeUploadModal, 700);
        } catch (error) {
            showUploadError(error.message || 'Unable to upload image.');
        } finally {
            isUploading = false;
            uploadWardrobeBtn.disabled = false;
            uploadWardrobeBtn.textContent = 'Upload';
        }
    }

    async function startCamera() {
        if (!navigator.mediaDevices?.getUserMedia) {
            showUploadError('Camera capture is not supported in this browser.');
            return;
        }

        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'environment' } }, audio: false });
            cameraPreview.srcObject = stream;
            cameraContainer.classList.remove('hidden');
            uploadPreview.classList.add('hidden');
        } catch (error) {
            showUploadError('Camera permission was denied or unavailable.');
        }
    }

    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach((track) => track.stop());
            stream = null;
        }
        cameraPreview.srcObject = null;
        cameraContainer.classList.add('hidden');
    }

    function captureFromCamera() {
        const context = cameraCanvas.getContext('2d');
        cameraCanvas.width = cameraPreview.videoWidth || 640;
        cameraCanvas.height = cameraPreview.videoHeight || 480;
        context.drawImage(cameraPreview, 0, 0, cameraCanvas.width, cameraCanvas.height);
        cameraCanvas.toBlob((blob) => {
            if (!blob) {
                showUploadError('Unable to capture photo.');
                return;
            }
            const file = new File([blob], `capture-${Date.now()}.png`, { type: 'image/png' });
            setSelectedFile(file);
            stopCamera();
        }, 'image/png');
    }

    function showError(message) {
        profileError.textContent = message;
        profileError.classList.remove('hidden');
    }

    function showSuccess(message) {
        profileSuccess.textContent = message;
        profileSuccess.classList.remove('hidden');
    }

    function showUploadError(message) {
        uploadError.textContent = message;
        uploadError.classList.remove('hidden');
    }

    function hideUploadError() {
        uploadError.classList.add('hidden');
        uploadError.textContent = '';
    }

    function clearUploadMessages() {
        uploadError.classList.add('hidden');
        uploadError.textContent = '';
        uploadSuccess.classList.add('hidden');
        uploadSuccess.textContent = '';
    }

    function setWardrobeStatus(message) {
        wardrobeStatus.textContent = message;
    }

    loadWardrobe();
});
