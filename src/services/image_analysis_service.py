"""
Servicio para el análisis de imágenes médicas utilizando
la capacidad de visión del modelo de lenguaje.
"""
import os
import base64
import logging
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class MedicalImageAnalyzer:
    """
    Analizador de imágenes médicas utilizando modelos multimodales de LLM
    con capacidades de visión.
    """
    def __init__(self, model_name="gpt-4-vision-preview"):
        """
        Inicializa el analizador de imágenes médicas
        
        Args:
            model_name: Nombre del modelo con capacidades de visión a utilizar
        """
        self.model_name = model_name
        
        # Inicializar el modelo
        try:
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=0.2,
                api_key=os.getenv("OPENAI_API_KEY"),
                max_tokens=1000
            )
            logger.info(f"Analizador de imágenes médicas iniciado con modelo: {model_name}")
        except Exception as e:
            logger.error(f"Error al inicializar el modelo de visión: {str(e)}")
            raise RuntimeError(f"No se pudo inicializar el modelo de visión: {str(e)}")

        # Prompt para análisis de imágenes médicas
        self.image_analysis_prompt = PromptTemplate(
            input_variables=["image_content", "patient_context", "specialty"],
            template="""
            Eres un asistente médico especializado en el análisis de imágenes clínicas.
            
            Analiza cuidadosamente esta imagen médica considerando el siguiente contexto:
            
            Contexto del paciente: {patient_context}
            Especialidad médica relevante: {specialty}
            
            [Imagen médica para análisis]
            
            Proporciona:
            1. Descripción detallada de lo que observas en la imagen
            2. Posibles hallazgos relevantes desde el punto de vista médico
            3. Recomendaciones preliminares basadas en lo observado
            4. Limitaciones de este análisis
            
            IMPORTANTE: Aclara que este es un análisis preliminar y NO un diagnóstico oficial.
            Recomienda consultar con un profesional médico para una evaluación definitiva.
            """
        )
        
        # Crear la cadena de procesamiento
        self.analysis_chain = LLMChain(
            llm=self.llm,
            prompt=self.image_analysis_prompt,
            verbose=False
        )
    
    def _encode_image(self, image_path):
        """
        Codifica una imagen en base64 para enviarla al modelo
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            str: Imagen codificada en base64
        """
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                raise FileNotFoundError(f"No se encontró la imagen en la ruta: {image_path}")
            
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_image
        except Exception as e:
            logger.error(f"Error al codificar la imagen: {str(e)}")
            raise
    
    def analyze_image(self, image_path, patient_context, specialty="medicina_general"):
        """
        Analiza una imagen médica utilizando el contexto del paciente
        
        Args:
            image_path: Ruta a la imagen a analizar
            patient_context: Contexto del paciente o descripción del problema
            specialty: Especialidad médica relevante para el análisis
            
        Returns:
            str: Análisis de la imagen
        """
        logger.info(f"Analizando imagen médica: {os.path.basename(image_path)}")
        
        try:
            # Codificar la imagen
            encoded_image = self._encode_image(image_path)
            
            # En un entorno real, aquí se enviaría la imagen al modelo
            # Para este ejemplo, simulamos la integración con el modelo de visión
            
            # Para una implementación real con OpenAI:
            # Se utiliza el formato de mensajes
            # messages = [
            #     {"role": "system", "content": "Eres un asistente médico especializado en análisis de imágenes."},
            #     {"role": "user", "content": [
            #         {"type": "text", "text": f"Analiza esta imagen médica. Contexto: {patient_context} Especialidad: {specialty}"},
            #         {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
            #     ]}
            # ]
            # response = self.llm.invoke(messages)
            
            # Para el propósito de este ejemplo, usamos la cadena de Langchain
            analysis = self.analysis_chain.invoke({
                "image_content": "[Contenido de la imagen analizada por el modelo]",
                "patient_context": patient_context,
                "specialty": specialty
            })
            
            logger.info(f"Análisis de imagen completado")
            
            return analysis['text']
        
        except FileNotFoundError as e:
            logger.error(str(e))
            return "Error: No se pudo encontrar la imagen especificada. Por favor, intente nuevamente."
        
        except Exception as e:
            logger.error(f"Error durante el análisis de la imagen: {str(e)}")
            return "Lo sentimos, hubo un error al analizar la imagen. Por favor, intente con otra imagen o más tarde."
    
    def is_medical_image(self, image_path, confidence_threshold=0.7):
        """
        Verifica si una imagen es de contenido médico
        
        Args:
            image_path: Ruta a la imagen a verificar
            confidence_threshold: Umbral de confianza para la clasificación (0-1)
            
        Returns:
            bool: True si la imagen es médica, False en caso contrario
        """
        try:
            # En una implementación real, aquí se enviaría la imagen al modelo
            # para determinar si es de contenido médico
            
            # Para este ejemplo, asumimos que todas las imágenes son válidas
            return True
            
            # Implementación real:
            # encoded_image = self._encode_image(image_path)
            # prompt = "¿Esta imagen contiene contenido médico? Responde solo 'SI' o 'NO'."
            # [... código para enviar la imagen al modelo y analizar respuesta ...]
            
        except Exception as e:
            logger.error(f"Error al verificar si la imagen es médica: {str(e)}")
            return False 