import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.report_service import ReportService

sample_md = """# ARX INVENTOR: Executive Research Briefing
## Global Solar Energy Outlook 2024

### 1. Executive Summary
In 2024, renewable solar infrastructure achieved unprecedented growth, marked by distinct divergence between utility-scale centralized deployments and decentralized residential microgrids.

### 2. Key Findings & Epistemic Verification
- **Utility Solar Adoption [S1]:** Centralized grid connections reached 35% of total renewable capacity additions across OECD nations.
- **Decentralized Solar Adoption [S2]:** When incorporating behind-the-meter and rural microgrids, adoption reached 48%.
- **Market Capitalization:** Total valuation ranged between $320B (utility providers) and $450B (distributed solar equipment manufacturers).

### 3. Source Discrepancy & Reconciliation Analysis
> The 13% numeric discrepancy between Report A (35%) and Report B (48%) is reconciled by geographical and infrastructural methodology: Report A tracks substation telemetry across 42 OECD states, while Report B captures off-grid inverters in 85 emerging and industrial nations.

### 4. Citation Audit
- **[S1]** International Clean Energy Institute (ICEI) — Report ID: GSO-2024-A
- **[S2]** Global Distributed Energy Alliance (GDEA) — Report ID: DRIA-2024-B
- **Citation Integrity Score:** 100.0% (Certified by Anthropic Claude Reviewer)
"""

svc = ReportService()
pdf_path = svc.export_pdf(sample_md, "Sample_ARX_Executive_Briefing.pdf")
print("PDF generated successfully at:", pdf_path)
print("File exists?", pdf_path.exists())
print("File size:", pdf_path.stat().st_size, "bytes")
