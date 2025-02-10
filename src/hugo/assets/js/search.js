/*
SPDX-FileCopyrightText: 2024 CERN (home.cern)

SPDX-License-Identifier: BSD-3-Clause
*/

import Fuse from 'https://cdn.jsdelivr.net/npm/fuse.js@7.0.0/dist/fuse.min.mjs';

const fuseOptions = {
  useExtendedSearch: true,
  ignoreLocation: true,
  threshold: 0,
  keys: [
    { name: 'title', weight: 3 },
    { name: 'tags', weight:2 },
    { name: 'content', weight: 1 }
  ]
};

let fuse;

initializeSearch();

function initializeSearch() {
  const searchInput = document.getElementById('searchInput');
  const searchButton = document.getElementById('searchButton');
  const urlParams = new URLSearchParams(window.location.search);

  searchInput.addEventListener('keypress', event => event.key === "Enter" && search());
  searchButton.addEventListener('click', search);
  searchInput.value = urlParams.get('q');

  fetchData()
    .then(data => {
      fuse = new Fuse(data, fuseOptions);
      search();
    })
    .catch(error => console.error("Error loading JSON:", error));
}

async function fetchData() {
  const response = await fetch(new URL('index.json', window.location.href).href);

  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }
  return await response.json();
}

function search() {
  const searchQuery = document.getElementById('searchInput').value.trim();
  const url = new URL(window.location);

  let searchResults;

  if (searchQuery) {
    searchResults = fuse.search(searchQuery).map(result => result.item);
    url.searchParams.set('q', searchQuery);
  } else {
    searchResults = fuse._docs;
    url.searchParams.delete('q');
  }

  window.history.pushState({}, '', url);
  displayResults([...searchResults].sort((a, b) => b.weight - a.weight));
}

function displayResults(results) {
  const resultsContainer = document.getElementById('searchResults');

  resultsContainer.innerHTML = results.length ? '' : '<p>No results found.</p>';

  results.forEach(item => {
    resultsContainer.innerHTML += atob(item.card);
  });
}
