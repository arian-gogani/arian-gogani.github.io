const source = "https://raw.githubusercontent.com/arian-gogani/arian-gogani/main/data/profile.json";

const revealElements = document.querySelectorAll(".reveal");

if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      }
    },
    { threshold: 0.12 }
  );
  revealElements.forEach((element) => observer.observe(element));
} else {
  revealElements.forEach((element) => element.classList.add("visible"));
}

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
