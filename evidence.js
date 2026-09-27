const search = document.querySelector("#ledger-search");
const records = [...document.querySelectorAll(".ledger-record")];
const filters = [...document.querySelectorAll("[data-filter]")];
const empty = document.querySelector(".ledger-empty");
let activeFilter = "all";

function applyFilters() {
  const query = (search?.value || "").trim().toLowerCase();
  let visible = 0;
  for (const record of records) {
    const inCategory = activeFilter === "all" || record.dataset.category === activeFilter;
    const matches = !query || record.dataset.search.includes(query);
    record.hidden = !(inCategory && matches);
    if (!record.hidden) visible += 1;
  }
  if (empty) empty.hidden = visible !== 0;
}

search?.addEventListener("input", applyFilters);
for (const button of filters) {
  button.addEventListener("click", () => {
    activeFilter = button.dataset.filter;
    for (const candidate of filters) candidate.classList.toggle("active", candidate === button);
    applyFilters();
  });
}
