"""
Sistema expandido de knowledge base médico para agentes especializados.
Contiene información detallada sobre diagnósticos, tratamientos y procedimientos.
"""
import json
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class MedicalCondition:
    """Información sobre una condición médica."""
    name: str
    icd_codes: List[str]
    symptoms: List[str]
    risk_factors: List[str]
    differential_diagnosis: List[str]
    treatments: List[str]
    medications: List[str]
    procedures: List[str]
    prognosis: str
    red_flags: List[str]
    specialty: str

@dataclass
class MedicalProcedure:
    """Información sobre un procedimiento médico."""
    name: str
    cpt_codes: List[str]
    indications: List[str]
    contraindications: List[str]
    complications: List[str]
    preparation: str
    procedure_steps: List[str]
    post_procedure_care: List[str]
    specialty: str

@dataclass
class Medication:
    """Información sobre medicamentos."""
    name: str
    generic_name: str
    drug_class: str
    indications: List[str]
    contraindications: List[str]
    side_effects: List[str]
    dosage: Dict[str, str]
    interactions: List[str]
    monitoring: List[str]
    specialty_specific_notes: str

class MedicalKnowledgeBase:
    """Sistema expandido de knowledge base médico."""
    
    def __init__(self):
        """Inicializar el knowledge base."""
        self.conditions: Dict[str, Dict[str, MedicalCondition]] = {}
        self.procedures: Dict[str, Dict[str, MedicalProcedure]] = {}
        self.medications: Dict[str, Dict[str, Medication]] = {}
        self.specialty_guidelines: Dict[str, Dict[str, Any]] = {}
        
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Cargar toda la información del knowledge base."""
        self._load_cardiology_knowledge()
        self._load_neurology_knowledge()
        self._load_pediatrics_knowledge()
        self._load_oncology_knowledge()
        self._load_dermatology_knowledge()
        self._load_psychiatry_knowledge()
        self._load_emergency_medicine_knowledge()
        self._load_internal_medicine_knowledge()
        
        logger.info("Medical knowledge base loaded successfully")
    
    def _load_cardiology_knowledge(self):
        """Cargar knowledge base de cardiología."""
        
        # Condiciones cardiológicas
        cardiology_conditions = {
            "myocardial_infarction": MedicalCondition(
                name="Infarto Agudo de Miocardio",
                icd_codes=["I21.9", "I22.9"],
                symptoms=[
                    "Dolor torácico opresivo", "Dolor irradiado a brazo izquierdo",
                    "Disnea", "Sudoración profusa", "Náuseas", "Vómitos",
                    "Sensación de muerte inminente", "Palidez"
                ],
                risk_factors=[
                    "Hipertensión arterial", "Diabetes mellitus", "Dislipidemia",
                    "Tabaquismo", "Obesidad", "Sedentarismo", "Antecedentes familiares",
                    "Edad avanzada", "Sexo masculino"
                ],
                differential_diagnosis=[
                    "Angina inestable", "Pericarditis", "Disección aórtica",
                    "Embolia pulmonar", "Neumotórax", "Esofagitis", "Costocondritis"
                ],
                treatments=[
                    "Revascularización percutánea urgente", "Trombólisis",
                    "Doble antiagregación", "Anticoagulación", "Beta-bloqueantes",
                    "IECA/ARA-II", "Estatinas", "Control de factores de riesgo"
                ],
                medications=[
                    "Aspirina", "Clopidogrel", "Atorvastatina", "Metoprolol",
                    "Enalapril", "Heparina", "Nitroglicerina"
                ],
                procedures=[
                    "Angioplastia coronaria", "Stent coronario", "Bypass coronario",
                    "Cateterismo cardíaco", "Ecocardiograma", "ECG seriados"
                ],
                prognosis="Variable según extensión, tiempo de revascularización y complicaciones",
                red_flags=[
                    "Shock cardiogénico", "Arritmias malignas", "Ruptura cardíaca",
                    "Insuficiencia mitral aguda", "Defecto septal ventricular"
                ],
                specialty="cardiology"
            ),
            
            "heart_failure": MedicalCondition(
                name="Insuficiencia Cardíaca",
                icd_codes=["I50.9", "I50.1"],
                symptoms=[
                    "Disnea de esfuerzo", "Ortopnea", "Disnea paroxística nocturna",
                    "Edema en miembros inferiores", "Fatiga", "Intolerancia al ejercicio",
                    "Tos nocturna", "Palpitaciones"
                ],
                risk_factors=[
                    "Cardiopatía isquémica", "Hipertensión arterial", "Diabetes",
                    "Valvulopatías", "Miocardiopatías", "Arritmias", "Edad avanzada"
                ],
                differential_diagnosis=[
                    "Enfermedad pulmonar", "Anemia", "Insuficiencia renal",
                    "Trastornos tiroideos", "Síndrome nefrótico"
                ],
                treatments=[
                    "IECA/ARA-II", "Beta-bloqueantes", "Diuréticos",
                    "Antagonistas de aldosterona", "Control de líquidos",
                    "Ejercicio supervisado", "Dispositivos implantables"
                ],
                medications=[
                    "Enalapril", "Carvedilol", "Furosemida", "Espironolactona",
                    "Digoxina", "Sacubitrilo/Valsartán"
                ],
                procedures=[
                    "Ecocardiograma", "Cateterismo cardíaco", "Resincronización",
                    "Desfibrilador implantable", "Trasplante cardíaco"
                ],
                prognosis="Variable, mejor con tratamiento óptimo y adherencia",
                red_flags=[
                    "Edema pulmonar agudo", "Shock cardiogénico",
                    "Arritmias sintomáticas", "Síncope"
                ],
                specialty="cardiology"
            )
        }
        
        # Procedimientos cardiológicos
        cardiology_procedures = {
            "cardiac_catheterization": MedicalProcedure(
                name="Cateterismo Cardíaco",
                cpt_codes=["93458", "93459"],
                indications=[
                    "Síndrome coronario agudo", "Angina refractaria",
                    "Valvulopatía severa", "Insuficiencia cardíaca"
                ],
                contraindications=[
                    "Infección activa", "Alergia a contraste", "Insuficiencia renal severa",
                    "Alteraciones de coagulación no corregidas"
                ],
                complications=[
                    "Sangrado en sitio de punción", "Hematoma", "Disección coronaria",
                    "Arritmias", "Embolia", "Nefropatía por contraste"
                ],
                preparation="Ayuno 6-8 horas, suspender metformina, hidratación",
                procedure_steps=[
                    "Acceso vascular", "Inserción de catéter", "Inyección de contraste",
                    "Obtención de imágenes", "Medición de presiones"
                ],
                post_procedure_care=[
                    "Reposo en cama 4-6 horas", "Control de sangrado",
                    "Hidratación", "Monitoreo de función renal"
                ],
                specialty="cardiology"
            )
        }
        
        # Medicamentos cardiológicos
        cardiology_medications = {
            "atorvastatin": Medication(
                name="Atorvastatina",
                generic_name="atorvastatin",
                drug_class="Estatina (inhibidor HMG-CoA reductasa)",
                indications=[
                    "Hipercolesterolemia", "Prevención cardiovascular primaria y secundaria",
                    "Síndrome coronario agudo"
                ],
                contraindications=[
                    "Enfermedad hepática activa", "Embarazo", "Lactancia",
                    "Hipersensibilidad conocida"
                ],
                side_effects=[
                    "Mialgia", "Elevación de transaminasas", "Rabdomiólisis (raro)",
                    "Cefalea", "Náuseas", "Estreñimiento"
                ],
                dosage={
                    "inicial": "20-40 mg/día",
                    "mantenimiento": "20-80 mg/día",
                    "máxima": "80 mg/día"
                },
                interactions=[
                    "Ciclosporina", "Gemfibrozilo", "Inhibidores CYP3A4",
                    "Warfarina", "Digoxina"
                ],
                monitoring=[
                    "Perfil lipídico a 4-6 semanas", "Transaminasas basales y a 12 semanas",
                    "CK si síntomas musculares"
                ],
                specialty_specific_notes="Iniciar dentro de 24-96h post-SCA independiente de niveles de colesterol"
            )
        }
        
        self.conditions["cardiology"] = cardiology_conditions
        self.procedures["cardiology"] = cardiology_procedures
        self.medications["cardiology"] = cardiology_medications
    
    def _load_neurology_knowledge(self):
        """Cargar knowledge base de neurología."""
        
        neurology_conditions = {
            "stroke": MedicalCondition(
                name="Accidente Cerebrovascular",
                icd_codes=["I64", "I63.9"],
                symptoms=[
                    "Hemiparesia súbita", "Afasia", "Disartria", "Alteración visual",
                    "Cefalea súbita severa", "Vértigo", "Alteración de conciencia"
                ],
                risk_factors=[
                    "Hipertensión", "Fibrilación auricular", "Diabetes",
                    "Dislipidemia", "Tabaquismo", "Edad", "Anticonceptivos orales"
                ],
                differential_diagnosis=[
                    "Crisis epiléptica", "Hipoglucemia", "Migraña hemipléjica",
                    "Tumor cerebral", "Intoxicación"
                ],
                treatments=[
                    "Trombólisis IV", "Trombectomía mecánica", "Antiagregación",
                    "Control de presión arterial", "Neurorehabilitación"
                ],
                medications=[
                    "Alteplase", "Aspirina", "Clopidogrel", "Atorvastatina"
                ],
                procedures=[
                    "TC craneal", "RM cerebral", "Angio-TC", "Trombectomía",
                    "Doppler carotídeo"
                ],
                prognosis="Depende del tiempo hasta tratamiento y extensión de lesión",
                red_flags=[
                    "Deterioro neurológico", "Edema cerebral", "Transformación hemorrágica"
                ],
                specialty="neurology"
            ),
            
            "epilepsy": MedicalCondition(
                name="Epilepsia",
                icd_codes=["G40.9", "G40.1"],
                symptoms=[
                    "Crisis convulsivas recurrentes", "Pérdida de conciencia",
                    "Movimientos tónico-clónicos", "Automatismos", "Confusión post-ictal"
                ],
                risk_factors=[
                    "Antecedentes familiares", "Trauma craneal", "Infecciones SNC",
                    "Tumores cerebrales", "Malformaciones vasculares"
                ],
                differential_diagnosis=[
                    "Síncope", "Crisis psicógenas", "Migraña", "Trastornos metabólicos"
                ],
                treatments=[
                    "Antiepilépticos", "Cirugía epilepsia", "Estimulación vagal",
                    "Dieta cetogénica"
                ],
                medications=[
                    "Levetiracetam", "Valproato", "Carbamazepina", "Fenitoína"
                ],
                procedures=[
                    "EEG", "RM cerebral", "Video-EEG", "PET cerebral"
                ],
                prognosis="70% control con medicación apropiada",
                red_flags=[
                    "Status epilepticus", "Crisis febriles complejas",
                    "Deterioro cognitivo progresivo"
                ],
                specialty="neurology"
            )
        }
        
        self.conditions["neurology"] = neurology_conditions
    
    def _load_pediatrics_knowledge(self):
        """Cargar knowledge base de pediatría."""
        
        pediatrics_conditions = {
            "bronchiolitis": MedicalCondition(
                name="Bronquiolitis",
                icd_codes=["J21.9"],
                symptoms=[
                    "Tos seca", "Dificultad respiratoria", "Fiebre", "Rinorrea",
                    "Sibilancias", "Irritabilidad", "Dificultad alimentación"
                ],
                risk_factors=[
                    "Edad < 2 años", "Época invernal", "Exposición a tabaco",
                    "Guarderías", "Prematuridad", "Cardiopatía congénita"
                ],
                differential_diagnosis=[
                    "Asma", "Neumonía", "Aspiración cuerpo extraño",
                    "Insuficiencia cardíaca"
                ],
                treatments=[
                    "Soporte respiratorio", "Hidratación", "Oxigenoterapia",
                    "Aspiración secreciones"
                ],
                medications=[
                    "Broncodilatadores (controvertido)", "Corticoides (no recomendados)",
                    "Solución salina hipertónica"
                ],
                procedures=[
                    "Radiografía tórax", "Saturometría", "Aspirado nasofaríngeo"
                ],
                prognosis="Generalmente autolimitada, resolución en 7-10 días",
                red_flags=[
                    "Apneas", "Cianosis", "Rechazo alimentación",
                    "Signos deshidratación"
                ],
                specialty="pediatrics"
            )
        }
        
        self.conditions["pediatrics"] = pediatrics_conditions
    
    def _load_oncology_knowledge(self):
        """Cargar knowledge base de oncología."""
        
        oncology_conditions = {
            "lung_cancer": MedicalCondition(
                name="Cáncer de Pulmón",
                icd_codes=["C78.0", "C34.1"],
                symptoms=[
                    "Tos persistente", "Hemoptisis", "Disnea", "Dolor torácico",
                    "Pérdida de peso", "Fatiga", "Ronquera"
                ],
                risk_factors=[
                    "Tabaquismo", "Exposición radón", "Asbesto", "Contaminación",
                    "Antecedentes familiares", "EPOC", "Fibrosis pulmonar"
                ],
                differential_diagnosis=[
                    "Neumonía", "Tuberculosis", "Metástasis pulmonar",
                    "Sarcoidosis", "Embolia pulmonar"
                ],
                treatments=[
                    "Cirugía", "Quimioterapia", "Radioterapia", "Inmunoterapia",
                    "Terapias dirigidas", "Cuidados paliativos"
                ],
                medications=[
                    "Cisplatino", "Carboplatin", "Pembrolizumab", "Erlotinib"
                ],
                procedures=[
                    "TC tórax", "PET-CT", "Broncoscopia", "Biopsia",
                    "Mediastinoscopia"
                ],
                prognosis="Variable según estadio y tipo histológico",
                red_flags=[
                    "Síndrome vena cava superior", "Derrame pleural maligno",
                    "Metástasis cerebrales"
                ],
                specialty="oncology"
            )
        }
        
        self.conditions["oncology"] = oncology_conditions
    
    def _load_dermatology_knowledge(self):
        """Cargar knowledge base de dermatología."""
        
        dermatology_conditions = {
            "atopic_dermatitis": MedicalCondition(
                name="Dermatitis Atópica",
                icd_codes=["L20.9"],
                symptoms=[
                    "Prurito intenso", "Eritema", "Descamación", "Vesículas",
                    "Liquenificación", "Xerosis", "Fisuras"
                ],
                risk_factors=[
                    "Antecedentes familiares atopia", "Asma", "Rinitis alérgica",
                    "Mutaciones filagrina", "Factores ambientales"
                ],
                differential_diagnosis=[
                    "Dermatitis seborreica", "Psoriasis", "Dermatitis contacto",
                    "Escabiosis", "Dishidrosis"
                ],
                treatments=[
                    "Corticoides tópicos", "Inhibidores calcineurina",
                    "Hidratación", "Antihistamínicos", "Biológicos"
                ],
                medications=[
                    "Hidrocortisona", "Tacrolimus", "Dupilumab", "Cetirizina"
                ],
                procedures=[
                    "Biopsia cutánea", "Pruebas alergia", "Fototerapia"
                ],
                prognosis="Crónica con exacerbaciones y remisiones",
                red_flags=[
                    "Infección secundaria", "Eccema herpeticum",
                    "Eritrodermia"
                ],
                specialty="dermatology"
            )
        }
        
        self.conditions["dermatology"] = dermatology_conditions
    
    def _load_psychiatry_knowledge(self):
        """Cargar knowledge base de psiquiatría."""
        
        psychiatry_conditions = {
            "major_depression": MedicalCondition(
                name="Trastorno Depresivo Mayor",
                icd_codes=["F32.9", "F33.9"],
                symptoms=[
                    "Estado ánimo deprimido", "Anhedonia", "Pérdida peso",
                    "Insomnio/hipersomnia", "Fatiga", "Sentimientos culpa",
                    "Dificultad concentración", "Ideas muerte"
                ],
                risk_factors=[
                    "Antecedentes familiares", "Eventos vitales estresantes",
                    "Enfermedades médicas", "Abuso sustancias", "Género femenino"
                ],
                differential_diagnosis=[
                    "Trastorno bipolar", "Distimia", "Trastorno adaptativo",
                    "Hipotiroidismo", "Anemia"
                ],
                treatments=[
                    "Antidepresivos", "Psicoterapia", "TEC", "Activación conductual"
                ],
                medications=[
                    "Sertralina", "Escitalopram", "Venlafaxina", "Bupropión"
                ],
                procedures=[
                    "Evaluación psiquiátrica", "Escalas depresión", "TEC"
                ],
                prognosis="Buena respuesta con tratamiento adecuado",
                red_flags=[
                    "Ideación suicida", "Síntomas psicóticos",
                    "Catatonia", "Deterioro funcional severo"
                ],
                specialty="psychiatry"
            )
        }
        
        self.conditions["psychiatry"] = psychiatry_conditions
    
    def _load_emergency_medicine_knowledge(self):
        """Cargar knowledge base de medicina de emergencia."""
        
        emergency_conditions = {
            "sepsis": MedicalCondition(
                name="Sepsis",
                icd_codes=["A41.9"],
                symptoms=[
                    "Fiebre >38°C o <36°C", "Taquicardia", "Taquipnea",
                    "Alteración mental", "Hipotensión", "Oliguria"
                ],
                risk_factors=[
                    "Inmunocompromiso", "Edad extremas", "Dispositivos invasivos",
                    "Hospitalización prolongada", "Cirugía reciente"
                ],
                differential_diagnosis=[
                    "SIRS no infeccioso", "Shock cardiogénico", "Embolia pulmonar"
                ],
                treatments=[
                    "Antibióticos empíricos", "Reanimación líquidos",
                    "Vasopresores", "Control foco infeccioso"
                ],
                medications=[
                    "Ceftriaxona", "Vancomicina", "Noradrenalina", "Dobutamina"
                ],
                procedures=[
                    "Hemocultivos", "Lactato", "PCT", "Ecocardiograma"
                ],
                prognosis="Mortalidad 20-40% según severidad",
                red_flags=[
                    "Shock séptico", "Falla orgánica múltiple",
                    "Lactato >4 mmol/L"
                ],
                specialty="emergency_medicine"
            )
        }
        
        self.conditions["emergency_medicine"] = emergency_conditions
    
    def _load_internal_medicine_knowledge(self):
        """Cargar knowledge base de medicina interna."""
        
        internal_medicine_conditions = {
            "diabetes_type2": MedicalCondition(
                name="Diabetes Mellitus Tipo 2",
                icd_codes=["E11.9"],
                symptoms=[
                    "Poliuria", "Polidipsia", "Polifagia", "Pérdida peso",
                    "Fatiga", "Visión borrosa", "Infecciones recurrentes"
                ],
                risk_factors=[
                    "Obesidad", "Sedentarismo", "Antecedentes familiares",
                    "Edad >45 años", "Hipertensión", "Dislipidemia"
                ],
                differential_diagnosis=[
                    "Diabetes tipo 1", "MODY", "Diabetes gestacional",
                    "Diabetes secundaria"
                ],
                treatments=[
                    "Metformina", "Insulina", "Cambios estilo vida",
                    "Control factores riesgo cardiovascular"
                ],
                medications=[
                    "Metformina", "Glibenclamida", "Sitagliptina", "Insulina"
                ],
                procedures=[
                    "HbA1c", "Glucemia ayunas", "PTOG", "Microalbuminuria"
                ],
                prognosis="Buena con control glucémico adecuado",
                red_flags=[
                    "Cetoacidosis", "Coma hiperosmolar",
                    "Hipoglucemia severa", "Complicaciones microvasculares"
                ],
                specialty="internal_medicine"
            )
        }
        
        self.conditions["internal_medicine"] = internal_medicine_conditions
    
    def get_condition_info(self, specialty: str, condition_name: str) -> Optional[MedicalCondition]:
        """Obtener información de una condición específica."""
        return self.conditions.get(specialty, {}).get(condition_name)
    
    def get_procedure_info(self, specialty: str, procedure_name: str) -> Optional[MedicalProcedure]:
        """Obtener información de un procedimiento específico."""
        return self.procedures.get(specialty, {}).get(procedure_name)
    
    def get_medication_info(self, specialty: str, medication_name: str) -> Optional[Medication]:
        """Obtener información de un medicamento específico."""
        return self.medications.get(specialty, {}).get(medication_name)
    
    def search_conditions_by_symptoms(self, symptoms: List[str], specialty: Optional[str] = None) -> List[MedicalCondition]:
        """Buscar condiciones que coincidan con síntomas dados."""
        results = []
        
        specialties_to_search = [specialty] if specialty else self.conditions.keys()
        
        for spec in specialties_to_search:
            if spec in self.conditions:
                for condition in self.conditions[spec].values():
                    # Verificar coincidencias de síntomas
                    matching_symptoms = 0
                    for symptom in symptoms:
                        for condition_symptom in condition.symptoms:
                            if symptom.lower() in condition_symptom.lower():
                                matching_symptoms += 1
                                break
                    
                    # Si hay al menos 1 síntoma coincidente, incluir
                    if matching_symptoms > 0:
                        results.append(condition)
        
        # Ordenar por número de síntomas coincidentes
        return sorted(results, key=lambda c: len([s for s in symptoms if any(s.lower() in cs.lower() for cs in c.symptoms)]), reverse=True)
    
    def get_specialty_overview(self, specialty: str) -> Dict[str, Any]:
        """Obtener resumen completo de una especialidad."""
        return {
            "conditions_count": len(self.conditions.get(specialty, {})),
            "procedures_count": len(self.procedures.get(specialty, {})),
            "medications_count": len(self.medications.get(specialty, {})),
            "common_conditions": list(self.conditions.get(specialty, {}).keys())[:5],
            "common_procedures": list(self.procedures.get(specialty, {}).keys())[:5],
        }
    
    def get_differential_diagnosis(self, specialty: str, primary_condition: str) -> List[str]:
        """Obtener diagnósticos diferenciales para una condición."""
        condition = self.get_condition_info(specialty, primary_condition)
        return condition.differential_diagnosis if condition else []
    
    def get_red_flags(self, specialty: str, condition_name: str) -> List[str]:
        """Obtener banderas rojas para una condición."""
        condition = self.get_condition_info(specialty, condition_name)
        return condition.red_flags if condition else []


# Instancia global del knowledge base
medical_kb = MedicalKnowledgeBase() 