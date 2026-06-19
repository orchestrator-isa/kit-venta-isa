#!/usr/bin/env python3
# generar-reporte.py — Genera reporte mensual en PDF
# Uso: python generar-reporte.py --cliente cafe-al-hizam --mes 06 --anio 2026

import argparse
import json
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

def generar_reporte(cliente_id, mes, anio):
    # Cargar datos (en producción: desde Neon DB)
    with open(f'../config/bot-configs/{cliente_id}.json') as f:
        config = json.load(f)

    # TODO: Conectar a base de datos y extraer métricas reales
    metricas = {
        'conversaciones': 1247,
        'pedidos': 89,
        'ventas': 28400,
        'resenas': 12,
        'posicion_maps': 2
    }

    filename = f"reporte-{cliente_id}-{mes}-{anio}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4,
                          rightMargin=2*cm, leftMargin=2*cm,
                          topMargin=2*cm, bottomMargin=2*cm)

    elements = []
    styles = getSampleStyleSheet()

    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#00E5FF'),
        spaceAfter=30
    )
    elements.append(Paragraph(f"REPORTE MENSUAL — {config['nombre']}", title_style))
    elements.append(Paragraph(f"{mes}/{anio} | Pack: {config['pack']}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Tabla de métricas
    data = [
        ['Métrica', 'Valor', 'vs Mes Anterior'],
        ['Conversaciones', str(metricas['conversaciones']), '+23% ↑'],
        ['Pedidos', str(metricas['pedidos']), '+18% ↑'],
        ['Ventas (MAD)', f"{metricas['ventas']:,}", '+15% ↑'],
        ['Reseñas nuevas', str(metricas['resenas']), '+40% ↑'],
        ['Posición Maps', f"#{metricas['posicion_maps']}", '↑ 3 posiciones']
    ]

    t = Table(data, colWidths=[6*cm, 4*cm, 4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#111827')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#00E5FF')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#0a0e17')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1a2332')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#0a0e17'), colors.HexColor('#111827')])
    ]))
    elements.append(t)
    elements.append(Spacer(1, 30))

    # ROI
    elements.append(Paragraph("<b>ROI DEL MES</b>", styles['Heading2']))
    inversion = config.get('mantenimiento', 500)
    roi = ((metricas['ventas'] - inversion) / inversion * 100) if inversion > 0 else 0
    elements.append(Paragraph(f"Inversión: {inversion:,} MAD | Ventas: {metricas['ventas']:,} MAD | ROI: {roi:.0f}%", styles['Normal']))

    doc.build(elements)
    print(f"✅ Reporte generado: {filename}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cliente', required=True)
    parser.add_argument('--mes', required=True)
    parser.add_argument('--anio', required=True)
    args = parser.parse_args()
    generar_reporte(args.cliente, args.mes, args.anio)
