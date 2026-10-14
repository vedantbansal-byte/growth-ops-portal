import os
import io
import csv
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

MB_BASE_URL = "https://metabase.kaip.in"

METABASE_CONFIG = [
    {"name": "Facebook PnL", "type": "card", "id": 7240},
    {"name": "Product PnL", "type": "card", "id": 5087},
    {"name": "Product PnL SKU level", "type": "card", "id": 5089},
    {"name": "Campaign PnL", "type": "card", "id": 5058},
    {"name": "State PnL", "type": "card", "id": 5058},
    {"name": "Tier", "type": "card", "id": 5097},
    {"name": "City", "type": "card", "id": 5099},
    {"name": "Payment Mode", "type": "card", "id": 5101},
    {"name": "Platform", "type": "card", "id": 5105},
    {"name": "Product mix", "type": "card", "id": 5108},
    {"name": "Age", "type": "card", "id": 5148},
    {"name": "Gender", "type": "card", "id": 5150},
    {"name": "City Wise RTO", "type": "dashboard", "id": 266},
    {"name": "State PnL - Campaign Split", "type": "card", "id": 4411}
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>L3 Automated Metabase & Marketing RCA Tool</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root { --bg: #F8FAFC; --card: #FFFFFF; --border: #E2E8F0; --text: #0F172A; --primary: #4338CA; --danger: #EF4444; --success: #10B981; }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
    body { background: var(--bg); color: var(--text); padding: 24px; font-size: 13px; }
    .header { margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
    .header h1 { font-size: 20px; font-weight: 800; color: var(--primary); }
    .grid { display: grid; grid-template-columns: 340px 1fr; gap: 20px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .form-group { margin-bottom: 12px; }
    .form-group label { display: block; font-weight: 700; font-size: 11px; text-transform: uppercase; color: #64748B; margin-bottom: 4px; }
    .form-input { width: 100%; border: 1px solid var(--border); border-radius: 8px; padding: 8px 12px; font-size: 12px; outline: none; }
    .btn-submit { width: 100%; background: var(--primary); color: #FFF; border: none; padding: 10px; border-radius: 8px; font-weight: 800; cursor: pointer; }
    .btn-submit:hover { opacity: 0.9; }
    .rca-box { background: #EEF2FF; border-left: 4px solid var(--primary); padding: 14px; border-radius: 0 8px 8px 0; margin-bottom: 16px; }
    .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin-bottom: 16px; }
    .m-card { background: #FAF5FF; border: 1px solid #E9D5FF; border-radius: 8px; padding: 10px; }
    .m-card .val { font-size: 16px; font-weight: 800; color: #581C87; }
    table { width: 100%; border-collapse: collapse; text-align: left; }
    th { background: #F8FAFC; border-bottom: 2px solid var(--border); padding: 8px; font-size: 10px; text-transform: uppercase; }
    td { border-bottom: 1px solid var(--border); padding: 8px; }
    .badge { padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: 800; text-transform: uppercase; }
    .badge-rto { background: #FEE2E2; color: #DC2626; }
    .badge-mkt { background: #FEF3C7; color: #D97706; }
    .badge-ops { background: #E0E7FF; color: #3730A3; }
    .status-box { background: #F1F5F9; border: 1px solid var(--border); border-radius: 8px; padding: 10px; margin-bottom: 12px; font-family: monospace; font-size: 11px; }
  </style>
</head>
<body>

  <div class="header">
    <h1>🚀 Company L3 Automated Metabase + Marketing Deep RCA Tool</h1>
    <span style="color:#64748B;">Live Query Extraction & Diagnostic Engine</span>
  </div>

  <div class="grid">
    <div class="card">
      <h3 style="margin-bottom:12px;">🔐 Metabase Credentials & Inputs</h3>
      <form id="rcaForm">
        <div class="form-group">
          <label>Metabase Username/Email</label>
          <input type="text" id="username" class="form-input" required placeholder="user@company.com">
        </div>
        <div class="form-group">
          <label>Metabase Password</label>
          <input type="password" id="password" class="form-input" required placeholder="••••••••">
        </div>
        <div class="form-group">
          <label>Seller ID</label>
          <input type="text" id="seller_id" class="form-input" required placeholder="e.g. 63c8ff0d4c19190012b48ddd">
        </div>
        <div class="form-group">
          <label>Start Date (YYYY-MM-DD)</label>
          <input type="date" id="start_date" class="form-input" required>
        </div>
        <div class="form-group">
          <label>End Date (YYYY-MM-DD)</label>
          <input type="date" id="end_date" class="form-input" required>
        </div>
        <div class="form-group">
          <label>Last Week Meta Marketing CSV <span style="color:red">*</span></label>
          <input type="file" id="last_week_csv" class="form-input" accept=".csv" required>
        </div>
        <div class="form-group">
          <label>Profitable Period Meta CSV (Optional)</label>
          <input type="file" id="profitable_csv" class="form-input" accept=".csv">
        </div>
        <button type="submit" class="btn-submit">Execute Deep L3 Diagnosis</button>
      </form>
    </div>

    <div class="card" id="reportCard">
      <h3>📋 Executive Correlated Diagnostic Summary</h3>
      <p id="placeholder" style="color:#64748B; padding:30px 0; text-align:center;">Enter credentials and files to execute full Metabase + Meta data extraction.</p>
      
      <div id="reportContent" style="display:none;">
        <div class="status-box" id="statusLog"></div>

        <div class="rca-box">
          <h2 id="rcaPrimaryTitle" style="font-size:16px; font-weight:800; color:var(--primary);">--</h2>
          <p id="rcaPrimaryDesc" style="margin-top:4px; color:#334155;">--</p>
        </div>

        <div class="metrics-grid" id="metricsGrid"></div>

        <h4 style="margin: 16px 0 8px 0;">🔍 Metabase + Meta Ads Extracted Diagnostics</h4>
        <table>
          <thead>
            <tr>
              <th>Source</th>
              <th>Extracted Shift & Metabase Evidence</th>
              <th>Impact</th>
              <th>Actionable Fix</th>
            </tr>
          </thead>
          <tbody id="diagnosticRows"></tbody>
        </table>
      </div>
    </div>
  </div>

  <script>
    const today = new Date();
    const day = today.getDay();
    const lastSun = new Date(today);
    lastSun.setDate(today.getDate() - (day === 0 ? 7 : day));
    const lastMon = new Date(lastSun);
    lastMon.setDate(lastSun.getDate() - 6);

    document.getElementById('start_date').value = lastMon.toISOString().split('T')[0];
    document.getElementById('end_date').value = lastSun.toISOString().split('T')[0];

    document.getElementById('rcaForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      document.getElementById('placeholder').innerText = "Querying Metabase API & Fetching Live Question Tables...";
      document.getElementById('reportContent').style.display = 'none';

      const formData = new FormData();
      formData.append('username', document.getElementById('username').value);
      formData.append('password', document.getElementById('password').value);
      formData.append('seller_id', document.getElementById('seller_id').value);
      formData.append('start_date', document.getElementById('start_date').value);
      formData.append('end_date', document.getElementById('end_date').value);
      formData.append('last_week_csv', document.getElementById('last_week_csv').files[0]);

      if (document.getElementById('profitable_csv').files[0]) {
        formData.append('profitable_csv', document.getElementById('profitable_csv').files[0]);
      }

      try {
        const response = await fetch('/api/diagnose', { method: 'POST', body: formData });
        const res = await response.json();

        if (!res.success) {
          alert('Error: ' + res.error);
          document.getElementById('placeholder').innerText = 'Diagnostic failed. Check inputs.';
          return;
        }

        document.getElementById('statusLog').innerHTML = `<b>Metabase Query Status:</b> Extracted ${res.mb_fetched}/${res.mb_total} query cards successfully (${res.rows_extracted} total data rows parsed).`;

        document.getElementById('rcaPrimaryTitle').innerText = "Primary Driver: " + res.primary_driver;
        document.getElementById('rcaPrimaryDesc').innerText = res.description;

        document.getElementById('metricsGrid').innerHTML = `
          <div class="m-card"><div>Spend</div><div class="val">₹${res.metrics.spend.toLocaleString()}</div></div>
          <div class="m-card"><div>ROAS</div><div class="val">${res.metrics.roas}x</div></div>
          <div class="m-card"><div>CPA</div><div class="val">₹${res.metrics.cpa}</div></div>
          <div class="m-card"><div>CTR</div><div class="val">${res.metrics.ctr}%</div></div>
          <div class="m-card"><div>CPM</div><div class="val">₹${res.metrics.cpm}</div></div>
        `;

        let rowsHtml = '';
        res.findings.forEach(f => {
          let badgeClass = 'badge-mkt';
          if (f.type === 'RTO') badgeClass = 'badge-rto';
          if (f.type === 'Metabase Data') badgeClass = 'badge-ops';

          rowsHtml += `
            <tr>
              <td><span class="badge ${badgeClass}">${
