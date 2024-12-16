export function showLoading(button) {
    button.disabled = true;
    button.innerHTML = `
      <div class="spinner"></div>
      <span>Loading...</span>
    `;
  }
  
  export function hideLoading(button, originalText) {
    button.disabled = false;
    button.innerHTML = originalText;
  }
  
  export function showQueryPage(urlPage, queryPage) {
    urlPage.classList.remove('active');
    queryPage.classList.add('active');
  }
  
  export function showUrlPage(urlPage, queryPage, urlInput, queryInput, resultsContainer) {
    queryPage.classList.remove('active');
    urlPage.classList.add('active');
    urlInput.value = '';
    queryInput.value = '';
    resultsContainer.innerHTML = '';
  }
  
  export function displayResults(resultsContainer, response) {
    resultsContainer.style.display = 'block';
    resultsContainer.innerHTML = `<p>${response}</p>`;
  }
  
  export function showError(message) {
    alert(message);
  }