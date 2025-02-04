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

document.addEventListener('DOMContentLoaded', () => {
  initializeSearch();
});

async function fetchData() {
  const response = await fetch(new URL('index.json', window.location.href).href);
  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }
  return await response.json();
}

function initializeSearch() {
  const filterButton = document.getElementById('filterButton');
  const searchInput = document.getElementById('searchInput');
  const searchButton = document.getElementById('searchButton');

  filterButton.addEventListener('click', search);
  searchInput.addEventListener('keypress', event => {
    if (event.key === "Enter") {
      search();
    }
  });
  searchButton.addEventListener('click', search);

  fetchData()
    .then(data => {
      fuse = new Fuse(data, fuseOptions);
      search();
    })
    .catch(error => console.error("Error loading JSON:", error));
}

function search() {
  const searchQuery = document.getElementById('searchInput').value.trim();
  const searchResults = searchQuery ? fuse.search(searchQuery).map(result => result.item) : fuse._docs;
  const sortedResults = [...searchResults].sort((a, b) => b.weight - a.weight);
  displayResults(sortedResults);
}

function displayResults(results) {
  const resultsContainer = document.getElementById('searchResults');
  resultsContainer.innerHTML = results.length ? '' : '<p>No results found.</p>';

  results.forEach(item => {
    resultsContainer.innerHTML += atob(item.card);
  });
}
