"""
Controlador para la orquestación y gestión de los diversos agentes médicos.
Coordina el triaje y la derivación a especialistas.
"""
from src.agents.triage_agent import TriageAgent
from src.agents.specialist_agent import SpecialistAgent
import os
import logging
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/agents.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class AgentController:
    """
    Controlador central para el sistema de agentes médicos.
    Coordina el triaje y la derivación a especialistas.
    """
    def __init__(self):
        """Inicializa el controlador de agentes y carga los agentes necesarios."""
        logger.info("Inicializando controlador de agentes médicos")
        self.triage_agent = TriageAgent()
        
        # Inicializar especialistas bajo demanda
        self._specialists = {}  # Se cargarán según se necesiten
        self._specialties = self.triage_agent.specialties
    
    def _get_specialist(self, specialty):
        """
        Obtiene o crea un agente especialista para la especialidad solicitada
        
        Args:
            specialty: Especialidad médica requerida
            
        Returns:
            SpecialistAgent: Agente especialista en el área solicitada
        """
        # Normalizar nombre de especialidad
        specialty = specialty.lower()
        
        # Si no existe, crearlo y almacenarlo
        if specialty not in self._specialists:
            logger.info(f"Creando nuevo agente especialista: {specialty}")
            self._specialists[specialty] = SpecialistAgent(specialty)
        
        return self._specialists[specialty]
    
    def process_query(self, patient_query, patient_history="", patient_id=None):
        """
        Procesa una consulta médica completa a través del sistema de agentes
        
        Args:
            patient_query: Consulta del paciente
            patient_history: Historial médico del paciente (opcional)
            patient_id: Identificador del paciente para seguimiento (opcional)
            
        Returns:
            dict: Resultado del procesamiento con información de triaje y respuesta especializada
        """
        # Registrar la consulta
        if patient_id:
            logger.info(f"Procesando consulta para paciente ID: {patient_id}")
        else:
            logger.info("Procesando consulta anónima")
        
        # Paso 1: Realizar triaje para determinar especialidad
        triage_result = self.triage_agent.evaluate(patient_query, patient_history)
        logger.info(f"Triaje completado - Especialidad: {triage_result['specialty']}, Urgencia: {triage_result['urgency']}")
        
        # Paso 2: Derivar al especialista adecuado
        specialty = triage_result["specialty"]
        
        try:
            # Obtener el especialista adecuado
            specialist = self._get_specialist(specialty)
            
            # Paso 3: Obtener respuesta del especialista
            specialist_response = specialist.respond(patient_query)
            logger.info(f"Respuesta generada por especialista en {specialty}")
            
            # Construir resultado
            result = {
                "triage": triage_result,
                "specialist_response": specialist_response,
                "specialty": specialty,
                "success": True
            }
            
        except Exception as e:
            # En caso de error, usar medicina interna como fallback
            logger.error(f"Error al procesar con especialista {specialty}: {str(e)}")
            fallback_specialty = "medicina_interna"
            
            try:
                fallback_specialist = self._get_specialist(fallback_specialty)
                specialist_response = fallback_specialist.respond(patient_query)
                
                # Construir resultado con advertencia
                result = {
                    "triage": triage_result,
                    "specialist_response": specialist_response,
                    "specialty": fallback_specialty,
                    "success": True,
                    "warning": f"Se utilizó medicina interna como alternativa debido a un error con {specialty}"
                }
                
            except Exception as e2:
                # Error crítico si falla incluso el fallback
                logger.critical(f"Error en especialista de fallback: {str(e2)}")
                result = {
                    "triage": triage_result,
                    "specialist_response": "Lo siento, no podemos procesar tu consulta en este momento. Por favor, intenta nuevamente más tarde.",
                    "specialty": None,
                    "success": False,
                    "error": "Error al procesar la consulta médica"
                }
        
        return result 