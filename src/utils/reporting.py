import os
import pandas as pd
from jinja2 import BaseLoader, Environment
from datetime import datetime


# This is the HTML template for every report.
# Jinja2 fills in the {{ variables }} at render time.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>INSIGHT — {{ title }}</title>
  <style>
    body        { font-family: Arial, sans-serif; margin: 0; padding: 28px;
                  background: #f7f7f5; color: #1a1a18; }
    h1          { font-size: 24px; font-weight: 600;
                  border-bottom: 2px solid #ddd; padding-bottom: 10px; }
    h2          { font-size: 18px; font-weight: 500; margin-top: 36px; }
    .meta       { font-size: 13px; color: #777; margin-bottom: 28px; }
    .card       { background: white; border-radius: 10px; padding: 22px;
                  margin: 16px 0; box-shadow: 0 1px 5px rgba(0,0,0,0.08); }
    .pass       { display:inline-block; background:#eaf3de; color:#3b6d11;
                  padding:2px 12px; border-radius:12px; font-size:12px;
                  font-weight:600; }
    .fail       { display:inline-block; background:#fcebeb; color:#791f1f;
                  padding:2px 12px; border-radius:12px; font-size:12px;
                  font-weight:600; }
    .warn       { display:inline-block; background:#faeeda; color:#633806;
                  padding:2px 12px; border-radius:12px; font-size:12px;
                  font-weight:600; }
    .stats-row  { display:flex; gap:14px; flex-wrap:wrap; margin:16px 0; }
    .stat-box   { background:white; border-radius:8px; padding:16px 22px;
                  box-shadow:0 1px 4px rgba(0,0,0,0.07); min-width:140px; }
    .stat-val   { font-size:30px; font-weight:600; color:#185fa5; }
    .stat-lbl   { font-size:12px; color:#888; margin-top:2px; }
    table       { width:100%; border-collapse:collapse; font-size:13px;
                  margin-top:12px; }
    th          { background:#f1efe8; text-align:left; padding:9px 14px;
                  font-weight:600; border-bottom:1px solid #ddd; }
    td          { padding:7px 14px; border-bottom:1px solid #eee; }
    tr:hover td { background:#f9f9f7; }
    p           { font-size:14px; color:#555; line-height:1.6; }
  </style>
</head>
<body>

<h1>INSIGHT Report — {{ title }}</h1>
<div class="meta">
  Study: <b>{{ study_name }}</b> &nbsp;|&nbsp;
  Generated: <b>{{ generated_at }}</b> &nbsp;|&nbsp;
  CDM version: <b>{{ cdm_version }}</b>
</div>

{% if stats %}
<div class="stats-row">
  {% for s in stats %}
  <div class="stat-box">
    <div class="stat-val">{{ s.value }}</div>
    <div class="stat-lbl">{{ s.label }}</div>
  </div>
  {% endfor %}
</div>
{% endif %}

{% for section in sections %}
<div class="card">
  <h2>
    {{ section.title }}
    {% if section.status == "pass" %}<span class="pass">PASS</span>{% endif %}
    {% if section.status == "fail" %}<span class="fail">FAIL</span>{% endif %}
    {% if section.status == "warn" %}<span class="warn">WARN</span>{% endif %}
  </h2>

  {% if section.description %}
  <p>{{ section.description }}</p>
  {% endif %}

  {% if section.table %}
  <table>
    <thead>
      <tr>{% for col in section.table.columns %}<th>{{ col }}</th>{% endfor %}</tr>
    </thead>
    <tbody>
      {% for row in section.table.rows %}
      <tr>{% for cell in row %}<td>{{ cell }}</td>{% endfor %}</tr>
      {% endfor %}
    </tbody>
  </table>
  {% endif %}

  {% if section.plot_html %}
  <div style="margin-top:16px">{{ section.plot_html | safe }}</div>
  {% endif %}

</div>
{% endfor %}

</body>
</html>
"""


def dataframe_to_table(df, max_rows=200):
    """
    Convert a pandas DataFrame into the format our HTML template expects:
    a dict with 'columns' (list of strings) and 'rows' (list of lists).
    """
    display_df = df.head(max_rows).fillna("—")
    return {
        "columns": list(display_df.columns),
        "rows": display_df.astype(str).values.tolist()
    }


def render_report(title, sections, config, output_path, filename, stats=None):
    """
    Build and save a complete HTML report.

    Parameters:
      title       : string shown at top of report
      sections    : list of dicts, each with keys:
                      title (str)
                      description (str, optional)
                      status (str: "pass", "fail", "warn", or None)
                      table (dict from dataframe_to_table, optional)
                      plot_html (str of HTML, optional)
      config      : the loaded YAML config dict
      output_path : folder where the HTML file will be saved
      filename    : e.g. "Level1_Report.html"
      stats       : list of dicts with "label" and "value" keys (optional)
    """
    env = Environment(loader=BaseLoader())
    template = env.from_string(HTML_TEMPLATE)

    html_content = template.render(
        title=title,
        study_name=config["study"]["name"],
        cdm_version=config.get("cdm_version", "2.2"),
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        sections=sections,
        stats=stats or []
    )

    os.makedirs(output_path, exist_ok=True)
    full_path = os.path.join(output_path, filename)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Report saved → {full_path}")
    return full_path