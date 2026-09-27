const source = "https://raw.githubusercontent.com/arian-gogani/arian-gogani/main/data/profile.json";

document.querySelectorAll(".reveal").forEach((element) => {
  const observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        element.classList.add("visible");
        observer.disconnect();
      }
    },
    { threshold: 0.12 }
  );
  observer.observe(element);
});

fetch(source, { cache: "no-store" })
  .then((response) => {
    if (!response.ok) throw new Error(`profile fetch returned ${response.status}`);
    return response.json();
  })
  .then((profile) => {
    const metrics = profile.metrics;
    for (const element of document.querySelectorAll("[data-metric]")) {
      const key = element.dataset.metric;
      if (Number.isInteger(metrics[key])) element.textContent = metrics[key];
    }
    const measured = document.querySelector("[data-measured-at]");
    if (measured && /^\d{4}-\d{2}-\d{2}$/.test(metrics.measured_at)) {
      measured.dateTime = metrics.measured_at;
      measured.textContent = metrics.measured_at;
    }
  })
  .catch(() => {
    // The generated HTML already contains the last verified snapshot.
  });
