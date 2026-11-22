const API_BASE = "";

// Set default dates to today
document.addEventListener("DOMContentLoaded", () => {
  const today = new Date().toISOString().split("T")[0];
  if (document.getElementById("meal-date")) document.getElementById("meal-date").value = today;
  if (document.getElementById("ctx-date")) document.getElementById("ctx-date").value = today;
  if (document.getElementById("pur-date")) document.getElementById("pur-date").value = today;

  checkHealth();
  loadMasterData();
  loadTodayMealLogs();
  loadAllReports();
  loadAuditLogs();
});

function switchTab(tabId) {
  document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  
  const target = document.getElementById(tabId);
  if (target) target.classList.add("active");

  const btn = Array.from(document.querySelectorAll(".tab-btn")).find(b => b.getAttribute("onclick").includes(tabId));
  if (btn) btn.classList.add("active");

  if (tabId === "tab-reports") loadAllReports();
  if (tabId === "tab-audit") loadAuditLogs();
}

async function checkHealth() {
  const badge = document.getElementById("system-status");
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    const data = await res.json();
    if (data.mysql.status === "ok" && data.mongodb.status === "ok") {
      badge.className = "status-badge online";
      badge.textContent = "🟢 MySQL 8 + MongoDB Online";
    } else {
      badge.className = "status-badge error";
      badge.textContent = "⚠️ DB Connection Issue";
    }
  } catch (err) {
    badge.className = "status-badge error";
    badge.textContent = "🔴 Backend Offline";
  }
}

async function loadMasterData() {
  try {
    const [itemsRes, staffRes, vendorsRes, matsRes] = await Promise.all([
      fetch(`${API_BASE}/api/master/items`),
      fetch(`${API_BASE}/api/master/staff`),
      fetch(`${API_BASE}/api/master/vendors`),
      fetch(`${API_BASE}/api/master/raw-materials`)
    ]);

    const items = await itemsRes.json();
    const staff = await staffRes.json();
    const vendors = await vendorsRes.json();
    const materials = await matsRes.json();

    // Populate Food Items
    const itemSelect = document.getElementById("meal-item");
    if (itemSelect) {
      itemSelect.innerHTML = items.map(i => `<option value="${i.item_id}">${i.name} (${i.category} - ${i.unit})</option>`).join("");
    }

    // Populate Staff
    const staffSelect = document.getElementById("meal-staff");
    const fbStaffSelect = document.getElementById("fb-staff-id");
    const staffOptions = staff.map(s => `<option value="${s.staff_id}">${s.name} (${s.role})</option>`).join("");
    if (staffSelect) staffSelect.innerHTML = staffOptions;
    if (fbStaffSelect) fbStaffSelect.innerHTML = staffOptions;

    // Populate Vendors
    const vendorSelect = document.getElementById("pur-vendor");
    if (vendorSelect) {
      vendorSelect.innerHTML = vendors.map(v => `<option value="${v.vendor_id}">${v.name} (${v.item_category_supplied || 'Supplier'})</option>`).join("");
    }

    // Populate Raw Materials
    const matSelect = document.getElementById("pur-material");
    if (matSelect) {
      matSelect.innerHTML = materials.map(m => `<option value="${m.material_id}">${m.name} (${m.unit})</option>`).join("");
    }
  } catch (err) {
    console.error("Error loading master data:", err);
  }
}

async function loadTodayMealLogs() {
  const dateInput = document.getElementById("meal-date");
  const date = dateInput ? dateInput.value : new Date().toISOString().split("T")[0];
  try {
    const res = await fetch(`${API_BASE}/api/meals/daily/${date}`);
    const logs = await res.json();
    
    const wastageSelect = document.getElementById("wastage-log-id");
    const fbSelect = document.getElementById("fb-log-id");
    
    if (logs && logs.length > 0) {
      const wastageOptions = logs.map(l => {
        const remaining = l.remaining_leftover !== undefined ? l.remaining_leftover : l.leftover_qty;
        const isExhausted = remaining <= 0;
        const statusText = isExhausted ? "(All Leftovers Accounted For)" : `(Remaining: ${remaining} / Total Leftover: ${l.leftover_qty})`;
        return `<option value="${l.log_id}" ${isExhausted ? "disabled" : ""}>#${l.log_id}: ${l.meal_type.toUpperCase()} - ${l.item_name} ${statusText}</option>`;
      }).join("");

      const fbOptions = logs.map(l => 
        `<option value="${l.log_id}">#${l.log_id}: ${l.meal_type.toUpperCase()} - ${l.item_name}</option>`
      ).join("");

      if (wastageSelect) wastageSelect.innerHTML = wastageOptions;
      if (fbSelect) fbSelect.innerHTML = fbOptions;
    } else {
      const fallback = '<option value="">No meals logged for this date yet</option>';
      if (wastageSelect) wastageSelect.innerHTML = fallback;
      if (fbSelect) fbSelect.innerHTML = fallback;
    }
  } catch (e) {
    console.error("Failed to load daily meal logs", e);
  }
}

async function handleMealLog(e) {
  e.preventDefault();
  const btn = e.target.querySelector("button[type='submit']");
  const originalText = btn.textContent;
  btn.textContent = "⏳ Saving...";
  btn.disabled = true;

  const msg = document.getElementById("meal-log-msg");
  msg.style.display = "none";

  const payload = {
    meal_date: document.getElementById("meal-date").value,
    meal_type: document.getElementById("meal-type").value,
    item_id: parseInt(document.getElementById("meal-item").value),
    staff_id: parseInt(document.getElementById("meal-staff").value),
    qty_prepared: parseInt(document.getElementById("meal-qty-prep").value),
    qty_sold: parseInt(document.getElementById("meal-qty-sold").value),
    price_per_unit: parseFloat(document.getElementById("meal-price").value),
    customer_count_est: document.getElementById("meal-customers").value ? parseInt(document.getElementById("meal-customers").value) : null
  };

  try {
    const res = await fetch(`${API_BASE}/api/meals/log`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to save meal log");

    msg.className = "alert-msg success";
    msg.style.display = "block";
    msg.innerHTML = `✅ <strong>Recorded in MySQL!</strong><br>• Cumulative Prepared: <strong>${data.meal_log.qty_prepared}</strong> | Sold: <strong>${data.meal_log.qty_sold}</strong><br>• Current Leftover: <strong>${data.meal_log.leftover_qty}</strong> units<br>🔒 <strong>MongoDB Audit Hash:</strong> <code>${data.audit_hash.substring(0, 16)}...</code>`;
    loadTodayMealLogs();
  } catch (err) {
    msg.className = "alert-msg error";
    msg.style.display = "block";
    msg.textContent = `❌ ${err.message}`;
  } finally {
    btn.textContent = originalText;
    btn.disabled = false;
  }
}

async function handleWastage(e) {
  e.preventDefault();
  const btn = e.target.querySelector("button[type='submit']");
  const origText = btn.textContent;
  btn.textContent = "⏳ Logging...";
  btn.disabled = true;

  const msg = document.getElementById("wastage-msg");
  msg.style.display = "none";

  const logId = document.getElementById("wastage-log-id").value;
  if (!logId) {
    alert("Please select an active meal log first");
    btn.textContent = origText;
    btn.disabled = false;
    return;
  }

  const payload = {
    log_id: parseInt(logId),
    qty_wasted: parseInt(document.getElementById("wastage-qty").value),
    reason_code: document.getElementById("wastage-reason").value,
    disposal_method: document.getElementById("wastage-disposal").value
  };

  try {
    const res = await fetch(`${API_BASE}/api/meals/wastage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to log wastage");

    msg.className = "alert-msg success";
    msg.style.display = "block";
    msg.innerHTML = `✅ Wastage recorded! 🔒 Audit Hash: <code>${data.audit_hash.substring(0, 16)}...</code>`;
    document.getElementById("wastage-qty").value = "";
    loadTodayMealLogs();
  } catch (err) {
    msg.className = "alert-msg error";
    msg.style.display = "block";
    msg.textContent = `❌ ${err.message}`;
  } finally {
    btn.textContent = origText;
    btn.disabled = false;
  }
}

async function handleContext(e) {
  e.preventDefault();
  const msg = document.getElementById("ctx-msg");
  msg.style.display = "none";

  const payload = {
    date: document.getElementById("ctx-date").value,
    weather: document.getElementById("ctx-weather").value,
    is_holiday: document.getElementById("ctx-holiday").checked,
    exam_period: document.getElementById("ctx-exam").checked,
    special_event: document.getElementById("ctx-event").value,
    notes: document.getElementById("ctx-notes").value
  };

  try {
    const res = await fetch(`${API_BASE}/api/context`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error("Failed to save context");

    msg.className = "alert-msg success";
    msg.style.display = "block";
    msg.textContent = `✅ Saved context for ${data.date} in MongoDB DailyContext!`;
  } catch (err) {
    msg.className = "alert-msg error";
    msg.style.display = "block";
    msg.textContent = `❌ ${err.message}`;
  }
}

async function handleFeedback(e) {
  e.preventDefault();
  const msg = document.getElementById("fb-msg");
  msg.style.display = "none";

  const logId = document.getElementById("fb-log-id").value;
  if (!logId) {
    alert("Please select a meal log to link feedback to");
    return;
  }

  const payload = {
    log_id: parseInt(logId),
    source: document.getElementById("fb-source").value,
    staff_id: document.getElementById("fb-source").value === "staff" ? parseInt(document.getElementById("fb-staff-id").value) : null,
    note_text: document.getElementById("fb-text").value
  };

  try {
    const res = await fetch(`${API_BASE}/api/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error("Failed to submit feedback");

    msg.className = "alert-msg success";
    msg.style.display = "block";
    msg.innerHTML = `✅ Feedback stored in MongoDB!<br>🏷️ Auto-matched tags: <strong>${data.tags.length ? data.tags.join(", ") : "None"}</strong>`;
    document.getElementById("fb-text").value = "";
  } catch (err) {
    msg.className = "alert-msg error";
    msg.style.display = "block";
    msg.textContent = `❌ ${err.message}`;
  }
}

async function handlePurchase(e) {
  e.preventDefault();
  const msg = document.getElementById("pur-msg");
  msg.style.display = "none";

  const payload = {
    purchase_date: document.getElementById("pur-date").value,
    vendor_id: parseInt(document.getElementById("pur-vendor").value),
    material_id: parseInt(document.getElementById("pur-material").value),
    qty_purchased: parseFloat(document.getElementById("pur-qty").value),
    cost: parseFloat(document.getElementById("pur-cost").value),
    batch_no: document.getElementById("pur-batch").value || null
  };

  try {
    const res = await fetch(`${API_BASE}/api/purchases`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to record purchase");

    msg.className = "alert-msg success";
    msg.style.display = "block";
    msg.innerHTML = `✅ Purchase recorded in MySQL! 🔒 Audit Hash: <code>${data.audit_hash.substring(0, 16)}...</code>`;
  } catch (err) {
    msg.className = "alert-msg error";
    msg.style.display = "block";
    msg.textContent = `❌ ${err.message}`;
  }
}

async function loadAllReports() {
  try {
    // 1. Weekday leftover
    const wRes = await fetch(`${API_BASE}/api/reports/weekday-leftover`);
    const wData = await wRes.json();
    const wBody = document.querySelector("#tbl-weekday tbody");
    if (wBody) {
      wBody.innerHTML = wData.map(r => `
        <tr>
          <td><strong>${r.item_name}</strong></td>
          <td>${r.weekday}</td>
          <td>${r.sessions_count}</td>
          <td><span style="color: ${r.avg_leftover_pct > 20 ? '#dc2626' : '#16a34a'}"><strong>${r.avg_leftover_pct}%</strong></span></td>
        </tr>
      `).join("") || '<tr><td colspan="4" style="text-align:center;">No data</td></tr>';
    }

    // 2. Weekly wastage
    const wasteRes = await fetch(`${API_BASE}/api/reports/weekly-wastage`);
    const wasteData = await wasteRes.json();
    const wasteBody = document.querySelector("#tbl-wastage tbody");
    if (wasteBody) {
      wasteBody.innerHTML = wasteData.map(r => `
        <tr>
          <td><strong>${r.item_name}</strong></td>
          <td>${r.category}</td>
          <td><strong style="color: #dc2626;">${r.total_wasted_qty}</strong></td>
          <td>${r.unit}</td>
        </tr>
      `).join("") || '<tr><td colspan="4" style="text-align:center;">No wastage logged in past 7 days</td></tr>';
    }

    // 3. Vendor spend
    const vRes = await fetch(`${API_BASE}/api/reports/vendor-spend`);
    const vData = await vRes.json();
    const vBody = document.querySelector("#tbl-vendor tbody");
    if (vBody) {
      vBody.innerHTML = vData.map(r => `
        <tr>
          <td><strong>${r.vendor_name}</strong></td>
          <td>${r.purchase_month}</td>
          <td>${r.total_orders}</td>
          <td>₹${Number(r.total_spend).toLocaleString()}</td>
        </tr>
      `).join("") || '<tr><td colspan="4" style="text-align:center;">No purchases recorded</td></tr>';
    }

    // 4. Exam period cross-store join
    const examRes = await fetch(`${API_BASE}/api/reports/exam-context-analysis`);
    const examData = await examRes.json();
    const examBody = document.querySelector("#tbl-exam tbody");
    if (examBody) {
      examBody.innerHTML = examData.comparison.map(r => `
        <tr>
          <td><strong>${r.period_type}</strong></td>
          <td>${r.total_meals}</td>
          <td><strong style="color: #2563eb;">${r.avg_leftover_pct}%</strong></td>
        </tr>
      `).join("") || '<tr><td colspan="3" style="text-align:center;">No comparison data yet</td></tr>';
    }
  } catch (err) {
    console.error("Error loading reports:", err);
  }
}

async function loadAuditLogs() {
  try {
    const res = await fetch(`${API_BASE}/api/audit/logs?limit=25`);
    const logs = await res.json();
    const tbody = document.querySelector("#tbl-audit tbody");
    if (tbody) {
      tbody.innerHTML = logs.map(l => `
        <tr>
          <td><span style="font-weight:600; color:#2563eb;">${l.action}</span></td>
          <td>${l.record_id}</td>
          <td>${new Date(l.timestamp).toLocaleString()}</td>
          <td class="hash-cell" title="${l.prev_hash}">${l.prev_hash}</td>
          <td class="hash-cell" title="${l.curr_hash}"><strong>${l.curr_hash}</strong></td>
        </tr>
      `).join("") || '<tr><td colspan="5" style="text-align:center;">Audit trail empty</td></tr>';
    }
  } catch (err) {
    console.error("Failed to load audit logs", err);
  }
}

async function verifyChain() {
  const banner = document.getElementById("audit-verify-result");
  banner.className = "verify-banner";
  banner.textContent = "Verifying cryptographic hash chain...";

  try {
    const res = await fetch(`${API_BASE}/api/audit/verify`);
    const result = await res.json();
    
    if (result.intact) {
      banner.className = "verify-banner valid";
      banner.innerHTML = `🛡️ <strong>Chain Verified Intact!</strong> ${result.message}<br><small>Verified ${result.total_records} records against SHA-256 block hashes.</small>`;
    } else {
      banner.className = "verify-banner invalid";
      banner.innerHTML = `🚨 <strong>Tamper Alert!</strong> ${result.reason} (Broken at record index ${result.broken_at_index}: ${result.record_id})`;
    }
    loadAuditLogs();
  } catch (err) {
    banner.className = "verify-banner invalid";
    banner.textContent = `Verification request failed: ${err.message}`;
  }
}

async function clearOldLogs() {
  const confirmed = confirm(
    "⚠️ ARE YOU SURE YOU WANT TO CLEAR OLD LOGS?\n\nThis will remove all transaction rows (meals, wastage, purchases, audit blocks, daily context, and feedback notes).\n\nYour Master Data (Food Menu, Staff, Vendors, Recipes, Raw Materials) will be safely KEPT intact."
  );
  if (!confirmed) return;

  try {
    const res = await fetch(`${API_BASE}/api/admin/clear-logs`, {
      method: "DELETE"
    });
    const data = await res.json();
    alert("✅ " + data.message);
    loadTodayMealLogs();
    loadAllReports();
    loadAuditLogs();
  } catch (err) {
    alert("❌ Error clearing logs: " + err.message);
  }
}

