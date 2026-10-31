// Leave empty to use the same origin. Override with ?api=... when the static
// frontend and FastAPI are served separately.
const configuredApi = new URLSearchParams(window.location.search).get("api");
const apiCandidates = configuredApi ? [configuredApi] : [window.location.origin];
let activeApiBase = apiCandidates[0].replace(/\/+$/, "");

const form = document.querySelector("#prediction-form");
const errorBox = document.querySelector("#error-message");
const submitButton = document.querySelector("#submit-button");
const apiStatus = document.querySelector("#api-status");
const apiPill = document.querySelector(".api-pill");
const resultTitle = document.querySelector("#result-title");
const resultSummary = document.querySelector("#result-summary");
const durationValue = document.querySelector("#duration-value");
const durationSeconds = document.querySelector("#duration-seconds");
const resultSymbol = document.querySelector(".result-symbol");

function setApiStatus(connected) {
  apiStatus.textContent = connected ? "API connected" : "Frontend only";
  apiPill.classList.toggle("connected", connected);
  apiPill.classList.toggle("offline", !connected);
}

async function checkApi() {
  for (const candidate of apiCandidates) {
    const base = candidate.replace(/\/+$/, "");
    try {
      const response = await fetch(`${base}/openapi.json`, { method: "GET" });
      if (response.ok) {
        activeApiBase = base;
        setApiStatus(true);
        return true;
      }
    } catch {
      // Try the next candidate. The UI remains usable without the API.
    }
  }
  setApiStatus(false);
  return false;
}

function clearResult() {
  errorBox.hidden = true;
  resultTitle.textContent = "Your trip duration estimate will appear here.";
  resultSummary.textContent = "Enter the trip details, then select “Predict duration”.";
  durationValue.textContent = "—";
  durationSeconds.textContent = "—";
  resultSymbol.textContent = "↗";
  resultSymbol.style.color = "var(--accent)";
}

function randomBetween(min, max, step = 1) {
  const count = Math.floor((max - min) / step);
  return min + Math.floor(Math.random() * (count + 1)) * step;
}

function randomizeInputs() {
  document.querySelector("#passenger-count").value = randomBetween(1, 5);
  document.querySelector("#vendor-id").value = Math.random() > 0.5 ? "1" : "2";
  document.querySelector("#store-and-fwd-flag").value = Math.random() > 0.9 ? "Y" : "N";
  document.querySelector("#pickup-latitude").value = (40.70 + Math.random() * 0.08).toFixed(5);
  document.querySelector("#pickup-longitude").value = (-74.02 + Math.random() * 0.08).toFixed(5);
  document.querySelector("#dropoff-latitude").value = (40.70 + Math.random() * 0.08).toFixed(5);
  document.querySelector("#dropoff-longitude").value = (-74.02 + Math.random() * 0.08).toFixed(5);

  const date = new Date();
  date.setMinutes(date.getMinutes() - Math.floor(Math.random() * 60 * 24 * 30));
  date.setHours(randomBetween(0, 23), randomBetween(0, 59), randomBetween(0, 59));
  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  document.querySelector("#pickup-datetime").value = localDate.toISOString().slice(0, 16);
  clearResult();
}

function collectTrip() {
  return {
    id: `frontend-${Date.now()}`,
    vendor_id: Number(document.querySelector("#vendor-id").value),
    pickup_datetime: document.querySelector("#pickup-datetime").value,
    pickup_longitude: Number(document.querySelector("#pickup-longitude").value),
    pickup_latitude: Number(document.querySelector("#pickup-latitude").value),
    dropoff_longitude: Number(document.querySelector("#dropoff-longitude").value),
    dropoff_latitude: Number(document.querySelector("#dropoff-latitude").value),
    passenger_count: Number(document.querySelector("#passenger-count").value),
    store_and_fwd_flag: document.querySelector("#store-and-fwd-flag").value,
  };
}

document.querySelector("#randomize-inputs").addEventListener("click", randomizeInputs);
document.querySelector("#reset-form").addEventListener("click", () => {
  form.reset();
  clearResult();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.hidden = true;
  submitButton.disabled = true;
  submitButton.innerHTML = "Predicting… <span>↻</span>";

  try {
    const response = await fetch(`${activeApiBase}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(collectTrip()),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.detail || payload.error || "The API rejected the request.");
    }

    const minutes = Number(payload.predicted_duration);
    if (!Number.isFinite(minutes)) throw new Error("The API response did not include a valid duration.");
    const seconds = Math.round(minutes * 60);
    durationValue.textContent = `${minutes.toFixed(1)} min`;
    durationSeconds.textContent = `${seconds.toLocaleString()} seconds`;
    resultTitle.textContent = "Estimated trip duration";
    resultSummary.textContent = "The estimate is based on the route, pickup time, passenger count, and vendor details.";
    resultSymbol.textContent = "✓";
    resultSymbol.style.color = "var(--success)";
    document.querySelector("#result-panel").scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (error) {
    errorBox.textContent = error instanceof TypeError
      ? "FastAPI is not reachable. Start it in the background, then try again."
      : (error.message || "Something went wrong. Please try again.");
    errorBox.hidden = false;
    await checkApi();
  } finally {
    submitButton.disabled = false;
    submitButton.innerHTML = "Predict duration <span>↗</span>";
  }
});

clearResult();
checkApi();
