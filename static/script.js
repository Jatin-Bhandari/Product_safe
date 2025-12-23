document.getElementById('upload-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const apiKey = document.getElementById('api-key').value;
    const imageFile = document.getElementById('image-file').files[0];
    const loader = document.getElementById('loader');
    const resultDiv = document.getElementById('result');

    if (!apiKey || !imageFile) {
        resultDiv.textContent = 'Please provide an API key and an image file.';
        return;
    }

    loader.classList.remove('hidden');
    resultDiv.innerHTML = '';

    const formData = new FormData();
    formData.append('api_key', apiKey);
    formData.append('image', imageFile);

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'An error occurred.');
        }

        const result = await response.json();
        resultDiv.innerHTML = marked.parse(result.result);

    } catch (error) {
        resultDiv.textContent = `Error: ${error.message}`;
    } finally {
        loader.classList.add('hidden');
    }
});