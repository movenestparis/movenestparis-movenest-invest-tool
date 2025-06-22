import io
import base64
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import Color
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

def generate_npv_chart(npv_data):
    """Generate NPV chart and return as base64 string"""
    plt.figure(figsize=(10, 6))
    years = [item['year'] for item in npv_data]
    npvs = [item['npv'] for item in npv_data]
    
    plt.plot(years, npvs, marker='o', linewidth=2, markersize=6, color='#2e5e4e')
    plt.fill_between(years, npvs, alpha=0.3, color='#2e5e4e')
    plt.axhline(y=0, color='red', linestyle='--', alpha=0.7)
    
    plt.title('Évolution VAN sur 10 ans', fontsize=16, fontweight='bold')
    plt.xlabel('Années')
    plt.ylabel('VAN (€)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    chart_data = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return chart_data

def generate_pdf_report(results, interpretations, form_data, calculator, language='fr'):
    """Generate PDF report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Define colors
    stromboli = Color(46/255, 94/255, 78/255)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=stromboli,
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=stromboli,
        spaceAfter=12
    )
    
    # Content
    content = []
    
    # Title
    if language == 'fr':
        title = "Rapport d'Analyse Immobilière - MoveNest Paris"
    else:
        title = "تقرير تحليل عقاري - MoveNest Paris"
    
    content.append(Paragraph(title, title_style))
    content.append(Spacer(1, 20))
    
    # Property details table
    if language == 'fr':
        property_data = [
            ['Détails de la Propriété', ''],
            ['Prix de la Propriété', f"{float(form_data.get('property_price', 0)):,.0f} €"],
            ['Loyer Mensuel', f"{float(form_data.get('monthly_rent', 0)):,.0f} €"],
            ['Budget Rénovation', f"{float(form_data.get('renovation_budget', 0)):,.0f} €"]
        ]
    else:
        property_data = [
            ['تفاصيل العقار', ''],
            ['سعر العقار', f"{float(form_data.get('property_price', 0)):,.0f} €"],
            ['الإيجار الشهري', f"{float(form_data.get('monthly_rent', 0)):,.0f} €"],
            ['ميزانية التجديد', f"{float(form_data.get('renovation_budget', 0)):,.0f} €"]
        ]
    
    property_table = Table(property_data, colWidths=[3*inch, 2*inch])
    property_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), stromboli),
        ('TEXTCOLOR', (0, 0), (-1, 0), Color(1, 1, 1)),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), Color(0.95, 0.95, 0.95)),
        ('GRID', (0, 0), (-1, -1), 1, Color(0.8, 0.8, 0.8))
    ]))
    
    content.append(property_table)
    content.append(Spacer(1, 20))
    
    # Results table
    if language == 'fr':
        results_data = [
            ['Métriques Financières', 'Valeur'],
            ['Rendement Net', f"{results['net_yield']:.2f}%"],
            ['VAN 10 ans', f"{results['npv_10']:,.0f} €"],
            ['TRI', f"{results['irr']:.2f}%"],
            ['Cash-Flow Mensuel', f"{results['monthly_cash_flow']:,.0f} €"]
        ]
        
        if results.get('dscr', 0) > 0:
            results_data.append(['DSCR', f"{results['dscr']:.2f}"])
        
        results_data.append(['Loyer Minimum Rentabilité', f"{results['breakeven_rent']:,.0f} €"])
    else:
        results_data = [
            ['المقاييس المالية', 'القيمة'],
            ['العائد الصافي', f"{results['net_yield']:.2f}%"],
            ['القيمة الحالية الصافية 10 سنوات', f"{results['npv_10']:,.0f} €"],
            ['معدل العائد الداخلي', f"{results['irr']:.2f}%"],
            ['التدفق النقدي الشهري', f"{results['monthly_cash_flow']:,.0f} €"]
        ]
        
        if results.get('dscr', 0) > 0:
            results_data.append(['نسبة تغطية خدمة الدين', f"{results['dscr']:.2f}"])
        
        results_data.append(['الحد الأدنى للإيجار للربحية', f"{results['breakeven_rent']:,.0f} €"])
    
    results_table = Table(results_data, colWidths=[3*inch, 2*inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), stromboli),
        ('TEXTCOLOR', (0, 0), (-1, 0), Color(1, 1, 1)),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), Color(0.95, 0.95, 0.95)),
        ('GRID', (0, 0), (-1, -1), 1, Color(0.8, 0.8, 0.8))
    ]))
    
    content.append(results_table)
    content.append(Spacer(1, 20))
    
    # NPV Chart
    chart_data = generate_npv_chart(results['npv_over_time'])
    chart_buffer = io.BytesIO(base64.b64decode(chart_data))
    chart_img = Image(chart_buffer, width=5*inch, height=3*inch)
    content.append(chart_img)
    content.append(Spacer(1, 20))
    
    # Interpretations
    if language == 'fr':
        content.append(Paragraph("Analyse CFA - Conseil Professionnel", heading_style))
    else:
        content.append(Paragraph("تحليل CFA - استشارة مهنية", heading_style))
    
    for symbol, text in interpretations:
        interp_text = f"{symbol} {text}"
        content.append(Paragraph(interp_text, styles['Normal']))
        content.append(Spacer(1, 6))
    
    # Build PDF
    doc.build(content)
    buffer.seek(0)
    return buffer.getvalue()