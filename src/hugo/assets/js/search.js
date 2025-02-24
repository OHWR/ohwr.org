/*
SPDX-FileCopyrightText: 2024 CERN (home.cern)

SPDX-License-Identifier: BSD-3-Clause
*/

import Fuse from "https://cdn.jsdelivr.net/npm/fuse.js@7.0.0/dist/fuse.min.mjs";

const searchScriptElement = document.getElementById("search-script");
const searchInputElement = document.getElementById("search-input");
const searchButtonElement = document.getElementById("search-button");
const searchFilterMenuElement = document.getElementById("search-filter-menu");
const searchResultsElement = document.getElementById("search-results");

let fuse;

document.addEventListener("DOMContentLoaded", initializeSearch);

async function initializeSearch() {
  const url = new URL("index.json", window.location.href);
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch data: ${response.status}`);
  }

  const data = await response.json();

  fuse = new Fuse(data, {
    useExtendedSearch: true,
    ignoreLocation: true,
    threshold: 0,
    keys: JSON.parse(searchScriptElement.dataset.keys),
  });

  searchInputElement.addEventListener("input", handleSearchInput);
  searchButtonElement.addEventListener("click", handleSearchButton);

  performSearch();
}

function performSearch() {
  const url = new URL(window.location);
  const query = url.searchParams.get("q");
  const filters = url.searchParams.getAll("f");

  displaySearchInput(query);

  let results = query ? fuse.search(query).map(({ item }) => item) : fuse._docs;

  if (filters.length) {
    results = results.filter(result =>
      result[searchScriptElement.dataset.filter] &&
      filters.every(filter =>
        result[searchScriptElement.dataset.filter].includes(filter)
      )
    );
  }

  displaySearchResults([...results].sort((a, b) => b.weight - a.weight));

  displaySearchFilters(
    filters,
    results.flatMap(result =>
      result[searchScriptElement.dataset.filter] || []
    ).filter(filter => !filters.includes(filter))
  );
}

function displaySearchInput(query) {
  searchInputElement.value = query;
}


function displaySearchResults(results) {
  searchResultsElement.innerHTML = results.length ? "" : "<p>No results found.</p>";

  results.forEach(item => {
    searchResultsElement.innerHTML += atob(item.card);
  });
}

function displaySearchFilters(activeFilters, inactiveFilters) {
  searchFilterMenuElement.innerHTML = "";

  activeFilters.forEach(item => {
    const button = Object.assign(document.createElement("button"), {
      type: "button",
      className: "search-filter-button",
      value: item,
      innerHTML: `<i class="fas fa-times mr-1"></i>${item}`
    });
    button.dataset.state = "active";
    button.addEventListener("click", handleFilterButton);
    searchFilterMenuElement.appendChild(button);
  });

  inactiveFilters = Object.values(
    inactiveFilters.reduce((acc, filter) => {
      acc[filter] = acc[filter] || { filter, count: 0 };
      acc[filter].count++;
      return acc;
    }, {})
  ).sort((a, b) => b.count - a.count);

  inactiveFilters.forEach(item => {
    const button = Object.assign(document.createElement("button"), {
      type: "button",
      className: "search-filter-button",
      value: item.filter,
      innerHTML: `${item.filter}
        <span class="badge badge-primary ml-1">${item.count}</span>`
    });
    button.addEventListener("click", handleFilterButton);
    searchFilterMenuElement.appendChild(button);
  });
}

function handleSearchInput(event) {
  if (event.key === "Enter") {
    updateQuery(event.target.value.trim());
  }
}

function handleSearchButton() {
  updateQuery(searchInputElement.value.trim());
}

function updateQuery(query) {
  const url = new URL(window.location);

  if (query) {
    url.searchParams.set("q", query);
  } else {
    url.searchParams.delete("q");
  }
  window.history.pushState({}, "", url);
  performSearch();
}

function handleFilterButton(event) {
  const filter = event.currentTarget.value;
  const url = new URL(window.location);

  if (event.currentTarget.dataset.state === "active") {
    url.searchParams.delete("f", filter);
  } else {
    url.searchParams.append("f", filter);
  }
  window.history.pushState({}, "", url);
  performSearch();
}
