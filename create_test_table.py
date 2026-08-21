from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

doc = SimpleDocTemplate("test_table.pdf", pagesize=A4)

styles = getSampleStyleSheet()

data = [
    ["Requirement", "Description", "Deadline"],
    ["R1", "Technical proposal", "30 days"],
    ["R2", "Financial proposal", "15 days"],
    ["R3", "Company documents", "10 days"],
]

table = Table(data)

table.setStyle(
    TableStyle(
        [
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ]
    )
)

doc.build(
    [
        Paragraph("Tender Requirements", styles["Title"]),
        table,
    ]
)
