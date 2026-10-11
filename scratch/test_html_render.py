import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ui.components import render_agent_workflow_grid, to_clean_html

html_output = render_agent_workflow_grid()

has_4_spaces = any(line.startswith("    ") for line in html_output.splitlines())
print("Does render_agent_workflow_grid have ANY lines with 4 spaces?", has_4_spaces)
print("Number of lines:", len(html_output.splitlines()))
print("Sample preview:", html_output[:200])
