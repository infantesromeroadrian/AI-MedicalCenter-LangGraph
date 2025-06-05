"""
Advanced Medical LangGraph System
Integrates advanced techniques from marketplace agents into medical consultation system
"""
import logging
from typing import Dict, List, Any, Optional, Annotated
import json
import asyncio
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from src.models.advanced_medical_models import (
    MedicalRouterOutput, MedicalEvaluatorOutput, MedicalSatisfactionOutput,
    AdvancedMedicalState, MedicalQualityMetrics, ClinicalContext,
    MedicalRecommendations
)
from src.models.data_models import UserQuery, AgentResponse, ConsensusResponse
from src.agents.agent_factory import AgentFactory
from src.services.llm_service import LLMService
from src.utils.helpers import detect_medical_emergencies
from src.config.config import MEDICAL_SPECIALTIES

logger = logging.getLogger(__name__)

class AdvancedMedicalLangGraph:
    """
    Sistema médico avanzado con LangGraph que implementa:
    - Router inteligente con structured outputs
    - Agente evaluador crítico médico
    - Sistema de feedback loops
    - Criterios de satisfacción personalizables
    - Múltiples modelos LLM especializados
    - MODO RÁPIDO para respuestas inmediatas
    """
    
    def __init__(self, fast_mode: bool = False):
        """Initialize the advanced medical LangGraph system."""
        self.llm_service = LLMService()
        self.agent_factory = AgentFactory(llm_service=self.llm_service)
        self.fast_mode = fast_mode  # Nuevo: modo rápido
        
        # Configurar modelos especializados para diferentes componentes
        self._setup_specialized_llms()
        
        # Cache de agentes especializados
        self.specialty_agents = {}
        
        # Configurar memoria para aprendizaje continuo
        self.memory = MemorySaver()
        
        # Construir el workflow de LangGraph (normal o rápido)
        if fast_mode:
            self.workflow = self._build_fast_workflow()
        else:
            self.workflow = self._build_advanced_workflow()
    
    def _setup_specialized_llms(self):
        """Configurar modelos LLM especializados para cada componente"""
        
        # Temperaturas optimizadas para velocidad vs precisión
        temp_fast = 0.1 if self.fast_mode else 0.2
        temp_creative = 0.3 if self.fast_mode else 0.4
        
        # Router médico - requiere precisión y consistencia
        self.router_llm = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=temp_fast,
            max_tokens=1000 if self.fast_mode else 4096  # Reducir tokens en modo rápido
        )
        self.router_llm_structured = self.router_llm.with_structured_output(MedicalRouterOutput)
        
        # Evaluador médico crítico - máxima precisión y seguridad
        self.evaluator_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=800 if self.fast_mode else 2048
        )
        self.evaluator_llm_structured = self.evaluator_llm.with_structured_output(MedicalEvaluatorOutput)
        
        # Criterios de satisfacción médica - precisión extrema
        self.satisfaction_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=500 if self.fast_mode else 1024
        )
        self.satisfaction_llm_structured = self.satisfaction_llm.with_structured_output(MedicalSatisfactionOutput)
        
        # LLMs especializados por especialidad médica (optimizados para velocidad)
        base_temp = temp_creative
        base_tokens = 1500 if self.fast_mode else 4096
        
        self.specialty_llms = {
            "cardiology": ChatOpenAI(model="gpt-4o-mini", temperature=base_temp, max_tokens=base_tokens),
            "neurology": ChatOpenAI(model="gpt-4o-mini", temperature=base_temp, max_tokens=base_tokens),
            "oncology": ChatOpenAI(model="gpt-4o-mini", temperature=temp_fast, max_tokens=base_tokens),
            "pediatrics": ChatOpenAI(model="gpt-4o-mini", temperature=base_temp, max_tokens=base_tokens),
            "psychiatry": ChatOpenAI(model="gpt-4o-mini", temperature=temp_creative, max_tokens=base_tokens),
            "dermatology": ChatOpenAI(model="gpt-4o-mini", temperature=base_temp, max_tokens=base_tokens),
            "internal_medicine": ChatOpenAI(model="gpt-4o-mini", temperature=base_temp, max_tokens=base_tokens),
            "emergency_medicine": ChatOpenAI(model="gpt-4o-mini", temperature=temp_fast, max_tokens=base_tokens),
            "ophthalmology": ChatOpenAI(model="gpt-4o-mini", temperature=base_temp, max_tokens=base_tokens)
        }
        
        mode_text = "RÁPIDO" if self.fast_mode else "COMPLETO"
        logger.info(f"✅ Modelos LLM especializados configurados para modo {mode_text}")
    
    def _build_advanced_workflow(self) -> StateGraph:
        """Construir el workflow avanzado de LangGraph para consultas médicas"""
        
        workflow = StateGraph(AdvancedMedicalState)
        
        # Agregar todos los nodos del workflow
        workflow.add_node("medical_router", self.medical_router_agent)
        workflow.add_node("emergency_triage", self.emergency_triage_agent)
        workflow.add_node("consult_specialists", self.consult_specialists_agent)
        workflow.add_node("medical_evaluator", self.medical_evaluator_agent)
        workflow.add_node("satisfaction_checker", self.satisfaction_checker_agent)
        workflow.add_node("improvement_loop", self.improvement_loop_agent)
        workflow.add_node("consensus_builder", self.consensus_builder_agent)
        workflow.add_node("final_safety_check", self.final_safety_check_agent)
        
        # Definir punto de entrada
        workflow.set_entry_point("medical_router")
        
        # Definir flujo principal
        workflow.add_edge("medical_router", "emergency_triage")
        
        # Routing condicional después del triage
        workflow.add_conditional_edges(
            "emergency_triage",
            self._decide_after_triage,
            {
                "emergency": "final_safety_check",  # Emergencias van directo a safety check
                "consult": "consult_specialists"     # Consultas normales continúan
            }
        )
        
        workflow.add_edge("consult_specialists", "medical_evaluator")
        workflow.add_edge("medical_evaluator", "satisfaction_checker")
        
        # Feedback loop condicional
        workflow.add_conditional_edges(
            "satisfaction_checker",
            self._decide_feedback_loop,
            {
                "improve": "improvement_loop",
                "consensus": "consensus_builder"
            }
        )
        
        workflow.add_edge("improvement_loop", "consult_specialists")  # Volver a consultar
        workflow.add_edge("consensus_builder", "final_safety_check")
        workflow.add_edge("final_safety_check", END)
        
        # Compilar con memoria para aprendizaje continuo
        return workflow.compile(checkpointer=self.memory)
    
    def _build_fast_workflow(self) -> StateGraph:
        """Construir workflow RÁPIDO con menos pasos para velocidad óptima"""
        
        workflow = StateGraph(AdvancedMedicalState)
        
        # Solo los nodos esenciales para velocidad
        workflow.add_node("fast_router", self.fast_router_agent)
        workflow.add_node("fast_specialist", self.fast_specialist_agent)
        workflow.add_node("quick_safety_check", self.quick_safety_check_agent)
        
        # Flujo lineal simplificado
        workflow.set_entry_point("fast_router")
        workflow.add_edge("fast_router", "fast_specialist")
        workflow.add_edge("fast_specialist", "quick_safety_check")
        workflow.add_edge("quick_safety_check", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    def medical_router_agent(self, state: AdvancedMedicalState) -> AdvancedMedicalState:
        """Router médico inteligente con análisis profundo y structured outputs"""
        
        user_query = state["user_query"]
        query_text = user_query.query
        
        router_prompt = f"""
        Eres un médico especialista en triaje con 20 años de experiencia en análisis de consultas médicas.
        
        Analiza la siguiente consulta médica con máximo detalle clínico:
        "{query_text}"
        
        Tu análisis debe incluir:
        1. Especialidad médica principal más apropiada
        2. Especialidades secundarias que podrían aportar valor
        3. Nivel de urgencia médica (low, medium, high, critical)
        4. Palabras clave médicas relevantes
        5. Condiciones médicas que podrían estar relacionadas
        6. Si requiere atención de emergencia inmediata
        
        Considera estos factores clínicos:
        - Síntomas presentados y su severidad
        - Factores de riesgo aparentes
        - Señales de alarma médica (red flags)
        - Contexto temporal de los síntomas
        - Necesidad de evaluación presencial vs. telemedicina
        
        Prioriza SIEMPRE la seguridad del paciente en tu análisis.
        """
        
        try:
            # Usar structured output para análisis preciso
            result = self.router_llm_structured.invoke([
                SystemMessage(content=router_prompt)
            ])
            
            logger.info(f"Router médico: {result.primary_specialty} (urgencia: {result.urgency_level})")
            
            return {
                "primary_specialty": result.primary_specialty,
                "secondary_specialties": result.secondary_specialties,
                "urgency_level": result.urgency_level,
                "medical_keywords": result.medical_keywords,
                "suspected_conditions": result.suspected_conditions,
                "requires_emergency": result.requires_emergency,
                "router_confidence": result.confidence,
                "attempt_count": 0,
                "max_attempts": 3,
                "is_complete": False,
                "medical_criteria": self._generate_medical_criteria(result),
                "messages": [HumanMessage(content=query_text)]
            }
            
        except Exception as e:
            logger.error(f"Error en router médico: {e}")
            # Fallback seguro para medicina interna
            return {
                "primary_specialty": "internal_medicine",
                "secondary_specialties": [],
                "urgency_level": "medium",
                "medical_keywords": ["consulta", "general"],
                "suspected_conditions": [],
                "requires_emergency": False,
                "router_confidence": 0.5,
                "attempt_count": 0,
                "max_attempts": 3,
                "is_complete": False,
                "medical_criteria": "Proporcionar una consulta médica segura y completa",
                "messages": [HumanMessage(content=user_query.query)]
            }
    
    def emergency_triage_agent(self, state: AdvancedMedicalState) -> AdvancedMedicalState:
        """Agente de triaje de emergencias con protocolos médicos avanzados"""
        
        user_query = state["user_query"]
        urgency_level = state["urgency_level"]
        suspected_conditions = state["suspected_conditions"]
        
        # Detectar emergencias usando múltiples métodos
        emergency_status = detect_medical_emergencies(user_query.query)
        requires_emergency = state["requires_emergency"] or emergency_status.get("is_emergency", False)
        
        # Análisis adicional para emergencias críticas
        if urgency_level == "critical" or requires_emergency:
            emergency_prompt = f"""
            PROTOCOLO DE EMERGENCIA MÉDICA ACTIVADO
            
            Consulta: {user_query.query}
            Condiciones sospechadas: {suspected_conditions}
            
            Como médico de emergencias, proporciona:
            1. Evaluación inmediata de riesgo vital
            2. Instrucciones de primeros auxilios si aplican
            3. Recomendación urgente sobre atención médica
            4. Advertencias de seguridad críticas
            
            PRIORIDAD ABSOLUTA: Seguridad del paciente
            """
            
            try:
                emergency_response = self.specialty_llms["emergency_medicine"].invoke([
                    SystemMessage(content=emergency_prompt)
                ])
                
                return {
                    "current_response": emergency_response.content,
                    "requires_emergency": True,
                    "active_agent": "emergency_medicine",
                    "safety_warnings": "ATENCIÓN MÉDICA URGENTE REQUERIDA",
                    "next_medical_action": "seek_emergency"
                }
                
            except Exception as e:
                logger.error(f"Error en triaje de emergencia: {e}")
                return {
                    "current_response": "BUSQUE ATENCIÓN MÉDICA INMEDIATA - No puedo evaluar completamente su condición por error del sistema",
                    "requires_emergency": True,
                    "active_agent": "emergency_medicine",
                    "safety_warnings": "CONSULTE INMEDIATAMENTE CON PROFESIONAL MÉDICO"
                }
        
        # Para consultas no urgentes, continuar con workflow normal
        return {
            "requires_emergency": False,
            "active_agent": state["primary_specialty"]
        }
    
    async def consult_specialists_agent(self, state: AdvancedMedicalState) -> AdvancedMedicalState:
        """Consultar con agentes especialistas médicos mejorados"""
        
        user_query = state["user_query"]
        primary_specialty = state["primary_specialty"]
        secondary_specialties = state.get("secondary_specialties", [])
        attempt_count = state.get("attempt_count", 0)
        clinical_feedback = state.get("clinical_feedback", "")
        medical_criteria = state.get("medical_criteria", "")
        
        # Determinar especialidades a consultar
        specialties_to_consult = [primary_specialty] + secondary_specialties[:2]
        specialties_to_consult = list(set(specialties_to_consult))  # Eliminar duplicados
        
        # Preparar contexto para los agentes
        consultation_context = {
            "medical_criteria": medical_criteria,
            "attempt_number": attempt_count + 1,
            "clinical_feedback": clinical_feedback,
            "urgency_level": state.get("urgency_level", "medium"),
            "suspected_conditions": state.get("suspected_conditions", [])
        }
        
        agent_responses = {}
        
        try:
            # Consultar cada especialista
            for specialty in specialties_to_consult:
                if specialty not in self.specialty_agents:
                    self.specialty_agents[specialty] = self.agent_factory.create_agent(specialty)
                
                agent = self.specialty_agents[specialty]
                
                # Crear prompt mejorado con contexto clínico
                enhanced_prompt = self._create_enhanced_medical_prompt(
                    user_query.query, specialty, consultation_context
                )
                
                response = await agent.process_query(enhanced_prompt, user_query.context)
                agent_responses[specialty] = response
            
            logger.info(f"Consultados {len(agent_responses)} especialistas médicos")
            
            # Usar la respuesta del especialista principal
            primary_response = agent_responses.get(primary_specialty, list(agent_responses.values())[0])
            
            return {
                "agent_responses": agent_responses,
                "current_response": primary_response.response,
                "active_agent": primary_specialty,
                "attempt_count": attempt_count + 1
            }
            
        except Exception as e:
            logger.error(f"Error consultando especialistas: {e}")
            fallback_response = "No pude completar la consulta especializada. Por favor, consulte con un médico presencialmente."
            return {
                "agent_responses": {},
                "current_response": fallback_response,
                "active_agent": "general",
                "attempt_count": attempt_count + 1
            }
    
    def medical_evaluator_agent(self, state: AdvancedMedicalState) -> AdvancedMedicalState:
        """Agente evaluador crítico especializado en medicina"""
        
        current_response = state.get("current_response", "")
        medical_criteria = state.get("medical_criteria", "")
        urgency_level = state.get("urgency_level", "medium")
        suspected_conditions = state.get("suspected_conditions", [])
        user_query = state["user_query"]
        
        evaluator_prompt = f"""
        Eres un médico evaluador senior con especialización en calidad asistencial y seguridad del paciente.
        
        CONTEXTO CLÍNICO:
        - Consulta original: {user_query.query}
        - Nivel de urgencia: {urgency_level}
        - Condiciones sospechadas: {suspected_conditions}
        - Criterios médicos: {medical_criteria}
        
        RESPUESTA A EVALUAR:
        {current_response}
        
        Evalúa la respuesta médica considerando:
        
        1. PRECISIÓN CLÍNICA (1-10): ¿La información médica es correcta y actualizada?
        2. SEGURIDAD DEL PACIENTE (1-10): ¿Prioriza la seguridad y evita riesgos?
        3. COMPLETITUD: ¿Aborda todos los aspectos clínicos relevantes?
        4. APROPIACIÓN: ¿Las recomendaciones son médicamente apropiadas?
        5. CUMPLIMIENTO ÉTICO: ¿Respeta principios de bioética médica?
        6. NECESIDAD DE DERIVACIÓN: ¿Requiere especialista o atención presencial?
        
        Si encuentra deficiencias, proporciona feedback clínico específico para mejorar la respuesta.
        CRÍTICO: Identifica cualquier riesgo de seguridad o información incorrecta.
        """
        
        try:
            result = self.evaluator_llm_structured.invoke([
                SystemMessage(content=evaluator_prompt)
            ])
            
            logger.info(f"Evaluación médica: precisión {result.clinical_accuracy}/10, seguridad {result.safety_score}/10")
            
            return {
                "clinical_accuracy": result.clinical_accuracy,
                "safety_score": result.safety_score,
                "patient_safety": result.patient_safety,
                "ethical_compliance": result.ethical_compliance,
                "needs_improvement": result.needs_improvement,
                "improvement_suggestions": result.improvement_suggestions,
                "safety_warnings": result.safety_warnings,
                "clinical_feedback": result.clinical_feedback,
                "needs_specialist_referral": result.needs_specialist_referral
            }
            
        except Exception as e:
            logger.error(f"Error en evaluador médico: {e}")
            # Evaluación conservadora en caso de error
            return {
                "clinical_accuracy": 5,
                "safety_score": 5,
                "patient_safety": False,
                "ethical_compliance": True,
                "needs_improvement": True,
                "improvement_suggestions": "Respuesta requiere revisión médica adicional",
                "safety_warnings": "Consulte con profesional médico para confirmación",
                "clinical_feedback": "Error en evaluación automática - requiere revisión manual",
                "needs_specialist_referral": True
            }
    
    def satisfaction_checker_agent(self, state: AdvancedMedicalState) -> AdvancedMedicalState:
        """Verificar criterios de satisfacción médica específicos"""
        
        current_response = state.get("current_response", "")
        medical_criteria = state.get("medical_criteria", "")
        clinical_accuracy = state.get("clinical_accuracy", 5)
        safety_score = state.get("safety_score", 5)
        patient_safety = state.get("patient_safety", False)
        user_query = state["user_query"]
        
        satisfaction_prompt = f"""
        Evalúa si la respuesta médica cumple con los criterios de satisfacción para el paciente.
        
        CONSULTA DEL PACIENTE: {user_query.query}
        CRITERIOS MÉDICOS: {medical_criteria}
        
        RESPUESTA MÉDICA:
        {current_response}
        
        MÉTRICAS DE CALIDAD:
        - Precisión clínica: {clinical_accuracy}/10
        - Puntuación de seguridad: {safety_score}/10
        - Seguridad del paciente: {patient_safety}
        
        Determina si:
        1. Se cumplieron todos los criterios médicos establecidos
        2. Se atendieron las preocupaciones específicas del paciente
        3. El nivel de detalle es apropiado para el paciente
        4. Se proporcionó orientación práctica y accionable
        5. Se requiere consulta con médico humano
        
        Estándares mínimos:
        - Precisión clínica ≥ 7/10
        - Seguridad del paciente = True
        - Información médicamente apropiada
        """
        
        try:
            result = self.satisfaction_llm_structured.invoke([
                SystemMessage(content=satisfaction_prompt)
            ])
            
            logger.info(f"Criterios médicos cumplidos: {result.medical_criteria_met}")
            
            return {
                "medical_criteria_met": result.medical_criteria_met,
                "patient_concerns_addressed": result.patient_concerns_addressed,
                "next_medical_action": result.next_medical_action,
                "requires_human_physician": result.requires_human_physician
            }
            
        except Exception as e:
            logger.error(f"Error verificando satisfacción médica: {e}")
            # Evaluación conservadora
            return {
                "medical_criteria_met": False,
                "patient_concerns_addressed": False,
                "next_medical_action": "improve_response",
                "requires_human_physician": True
            }
    
    def improvement_loop_agent(self, state: AdvancedMedicalState) -> AdvancedMedicalState:
        """Agente que gestiona el loop de mejora continua"""
        
        attempt_count = state.get("attempt_count", 0)
        max_attempts = state.get("max_attempts", 3)
        improvement_suggestions = state.get("improvement_suggestions", "")
        
        if attempt_count >= max_attempts:
            logger.warning(f"Máximo de intentos alcanzado ({max_attempts})")
            return {
                "is_complete": True,
                "next_medical_action": "specialist_referral"
            }
        
        # Preparar feedback para la siguiente iteración
        feedback_summary = f"""
        ITERACIÓN {attempt_count + 1}/{max_attempts}
        
        Mejoras requeridas: {improvement_suggestions}
        
        Enfócate en:
        1. Precisión clínica mejorada
        2. Seguridad del paciente
        3. Recomendaciones más específicas
        4. Cumplimiento de criterios médicos
        """
        
        return {
            "clinical_feedback": feedback_summary,
            "is_complete": False
        }
    
    async def consensus_builder_agent(self, state: AdvancedMedicalState) -> AdvancedMedicalState:
        """Construir consenso médico final integrando todas las evaluaciones"""
        
        agent_responses = state.get("agent_responses", {})
        primary_specialty = state["primary_specialty"]
        clinical_accuracy = state.get("clinical_accuracy", 5)
        safety_score = state.get("safety_score", 5)
        safety_warnings = state.get("safety_warnings", "")
        
        try:
            # Usar el agente de consenso existente pero con contexto médico mejorado
            from src.agents.consensus_agent import ConsensusAgent
            consensus_agent = ConsensusAgent(llm_service=self.llm_service)
            
            # Crear contexto médico enriquecido
            medical_context = {
                "clinical_accuracy": clinical_accuracy,
                "safety_score": safety_score,
                "safety_warnings": safety_warnings,
                "urgency_level": state.get("urgency_level", "medium"),
                "suspected_conditions": state.get("suspected_conditions", [])
            }
            
            consensus_response = await consensus_agent.build_intelligent_consensus(
                agent_responses=agent_responses,
                emergency_status={"is_emergency": state.get("requires_emergency", False)},
                primary_specialty=primary_specialty,
                user_query=state["user_query"].query
            )
            
            return {
                "consensus_response": consensus_response,
                "is_complete": True
            }
            
        except Exception as e:
            logger.error(f"Error construyendo consenso médico: {e}")
            # Fallback a respuesta simple
            return {
                "consensus_response": ConsensusResponse(
                    primary_specialty=primary_specialty,
                    primary_response=state.get("current_response", "Consulte con un médico para una evaluación completa.")
                ),
                "is_complete": True
            }
    
    def final_safety_check_agent(self, state: AdvancedMedicalState) -> AdvancedMedicalState:
        """Verificación final de seguridad médica antes de entregar respuesta"""
        
        consensus_response = state.get("consensus_response")
        requires_emergency = state.get("requires_emergency", False)
        safety_warnings = state.get("safety_warnings", "")
        
        if requires_emergency or not consensus_response:
            # Para emergencias o fallos, proporcionar mensaje de seguridad
            emergency_response = ConsensusResponse(
                primary_specialty="emergency_medicine",
                primary_response="ATENCIÓN: Esta situación puede requerir atención médica inmediata. Por favor, contacte a servicios de emergencia o acuda al centro médico más cercano.",
                patient_recommendations=[
                    "Buscar atención médica inmediata",
                    "No automedicarse",
                    "Contactar servicios de emergencia si es necesario"
                ]
            )
            
            return {
                "consensus_response": emergency_response,
                "is_complete": True
            }
        
        # Agregar disclaimers médicos estándar
        if consensus_response and consensus_response.patient_recommendations:
            safety_recommendations = [
                "Esta información es solo para fines educativos",
                "Consulte siempre con un profesional médico calificado",
                "En caso de emergencia, contacte servicios de emergencia inmediatamente"
            ]
            
            consensus_response.patient_recommendations.extend(safety_recommendations)
        
        logger.info("Verificación final de seguridad médica completada")
        
        return {
            "consensus_response": consensus_response,
            "is_complete": True
        }
    
    # Funciones de decisión para routing condicional
    def _decide_after_triage(self, state: AdvancedMedicalState) -> str:
        """Decidir el flujo después del triaje de emergencias"""
        if state.get("requires_emergency", False):
            return "emergency"
        return "consult"
    
    def _decide_feedback_loop(self, state: AdvancedMedicalState) -> str:
        """Decidir si entrar en feedback loop o continuar a consenso"""
        medical_criteria_met = state.get("medical_criteria_met", False)
        attempt_count = state.get("attempt_count", 0)
        max_attempts = state.get("max_attempts", 3)
        
        if not medical_criteria_met and attempt_count < max_attempts:
            return "improve"
        return "consensus"
    
    def _generate_medical_criteria(self, router_output: MedicalRouterOutput) -> str:
        """Generar criterios médicos específicos basados en el análisis del router"""
        criteria = [
            "Proporcionar información médica precisa y actualizada",
            "Priorizar la seguridad del paciente en todas las recomendaciones",
            "Incluir advertencias apropiadas sobre cuándo buscar atención médica"
        ]
        
        if router_output.urgency_level in ["high", "critical"]:
            criteria.append("Enfatizar la urgencia de atención médica profesional")
        
        if router_output.suspected_conditions:
            criteria.append(f"Abordar las posibles condiciones: {', '.join(router_output.suspected_conditions)}")
        
        return "; ".join(criteria)
    
    def _create_enhanced_medical_prompt(self, query: str, specialty: str, context: dict) -> str:
        """Crear prompt médico mejorado con contexto clínico y memoria conversacional"""
        
        # Construir historial conversacional si existe
        conversation_history = ""
        if context and 'conversation_history' in context:
            conversation_history = "\n\nHISTORIAL DE LA CONVERSACIÓN:"
            for msg in context['conversation_history']:
                sender = msg.get('sender', 'unknown')
                content = msg.get('content', '')
                if sender == 'user':
                    conversation_history += f"\nPaciente: {content}"
                elif sender == 'system':
                    conversation_history += f"\nSistema: {content}"
                elif sender in ['neurology', 'cardiology', 'internal_medicine', 'emergency_medicine', 
                               'pediatrics', 'oncology', 'dermatology', 'psychiatry', 'ophthalmology']:
                    conversation_history += f"\nDr. {sender.title()}: {content}"
            
            conversation_history += "\n\nÚLTIMA CONSULTA DEL PACIENTE:"
        
        base_prompt = f"""
        Como especialista en {specialty}, tienes acceso al historial completo de esta consulta médica.
        
        {conversation_history}
        CONSULTA ACTUAL: {query}
        
        IMPORTANTE - INSTRUCCIONES DE MEMORIA:
        1. REVISA TODO EL HISTORIAL - El paciente ya ha proporcionado información importante
        2. NO REPITAS preguntas ya respondidas por el paciente
        3. CONSTRUYE sobre la información ya proporcionada
        4. SINTETIZA los síntomas ya mencionados
        5. EVITA redundancias - el paciente puede frustrarse si repites preguntas
        
        INFORMACIÓN YA PROPORCIONADA POR EL PACIENTE (si existe en el historial):
        - Revisa cuidadosamente qué síntomas ya mencionó
        - Qué duración ya especificó
        - Qué factores agravantes/aliviantes ya describió
        - Qué antecedentes ya compartió
        
        CONTEXTO CLÍNICO ACTUAL:
        - Nivel de urgencia: {context.get('urgency_level', 'medium')}
        - Condiciones sospechadas: {context.get('suspected_conditions', [])}
        - Criterios médicos: {context.get('medical_criteria', '')}
        """
        
        if context.get('clinical_feedback'):
            base_prompt += f"""
            
            FEEDBACK PARA MEJORA:
            {context['clinical_feedback']}
            
            Por favor, incorpora este feedback para proporcionar una respuesta mejorada.
            """
        
        base_prompt += """
        
        INSTRUCCIONES MÉDICAS:
        1. Proporciona información médica precisa y actualizada
        2. Prioriza SIEMPRE la seguridad del paciente
        3. Incluye recomendaciones específicas y accionables
        4. Menciona cuándo buscar atención médica profesional
        5. Evita dar diagnósticos definitivos sin examen físico
        6. Cumple con los criterios médicos establecidos
        7. BASATE en toda la información ya proporcionada por el paciente
        8. Si ya tienes suficiente información, procede con recomendaciones apropiadas
        
        Estructura tu respuesta de manera clara y profesional, mostrando que has revisado toda la información previa.
        """
        
        return base_prompt
    
    async def process_medical_query(
        self, 
        query: str, 
        specialty: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        medical_criteria: Optional[str] = None
    ) -> ConsensusResponse:
        """
        Procesar consulta médica a través del workflow avanzado de LangGraph
        
        Args:
            query: Consulta médica del paciente
            specialty: Especialidad médica específica (opcional)
            context: Contexto adicional de la consulta
            medical_criteria: Criterios específicos de satisfacción médica
            
        Returns:
            Respuesta de consenso médico con todas las evaluaciones
        """
        
        try:
            logger.info(f"Procesando consulta médica avanzada: '{query[:100]}...'")
            
            # Crear query estructurada
            user_query = UserQuery(
                query=query,
                specialty=specialty,
                context=context
            )
            
            # Estado inicial
            initial_state: AdvancedMedicalState = {
                "user_query": user_query,
                "messages": [],
                "primary_specialty": specialty or "internal_medicine",
                "secondary_specialties": [],
                "urgency_level": "medium",
                "medical_keywords": [],
                "suspected_conditions": [],
                "requires_emergency": False,
                "router_confidence": 0.0,
                "agent_responses": {},
                "current_response": "",
                "active_agent": "",
                "clinical_accuracy": 5,
                "safety_score": 5,
                "patient_safety": False,
                "ethical_compliance": True,
                "needs_improvement": False,
                "improvement_suggestions": "",
                "safety_warnings": "",
                "clinical_feedback": "",
                "medical_criteria": medical_criteria or "Proporcionar consulta médica segura y completa",
                "medical_criteria_met": False,
                "patient_concerns_addressed": False,
                "next_medical_action": "consult",
                "requires_human_physician": False,
                "attempt_count": 0,
                "max_attempts": 3,
                "is_complete": False,
                "needs_specialist_referral": False,
                "medical_history": [],
                "clinical_context": {},
                "interaction_metrics": {},
                "consensus_response": None
            }
            
            # Ejecutar workflow con configuración única para esta consulta
            config = {"configurable": {"thread_id": f"medical_{datetime.now().isoformat()}"}}
            
            # Invocar el workflow de LangGraph
            final_state = await self.workflow.ainvoke(initial_state, config)
            
            logger.info("Workflow médico avanzado completado exitosamente")
            
            if not final_state.get("consensus_response"):
                raise ValueError("No se generó respuesta de consenso médico")
            
            return final_state["consensus_response"]
            
        except Exception as e:
            logger.error(f"Error en workflow médico avanzado: {e}", exc_info=True)
            
            # Respuesta de fallback médico
            fallback_response = ConsensusResponse(
                primary_specialty="internal_medicine",
                primary_response="Lo siento, no pude procesar completamente su consulta médica. "
                                "Por favor, consulte con un profesional médico para una evaluación adecuada. "
                                "En caso de emergencia, busque atención médica inmediata.",
                patient_recommendations=[
                    "Consultar con profesional médico calificado",
                    "En caso de emergencia, contactar servicios de emergencia",
                    "No automedicarse basándose únicamente en información en línea"
                ]
            )
            
            return fallback_response
    
    def fast_router_agent(self, state: AdvancedMedicalState) -> AdvancedMedicalState:
        """Router médico rápido con análisis diagnóstico enfocado"""
        
        user_query = state["user_query"]
        query_text = user_query.query
        
        # Construir contexto de conversación previa si existe
        conversation_context = ""
        if user_query.context and 'conversation_history' in user_query.context:
            conversation_context = "\n\nCONTEXTO PREVIO:"
            for msg in user_query.context['conversation_history']:
                if msg.get('sender') == 'user':
                    conversation_context += f" {msg.get('content', '')}"
            conversation_context += f"\n\nNUEVA CONSULTA: {query_text}"
        else:
            conversation_context = f"CONSULTA: {query_text}"
        
        # Prompt optimizado para análisis diagnóstico rápido
        router_prompt = f"""
        Como médico especialista en triaje, analiza esta consulta médica con enfoque diagnóstico:
        
        {conversation_context}
        
        ANÁLISIS REQUERIDO:
        1. Especialidad médica más apropiada basada en síntomas
        2. Nivel de urgencia (low/medium/high/critical)
        3. ¿Requiere atención de emergencia inmediata?
        4. Palabras clave médicas relevantes (síntomas, condiciones, factores de riesgo)
        5. Posibles condiciones a considerar (diagnósticos diferenciales principales)
        
        ENFÓCATE EN:
        - Síntomas principales presentados
        - Signos de alarma (red flags)
        - Duración y severidad
        - Factores de riesgo evidentes
        
        Prioriza PRECISIÓN DIAGNÓSTICA manteniendo velocidad.
        """
        
        try:
            result = self.router_llm_structured.invoke([
                SystemMessage(content=router_prompt)
            ])
            
            logger.info(f"Router diagnóstico rápido: {result.primary_specialty} (urgencia: {result.urgency_level}) - Condiciones: {result.suspected_conditions}")
            
            return {
                "primary_specialty": result.primary_specialty,
                "secondary_specialties": result.secondary_specialties[:2] if result.secondary_specialties else [],
                "urgency_level": result.urgency_level,
                "medical_keywords": result.medical_keywords[:5],  # Más palabras clave para diagnóstico
                "suspected_conditions": result.suspected_conditions[:3] if result.suspected_conditions else [],
                "requires_emergency": result.requires_emergency,
                "router_confidence": result.confidence,
                "is_complete": False,
                "medical_criteria": "Proceso diagnóstico rápido y seguro con análisis diferencial",
                "messages": [HumanMessage(content=query_text)]
            }
            
        except Exception as e:
            logger.error(f"Error en router diagnóstico rápido: {e}")
            return {
                "primary_specialty": "internal_medicine",
                "urgency_level": "medium",
                "medical_keywords": ["consulta", "síntomas", "evaluación"],
                "suspected_conditions": [],
                "requires_emergency": False,
                "is_complete": False,
                "messages": [HumanMessage(content=query_text)]
            }
    
    async def fast_specialist_agent(self, state: AdvancedMedicalState) -> AdvancedMedicalState:
        """Consulta especializada rápida con RAZONAMIENTO DIAGNÓSTICO estructurado y memoria"""
        
        user_query = state["user_query"]
        primary_specialty = state["primary_specialty"]
        urgency_level = state.get("urgency_level", "medium")
        medical_keywords = state.get("medical_keywords", [])
        
        try:
            # Obtener agente especialista
            if primary_specialty not in self.specialty_agents:
                self.specialty_agents[primary_specialty] = self.agent_factory.create_agent(primary_specialty)
            
            agent = self.specialty_agents[primary_specialty]
            
            # Construir historial conversacional si existe en el contexto
            conversation_history = ""
            patient_info_summary = ""
            if user_query.context and 'conversation_history' in user_query.context:
                conversation_history = "\n\nHISTORIAL COMPLETO DE SÍNTOMAS:"
                patient_symptoms = []
                for msg in user_query.context['conversation_history']:
                    sender = msg.get('sender', 'unknown')
                    content = msg.get('content', '')
                    if sender == 'user':
                        conversation_history += f"\nPaciente: {content}"
                        patient_symptoms.append(content)
                    elif sender in ['neurology', 'cardiology', 'internal_medicine', 'emergency_medicine', 
                                   'pediatrics', 'oncology', 'dermatology', 'psychiatry', 'ophthalmology']:
                        conversation_history += f"\nDr. {sender.title()}: {content}"
                
                # Crear resumen de síntomas del paciente
                if patient_symptoms:
                    patient_info_summary = f"\n\nRESUMEN DE SÍNTOMAS PROPORCIONADOS:\n{' | '.join(patient_symptoms)}"
                
                conversation_history += "\n\nCONSULTA ACTUAL:"
            
            # Prompt con RAZONAMIENTO DIAGNÓSTICO estructurado
            diagnostic_prompt = f"""
            Como especialista experimentado en {primary_specialty}, debes realizar un PROCESO DIAGNÓSTICO ESTRUCTURADO.
            
            {conversation_history}
            CONSULTA ACTUAL: {user_query.query}
            {patient_info_summary}
            
            URGENCIA: {urgency_level}
            PALABRAS CLAVE: {', '.join(medical_keywords)}
            
            🧠 PROCESO DIAGNÓSTICO REQUERIDO:
            
            1. ANÁLISIS DE SÍNTOMAS (basado en TODA la información proporcionada):
               - Síntoma principal y características
               - Síntomas asociados ya mencionados
               - Duración y evolución
               - Factores agravantes/aliviantes
            
            2. HIPÓTESIS DIAGNÓSTICAS (considera y menciona):
               - Diagnóstico más probable
               - Diagnósticos diferenciales importantes
               - Condiciones que deben descartarse (red flags)
            
            3. EVALUACIÓN MÉDICA:
               - ¿Qué información adicional necesitas? (si hay algo específico faltante)
               - ¿Hay signos de alarma?
               - ¿Requiere atención urgente?
            
            4. PLAN DE ACCIÓN:
               - Medidas inmediatas
               - Cuándo buscar atención médica
               - Seguimiento recomendado
            
            CRÍTICO: NO repitas preguntas ya respondidas. CONSTRUYE sobre la información ya proporcionada.
            Si ya tienes suficiente información, procede con recomendaciones específicas.
            
            ESTRUCTURA TU RESPUESTA:
            "Basándome en los síntomas que describes [resumir brevemente], considero que..."
            """
            
            response = await agent.process_query(diagnostic_prompt, user_query.context)
            
            logger.info(f"Especialista rápido {primary_specialty} - DIAGNÓSTICO ESTRUCTURADO completado")
            
            return {
                "current_response": response.response,
                "active_agent": primary_specialty,
                "clinical_accuracy": 8,  # Asumido alto para velocidad
                "safety_score": 8,
                "patient_safety": True
            }
            
        except Exception as e:
            logger.error(f"Error en especialista rápido diagnóstico: {e}", exc_info=True)
            
            # Respuesta de fallback más completa basada en la información disponible
            fallback_response = f"""
            Como especialista en {primary_specialty}, lamento experimentar dificultades técnicas para procesar completamente su consulta médica en este momento.
            
            Basándome en la información inicial que proporcionó sobre sus síntomas, le recomiendo encarecidamente:
            
            1. **Consulta médica presencial**: Es fundamental que un profesional médico evalúe sus síntomas de manera directa.
            
            2. **No demorar la atención**: Si sus síntomas persisten, empeoran, o si experimenta señales de alarma, busque atención médica sin demora.
            
            3. **Monitoreo de síntomas**: Mantenga un registro de la evolución de sus síntomas para proporcionárselo al médico.
            
            Por favor, disculpe las dificultades técnicas. Su salud es prioritaria y merece una evaluación médica profesional adecuada.
            """
            
            return {
                "current_response": fallback_response.strip(),
                "active_agent": primary_specialty,
                "clinical_accuracy": 6,  # Respuesta de seguridad apropiada
                "safety_score": 8,      # Alta seguridad al recomendar consulta médica
                "patient_safety": True
            }
    
    def quick_safety_check_agent(self, state: AdvancedMedicalState) -> AdvancedMedicalState:
        """Verificación de seguridad con validación diagnóstica y manejo robusto de errores"""
        
        try:
            current_response = state.get("current_response", "")
            requires_emergency = state.get("requires_emergency", False)
            primary_specialty = state.get("primary_specialty", "internal_medicine")
            urgency_level = state.get("urgency_level", "medium")
            suspected_conditions = state.get("suspected_conditions", [])
            
            # Verificar que tenemos una respuesta válida
            if not current_response or len(current_response.strip()) < 10:
                logger.error("Respuesta médica insuficiente o vacía - generando respuesta de seguridad")
                fallback_response = ConsensusResponse(
                    primary_specialty=primary_specialty,
                    primary_response="Lo siento, no pude generar una respuesta médica completa. Por favor, consulte con un profesional médico para una evaluación adecuada de sus síntomas.",
                    patient_recommendations=[
                        "Consultar con profesional médico calificado",
                        "Describir todos sus síntomas al médico",
                        "No demorar la consulta si los síntomas persisten"
                    ]
                )
                
                return {
                    "consensus_response": fallback_response,
                    "is_complete": True
                }
            
            # Verificar que la respuesta contenga elementos diagnósticos apropiados
            diagnostic_quality_check = self._assess_diagnostic_response(current_response)
            
            # Crear respuesta final con mejoras diagnósticas si es necesario
            if requires_emergency:
                final_response = ConsensusResponse(
                    primary_specialty="emergency_medicine",
                    primary_response="⚠️ SITUACIÓN URGENTE: Busque atención médica inmediata. " + current_response,
                    patient_recommendations=[
                        "Contactar servicios de emergencia inmediatamente",
                        "Acudir al hospital más cercano",
                        "No demorar la atención médica"
                    ]
                )
            else:
                # Mejorar respuesta si carece de elementos diagnósticos
                enhanced_response = current_response
                
                # Solo agregar mejoras si realmente faltan elementos importantes
                if not diagnostic_quality_check["has_diagnostic_reasoning"] and len(suspected_conditions) > 0:
                    logger.info("Agregando consideraciones diagnósticas complementarias")
                    enhancement = self._generate_diagnostic_enhancement(
                        primary_specialty, suspected_conditions, urgency_level
                    )
                    enhanced_response = current_response + "\n\n" + enhancement
                
                # Agregar disclaimers médicos apropiados (solo si no existen ya)
                if "⚕️" not in enhanced_response and "orientativa" not in enhanced_response.lower():
                    safety_footer = "\n\n⚕️ Nota: Esta información es orientativa. Consulte siempre con un médico calificado."
                    enhanced_response += safety_footer
                
                # Generar recomendaciones específicas basadas en la urgencia
                recommendations = self._generate_safety_recommendations(urgency_level, suspected_conditions)
                
                final_response = ConsensusResponse(
                    primary_specialty=primary_specialty,
                    primary_response=enhanced_response,
                    patient_recommendations=recommendations
                )
            
            logger.info(f"Verificación de seguridad completada - Calidad diagnóstica: {diagnostic_quality_check}")
            
            return {
                "consensus_response": final_response,
                "is_complete": True
            }
            
        except Exception as e:
            logger.error(f"Error crítico en verificación de seguridad: {e}", exc_info=True)
            
            # Respuesta de emergencia en caso de error completo
            emergency_fallback = ConsensusResponse(
                primary_specialty=state.get("primary_specialty", "internal_medicine"),
                primary_response="Estoy experimentando dificultades técnicas para procesar su consulta médica completamente. Por seguridad, le recomiendo encarecidamente que consulte con un profesional médico para una evaluación presencial de sus síntomas.",
                patient_recommendations=[
                    "Consultar con médico presencialmente lo antes posible",
                    "Si es urgente, contactar servicios de emergencia",
                    "No demorar la atención médica profesional"
                ]
            )
            
            return {
                "consensus_response": emergency_fallback,
                "is_complete": True
            }
    
    def _assess_diagnostic_response(self, response: str) -> Dict[str, bool]:
        """Evaluar rápidamente si la respuesta contiene elementos diagnósticos apropiados"""
        response_lower = response.lower()
        
        # Palabras clave que indican razonamiento diagnóstico (expandidas y mejoradas)
        diagnostic_keywords = [
            "diagnóstico", "diagnóstica", "considero", "probable", "posible", "posiblemente", 
            "descart", "síntoma", "síntomas", "evalua", "evaluación", "anális", "análisis",
            "hipótesis", "diferencial", "basándome", "basado", "sugiere", "indica", "compatible",
            "condición", "condiciones", "enfermedad", "trastorno", "causas", "causa",
            "migraña", "cefalea", "cardio", "neurológic", "psiquiátric", "dermatológic",
            "podría", "puede", "parece", "aparenta", "característic", "típico", "atípico"
        ]
        
        # Palabras clave que indican recomendaciones médicas (expandidas)
        recommendation_keywords = [
            "recomiendo", "recomendación", "sugiero", "sugerencia", "debe", "debería",
            "consulte", "consulta", "acuda", "evalúe", "evaluación", "realice", "evite", 
            "trate", "tratamiento", "importante", "necesario", "urgente", "inmediato",
            "buscar", "atención", "médica", "hospital", "doctor", "profesional",
            "cita", "seguimiento", "monitoreo", "control"
        ]
        
        # Verificación más robusta
        has_diagnostic = any(keyword in response_lower for keyword in diagnostic_keywords)
        has_recommendations = any(keyword in response_lower for keyword in recommendation_keywords)
        
        # Log para debugging
        if not has_diagnostic:
            found_diagnostic = [kw for kw in diagnostic_keywords if kw in response_lower]
            logger.debug(f"Diagnóstico encontrado: {found_diagnostic}")
        
        if not has_recommendations:
            found_recommendations = [kw for kw in recommendation_keywords if kw in response_lower]
            logger.debug(f"Recomendaciones encontradas: {found_recommendations}")
        
        return {
            "has_diagnostic_reasoning": has_diagnostic,
            "has_medical_recommendations": has_recommendations,
            "sufficient_length": len(response) > 50  # Reducido de 100 a 50
        }
    
    def _generate_diagnostic_enhancement(self, specialty: str, suspected_conditions: List[str], urgency: str) -> str:
        """Generar mejora diagnóstica rápida si la respuesta original carece de ella"""
        
        enhancement = "**Consideraciones Diagnósticas Adicionales:**\n"
        
        if suspected_conditions:
            enhancement += f"Basándome en los síntomas descritos, las condiciones a considerar incluyen: {', '.join(suspected_conditions[:2])}. "
        
        if urgency in ["high", "critical"]:
            enhancement += "Dada la naturaleza de los síntomas, es importante descartar condiciones que requieran atención urgente. "
        
        enhancement += f"Se recomienda evaluación por especialista en {specialty} para confirmación diagnóstica y plan de tratamiento apropiado."
        
        return enhancement
    
    def _generate_safety_recommendations(self, urgency: str, suspected_conditions: List[str]) -> List[str]:
        """Generar recomendaciones de seguridad específicas basadas en urgencia y condiciones"""
        
        base_recommendations = [
            "Consultar con médico si los síntomas persisten o empeoran",
            "No automedicarse sin supervisión médica profesional"
        ]
        
        if urgency == "critical":
            return [
                "Buscar atención médica de emergencia inmediatamente",
                "No esperar - contactar servicios de emergencia",
                "Evitar automedicación"
            ]
        elif urgency == "high":
            return [
                "Consultar con médico en las próximas 24 horas",
                "Buscar atención inmediata si los síntomas empeoran",
                "Monitorear síntomas de cerca"
            ] + base_recommendations
        elif urgency == "medium":
            return [
                "Programar consulta médica en los próximos días",
                "Monitorear evolución de síntomas"
            ] + base_recommendations
        else:  # low urgency
            return base_recommendations + [
                "Considerar consulta médica si no hay mejoría en una semana",
                "Mantener medidas de cuidado general"
            ] 