"""
Agente especializado en Oftalmología
Proporciona consultas especializadas en salud ocular y visual
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.agents.base_agent import BaseMedicalAgent
from src.models.data_models import AgentResponse, UserQuery

logger = logging.getLogger(__name__)

class OphthalmologyAgent(BaseMedicalAgent):
    """Agente especializado en oftalmología y salud ocular"""
    
    def __init__(self, llm_service=None):
        super().__init__(
            specialty="ophthalmology", 
            llm_service=llm_service,
            system_prompt=self._get_ophthalmology_system_prompt()
        )
        
        # Configuraciones específicas de oftalmología
        self.common_conditions = [
            "miopía", "hipermetropía", "astigmatismo", "presbicia",
            "glaucoma", "cataratas", "retinopatía diabética", 
            "degeneración macular", "conjuntivitis", "ojo seco",
            "desprendimiento de retina", "uveítis", "queratitis",
            "estrabismo", "ambliopía", "pterigión"
        ]
        
        self.emergency_keywords = [
            "pérdida súbita de visión", "dolor ocular severo", "flashes de luz",
            "moscas volantes súbitas", "visión doble", "halos alrededor de luces",
            "trauma ocular", "cuerpo extraño en ojo", "quemadura química",
            "cortina en la visión", "pérdida de campo visual"
        ]
        
        self.diagnostic_tests = [
            "agudeza visual", "tonometría", "oftalmoscopia", "biomicroscopia",
            "angiografía fluoresceínica", "OCT (tomografía de coherencia óptica)",
            "campimetría", "topografía corneal", "paquimetría", "gonioscopia"
        ]
        
        logger.info("Agente de oftalmología inicializado correctamente")
    
    def _get_ophthalmology_system_prompt(self) -> str:
        """Prompt del sistema especializado en oftalmología"""
        return """
        Eres un oftalmólogo experto con amplia experiencia en:
        
        ESPECIALIDADES OFTALMOLÓGICAS:
        • Córnea y superficie ocular
        • Retina y vítreo  
        • Glaucoma
        • Cataratas y cirugía refractiva
        • Neuro-oftalmología
        • Oftalmología pediátrica
        • Oculoplástica
        • Uveítis e inflamación ocular
        
        ÁREAS DE CONOCIMIENTO:
        • Errores refractivos (miopía, hipermetropía, astigmatismo)
        • Enfermedades retinianas (retinopatía diabética, DMAE)
        • Patología del segmento anterior
        • Emergencias oftalmológicas
        • Cirugía ocular (catarata, glaucoma, retina)
        • Optometría y adaptación de lentes
        
        PROTOCOLOS DE EVALUACIÓN:
        • Historia clínica oftalmológica detallada
        • Examen ocular completo estructurado
        • Interpretación de pruebas diagnósticas
        • Identificación de signos de alarma
        • Criterios de derivación urgente
        
        PRINCIPIOS CLÍNICOS:
        • Priorizar emergencias oftalmológicas
        • Evaluar riesgo de pérdida visual
        • Considerar enfermedades sistémicas asociadas
        • Enfoque preventivo en salud ocular
        • Educación en higiene visual
        
        Siempre considera:
        - Antecedentes familiares de enfermedades oculares
        - Medicamentos que pueden afectar la visión
        - Enfermedades sistémicas (diabetes, hipertensión)
        - Factores ocupacionales y ambientales
        - Edad del paciente para condiciones específicas
        """
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Procesar consulta oftalmológica con análisis especializado
        """
        try:
            # Análisis de urgencia oftalmológica
            urgency_level, urgency_reason = self._assess_ophthalmology_urgency(query)
            
            # Análisis de síntomas oculares
            symptom_analysis = self._analyze_ocular_symptoms(query)
            
            # Recomendaciones de exámenes
            recommended_tests = self._recommend_ophthalmology_tests(query, symptom_analysis)
            
            # Contexto oftalmológico mejorado
            enhanced_context = self._build_ophthalmology_context(
                query, context, urgency_level, symptom_analysis, recommended_tests
            )
            
            # Generar respuesta especializada
            response = await self._generate_ophthalmology_response(query, enhanced_context)
            
            # Construir respuesta estructurada
            recommendations = self._generate_ophthalmology_recommendations(
                symptom_analysis, recommended_tests, urgency_level
            )
            
            return AgentResponse(
                agent_type="ophthalmology",
                response=response,
                confidence=self._calculate_confidence(query, symptom_analysis),
                recommendations=recommendations,
                sources=self._get_ophthalmology_sources(),
                timestamp=datetime.now(),
                metadata={
                    "urgency_level": urgency_level,
                    "urgency_reason": urgency_reason,
                    "symptom_analysis": symptom_analysis,
                    "recommended_tests": recommended_tests,
                    "emergency_indicators": self._check_emergency_indicators(query)
                }
            )
            
        except Exception as e:
            logger.error(f"Error procesando consulta oftalmológica: {e}")
            return self._create_error_response(
                "Error procesando consulta oftalmológica. Consulte con un oftalmólogo presencialmente."
            )
    
    def _assess_ophthalmology_urgency(self, query: str) -> tuple:
        """Evaluar urgencia oftalmológica específica"""
        query_lower = query.lower()
        
        # Emergencias oftalmológicas críticas
        critical_indicators = [
            "pérdida súbita de visión", "ceguera súbita", "no veo nada",
            "dolor ocular severo", "ojo muy rojo y doloroso",
            "trauma ocular", "golpe en el ojo", "lesión ocular",
            "quemadura química", "ácido en el ojo", "producto químico"
        ]
        
        # Urgencias altas
        high_urgency_indicators = [
            "flashes de luz", "luces intermitentes", "relámpagos",
            "moscas volantes súbitas", "puntos negros súbitos",
            "cortina en la visión", "sombra en la visión",
            "visión doble", "diplopía", "veo doble"
        ]
        
        # Urgencias moderadas
        moderate_urgency_indicators = [
            "halos alrededor de luces", "visión borrosa súbita",
            "dolor de cabeza con problemas visuales",
            "pérdida gradual de visión", "campo visual reducido"
        ]
        
        # Evaluar crítico
        for indicator in critical_indicators:
            if indicator in query_lower:
                return "crítica", f"Posible emergencia oftalmológica: {indicator}"
        
        # Evaluar alto
        for indicator in high_urgency_indicators:
            if indicator in query_lower:
                return "alta", f"Síntoma preocupante: {indicator}"
        
        # Evaluar moderado
        for indicator in moderate_urgency_indicators:
            if indicator in query_lower:
                return "moderada", f"Síntoma que requiere evaluación: {indicator}"
        
        return "rutina", "Consulta oftalmológica de rutina"
    
    def _analyze_ocular_symptoms(self, query: str) -> Dict[str, Any]:
        """Analizar síntomas oculares específicos"""
        query_lower = query.lower()
        
        symptoms = {
            "visual_symptoms": [],
            "pain_discomfort": [],
            "external_signs": [],
            "functional_issues": []
        }
        
        # Síntomas visuales
        visual_patterns = {
            "visión borrosa": ["borrosa", "desenfocada", "no veo bien"],
            "pérdida de visión": ["no veo", "ceguera", "pérdida de visión"],
            "moscas volantes": ["moscas", "puntos negros", "manchas flotantes"],
            "flashes": ["flashes", "luces", "relámpagos", "destellos"],
            "halos": ["halos", "aureolas", "círculos de luz"],
            "visión doble": ["doble", "diplopía", "veo dos veces"]
        }
        
        for symptom, patterns in visual_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                symptoms["visual_symptoms"].append(symptom)
        
        # Dolor y molestias
        pain_patterns = {
            "dolor ocular": ["dolor", "duele", "molestia"],
            "sensación de cuerpo extraño": ["arena", "basura", "algo en el ojo"],
            "picazón": ["picazón", "comezón", "pica"],
            "ardor": ["ardor", "quema", "arde"]
        }
        
        for symptom, patterns in pain_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                symptoms["pain_discomfort"].append(symptom)
        
        # Signos externos
        external_patterns = {
            "ojo rojo": ["rojo", "inyectado", "irritado"],
            "secreción": ["secreción", "lagañas", "pus"],
            "hinchazón": ["hinchado", "inflamado", "edema"],
            "párpado caído": ["párpado caído", "ptosis"]
        }
        
        for symptom, patterns in external_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                symptoms["external_signs"].append(symptom)
        
        # Problemas funcionales
        functional_patterns = {
            "dificultad para leer": ["leer", "lectura", "letra pequeña"],
            "sensibilidad a la luz": ["luz molesta", "fotofobia", "brillo"],
            "fatiga visual": ["cansancio", "fatiga", "tensión ocular"],
            "sequedad": ["seco", "sequedad", "resequedad"]
        }
        
        for symptom, patterns in functional_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                symptoms["functional_issues"].append(symptom)
        
        return symptoms
    
    def _recommend_ophthalmology_tests(self, query: str, symptom_analysis: Dict[str, Any]) -> List[str]:
        """Recomendar exámenes oftalmológicos específicos"""
        recommended_tests = ["Examen oftalmológico completo", "Agudeza visual"]
        
        # Basado en síntomas visuales
        visual_symptoms = symptom_analysis.get("visual_symptoms", [])
        
        if "pérdida de visión" in visual_symptoms or "moscas volantes" in visual_symptoms:
            recommended_tests.extend([
                "Oftalmoscopia (fondo de ojo)",
                "OCT (tomografía de coherencia óptica)",
                "Angiografía fluoresceínica"
            ])
        
        if "halos" in visual_symptoms or "dolor ocular" in symptom_analysis.get("pain_discomfort", []):
            recommended_tests.append("Tonometría (presión intraocular)")
        
        if "visión doble" in visual_symptoms:
            recommended_tests.extend([
                "Evaluación de motilidad ocular",
                "Prismas de Fresnel",
                "Campimetría"
            ])
        
        if any("fatiga" in symptom for symptom in symptom_analysis.get("functional_issues", [])):
            recommended_tests.extend([
                "Refracción completa",
                "Evaluación binocular",
                "Test de acomodación"
            ])
        
        # Exámenes adicionales basados en edad (si se puede inferir)
        if "presbicia" in query.lower() or "lectura" in query.lower():
            recommended_tests.append("Evaluación de visión cercana")
        
        return list(set(recommended_tests))  # Eliminar duplicados
    
    def _build_ophthalmology_context(self, query: str, context: Dict[str, Any], 
                                   urgency_level: str, symptom_analysis: Dict[str, Any],
                                   recommended_tests: List[str]) -> str:
        """Construir contexto oftalmológico especializado"""
        
        context_parts = [
            f"CONSULTA OFTALMOLÓGICA: {query}",
            f"NIVEL DE URGENCIA: {urgency_level}",
            f"SÍNTOMAS ANALIZADOS: {symptom_analysis}",
            f"EXÁMENES RECOMENDADOS: {', '.join(recommended_tests[:5])}"
        ]
        
        # Agregar contexto adicional si está disponible
        if context:
            if context.get("age"):
                context_parts.append(f"EDAD DEL PACIENTE: {context['age']} años")
            if context.get("medical_history"):
                context_parts.append(f"ANTECEDENTES: {context['medical_history']}")
            if context.get("medications"):
                context_parts.append(f"MEDICAMENTOS: {context['medications']}")
        
        # Consideraciones especiales
        special_considerations = []
        
        if urgency_level in ["crítica", "alta"]:
            special_considerations.append("PRIORIZAR DERIVACIÓN URGENTE")
        
        if "diabetes" in query.lower():
            special_considerations.append("CONSIDERAR RETINOPATÍA DIABÉTICA")
        
        if "hipertensión" in query.lower():
            special_considerations.append("EVALUAR RETINOPATÍA HIPERTENSIVA")
        
        if special_considerations:
            context_parts.append(f"CONSIDERACIONES ESPECIALES: {'; '.join(special_considerations)}")
        
        return "\n".join(context_parts)
    
    def _generate_ophthalmology_recommendations(self, symptom_analysis: Dict[str, Any],
                                              recommended_tests: List[str],
                                              urgency_level: str) -> List[str]:
        """Generar recomendaciones oftalmológicas específicas"""
        recommendations = []
        
        # Recomendaciones basadas en urgencia
        if urgency_level == "crítica":
            recommendations.extend([
                "🚨 BUSCAR ATENCIÓN OFTALMOLÓGICA INMEDIATA",
                "Acudir a urgencias oftalmológicas o servicios de emergencia",
                "No automedicarse ni aplicar remedios caseros"
            ])
        elif urgency_level == "alta":
            recommendations.extend([
                "Solicitar cita urgente con oftalmólogo (máximo 24-48 horas)",
                "Evitar esfuerzos visuales intensos hasta la evaluación"
            ])
        
        # Recomendaciones generales de higiene visual
        recommendations.extend([
            "Descansar la vista cada 20 minutos (regla 20-20-20)",
            "Mantener buena iluminación al leer o trabajar",
            "Usar gafas de sol con protección UV cuando sea necesario"
        ])
        
        # Recomendaciones específicas por síntomas
        if "sequedad" in str(symptom_analysis.get("functional_issues", [])):
            recommendations.extend([
                "Usar lágrimas artificiales sin conservantes",
                "Mantener humedad adecuada en el ambiente",
                "Parpadear conscientemente más frecuentemente"
            ])
        
        if "fatiga visual" in str(symptom_analysis.get("functional_issues", [])):
            recommendations.extend([
                "Ajustar distancia y altura de pantallas",
                "Tomar descansos frecuentes del trabajo visual",
                "Considerar evaluación de la graduación"
            ])
        
        # Exámenes recomendados
        if recommended_tests:
            recommendations.append(f"Exámenes recomendados: {', '.join(recommended_tests[:3])}")
        
        return recommendations
    
    def _check_emergency_indicators(self, query: str) -> List[str]:
        """Identificar indicadores de emergencia oftalmológica"""
        query_lower = query.lower()
        emergencies = []
        
        emergency_conditions = {
            "desprendimiento de retina": ["cortina", "sombra", "moscas súbitas", "flashes"],
            "glaucoma agudo": ["dolor severo", "halos", "visión borrosa súbita", "náuseas"],
            "neuritis óptica": ["pérdida visual súbita", "dolor al mover ojo"],
            "oclusión vascular": ["pérdida súbita", "ceguera súbita"],
            "trauma ocular": ["golpe", "trauma", "lesión", "accidente"]
        }
        
        for condition, indicators in emergency_conditions.items():
            if any(indicator in query_lower for indicator in indicators):
                emergencies.append(condition)
        
        return emergencies
    
    def _calculate_confidence(self, query: str, symptom_analysis: Dict[str, Any]) -> float:
        """Calcular confianza de la respuesta oftalmológica"""
        confidence = 0.7  # Base confidence
        
        # Incrementar confianza si hay síntomas específicos
        total_symptoms = sum(len(symptoms) for symptoms in symptom_analysis.values())
        confidence += min(0.2, total_symptoms * 0.05)
        
        # Incrementar si contiene términos oftalmológicos específicos
        ophthalmology_terms = [
            "visión", "ojo", "vista", "pupila", "córnea", "retina",
            "párpado", "lágrima", "lente", "gafa", "miopía"
        ]
        
        term_count = sum(1 for term in ophthalmology_terms if term in query.lower())
        confidence += min(0.1, term_count * 0.02)
        
        return min(0.98, confidence)
    
    def _get_ophthalmology_sources(self) -> List[str]:
        """Fuentes de información oftalmológica"""
        return [
            "American Academy of Ophthalmology (AAO)",
            "Sociedad Española de Oftalmología (SEO)",
            "International Council of Ophthalmology (ICO)",
            "Retina Specialists Guidelines",
            "Glaucoma Research Foundation",
            "Cornea Society Clinical Guidelines"
        ] 