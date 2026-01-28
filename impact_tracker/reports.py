"""
PDF Report generation views using reportlab.
"""

import logging
from datetime import datetime
from io import BytesIO

from django.http import FileResponse, HttpResponse
from django.utils.text import slugify
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import SDGGoal, Activity, SDGImpact

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def generate_sdg_report_pdf(request, sdg_id):
    """
    Generate a PDF report listing all activities linked to a specific SDG.
    
    Endpoint: GET /api/reports/generate/{sdg_id}/
    
    The PDF includes:
        - SDG information (name, description)
        - List of all activities linked to this SDG
        - For each activity: title, description, author, relevance score, justification
    
    Query Parameters:
        - format: 'pdf' or 'html' (default: 'pdf')
    
    Returns:
        PDF file download or HTML preview
    """
    try:
        # Get the SDG goal
        try:
            sdg_goal = SDGGoal.objects.get(pk=sdg_id)
        except SDGGoal.DoesNotExist:
            return Response(
                {'error': f'SDG Goal with ID {sdg_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all impacts for this SDG
        impacts = SDGImpact.objects.filter(sdg_goal=sdg_goal).select_related('activity', 'activity__lead_author')
        
        if not impacts.exists():
            return Response(
                {'message': f'No activities found for SDG {sdg_goal.number}: {sdg_goal.name}'},
                status=status.HTTP_200_OK
            )
        
        # Create PDF
        pdf_buffer = _generate_pdf_content(sdg_goal, impacts)
        
        # Return as downloadable file
        filename = f"SDG_{sdg_goal.number}_{slugify(sdg_goal.name)}_Report.pdf"
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        logger.info(f"Generated PDF report for SDG {sdg_goal.number}")
        return response
    
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to generate report'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _generate_pdf_content(sdg_goal, impacts):
    """
    Generate PDF content for SDG report.
    
    Args:
        sdg_goal: SDGGoal instance
        impacts: QuerySet of SDGImpact records
    
    Returns:
        BytesIO object containing PDF
    """
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    
    # Container for PDF elements
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2b5fa3'),
        spaceAfter=12,
        spaceBefore=12,
        borderColor=colors.HexColor('#2b5fa3'),
        borderWidth=1,
        borderPadding=6
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        leading=14,
    )
    
    # Title
    title = Paragraph(
        f"SDG {sdg_goal.number}: {sdg_goal.name}",
        title_style
    )
    story.append(title)
    story.append(Spacer(1, 0.2 * inch))
    
    # SDG Description
    story.append(Paragraph("<b>Description:</b>", heading_style))
    story.append(Paragraph(sdg_goal.description, body_style))
    story.append(Spacer(1, 0.3 * inch))
    
    # Report metadata
    metadata_text = f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %H:%M')}<br/><b>Total Activities:</b> {impacts.count()}"
    story.append(Paragraph(metadata_text, body_style))
    story.append(Spacer(1, 0.3 * inch))
    
    # Activities Section
    story.append(Paragraph("Activities Linked to This SDG", heading_style))
    story.append(Spacer(1, 0.15 * inch))
    
    # Create activity list with details
    for idx, impact in enumerate(impacts, 1):
        activity = impact.activity
        author = activity.lead_author
        
        # Activity header with score
        activity_header = f"<b>{idx}. {activity.title}</b> (Relevance Score: {impact.score}%)"
        story.append(Paragraph(activity_header, styles['Heading3']))
        
        # Activity details
        details = f"""
        <b>Type:</b> {activity.get_activity_type_display()}<br/>
        <b>Author:</b> {author.get_full_name() or author.username}<br/>
        <b>Date Created:</b> {activity.date_created.strftime('%B %d, %Y')}<br/>
        """
        story.append(Paragraph(details, body_style))
        
        # Description
        story.append(Paragraph("<b>Description:</b>", styles['Normal']))
        story.append(Paragraph(activity.description, body_style))
        
        # AI Justification
        story.append(Paragraph("<b>Impact Justification:</b>", styles['Normal']))
        story.append(Paragraph(impact.justification, body_style))
        
        # Evidence file note
        if activity.evidence_file:
            story.append(Paragraph(
                f"<i>Evidence file attached: {activity.evidence_file.name}</i>",
                styles['Normal']
            ))
        
        # Separator
        story.append(Spacer(1, 0.2 * inch))
        
        # Page break after every 3 activities (or at the end)
        if idx % 3 == 0 and idx < impacts.count():
            story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    
    # Get the value of the BytesIO buffer and write response
    buffer.seek(0)
    return buffer


@api_view(['GET'])
@permission_classes([AllowAny])
def generate_comprehensive_report(request):
    """
    Generate a comprehensive report of all SDGs and activities.
    
    Endpoint: GET /api/reports/comprehensive/
    
    Returns:
        PDF file with summary of all SDGs and their linked activities
    """
    try:
        # Get all SDG goals with impacts
        sdg_goals = SDGGoal.objects.annotate(
            impact_count=Count('impacts')
        ).filter(impact_count__gt=0).order_by('number')
        
        if not sdg_goals.exists():
            return Response(
                {'message': 'No SDG data available for report'},
                status=status.HTTP_200_OK
            )
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=1
        )
        
        story.append(Paragraph("SDG Impact Dashboard - Comprehensive Report", title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Report metadata
        metadata_text = f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %H:%M')}"
        story.append(Paragraph(metadata_text, styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Summary table
        summary_data = [['SDG', 'Name', 'Activities', 'Avg Score']]
        for sdg in sdg_goals:
            impacts = sdg.impacts.all()  # type: ignore
            avg_score = sum(i.score for i in impacts) / len(impacts) if impacts else 0
            summary_data.append([
                f"SDG {sdg.number}",
                sdg.name[:20] + "..." if len(sdg.name) > 20 else sdg.name,
                str(impacts.count()),
                f"{avg_score:.1f}%"
            ])
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b5fa3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Build PDF
        doc.build(story)
        
        # Return as downloadable file
        buffer.seek(0)
        filename = f"SDG_Dashboard_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        logger.info("Generated comprehensive SDG report")
        return response
    
    except Exception as e:
        logger.error(f"Error generating comprehensive report: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to generate report'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Import Count for annotations
from django.db.models import Count