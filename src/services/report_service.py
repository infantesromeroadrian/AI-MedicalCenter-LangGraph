import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
import io
import traceback

from src.models.data_models import InteractiveConversation
from src.services.llm_service import LLMService
from src.config.config import BASE_DIR

logger = logging.getLogger(__name__)

# Inicializar el servicio LLM
llm_service = LLMService()

async def generate_medical_report(conversation: InteractiveConversation) -> str:
    """
    Genera un informe médico basado en una conversación utilizando LLM.
    
    Args:
        conversation: La conversación para generar el informe.
        
    Returns:
        Informe médico en formato HTML.
    """
    try:
        logger.info(f"Generando informe médico para conversación: {conversation.conversation_id}")
        
        # Prompt específico para generar el informe
        system_prompt = """Eres un profesional médico especializado en generar informes médicos completos y bien estructurados.
Tu tarea es analizar la conversación médica proporcionada y crear un informe médico formal en español que incluya:

1. DATOS DEL PACIENTE: Identifica cualquier información demográfica mencionada en la conversación.
2. MOTIVO DE CONSULTA: Resume brevemente la razón principal por la que el paciente buscó atención médica.
3. ANTECEDENTES: Incluye cualquier información relevante sobre la historia médica, medicamentos o alergias mencionadas.
4. EXAMEN CLÍNICO: Resume la evaluación clínica realizada o los síntomas descritos.
5. IMPRESIÓN DIAGNÓSTICA: Ofrece una lista de posibles diagnósticos basados en la conversación.
6. PLAN DE ACCIÓN: Resume las recomendaciones y tratamientos propuestos.
7. CONCLUSIONES: Proporciona un resumen conciso de los hallazgos y próximos pasos.

ASPECTOS IMPORTANTES:
- Utiliza un tono profesional y objetivo.
- Formatea el informe con encabezados claros utilizando HTML para mayor legibilidad.
- No inventes información que no esté presente en la conversación.
- Si falta alguna información, indica "No mencionado" en esa sección.
- Incluye las especialidades médicas involucradas en la conversación.
- Utiliza terminología médica apropiada pero asegúrate que sea comprensible.
- El informe debe ser entregado en formato HTML con estilos básicos para mejorar su presentación.

FORMATO DE RESPUESTA:
Utiliza etiquetas HTML para estructurar el documento con un estilo profesional de informe médico.
"""

        # Preparar los mensajes de la conversación en formato legible para el LLM
        formatted_conversation = _format_conversation_for_report(conversation)
        
        # Prompt del usuario con la conversación
        user_prompt = f"""Genera un informe médico completo en español basado en la siguiente conversación médica entre paciente y especialista(s).

ESPECIALIDADES INVOLUCRADAS: {', '.join(conversation.all_specialties)}
ID DE CONVERSACIÓN: {conversation.conversation_id}
FECHA: {datetime.now().strftime('%d/%m/%Y')}

TRANSCRIPCIÓN DE LA CONVERSACIÓN:
{formatted_conversation}

Por favor, genera un informe médico completo basado en esta información.
"""

        # Llamar al LLM para generar el informe
        logger.info("Llamando al LLM para generar el informe")
        report_content = await llm_service.generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3  # Temperatura baja para respuestas más consistentes
        )
        logger.info("Informe generado correctamente por el LLM")
        
        # Aplicar estilos adicionales al informe HTML
        styled_report = f"""
        <div class="medical-report">
            <style>
                .medical-report {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .medical-report h1 {{
                    color: #2a5885;
                    border-bottom: 2px solid #2a5885;
                    padding-bottom: 10px;
                }}
                .medical-report h2 {{
                    color: #2a5885;
                    margin-top: 20px;
                    border-bottom: 1px solid #ccc;
                    padding-bottom: 5px;
                }}
                .medical-report .header-info {{
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .medical-report .diagnosis {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-left: 4px solid #2a5885;
                    margin: 15px 0;
                }}
                .medical-report footer {{
                    margin-top: 30px;
                    border-top: 1px solid #ccc;
                    padding-top: 10px;
                    font-size: 0.9em;
                    color: #666;
                }}
            </style>
            {report_content}
            <footer>
                <p>Informe generado automáticamente el {datetime.now().strftime('%d/%m/%Y %H:%M')} basado en la conversación médica.</p>
                <p>ID de Consulta: {conversation.conversation_id}</p>
                <p><strong>NOTA:</strong> Este informe es generado por IA y debe ser revisado por un profesional médico antes de tomar decisiones clínicas.</p>
            </footer>
        </div>
        """
        
        return styled_report
        
    except Exception as e:
        logger.error(f"Error generando informe médico: {e}")
        logger.error(traceback.format_exc())
        
        # Devolver un mensaje de error en formato HTML
        error_html = f"""
        <div class="alert alert-danger">
            <h4>Error al generar el informe médico</h4>
            <p>Lo sentimos, ha ocurrido un error al procesar la conversación: {str(e)}</p>
            <p>Por favor, inténtelo de nuevo más tarde o contacte con soporte técnico.</p>
        </div>
        """
        return error_html


def _format_conversation_for_report(conversation: InteractiveConversation) -> str:
    """
    Formatea los mensajes de la conversación en un formato legible para el LLM.
    
    Args:
        conversation: La conversación a formatear.
        
    Returns:
        Conversación formateada como texto.
    """
    formatted_text = ""
    
    for msg in conversation.messages:
        sender = msg.sender
        content = msg.content
        timestamp = msg.timestamp if isinstance(msg.timestamp, str) else msg.timestamp.isoformat()
        
        # Formatear cada mensaje según el remitente
        if sender == "user":
            formatted_text += f"[PACIENTE] {timestamp}:\n{content}\n\n"
        elif sender == "system":
            formatted_text += f"[SISTEMA] {timestamp}:\n{content}\n\n"
        else:
            # Especialista médico
            formatted_text += f"[ESPECIALISTA: {sender.upper()}] {timestamp}:\n{content}\n\n"
    
    return formatted_text


async def generate_pdf_report(html_content: str, conversation_id: str) -> bytes:
    """
    Genera un archivo PDF a partir del contenido HTML del informe.
    
    Args:
        html_content: Contenido HTML del informe.
        conversation_id: ID de la conversación para el nombre del archivo.
        
    Returns:
        Buffer de bytes con el contenido del PDF.
    """
    try:
        logger.info(f"Generando PDF para conversación: {conversation_id}")
        
        # Función para guardar logs detallados
        def log_debug(msg):
            logger.info(f"[PDF Debug] {msg}")
        
        log_debug("Iniciando generación de PDF con múltiples alternativas")
        
        # Método 1: Usar reportlab (más confiable)
        try:
            log_debug("Intentando con ReportLab")
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.units import inch
            import re
            
            # Crear buffer en memoria
            buffer = io.BytesIO()
            
            # Crear documento PDF
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            # Obtener estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Center
            )
            
            # Procesar HTML para extraer texto
            text_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
            text_content = re.sub(r'<[^>]*>', '', text_content)
            text_content = re.sub(r'\n\s*\n', '\n', text_content.strip())
            
            # Construir contenido del PDF
            story = []
            
            # Título
            story.append(Paragraph("INFORME MÉDICO", title_style))
            story.append(Spacer(1, 12))
            
            # Información básica
            story.append(Paragraph(f"<b>ID de Conversación:</b> {conversation_id}", styles['Normal']))
            story.append(Paragraph(f"<b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Contenido principal
            paragraphs = text_content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    # Detectar títulos/secciones
                    if para.strip().isupper() or len(para) < 50:
                        story.append(Paragraph(f"<b>{para}</b>", styles['Heading2']))
                    else:
                        story.append(Paragraph(para, styles['Normal']))
                    story.append(Spacer(1, 6))
            
            # Generar PDF
            doc.build(story)
            buffer.seek(0)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            log_debug(f"PDF generado exitosamente con ReportLab, tamaño: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            log_debug(f"Error con ReportLab: {str(e)}")
            
            # Método 2: Usar weasyprint (corregido)
            try:
                log_debug("Intentando con WeasyPrint corregido")
                from weasyprint import HTML
                
                # Crear contenido HTML limpio para WeasyPrint
                clean_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 2cm; line-height: 1.6; }}
                        h1 {{ color: #2a5885; text-align: center; }}
                        h2 {{ color: #2a5885; border-bottom: 1px solid #ccc; }}
                        .header {{ background-color: #f5f5f5; padding: 15px; margin-bottom: 20px; }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
                </html>
                """
                
                # Generar PDF con WeasyPrint
                html_doc = HTML(string=clean_html)
                pdf_bytes = html_doc.write_pdf()
                
                log_debug(f"PDF generado exitosamente con WeasyPrint, tamaño: {len(pdf_bytes)} bytes")
                return pdf_bytes
                
            except Exception as weasy_error:
                log_debug(f"Error con WeasyPrint: {str(weasy_error)}")
                
                # Método 3: Usar fpdf2 como respaldo
                try:
                    log_debug("Usando fpdf2 como respaldo")
                    from fpdf import FPDF
                    
                    class PDF(FPDF):
                        def header(self):
                            self.set_font('Arial', 'B', 15)
                            self.cell(0, 10, 'INFORME MÉDICO', 0, 1, 'C')
                            self.ln(10)
                        
                        def footer(self):
                            self.set_y(-15)
                            self.set_font('Arial', 'I', 8)
                            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
                    
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font('Arial', '', 12)
                    
                    # Eliminar etiquetas HTML
                    import re
                    text_content = re.sub(r'<[^>]*>', '', html_content)
                    text_content = re.sub(r'\n\s*\n', '\n', text_content)
                    
                    # Información básica
                    pdf.multi_cell(0, 10, f"ID Conversación: {conversation_id}")
                    pdf.multi_cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                    pdf.ln(10)
                    
                    # Contenido principal (limitado para evitar problemas de encoding)
                    preview_content = text_content[:2000] + "..." if len(text_content) > 2000 else text_content
                    
                    # Reemplazar caracteres problemáticos
                    preview_content = preview_content.encode('latin1', errors='replace').decode('latin1')
                    pdf.multi_cell(0, 10, preview_content)
                    
                    pdf.ln(10)
                    pdf.multi_cell(0, 10, "NOTA: Este es un informe simplificado. El informe completo está disponible en la interfaz web.")
                    
                    log_debug("PDF básico generado con fpdf2")
                    return pdf.output()
                    
                except Exception as fpdf_error:
                    log_debug(f"Error con fpdf2: {str(fpdf_error)}")
                    raise Exception(f"Todos los métodos de PDF fallaron: ReportLab, WeasyPrint, fpdf2")
                
    except Exception as e:
        logger.error(f"Error crítico generando PDF: {e}")
        logger.error(traceback.format_exc())
        
        # Como último recurso, generar un PDF simple con mensaje de error
        try:
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Error al generar el informe PDF', 0, 1)
            pdf.ln(10)
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(0, 10, f"Se produjo un error: {str(e)}")
            pdf.ln(5)
            pdf.multi_cell(0, 10, "Por favor, inténtelo de nuevo o descargue el informe HTML.")
            
            return pdf.output()
            
        except Exception as final_error:
            logger.critical(f"Error fatal generando PDF: {final_error}")
            # Si absolutamente todo falla, devolver un mensaje de error en bytes
            error_message = f"Error generando PDF: {str(e)}"
            return error_message.encode('utf-8') 