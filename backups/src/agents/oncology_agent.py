from typing import Dict, List, Any, Optional

from src.agents.base_agent import BaseMedicalAgent
from src.services.llm_service import LLMService

class OncologyAgent(BaseMedicalAgent):
    """Agent specialized in oncology and cancer treatment."""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """Initialize the oncology agent."""
        super().__init__(specialty="oncology", llm_service=llm_service)
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt specific to oncology."""
        return """Eres un oncólogo especializado en el diagnóstico, tratamiento y seguimiento del cáncer.

COMPORTAMIENTO CRUCIAL: Debes emular el comportamiento de un oncólogo real en consulta:

1. ENFOQUE ONCOLÓGICO INTEGRAL:
   - Evalúa tanto aspectos médicos como psicosociales del paciente
   - Considera el estadio del cáncer y pronóstico
   - Valora la calidad de vida y funcionalidad del paciente
   - Aborda miedos y preocupaciones sobre el diagnóstico

2. ESTRUCTURA DE CONSULTA ONCOLÓGICA:
   - Saludo empático y establecimiento de un ambiente de confianza
   - Historia oncológica detallada:
     * Tipo histológico y estadio del tumor
     * Fecha de diagnóstico y tratamientos previos
     * Respuesta a tratamientos anteriores
     * Efectos secundarios experimentados
   - Evaluación del estado funcional (ECOG, Karnofsky)
   - Síntomas actuales relacionados con el cáncer o tratamiento

3. EVALUACIÓN ESPECÍFICA POR TIPO DE CÁNCER:
   - Tumores sólidos: localización, tamaño, metástasis
   - Neoplasias hematológicas: tipo celular, citogenética, marcadores
   - Factores pronósticos específicos para cada tipo tumoral
   - Biomarcadores y medicina personalizada

4. MANEJO DE TRATAMIENTOS ONCOLÓGICOS:
   - Quimioterapia: esquemas, ciclos, toxicidades esperadas
   - Radioterapia: indicaciones, efectos secundarios agudos y tardíos
   - Inmunoterapia: criterios de respuesta, efectos adversos inmunológicos
   - Terapias dirigidas: biomarcadores, resistencias
   - Cirugía oncológica: resecabilidad, riesgos quirúrgicos

5. EFECTOS SECUNDARIOS Y TOXICIDADES:
   - Hematológicas: neutropenia, anemia, trombocitopenia
   - Gastrointestinales: náuseas, vómitos, mucositis, diarrea
   - Neurológicas: neuropatía periférica, ototoxicidad
   - Dermatológicas: alopecia, rash, síndrome mano-pie
   - Cardíacas: cardiotoxicidad por antraciclinas, trastuzumab
   - Renales: nefrotoxicidad

6. CUIDADOS DE SOPORTE:
   - Manejo del dolor oncológico
   - Control de síntomas (náuseas, fatiga, anorexia)
   - Prevención de infecciones en neutropenia
   - Soporte nutricional
   - Aspectos psicológicos y cuidados paliativos

7. SEGUIMIENTO Y VIGILANCIA:
   - Detección temprana de recidivas
   - Monitoreo de marcadores tumorales
   - Evaluación de respuesta por imágenes
   - Vigilancia de segundas neoplasias
   - Supervivencia libre de enfermedad

8. COMUNICACIÓN SENSIBLE:
   - Dar información clara pero esperanzadora cuando sea apropiado
   - Explicar conceptos complejos en términos comprensibles
   - Abordar el pronóstico de manera gradual y empática
   - Involucrar a la familia en las decisiones de tratamiento

IMPORTANTE:
- Mantén siempre un equilibrio entre honestidad médica y esperanza
- Enfatiza los avances en tratamientos oncológicos
- Aborda tanto los aspectos curativos como paliativos según corresponda
- Considera siempre la calidad de vida del paciente
- Proporciona apoyo emocional además del médico

Al final de tu respuesta, incluye una sección "RECOMENDACIONES ONCOLÓGICAS:" con consejos sobre tratamiento, seguimiento, cuidados de soporte y recursos de apoyo para el paciente y familia."""
    
    def _evaluate_confidence(self, query: str, response: str) -> float:
        """
        Evaluate the confidence for oncology-related queries.
        Override base implementation to check for oncology-specific keywords.
        """
        base_confidence = super()._evaluate_confidence(query, response)
        
        # Check for oncology-related keywords to potentially increase confidence
        oncology_keywords = [
            "cancer", "tumor", "oncology", "chemotherapy", "radiation", "metastasis",
            "biopsy", "malignant", "benign", "carcinoma", "sarcoma", "lymphoma",
            "leukemia", "staging", "prognosis", "immunotherapy", "targeted therapy",
            "palliative", "hospice", "remission", "recurrence", "survival",
            # Spanish keywords
            "cáncer", "tumor", "oncología", "quimioterapia", "radioterapia", "metástasis",
            "biopsia", "maligno", "benigno", "carcinoma", "sarcoma", "linfoma",
            "leucemia", "estadificación", "pronóstico", "inmunoterapia", "terapia dirigida",
            "paliativo", "remisión", "recurrencia", "supervivencia", "oncólogo"
        ]
        
        # Cancer types
        cancer_types = [
            "breast cancer", "lung cancer", "prostate cancer", "colon cancer",
            "melanoma", "bladder cancer", "kidney cancer", "liver cancer",
            "pancreatic cancer", "ovarian cancer", "cervical cancer",
            # Spanish cancer types
            "cáncer de mama", "cáncer de pulmón", "cáncer de próstata", "cáncer de colon",
            "melanoma", "cáncer de vejiga", "cáncer de riñón", "cáncer de hígado",
            "cáncer de páncreas", "cáncer de ovario", "cáncer cervical"
        ]
        
        # Treatment-related terms
        treatment_terms = [
            "chemotherapy", "radiotherapy", "surgery", "immunotherapy", "clinical trial",
            "side effects", "nausea", "hair loss", "fatigue", "neuropathy",
            # Spanish treatment terms
            "quimioterapia", "radioterapia", "cirugía", "inmunoterapia", "ensayo clínico",
            "efectos secundarios", "náuseas", "pérdida de cabello", "fatiga", "neuropatía"
        ]
        
        # Count oncology keywords in query
        keyword_count = sum(1 for keyword in oncology_keywords if keyword.lower() in query.lower())
        cancer_count = sum(1 for cancer in cancer_types if cancer.lower() in query.lower())
        treatment_count = sum(1 for treatment in treatment_terms if treatment.lower() in query.lower())
        
        # Increase confidence based on keyword matches
        confidence_boost = min(0.5, (keyword_count * 0.1) + (cancer_count * 0.15) + (treatment_count * 0.08))
        adjusted_confidence = base_confidence + confidence_boost
        
        # Ensure confidence stays in range [0.1, 1.0]
        return max(0.1, min(1.0, adjusted_confidence)) 