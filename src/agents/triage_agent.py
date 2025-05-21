"""
Agente de triaje para clasificar consultas médicas y dirigirlas
al especialista adecuado.
"""
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class TriageAgent:
    """
    Agente que evalúa consultas médicas y determina qué especialidad
    médica es la más adecuada para atenderlas.
    """
    def __init__(self, llm=None):
        """
        Inicializa el agente de triaje
        
        Args:
            llm: Modelo de lenguaje a utilizar (opcional)
        """
        # Usar el LLM proporcionado o crear uno nuevo con GPT-4
        self.llm = llm or ChatOpenAI(
            model="gpt-4-turbo", 
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Lista de especialidades médicas disponibles
        self.specialties = [
            "cardiología", "neurología", "pediatría", "oncología",
            "dermatología", "psiquiatría", "medicina_interna", "emergencia"
        ]
        
        # Prompt para el triaje médico
        self.triage_prompt = PromptTemplate(
            input_variables=["patient_query", "specialties", "patient_history"],
            template="""
            Actúa como un médico de triaje en la entrada de un hospital. Analiza esta consulta médica:
            
            Consulta del paciente: {patient_query}
            
            Historial del paciente: {patient_history}
            
            Basado en esta información, determina qué especialidad médica sería más adecuada para atender 
            esta consulta. Las especialidades disponibles son: {specialties}
            
            Proporciona:
            1. La especialidad más adecuada (SÓLO UNA)
            2. Un breve razonamiento (2-3 frases)
            3. Nivel de urgencia (1-5, donde 5 es emergencia)
            
            Formato de respuesta:
            Especialidad: [nombre de la especialidad]
            Razonamiento: [explicación]
            Urgencia: [nivel]
            """
        )
        
        # Crear la cadena de procesamiento
        self.triage_chain = LLMChain(llm=self.llm, prompt=self.triage_prompt)
    
    def evaluate(self, patient_query, patient_history="No hay historial previo disponible"):
        """
        Evalúa la consulta y determina la especialidad y urgencia
        
        Args:
            patient_query: Consulta del paciente
            patient_history: Historial médico del paciente (opcional)
            
        Returns:
            dict: Diccionario con especialidad, razonamiento y nivel de urgencia
        """
        response = self.triage_chain.invoke({
            "patient_query": patient_query,
            "specialties": ", ".join(self.specialties),
            "patient_history": patient_history
        })
        
        # Parsear la respuesta
        lines = response['text'].strip().split('\n')
        specialty = None
        reasoning = None
        urgency = None
        
        for line in lines:
            if line.startswith("Especialidad:"):
                specialty = line.split(':', 1)[1].strip().lower()
            elif line.startswith("Razonamiento:"):
                reasoning = line.split(':', 1)[1].strip()
            elif line.startswith("Urgencia:"):
                try:
                    urgency = int(line.split(':', 1)[1].strip())
                except ValueError:
                    urgency = 1  # Valor predeterminado si hay error de formato
        
        # Si no se logró extraer algún valor, establecer valores predeterminados
        if specialty is None or specialty not in [s.lower() for s in self.specialties]:
            specialty = "medicina_interna"  # Especialidad predeterminada
        if reasoning is None:
            reasoning = "No se proporcionó razonamiento."
        if urgency is None or urgency < 1 or urgency > 5:
            urgency = 1  # Urgencia predeterminada
        
        return {
            "specialty": specialty,
            "reasoning": reasoning,
            "urgency": urgency
        } 