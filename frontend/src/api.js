// src/api.js
const apiUrl = import.meta.env.VITE_API_URL;

// Generic GET
export async function fetchData(endpoint) {
  const res = await fetch(`${apiUrl}/${endpoint}`);
  if (!res.ok) throw new Error('Network response was not ok');
  return res.json();
}

// Generic POST
export async function postData(endpoint, payload, isFormData = false) {
  const res = await fetch(`${apiUrl}/${endpoint}`, {
    method: 'POST',
    body: isFormData ? payload : JSON.stringify(payload),
    headers: isFormData ? {} : { 'Content-Type': 'application/json' },
  });
  if (!res.ok) throw new Error('Network response was not ok');
  return res.json();
}
