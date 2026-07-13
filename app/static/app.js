const tabs = document.querySelectorAll(".tab");
const panels = document.querySelectorAll(".panel");

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => t.classList.remove("active"));
    panels.forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(tab.dataset.tab).classList.add("active");

    if (tab.dataset.tab === "papers") loadPapers();
    if (tab.dataset.tab === "analytics" || tab.dataset.tab === "dashboard") loadAnalytics();
  });
});

function showAlert(container, message, type = "success") {
  container.innerHTML = `<div class="alert ${type}">${message}</div>`;
}

function renderBars(items, labelKey = "field", valueKey = "count") {
  if (!items.length) return "<p class='muted'>No data yet. Upload papers to see analytics.</p>";

  const max = Math.max(...items.map((item) => item[valueKey]), 1);
  return items
    .map((item) => {
      const width = (item[valueKey] / max) * 100;
      return `
        <div class="bar-row">
          <span>${item[labelKey]}</span>
          <div class="bar-track"><div class="bar-fill" style="width:${width}%"></div></div>
          <span>${item[valueKey]}</span>
        </div>`;
    })
    .join("");
}

async function loadAnalytics() {
  try {
    const response = await fetch("/api/analytics/overview");
    const data = await response.json();

    document.getElementById("stat-total").textContent = data.summary.total_papers;
    document.getElementById("stat-fields").textContent = data.summary.unique_fields;
    document.getElementById("stat-format").textContent = `${data.summary.average_format_score}%`;

    document.getElementById("top-fields").innerHTML = renderBars(data.top_researched_fields);
    document.getElementById("field-distribution").innerHTML = renderBars(data.field_distribution);

    const underexplored = data.underexplored_fields
      .map(
        (item) => `
        <div class="opportunity">
          <strong>${item.field} (${item.count} papers)</strong>
          <span class="muted">${item.scope_note}</span>
        </div>`
      )
      .join("");
    document.getElementById("underexplored").innerHTML =
      underexplored || "<p class='muted'>All fields have healthy representation.</p>";

    const opportunities = data.opportunity_fields
      .map(
        (item) => `
        <div class="opportunity">
          <strong>${item.field}</strong>
          <span class="muted">${item.reason}</span><br />
          <span class="muted">${item.suggested_action}</span>
        </div>`
      )
      .join("");
    document.getElementById("opportunities").innerHTML =
      opportunities || "<p class='muted'>Upload more papers to detect emerging opportunities.</p>";

    const keywords = data.trending_keywords
      .map((item) => `<span class="tag">${item.keyword} (${item.count})</span>`)
      .join("");
    document.getElementById("keywords").innerHTML =
      keywords || "<p class='muted'>No keywords extracted yet.</p>";

    document.getElementById("departments").innerHTML = renderBars(
      data.department_activity,
      "department",
      "count"
    );
  } catch (error) {
    console.error(error);
  }
}

async function loadPapers() {
  const container = document.getElementById("papers-list");
  container.innerHTML = "<p class='loading'>Loading papers...</p>";

  try {
    const response = await fetch("/api/papers");
    const papers = await response.json();

    if (!papers.length) {
      container.innerHTML = "<p class='muted'>No papers uploaded yet.</p>";
      return;
    }

    container.innerHTML = papers
      .map(
        (paper) => `
        <div class="paper-item">
          <div>
            <h4>${paper.title}</h4>
            <p class="muted">${paper.author || "Unknown author"} · ${paper.department || "No department"} · ${paper.publication_year || "N/A"}</p>
            <span class="tag">${paper.primary_field || "Unclassified"}</span>
            <span class="tag">Format: ${paper.format_score}%</span>
            ${(paper.keywords || []).slice(0, 4).map((k) => `<span class="tag">${k}</span>`).join("")}
          </div>
          <button class="danger" onclick="deletePaper(${paper.id})">Delete</button>
        </div>`
      )
      .join("");
  } catch (error) {
    container.innerHTML = "<p class='muted'>Failed to load papers.</p>";
  }
}

async function deletePaper(id) {
  if (!confirm("Delete this paper?")) return;
  await fetch(`/api/papers/${id}`, { method: "DELETE" });
  loadPapers();
  loadAnalytics();
}

document.getElementById("upload-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const result = document.getElementById("upload-result");
  const formData = new FormData(event.target);

  showAlert(result, "Uploading and analyzing...", "warning");

  try {
    const response = await fetch("/api/papers/upload", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      let message = data.detail?.message || data.detail || "Upload failed.";
      if (data.detail?.plagiarism_report) {
        const matches = data.detail.plagiarism_report.matches
          .map((m) => `${m.title} (${m.similarity_percent}% similar)`)
          .join("<br>");
        message += `<br><br>Matches:<br>${matches}`;
      }
      showAlert(result, message, "error");
      return;
    }

    const similarity = data.plagiarism_report?.highest_similarity || 0;
    showAlert(
      result,
      `Uploaded successfully!<br>
       Field: <strong>${data.primary_field}</strong><br>
       Format score: ${data.structure.format_score}%<br>
       Highest similarity with existing papers: ${similarity}%`,
      "success"
    );
    event.target.reset();
    loadAnalytics();
  } catch (error) {
    showAlert(result, "Upload failed. Please try again.", "error");
  }
});

document.getElementById("plagiarism-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const result = document.getElementById("plagiarism-result");
  const formData = new FormData(event.target);

  showAlert(result, "Checking document...", "warning");

  try {
    const response = await fetch("/api/papers/check-plagiarism", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    if (!data.matches.length) {
      showAlert(result, "No significant similarity found with stored papers.", "success");
      return;
    }

    const matches = data.matches
      .map(
        (match) => `
        <div class="opportunity">
          <strong>${match.title} — ${match.similarity_percent}% similar</strong>
          ${match.is_duplicate ? '<span class="tag">Possible Duplicate</span>' : ""}
          ${(match.matching_passages || [])
            .slice(0, 2)
            .map(
              (p) => `<p class="muted">"${p.source_excerpt}..."</p>`
            )
            .join("")}
        </div>`
      )
      .join("");

    const type = data.status === "duplicate_detected" ? "error" : "warning";
    showAlert(
      result,
      `Status: <strong>${data.status.replace(/_/g, " ")}</strong> (${data.highest_similarity}% max similarity)<br>${matches}`,
      type
    );
  } catch (error) {
    showAlert(result, "Plagiarism check failed.", "error");
  }
});

loadAnalytics();
