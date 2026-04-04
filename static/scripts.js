// Finance Dashboard — frontend scripts

const API = ""
let editingRecordId = null
let currentUser = null

// ── Token ─────────────────────────────────────────────────────────────────────

function token() { return localStorage.getItem("fd_token") }

function logout() {
    localStorage.removeItem("fd_token")
    location.href = "/login"
}

// ── API helper ────────────────────────────────────────────────────────────────

async function apiFetch(method, path, body = null) {
    const opts = { method, headers: { "Content-Type": "application/json" } }
    if (token()) opts.headers["Authorization"] = "Bearer " + token()
    if (body)    opts.body = JSON.stringify(body)
    try {
        const r = await fetch(path, opts)
        if (r.status === 204) return {}
        const d = await r.json()
        return r.ok ? d : { error: d.detail || "Something went wrong." }
    } catch {
        return { error: "Network error." }
    }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function fmt(n) {
    return "$" + Number(n).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function showErr(id, msg) {
    const el = document.getElementById(id)
    if (el) el.textContent = msg
}

function clearErr(id) {
    const el = document.getElementById(id)
    if (el) el.textContent = ""
}

// ── Register page ─────────────────────────────────────────────────────────────

function toggleKeyField() {
    const role = document.getElementById("role")?.value
    const field = document.getElementById("key-field")
    if (field) field.style.display = (role === "admin" || role === "analyst") ? "block" : "none"
}

async function register() {
    clearErr("register-error")
    const data = {
        name:      document.getElementById("name").value.trim(),
        username:  document.getElementById("username").value.trim(),
        email:     document.getElementById("email").value.trim(),
        password:  document.getElementById("password").value,
        role:      document.getElementById("role").value,
        admin_key: document.getElementById("admin_key")?.value || null,
    }
    if (!data.name || !data.username || !data.email || !data.password) {
        showErr("register-error", "All fields are required.")
        return
    }
    const r = await apiFetch("POST", "/auth/register", data)
    if (r.error) { showErr("register-error", r.error); return }
    alert("Account created. You can now log in.")
    location.href = "/login"
}

// ── Login page ────────────────────────────────────────────────────────────────

async function login() {
    clearErr("login-error")
    const username = document.getElementById("username").value.trim()
    const password = document.getElementById("password").value
    if (!username || !password) { showErr("login-error", "Username and password are required."); return }
    const r = await apiFetch("POST", "/auth/login", { username, password })
    if (r.error) { showErr("login-error", r.error); return }
    localStorage.setItem("fd_token", r.access_token)
    location.href = "/dashboard"
}

// ── Dashboard init ────────────────────────────────────────────────────────────

async function initDashboard() {
    const user = await apiFetch("GET", "/auth/me")
    if (user.error) { location.href = "/login"; return }
    currentUser = user

    document.getElementById("userInfo").innerText = user.name
    document.getElementById("roleText").innerText  = user.role

    // Show/hide role-gated elements
    document.querySelectorAll(".admin-only").forEach(el =>
        el.classList.toggle("hidden", user.role !== "admin"))
    document.querySelectorAll(".analyst-tab").forEach(el =>
        el.classList.toggle("hidden", user.role === "viewer"))
    document.querySelectorAll(".admin-tab").forEach(el =>
        el.classList.toggle("hidden", user.role !== "admin"))

    loadSummary()
    showTab("records")   // sets active tab + loads records correctly
}

// ── Tabs ──────────────────────────────────────────────────────────────────────

function showTab(name) {
    // Hide all panels and deactivate all tab buttons
    document.querySelectorAll(".tab-panel").forEach(p => p.style.display = "none")
    document.querySelectorAll(".tab").forEach(b => b.classList.remove("active"))

    // Show chosen panel and mark its button active
    document.getElementById("tab-" + name).style.display = "block"
    const btn = document.getElementById("tab-btn-" + name)
    if (btn) btn.classList.add("active")

    if (name === "records")   loadRecords()
    if (name === "analytics") { loadCategories(); loadTrends() }
    if (name === "users")     loadUsers()
}

// ── Summary ───────────────────────────────────────────────────────────────────

async function loadSummary() {
    const d = await apiFetch("GET", "/records/summary")
    if (d.error) return
    document.getElementById("sum-income").textContent  = fmt(d.total_income)
    document.getElementById("sum-expense").textContent = fmt(d.total_expenses)
    document.getElementById("sum-count").textContent   = d.record_count
    const bal = document.getElementById("sum-balance")
    bal.textContent = fmt(d.net_balance)
    bal.className   = "card-val " + (d.net_balance >= 0 ? "green" : "red")
}

// ── Records ───────────────────────────────────────────────────────────────────

async function loadRecords() {
    const qs   = []
    const type = document.getElementById("f-type").value
    const cat  = document.getElementById("f-cat").value
    const from = document.getElementById("f-from").value
    const to   = document.getElementById("f-to").value
    if (type) qs.push("type=" + type)
    if (cat)  qs.push("category=" + encodeURIComponent(cat))
    if (from) qs.push("from_date=" + from)
    if (to)   qs.push("to_date=" + to)

    const d       = await apiFetch("GET", "/records/?" + qs.join("&"))
    const body    = document.getElementById("recordBody")
    const isAdmin = currentUser?.role === "admin"

    if (!Array.isArray(d) || !d.length) {
        body.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:2rem;color:#aaa">No records found.</td></tr>`
        return
    }
    body.innerHTML = d.map(r => `<tr>
        <td>${r.date}</td>
        <td><span class="pill pill-${r.type}">${r.type}</span></td>
        <td style="text-transform:capitalize">${r.category}</td>
        <td class="amt-${r.type}">${r.type === "income" ? "+" : "−"}${fmt(r.amount)}</td>
        <td style="color:#888">${r.notes || "—"}</td>
        <td>${isAdmin ? `<button onclick="editRecord(${r.id},'${r.type}',${r.amount},'${r.category}','${r.date}','${(r.notes||"").replace(/'/g,"\\'")}')">Edit</button>
            <button onclick="deleteRecord(${r.id})">Delete</button>` : ""}</td>
    </tr>`).join("")
}

function openRecordModal() {
    editingRecordId = null
    document.getElementById("modal-record-title").textContent = "Add Record"
    document.getElementById("m-type").value   = "income"
    document.getElementById("m-amount").value = ""
    document.getElementById("m-cat").value    = ""
    document.getElementById("m-date").value   = new Date().toISOString().slice(0, 10)
    document.getElementById("m-notes").value  = ""
    clearErr("record-error")
    document.getElementById("modal-record").classList.add("open")
}

function editRecord(id, type, amount, cat, date, notes) {
    editingRecordId = id
    document.getElementById("modal-record-title").textContent = "Edit Record"
    document.getElementById("m-type").value   = type
    document.getElementById("m-amount").value = amount
    document.getElementById("m-cat").value    = cat
    document.getElementById("m-date").value   = date
    document.getElementById("m-notes").value  = notes
    clearErr("record-error")
    document.getElementById("modal-record").classList.add("open")
}

async function submitRecord() {
    clearErr("record-error")
    const payload = {
        type:     document.getElementById("m-type").value,
        amount:   parseFloat(document.getElementById("m-amount").value),
        category: document.getElementById("m-cat").value.trim(),
        date:     document.getElementById("m-date").value,
        notes:    document.getElementById("m-notes").value.trim(),
    }
    if (!payload.amount || !payload.category || !payload.date) {
        showErr("record-error", "Amount, category, and date are required.")
        return
    }
    const r = editingRecordId
        ? await apiFetch("PUT", `/records/${editingRecordId}`, payload)
        : await apiFetch("POST", "/records/", payload)
    if (r.error) { showErr("record-error", r.error); return }
    closeModal("modal-record")
    loadRecords()
    loadSummary()
}

async function deleteRecord(id) {
    if (!confirm("Delete this record?")) return
    await apiFetch("DELETE", `/records/${id}`)
    loadRecords()
    loadSummary()
}

// ── Analytics ─────────────────────────────────────────────────────────────────

async function loadCategories() {
    const d  = await apiFetch("GET", "/records/by-category")
    const el = document.getElementById("cat-rows")
    if (d.error) { el.innerHTML = `<p style="color:#888">${d.error}</p>`; return }
    const cats = d.by_category
    if (!Object.keys(cats).length) { el.innerHTML = `<p style="color:#888">No data yet.</p>`; return }
    const max = Math.max(...Object.values(cats))
    el.innerHTML = Object.entries(cats).map(([k, v]) => `
        <div class="bar-row">
            <span class="bar-label">${k}</span>
            <div class="bar-bg"><div class="bar-fill" style="width:${Math.round((v/max)*100)}%"></div></div>
            <span class="bar-val">${fmt(v)}</span>
        </div>`).join("")
}

async function loadTrends() {
    const qs   = []
    const from = document.getElementById("tr-from").value
    const to   = document.getElementById("tr-to").value
    if (from) qs.push("from_date=" + from)
    if (to)   qs.push("to_date=" + to)
    const d  = await apiFetch("GET", "/records/trends?" + qs.join("&"))
    const el = document.getElementById("trend-rows")
    if (d.error) { el.innerHTML = `<p style="color:#888">${d.error}</p>`; return }
    const months = d.trends
    if (!Object.keys(months).length) { el.innerHTML = `<p style="color:#888">No data yet.</p>`; return }
    const maxVal = Math.max(...Object.values(months).flatMap(m => [m.income||0, m.expense||0]))
    el.innerHTML = Object.entries(months).map(([m, v]) => `
        <div class="trend-row">
            <span class="trend-month">${m}</span>
            <div class="trend-bars">
                <div class="trend-bar" style="width:${maxVal ? Math.round(((v.income||0)/maxVal)*100) : 0}%;background:#16a34a"></div>
                <div class="trend-bar" style="width:${maxVal ? Math.round(((v.expense||0)/maxVal)*100) : 0}%;background:#dc2626"></div>
            </div>
            <div class="trend-vals">
                <div class="green">${fmt(v.income||0)}</div>
                <div class="red">${fmt(v.expense||0)}</div>
            </div>
        </div>`).join("")
}

// ── Users ─────────────────────────────────────────────────────────────────────

async function loadUsers() {
    const d    = await apiFetch("GET", "/users/list")
    const body = document.getElementById("userBody")
    if (!Array.isArray(d)) {
        body.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:2rem;color:#aaa">Could not load users.</td></tr>`
        return
    }
    body.innerHTML = d.map(u => `<tr>
        <td>${u.name}</td>
        <td style="color:#888">${u.username}</td>
        <td style="color:#888">${u.email}</td>
        <td>${u.role}</td>
        <td>
            <select onchange="updateUser(${u.id}, {is_active: this.value === 'true'})">
                <option value="true"  ${u.is_active  ? "selected" : ""}>Active</option>
                <option value="false" ${!u.is_active ? "selected" : ""}>Inactive</option>
            </select>
        </td>
        <td>
            <select onchange="updateUser(${u.id}, {role: this.value})">
                <option value="viewer"  ${u.role==="viewer"  ? "selected" : ""}>Viewer</option>
                <option value="analyst" ${u.role==="analyst" ? "selected" : ""}>Analyst</option>
                <option value="admin"   ${u.role==="admin"   ? "selected" : ""}>Admin</option>
            </select>
            <button onclick="deleteUser(${u.id})">Delete</button>
        </td>
    </tr>`).join("")
}

function openUserModal() {
    ["u-name","u-username","u-email","u-pass"].forEach(id => document.getElementById(id).value = "")
    document.getElementById("u-role").value = "viewer"
    clearErr("user-error")
    document.getElementById("modal-user").classList.add("open")
}

async function submitUser() {
    clearErr("user-error")
    const data = {
        name:     document.getElementById("u-name").value.trim(),
        username: document.getElementById("u-username").value.trim(),
        email:    document.getElementById("u-email").value.trim(),
        password: document.getElementById("u-pass").value,
        role:     document.getElementById("u-role").value,
    }
    if (!data.name || !data.username || !data.email || !data.password) {
        showErr("user-error", "All fields are required.")
        return
    }
    const r = await apiFetch("POST", "/auth/register", data)
    if (r.error) { showErr("user-error", r.error); return }
    closeModal("modal-user")
    loadUsers()
}

async function updateUser(id, patch) {
    await apiFetch("PUT", `/users/${id}`, patch)
    loadUsers()
}

async function deleteUser(id) {
    if (!confirm("Delete this user and all their records?")) return
    const r = await apiFetch("DELETE", `/users/${id}`)
    if (r.error) alert(r.error)
    else loadUsers()
}

// ── Modals ────────────────────────────────────────────────────────────────────

function closeModal(id) { document.getElementById(id).classList.remove("open") }

document.querySelectorAll(".modal-overlay").forEach(o =>
    o.addEventListener("click", e => { if (e.target === o) o.classList.remove("open") }))
