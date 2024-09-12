document.getElementById('generate-world').addEventListener('click', function() {
    const description = document.getElementById('world-description').value;
    retryFetch('/generate_game_world', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description: description }),
    })
    .then(data => {
        const resultDiv = document.getElementById('game-world-result');
        resultDiv.innerHTML = '<h3>Generated Game World:</h3>';
        data.forEach(item => {
            resultDiv.innerHTML += `
                <div class="asset-item">
                    <input type="checkbox" id="${item.name}" checked>
                    <label for="${item.name}">${item.name} (${item.type})</label>
                </div>`;
        });
        resultDiv.innerHTML += `
            <div id="custom-assets">
                <h4>Add Custom Assets:</h4>
                <input type="text" id="custom-asset-name" placeholder="Asset Name">
                <select id="custom-asset-type">
                    <option value="location">Location</option>
                    <option value="item">Item</option>
                    <option value="interactive_entity">Interactive Entity</option>
                    <option value="tile">Tile</option>
                </select>
                <button id="add-custom-asset">Add</button>
            </div>
        `;
        document.getElementById('approve-assets').style.display = 'block';
        document.getElementById('auto-approve-assets').style.display = 'block';
        
        // Add event listener for adding custom assets
        document.getElementById('add-custom-asset').addEventListener('click', addCustomAsset);
        
        if (autoApproveCheckbox.checked) {
            approveAssets();
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('Failed to generate game world. Please try again.');
    });
});

function addCustomAsset() {
    const name = document.getElementById('custom-asset-name').value;
    const type = document.getElementById('custom-asset-type').value;
    if (name) {
        const resultDiv = document.getElementById('game-world-result');
        const newAssetDiv = document.createElement('div');
        newAssetDiv.className = 'asset-item custom-asset';
        newAssetDiv.innerHTML = `
            <input type="checkbox" id="${name}" checked>
            <label for="${name}">${name} (${type})</label>
        `;
        resultDiv.appendChild(newAssetDiv);
        document.getElementById('custom-asset-name').value = '';
    }
}

document.getElementById('approve-assets').addEventListener('click', approveAssets);

function approveAssets() {
    const assets = Array.from(document.querySelectorAll('#game-world-result .asset-item input:checked')).map(checkbox => {
        const label = checkbox.nextElementSibling;
        const [name, type] = label.textContent.split('(');
        return { name: name.trim(), type: type.replace(')', '').trim() };
    });
    
    fetch('/approve_asset_list', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ approved_assets: assets }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Assets approved:', data);
        document.getElementById('aesthetic-theme-generator').style.display = 'block';
        if (autoApproveCheckbox.checked) {
            generateAestheticTheme();
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred while approving assets. Please check the console for details.');
    });
}

// Add a new auto-approve checkbox for assets
const autoApproveAssetsCheckbox = document.getElementById('auto-approve-assets');

autoApproveAssetsCheckbox.addEventListener('change', function() {
    if (this.checked) {
        approveAssets();
    }
});

const generateAestheticBtn = document.getElementById('generate-aesthetic');
const approveAestheticBtn = document.getElementById('approve-aesthetic');
const aestheticThemeResult = document.getElementById('aesthetic-theme-result');

let isGeneratingAesthetic = false;

generateAestheticBtn.addEventListener('click', generateAestheticTheme);
approveAestheticBtn.addEventListener('click', approveAestheticTheme);

function generateAestheticTheme() {
    if (isGeneratingAesthetic) return;
    isGeneratingAesthetic = true;

    retryFetch('/generate_aesthetic_theme', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        const aestheticTheme = data.aesthetic_theme;
        const themeHTML = aestheticTheme.split('\n')
            .map(line => {
                const [key, value] = line.split(':');
                return `<p><strong>${key}:</strong> ${value.trim()}</p>`;
            })
            .join('');
        aestheticThemeResult.innerHTML = themeHTML;
        approveAestheticBtn.style.display = 'block';
        if (document.getElementById('auto-approve').checked) {
            approveAestheticTheme();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        aestheticThemeResult.innerHTML = `An error occurred while generating the aesthetic theme: ${error.message}`;
    })
    .finally(() => {
        isGeneratingAesthetic = false;
    });
}

function approveAestheticTheme() {
    document.getElementById('image-prompt-generator').style.display = 'block';
    if (document.getElementById('auto-approve').checked) {
        generateImagePrompts();
    }
}

const autoApproveCheckbox = document.getElementById('auto-approve');

const generatePromptsBtn = document.getElementById('generate-prompts');

generatePromptsBtn.addEventListener('click', generateImagePrompts);

function generateImagePrompts() {
    generatePromptsBtn.disabled = true;
    generatePromptsBtn.textContent = 'Forging...';

    retryFetch('/generate_image_prompts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(data => {
        if (Array.isArray(data)) {
            const resultDiv = document.getElementById('image-prompts-result');
            resultDiv.innerHTML = '<h3>Generated Image Prompts:</h3>';
            const fragment = document.createDocumentFragment();
            data.forEach(item => {
                const promptDiv = document.createElement('div');
                promptDiv.className = 'prompt-item';
                promptDiv.innerHTML = `
                    <h4>${item.asset.name} (${item.asset.type})</h4>
                    <pre>${JSON.stringify(item.prompt, null, 2)}</pre>
                `;
                fragment.appendChild(promptDiv);
            });
            resultDiv.appendChild(fragment);
            
            document.getElementById('approve-prompts').style.display = 'block';
            
            if (autoApproveCheckbox.checked) {
                approveImagePrompts(data);
            }
        } else if (data.error) {
            throw new Error(data.error);
        } else {
            throw new Error('Unexpected response format');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        const resultDiv = document.getElementById('image-prompts-result');
        resultDiv.innerHTML = `<h3>Error Generating Image Prompts:</h3><p>${error.message}</p>`;
    })
    .finally(() => {
        generatePromptsBtn.disabled = false;
        generatePromptsBtn.textContent = 'Forge Image Prompts';
    });
}

document.getElementById('approve-prompts').addEventListener('click', function() {
    const prompts = Array.from(document.querySelectorAll('.prompt-item')).map(item => {
        const assetName = item.querySelector('h4').textContent.split('(')[0].trim();
        const assetType = item.querySelector('h4').textContent.split('(')[1].replace(')', '').trim();
        const prompt = JSON.parse(item.querySelector('pre').textContent);
        return { asset: { name: assetName, type: assetType }, prompt: prompt };
    });
    approveImagePrompts(prompts);
});

function approveImagePrompts(prompts) {
    fetch('/approve_image_prompts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ approved_prompts: prompts }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Image prompts approved:', data);
        document.getElementById('image-generator').style.display = 'block';
        if (autoApproveCheckbox.checked) {
            generateImages();
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred while approving prompts. Please check the console for details.');
    });
}

const generateImagesBtn = document.getElementById('generate-images');

generateImagesBtn.addEventListener('click', generateImages);

function generateImages() {
    generateImagesBtn.disabled = true;
    generateImagesBtn.textContent = 'Generating...';
    
    retryFetch('/generate_images', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(images => {
        const imageResultDiv = document.getElementById('image-generation-result');
        imageResultDiv.innerHTML = '<h3>Generated Images:</h3>';
        images.forEach((item, index) => {
            const imgContainer = document.createElement('div');
            imgContainer.className = 'image-container';
            
            const img = document.createElement('img');
            img.src = `data:image/png;base64,${item.image}`;
            img.alt = item.asset.name;
            img.style.maxWidth = '512px';
            img.style.maxHeight = '512px';
            
            const caption = document.createElement('p');
            caption.textContent = `${item.asset.name} (${item.asset.type})`;
            
            const regenerateBtn = document.createElement('button');
            regenerateBtn.textContent = 'Regenerate';
            regenerateBtn.className = 'regenerate-btn';
            regenerateBtn.addEventListener('click', function() {
                regenerateImage(index, img);
            });
            
            imgContainer.appendChild(img);
            imgContainer.appendChild(caption);
            imgContainer.appendChild(regenerateBtn);
            imageResultDiv.appendChild(imgContainer);
        });
        document.getElementById('save-game').style.display = 'block';
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred while generating images. Please check the console for details.');
    })
    .finally(() => {
        generateImagesBtn.disabled = false;
        generateImagesBtn.textContent = 'Bring Forth Images';
    });
}

function regenerateImage(index, imgElement) {
    retryFetch('/regenerate_image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ index: index }),
    })
    .then(data => {
        if (data.image) {
            imgElement.src = `data:image/png;base64,${data.image}`;
        } else {
            throw new Error(data.error || 'Failed to regenerate image');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while regenerating the image. Please check the console for details.');
    });
}

const saveGameButton = document.getElementById('save-game');

saveGameButton.addEventListener('click', function() {
    fetch('/save_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'game_world.zip';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred while saving the game. Please check the console for details.');
    });
});

function retryFetch(url, options, maxRetries = 3, delay = 1000) {
    return new Promise((resolve, reject) => {
        function attempt(retryCount) {
            fetch(url, options)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.error) {
                        throw new Error(data.error);
                    }
                    resolve(data);
                })
                .catch(error => {
                    if (retryCount < maxRetries) {
                        console.log(`Attempt ${retryCount + 1} failed, retrying in ${delay}ms...`);
                        setTimeout(() => attempt(retryCount + 1), delay);
                    } else {
                        reject(error);
                    }
                });
        }
        attempt(0);
    });
}