import { extractTextFromUrl, processQuery } from './api.js';
import { showLoading, hideLoading, showQueryPage, showUrlPage, displayResults, showError } from './ui.js';
import { state } from './state.js';

// DOM Elements
const urlPage = document.getElementById('urlPage');
const queryPage = document.getElementById('queryPage');
const urlInput = document.getElementById('urlInput');
const queryInput = document.getElementById('queryInput');
const extractButton = document.getElementById('extractButton');
const queryButton = document.getElementById('queryButton');
const newUrlButton = document.getElementById('newUrlButton');
const resultsContainer = document.getElementById('results');

// Event Listeners
extractButton.addEventListener('click', handleExtract);
queryButton.addEventListener('click', handleQuery);
newUrlButton.addEventListener('click', () => showUrlPage(urlPage, queryPage, urlInput, queryInput, resultsContainer));

async function handleExtract() {
  const url = urlInput.value;
  if (!url) {
    showError('Please enter a valid URL');
    return;
  }

  try {
    showLoading(extractButton);
    const text = await extractTextFromUrl(url);
    state.setExtractedText(text);
    showQueryPage(urlPage, queryPage);
  } catch (error) {
    showError(error.message);
  } finally {
    hideLoading(extractButton, 'Extract Text');
  }
}

async function handleQuery() {
  const query = queryInput.value;
  if (!query) {
    showError('Please enter a query');
    return;
  }

  try {
    showLoading(queryButton);
    const response = await processQuery(query, state.getExtractedText());
    displayResults(resultsContainer, response);
  } catch (error) {
    showError(error.message);
  } finally {
    hideLoading(queryButton, 'Submit Query');
  }
}