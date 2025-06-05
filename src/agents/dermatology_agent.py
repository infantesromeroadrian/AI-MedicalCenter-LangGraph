from typing import Dict, List, Any, Optional

from src.agents.base_agent import BaseMedicalAgent
from src.services.llm_service import LLMService

class DermatologyAgent(BaseMedicalAgent):
    """Agent specialized in dermatology and skin conditions."""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """Initialize the dermatology agent."""
        super().__init__(specialty="dermatology", llm_service=llm_service)
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt specific to dermatology."""
        return """Eres un dermatólogo especializado en enfermedades de la piel, cabello, uñas y mucosas.

COMPORTAMIENTO CRUCIAL: Debes emular el comportamiento de un dermatólogo real en consulta:

1. ENFOQUE DERMATOLÓGICO ESPECÍFICO:
   - Realiza una anamnesis dermatológica detallada
   - Evalúa las características morfológicas de las lesiones cutáneas
   - Considera factores ambientales, ocupacionales y genéticos
   - Valora el impacto psicosocial de las condiciones dermatológicas

2. ESTRUCTURA DE CONSULTA DERMATOLÓGICA:
   - Saludo y establecimiento de confianza para el examen físico
   - Historia de la enfermedad actual:
     * Tiempo de evolución de las lesiones
     * Localización inicial y progresión
     * Síntomas asociados (prurito, dolor, ardor)
     * Factores desencadenantes o agravantes
   - Antecedentes dermatológicos personales y familiares
   - Exposición solar y hábitos de fotoprotección
   - Medicamentos y productos cosméticos utilizados

3. DESCRIPCIÓN DE LESIONES DERMATOLÓGICAS:
   - Lesiones primarias: mácula, pápula, nódulo, vesícula, ampolla, pústula
   - Lesiones secundarias: escama, costra, erosión, úlcera, cicatriz
   - Distribución: localizada, generalizada, simétrica, asimétrica
   - Morfología: forma, bordes, color, textura, tamaño
   - Patrón de distribución: dermatomos, áreas fotoexpuestas, pliegues

4. PRINCIPALES CONDICIONES DERMATOLÓGICAS:
   - Dermatitis: atópica, de contacto, seborreica, numular
   - Psoriasis: en placas, guttata, inversa, palmoplantar
   - Infecciones: bacterianas, fúngicas, virales, parasitarias
   - Acné: comedogénico, inflamatorio, conglobata, rosácea
   - Cáncer de piel: carcinoma basocelular, espinocelular, melanoma
   - Enfermedades autoinmunes: lupus, pénfigo, penfigoide
   - Trastornos de pigmentación: vitíligo, melasma, hiperpigmentación

5. TRATAMIENTOS DERMATOLÓGICOS:
   - Tópicos: corticosteroides, retinoides, antibióticos, antifúngicos
   - Sistémicos: antibióticos, antihistamínicos, inmunosupresores
   - Procedimientos: biopsia, criocirugía, electrocirugía, láser
   - Fototerapia: UVB, PUVA, luz LED
   - Terapias biológicas para condiciones severas

6. MEDICINA COSMÉTICA Y ESTÉTICA:
   - Tratamientos antienvejecimiento
   - Manejo de cicatrices y estrías
   - Tratamientos para hiperpigmentación
   - Procedimientos mínimamente invasivos
   - Cuidados de la piel preventivos

7. DERMATOLOGÍA PEDIÁTRICA:
   - Dermatitis del pañal
   - Hemangiomas y malformaciones vasculares
   - Nevos congénitos
   - Dermatitis atópica infantil
   - Infecciones cutáneas pediátricas

8. FOTOPROTECCIÓN Y PREVENCIÓN:
   - Educación sobre protección solar
   - Autoexamen de lunares y lesiones
   - Detección temprana de cáncer de piel
   - Cuidados preventivos según tipo de piel

IMPORTANTE:
- Siempre enfatiza la importancia del examen físico directo para el diagnóstico definitivo
- Explica cuándo una lesión requiere evaluación dermatológica urgente
- Proporciona consejos de cuidado de la piel apropiados para cada condición
- Aborda tanto aspectos médicos como estéticos de las condiciones dermatológicas
- Considera el impacto psicológico de las enfermedades de la piel

Al final de tu respuesta, incluye una sección "Recomendaciones:" con consejos sobre cuidado de la piel, tratamientos recomendados, prevención y cuándo buscar atención especializada."""
    
    def _evaluate_confidence(self, query: str, response: str) -> float:
        """
        Evaluate the confidence for dermatology-related queries.
        Override base implementation to check for dermatology-specific keywords.
        """
        base_confidence = super()._evaluate_confidence(query, response)
        
        # Check for dermatology-related keywords to potentially increase confidence
        dermatology_keywords = [
            "skin", "rash", "dermatitis", "eczema", "psoriasis", "acne", "mole",
            "lesion", "dermatology", "itching", "burning", "scaling", "redness",
            "blistering", "hives", "urticaria", "melanoma", "basal cell", "squamous cell",
            "fungal infection", "bacterial infection", "viral infection", "warts",
            # Spanish keywords
            "piel", "sarpullido", "dermatitis", "eccema", "psoriasis", "acné", "lunar",
            "lesión", "dermatología", "picazón", "ardor", "descamación", "enrojecimiento",
            "ampollas", "urticaria", "melanoma", "carcinoma basocelular", "carcinoma espinocelular",
            "infección fúngica", "infección bacteriana", "infección viral", "verrugas",
            "dermatólogo", "dermatológico"
        ]
        
        # Skin conditions
        skin_conditions = [
            "atopic dermatitis", "contact dermatitis", "seborrheic dermatitis",
            "plaque psoriasis", "guttate psoriasis", "pustular psoriasis",
            "tinea corporis", "tinea pedis", "tinea versicolor", "candidiasis",
            "impetigo", "cellulitis", "herpes simplex", "herpes zoster", "molluscum",
            # Spanish skin conditions
            "dermatitis atópica", "dermatitis de contacto", "dermatitis seborreica",
            "psoriasis en placas", "psoriasis guttata", "psoriasis pustular",
            "tiña corporal", "pie de atleta", "tiña versicolor", "candidiasis",
            "impétigo", "celulitis", "herpes simple", "herpes zóster"
        ]
        
        # Skin symptoms
        skin_symptoms = [
            "itchy", "scaly", "dry skin", "oily skin", "sensitive skin", "rough skin",
            "bumps", "patches", "spots", "discoloration", "pigmentation", "hair loss",
            "nail changes", "brittle nails", "thick nails",
            # Spanish skin symptoms  
            "picazón", "escamoso", "piel seca", "piel grasa", "piel sensible", "piel áspera",
            "protuberancias", "manchas", "decoloración", "pigmentación", "pérdida de cabello",
            "cambios en las uñas", "uñas quebradizas", "uñas gruesas"
        ]
        
        # Count dermatology keywords in query
        keyword_count = sum(1 for keyword in dermatology_keywords if keyword.lower() in query.lower())
        condition_count = sum(1 for condition in skin_conditions if condition.lower() in query.lower())
        symptom_count = sum(1 for symptom in skin_symptoms if symptom.lower() in query.lower())
        
        # Increase confidence based on keyword matches
        confidence_boost = min(0.4, (keyword_count * 0.08) + (condition_count * 0.12) + (symptom_count * 0.06))
        adjusted_confidence = base_confidence + confidence_boost
        
        # Ensure confidence stays in range [0.1, 1.0]
        return max(0.1, min(1.0, adjusted_confidence)) 