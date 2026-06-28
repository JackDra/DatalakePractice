const refreshButton = document.querySelector("#refreshButton");
const statusText = document.querySelector("#statusText");
const summaryBody = document.querySelector("#summaryBody");
const totalSales = document.querySelector("#totalSales");
const totalOrders = document.querySelector("#totalOrders");
const totalUnits = document.querySelector("#totalUnits");

const currencyFormatter = new Intl.NumberFormat("en-AU", {
  style: "currency",
  currency: "AUD",
});

const numberFormatter = new Intl.NumberFormat("en-AU");

function toNumber(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function renderRows(rows) {
  summaryBody.innerHTML = "";

  let sales = 0;
  let orders = 0;
  let units = 0;

  for (const row of rows) {
    const grossSales = toNumber(row.gross_sales);
    const orderCount = toNumber(row.order_count);
    const unitCount = toNumber(row.units_sold);
    sales += grossSales;
    orders += orderCount;
    units += unitCount;

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.order_date ?? ""}</td>
      <td>${row.channel ?? ""}</td>
      <td>${row.category ?? ""}</td>
      <td class="numeric">${numberFormatter.format(orderCount)}</td>
      <td class="numeric">${numberFormatter.format(unitCount)}</td>
      <td class="numeric">${currencyFormatter.format(grossSales)}</td>
      <td class="numeric">${currencyFormatter.format(toNumber(row.avg_line_total))}</td>
    `;
    summaryBody.appendChild(tr);
  }

  totalSales.textContent = currencyFormatter.format(sales);
  totalOrders.textContent = numberFormatter.format(orders);
  totalUnits.textContent = numberFormatter.format(units);
  statusText.textContent = `${rows.length} gold rows loaded`;
}

async function refreshDashboard() {
  refreshButton.disabled = true;
  statusText.textContent = "Refreshing";

  try {
    const response = await fetch("/api/daily-sales-summary");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || "Failed to load dashboard data");
    }

    renderRows(payload.rows || []);
  } catch (error) {
    statusText.textContent = error.message;
  } finally {
    refreshButton.disabled = false;
  }
}

refreshButton.addEventListener("click", refreshDashboard);
refreshDashboard();
setInterval(refreshDashboard, 30000);
