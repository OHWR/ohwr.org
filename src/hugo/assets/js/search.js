/*
SPDX-FileCopyrightText: 2025 CERN (home.cern)

SPDX-License-Identifier: BSD-3-Clause
*/

import Fuse from "https://cdn.jsdelivr.net/npm/fuse.js@7.0.0/dist/fuse.min.mjs";

const searchInputElement = document.getElementById("search-input");
const searchButtonElement = document.getElementById("search-button");
const searchSuggestionsElement = document.getElementById('search-suggestions');
const searchFilterMenuElement = document.getElementById("search-filter-menu");
const searchActiveFiltersElement = document.getElementById("search-active-filters");
const searchAvailableFiltersElement = document.getElementById("search-available-filters");
const searchResultsElement = document.getElementById("search-results");
const searchPaginationElement = document.getElementById("search-pagination");
const infoIconElement = document.getElementById('search-info-icon');
const tooltipElement = document.getElementById('info-tooltip');

let searchView;
let searchFilter;
let fuse;
let filterFuse;
let results;
let suggestions;
let selectedSuggestionIndex = -1;
const perPage = 9;

document.addEventListener("DOMContentLoaded", initializeSearch);

async function initializeSearch() {
  const url = new URL("index.json", window.location.href);
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch data: ${response.status}`);
  }

  const data = await response.json();

  fuse = new Fuse(data['index'], {
    useExtendedSearch: true,
    ignoreLocation: true,
    threshold: 0,
    keys: data['keys'],
  });

  searchView = data['view'];
  searchFilter = data['filter'];

  const filterData = [...new Set(data['index'].flatMap(item =>
    item[searchFilter] || []
  ))];

  filterFuse = new Fuse(filterData, {minMatchCharLength: 2});

  searchInputElement.addEventListener("input", handleSearchInput);
  searchInputElement.addEventListener("keydown", handleSearchKeydown);
  searchButtonElement.addEventListener("click", handleSearchButton);

  initializeInfo();
  performSearch();
}

function initializeInfo() {
  infoIconElement.addEventListener('click', function (e) {
    e.stopPropagation();
    tooltipElement.classList.toggle('visible');

    const iconRect = infoIconElement.getBoundingClientRect();
    const tooltipWidth = tooltipElement.offsetWidth;
    const leftPosition = iconRect.left + (iconRect.width / 2) - (tooltipWidth / 2);

    tooltipElement.style.left = `${leftPosition}px`;
    tooltipElement.style.top = `${iconRect.bottom + window.scrollY + 8}px`;
  });

  document.addEventListener('click', function (e) {
    if (!tooltipElement.contains(e.target) && !infoIconElement.contains(e.target)) {
      tooltipElement.classList.remove('visible');
    }
  });
}

function performSearch() {
  const url = new URL(window.location);
  const query = url.searchParams.get("q");
  const filters = url.searchParams.getAll("f");

  displaySearchInput(query);

  hideSuggestions();

  results = query ? fuse.search(query).map(({ item }) => item) : fuse._docs;

  if (filters.length) {
    results = results.filter(result =>
      result[searchFilter] &&
      filters.every(filter =>
        result[searchFilter].includes(filter)
      )
    );
  }

  results = [...results].sort((a, b) => b.weight - a.weight);

  displaySearchResults(results);

  displayActiveFilters(filters);
  displayAvailableFilters(results.flatMap(result =>
    result[searchFilter] || []
    ).filter(filter => !filters.includes(filter)));

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

  if (paginatedResults.length) {
    let cards;
    if (searchView === "grid") {
      searchResultsElement.classList.add("row");
      cards = paginatedResults.map(item => {
        return gridViewElement(
          item.image,
          item.title,
          item.text,
          item.url
        );
      });
    } else if (searchView === "list") {
      searchResultsElement.classList.remove("row");
      cards = paginatedResults.map(item => {
        return listViewElement(
          item.project,
          item.url,
          item.title,
          item.date,
          item.text,
          item.image
        );
      });
    }
    searchResultsElement.replaceChildren(...cards);
  } else {
    searchResultsElement.classList.remove("row");
    const textElement = document.createElement("p");
    textElement.innerText = "No results found.";
    searchResultsElement.replaceChildren(textElement);
  }
}

function displayActiveFilters(filters) {
  searchActiveFiltersElement.innerHTML = "";
  if (filters.length) {
    searchFilterMenuElement.classList.add("show");
  }
  filters.forEach(item => {
    const button = Object.assign(document.createElement("button"), {
      type: "button",
      className: "search-filter-button",
      value: item,
      innerHTML: `<i class="fas fa-times mr-1"></i>${item}`
    });
    button.dataset.state = "active";
    button.addEventListener("click", handleFilterButton);
    searchActiveFiltersElement.appendChild(button);
  });
}

function displayAvailableFilters(filters) {
  searchAvailableFiltersElement.innerHTML = "";

  filters = Object.values(
    filters.reduce((acc, filter) => {
      acc[filter] = acc[filter] || { filter, count: 0 };
      acc[filter].count++;
      return acc;
    }, {})
  ).sort((a, b) => b.count - a.count);

  filters.forEach(item => {
    const button = Object.assign(document.createElement("button"), {
      type: "button",
      className: "search-filter-button",
      value: item.filter,
      innerHTML: `${item.filter}
        <span class="badge badge-filter ml-1">${item.count}</span>`
    });
    button.addEventListener("click", handleFilterButton);
    searchAvailableFiltersElement.appendChild(button);
  });
}

function displayPagination() {
  const url = new URL(window.location);
  const page = parseInt(url.searchParams.get("p"), 10) || 1;
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
  const url = new URL(window.location);
  const filters = url.searchParams.getAll("f");
  const inputValue = event.target.value.trim();
  suggestions = inputValue ? filterFuse.search(inputValue).map(({ item }) => item) : [];
  suggestions = suggestions.filter(filter => !filters.includes(filter)).slice(0, 8);
  displaySuggestions(suggestions);
}

function handleSearchKeydown(event) {
  const inputValue = event.target.value.trim();
  if (event.key === "Enter") {
    if (selectedSuggestionIndex >= 0) {
      updateFilter(suggestions[selectedSuggestionIndex]);
    } else {
      updateQuery(inputValue);
    }
  } else if (event.key === "ArrowDown") {
    selectedSuggestionIndex = (selectedSuggestionIndex + 1) % suggestions.length;
    highlightSuggestion(selectedSuggestionIndex);
  } else if (event.key === "ArrowUp") {
    selectedSuggestionIndex = (selectedSuggestionIndex - 1 + suggestions.length) % suggestions.length;
    highlightSuggestion(selectedSuggestionIndex);
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

function displaySuggestions(suggestions) {
  selectedSuggestionIndex = -1;
  searchSuggestionsElement.querySelectorAll(".search-suggestion-item").forEach(item => item.remove());
  suggestions.forEach(suggestion => {
    const button = document.createElement("button");
    button.className = "search-suggestion-item text-muted pl-3 row w-100 m-0";
    button.innerText = suggestion;
    button.value = suggestion;
    button.addEventListener("click", handleSuggestionButton);
    searchSuggestionsElement.appendChild(button);
  });
  if (suggestions.length) {
    searchSuggestionsElement.style.display = "block";
  } else {
    searchSuggestionsElement.style.display = "none";
  }
}

function updateFilter(filter) {
  const url = new URL(window.location);

  url.searchParams.append("f", filter);
  url.searchParams.delete("q");
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

function handleSuggestionButton(event) {
  updateFilter(event.currentTarget.value);
}

function hideSuggestions() {
  searchSuggestionsElement.style.display = "none";
}

function highlightSuggestion(index) {
  const suggestionButtons = searchSuggestionsElement.querySelectorAll(".search-suggestion-item");
  suggestionButtons.forEach((button, i) => {
    if (i === index) {
      button.dataset.state = "active";
    } else {
      button.dataset.state = "";
    }
  });
}

function gridViewElement(image, title, text, url) {
  const frameElement = document.createElement("div")
  frameElement.classList.add(
    "mb-3", "position-relative", "embed-responsive", "embed-responsive-4by3"
  );
  if (image) {
    const imgElement = document.createElement("img");
    imgElement.classList.add(
      "mh-100", "mw-100", "position-absolute", "grid-card-image"
    );
    imgElement.src = image;
    frameElement.appendChild(imgElement);
  } else {
    const svgElement = document.createElementNS(
      "http://www.w3.org/2000/svg", "svg"
    );
    svgElement.setAttribute("width", "400");
    svgElement.setAttribute("height", "300");
    svgElement.classList.add(
      "mh-100", "mw-100", "position-absolute", "grid-card-image"
    );
    const circleElement = document.createElementNS(
      "http://www.w3.org/2000/svg", "circle"
    );
    circleElement.setAttribute("cx", "50%");
    circleElement.setAttribute("cy", "50%");
    circleElement.setAttribute("r", "100");
    circleElement.setAttribute(
      "fill",
      `hsl(${title.split("").reduce(
        (acc, char) => acc + char.charCodeAt(0), 0
      ) % 360}, 50%, 30%)`
    );
    svgElement.appendChild(circleElement);
    const textElement = document.createElementNS(
      "http://www.w3.org/2000/svg", "text"
    );
    textElement.setAttribute("x", "50%");
    textElement.setAttribute("y", "50%");
    textElement.setAttribute("dy", "0.35em");
    textElement.setAttribute("text-anchor", "middle");
    textElement.setAttribute("fill", "white");
    textElement.setAttribute("font-size", "100");
    textElement.setAttribute("font-family", "Arial, sans-serif");
    textElement.appendChild(document.createTextNode(title[0].toUpperCase()));
    svgElement.appendChild(textElement);
    frameElement.appendChild(svgElement);
  }
  const bodyElement = document.createElement("div");
  bodyElement.classList.add("card-body", "d-flex", "flex-column");
  bodyElement.appendChild(frameElement);
  const linkElement = document.createElement("a");
  linkElement.href = url;
  linkElement.classList.add("stretched-link", "post-title");
  linkElement.innerText = title;
  const titleElement = document.createElement("h3");
  titleElement.appendChild(linkElement);
  bodyElement.appendChild(titleElement);
  const summaryElement = document.createElement("p");
  summaryElement.classList.add("card-text");
  summaryElement.innerText = text;
  bodyElement.appendChild(summaryElement);
  const cardElement = document.createElement("div");
  cardElement.classList.add(
    "card", "interactive-card", "shadow-lg", "border-0", "h-100"
  );
  cardElement.appendChild(bodyElement);
  const colElement = document.createElement("div");
  colElement.classList.add("col-lg-4", "col-sm-6", "mb-5");
  colElement.appendChild(cardElement);
  return colElement;
}

function listViewElement(project, url, title, date, text, image) {
  const bodyElement = document.createElement("div");
  bodyElement.classList.add("card-body");
  if (project) {
    const projectElement = document.createElement("h6");
    const iconElement = document.createElement("i");
    iconElement.classList.add("fas", "fa-rss");
    projectElement.appendChild(iconElement);
    const textElement = document.createElement("small");
    textElement.classList.add("ml-1");
    textElement.innerText = project;
    projectElement.appendChild(textElement);
    bodyElement.appendChild(projectElement);
  }
  const titleElement = document.createElement("h3");
  const linkElement = document.createElement("a");
  linkElement.href = url;
  linkElement.classList.add("stretched-link", "post-title");
  linkElement.innerText = title;
  titleElement.appendChild(linkElement);
  bodyElement.appendChild(titleElement);
  if (date) {
    const dateElement = document.createElement("div");
    dateElement.classList.add("mb-2");
    const timeElement = document.createElement("time");
    timeElement.innerText = date;
    dateElement.appendChild(timeElement);
    bodyElement.appendChild(dateElement);
  }
  const textElement = document.createElement("p");
  textElement.classList.add("card-text");
  textElement.innerText = text;
  bodyElement.appendChild(textElement);
  const cardElement = document.createElement("div");
  cardElement.classList.add(
    "card", "interactive-card", "border-0", "shadow-lg", "mb-4"
  );
  if (image) {
    const imgElement = document.createElement("img")
    imgElement.classList.add("m-3", "w-100", "mh-100", "rounded");
    imgElement.src = image;
    const frameElement = document.createElement("div");
    frameElement.classList.add("col-md-3");
    frameElement.appendChild(imgElement);
    const rowElement = document.createElement("div");
    rowElement.classList.add("row");
    rowElement.appendChild(frameElement);
    const columnElement = document.createElement("div");
    columnElement.classList.add("col-md-9", "p-0", "position-static");
    columnElement.appendChild(bodyElement);
    rowElement.appendChild(columnElement);
    cardElement.appendChild(rowElement);
  } else {
    cardElement.appendChild(bodyElement);
  }
  return cardElement;
}
