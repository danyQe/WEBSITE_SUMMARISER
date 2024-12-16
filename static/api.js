const API_URL = 'http://localhost:5000';

export async function extractTextFromUrl(url) {
  const response = await fetch(`${API_URL}/extract`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error);
  }
  return data.text;
}

export async function processQuery(query, text) {
  const response = await fetch(`${API_URL}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, text }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error);
  }
  return data.response;
}