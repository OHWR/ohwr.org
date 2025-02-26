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
const searchPaginationElement = document.getElementById("search-pagination");

let fuse;
let results;
const perPage = 9;

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

  searchInputElement.addEventListener("keypress", handleSearchInput);
  searchButtonElement.addEventListener("click", handleSearchButton);

  performSearch();
}

function performSearch() {
  const url = new URL(window.location);
  const query = url.searchParams.get("q");
  const filters = url.searchParams.getAll("f");

  displaySearchInput(query);

  results = query ? fuse.search(query).map(({ item }) => item) : fuse._docs;

  if (filters.length) {
    results = results.filter(result =>
      result[searchScriptElement.dataset.filter] &&
      filters.every(filter =>
        result[searchScriptElement.dataset.filter].includes(filter)
      )
    );
  }

  results = [...results].sort((a, b) => b.weight - a.weight);

  displaySearchResults(results);

  displaySearchFilters(
    filters,
    results.flatMap(result =>
      result[searchScriptElement.dataset.filter] || []
    ).filter(filter => !filters.includes(filter))
  );

  displayPagination();
}

function displaySearchInput(query) {
  searchInputElement.value = query;
}

function displaySearchResults() {
  const url = new URL(window.location);
  const page = parseInt(url.searchParams.get("p"), 10) || 1;
  const startIndex = (page - 1) * perPage;
  const endIndex = startIndex + perPage;
  const paginatedResults = results.slice(startIndex, endIndex);

  searchResultsElement.innerHTML = paginatedResults.length ? "" : "<p>No results found.</p>";

  paginatedResults.forEach(item => {
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
        <span class="badge badge-filter ml-1">${item.count}</span>`
    });
    button.addEventListener("click", handleFilterButton);
    searchFilterMenuElement.appendChild(button);
  });
}


function displayPagination() {
  const url = new URL(window.location);
  const page = parseInt(url.searchParams.get("p")) || 1;
  const total = Math.ceil(results.length / perPage);
  searchPaginationElement.innerHTML = "";

  if (total > 1) {
    if (page > 1) {
      const startLi = Object.assign(document.createElement("li"), {
        className: "page-item",
      });
      const startButton = Object.assign(document.createElement("button"), {
        type: "button",
        className: "page-link",
        value: 1,
        innerHTML: "&laquo;&laquo;",
      });
      startButton.addEventListener("click", handlePaginationButton);
      startLi.appendChild(startButton);
      searchPaginationElement.appendChild(startLi);
      const previousLi = Object.assign(document.createElement("li"), {
        className: "page-item",
      });
      const previousButton = Object.assign(document.createElement("button"), {
        type: "button",
        className: "page-link",
        value: page - 1,
        innerHTML: "&laquo;",
      });
      previousButton.addEventListener("click", handlePaginationButton);
      previousLi.appendChild(previousButton);
      searchPaginationElement.appendChild(previousLi);
    }

    let startPage = Math.max(1, page - 2);
    let endPage = Math.min(total, page + 2);

    if (endPage - startPage < 4) {
      if (startPage === 1) {
        endPage = Math.min(total, startPage + 4);
      } else if (endPage === total) {
        startPage = Math.max(1, endPage - 4);
      }
    }

    for (let i = startPage; i <= endPage; i++) {
      const li = Object.assign(document.createElement("li"), {
        className: "page-item",
      });
      if (i === page) {
        li.classList.add("active");
      }
      const button = Object.assign(document.createElement("button"), {
        type: "button",
        className: "page-link",
        value: i,
        innerText: i,
      });
      button.addEventListener("click", handlePaginationButton);
      li.appendChild(button);
      searchPaginationElement.appendChild(li);
    }
    if (page < total) {
      const nextLi = Object.assign(document.createElement("li"), {
        className: "page-item",
      });
      const nextButton = Object.assign(document.createElement("button"), {
        type: "button",
        className: "page-link",
        value: page + 1,
        innerHTML: "&raquo;",
      });
      nextButton.addEventListener("click", handlePaginationButton);
      nextLi.appendChild(nextButton);
      searchPaginationElement.appendChild(nextLi);
      const endLi = Object.assign(document.createElement("li"), {
        className: "page-item",
      });
      const endButton = Object.assign(document.createElement("button"), {
        type: "button",
        className: "page-link",
        value: total,
        innerHTML: "&raquo;&raquo;",
      });
      endButton.addEventListener("click", handlePaginationButton);
      endLi.appendChild(endButton);
      searchPaginationElement.appendChild(endLi);
    }
  }
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
  url.searchParams.delete("p");
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
  url.searchParams.delete("p");
  window.history.pushState({}, "", url);
  performSearch();
}

function handlePaginationButton(event) {
  const page = event.currentTarget.value;
  const url = new URL(window.location);

  url.searchParams.set("p", page);
  window.history.pushState({}, "", url);
  displaySearchResults();
  displayPagination();
}
