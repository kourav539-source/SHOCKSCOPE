"""Printable offline HTML, with escaped text and no scripts or remote assets."""
from html import escape
from urllib.parse import urlsplit

HEADINGS = {'EXECUTIVE SUMMARY','ASSUMPTIONS AND CALCULATIONS',
            'COUNTRY AND INDUSTRY CONTEXT (QUALITATIVE, NOT A MODEL INPUT)',
            'MANAGEMENT ACTIONS','HISTORICAL EVIDENCE (EVENT CONTEXT ONLY)','LIMITATIONS'}


def report_sections(report):
    sections = [('Report overview', [])]
    for line in report.splitlines():
        if line in HEADINGS:
            sections.append((line.title(), []))
        elif line.strip():
            sections[-1][1].append(line)
    return sections


def report_html(report):
    blocks = []
    for heading, lines in report_sections(report):
        blocks.append('<section><h2>' + escape(heading) + '</h2>')
        for line in lines:
            safe = escape(line)
            # Only source lines containing a plain HTTPS URL become links.
            if heading == 'Historical Evidence (Event Context Only)' and line.startswith('https://'):
                parsed = urlsplit(line)
                if parsed.netloc and not any(c.isspace() for c in line):
                    safe = '<a href="' + escape(line, quote=True) + '">' + safe + '</a>'
            blocks.append('<p>' + safe + '</p>')
        blocks.append('</section>')
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SHOCKSCOPE | Company Impact Report</title><style>
body{font:16px/1.6 system-ui,Arial,sans-serif;color:#17283c;background:#eef3f6;margin:0}
main{max-width:900px;margin:32px auto;padding:36px;background:#fff;border:1px solid #d9e2e9;border-radius:14px}
header{border-bottom:4px solid #147d79;padding-bottom:16px}h1{font-size:30px;margin:0}header p{color:#48637a}h2{font-size:19px;color:#126762;border-bottom:1px solid #d9e2e9;padding-bottom:6px}p{margin:8px 0;overflow-wrap:anywhere}section{margin:24px 0}a{color:#126762}footer{border-top:1px solid #d9e2e9;color:#48637a;font-size:12px;padding-top:12px}
@media print{body{background:#fff;font-size:11pt}main{margin:0;padding:0;border:0}h2{break-after:avoid}p{orphans:2;widows:2}a{color:#17283c}}
</style></head><body><main><header><h1>SHOCKSCOPE</h1><p>Company impact intelligence | Hypothetical scenario analysis</p></header>''' + ''.join(blocks) + '''<footer>Academic startup prototype · Local rule-based reporting · Not investment advice</footer></main></body></html>'''
