# 📋 Sistema de Recursos Médicos

## **🎯 Descripción General**

El sistema de recursos médicos permite a los usuarios acceder, gestionar y visualizar información médica organizada y extraída automáticamente de sus consultas. Esta funcionalidad convierte el panel lateral del chat en un centro de control médico interactivo.

## **🏗️ Arquitectura del Sistema**

### **Componentes Principales**

```
Frontend (Interactive Chat)
├── Panel de Recursos Médicos (HTML/CSS/JS)
├── Modales de Visualización 
├── Extractores de Información (JavaScript)
└── Actualización en Tiempo Real

Backend (Flask)
├── medical_resources_controller.py
├── Endpoints API REST
├── Extractores de Información (Python)
└── Integración con ConversationService
```

---

## **📊 Funcionalidades Implementadas**

### **1. 💊 Medicamentos Recetados**
- **Extracción automática** de medicamentos mencionados en consultas
- **Información detallada**: nombre, dosis, frecuencia, duración
- **Visualización en tabla** con formato médico profesional
- **Contadores dinámicos** que se actualizan en tiempo real

**Patrones de detección:**
- "Receto [medicamento] [dosis] [unidad]"
- "Tome [medicamento] cada [frecuencia]"
- Medicamentos comunes: paracetamol, ibuprofeno, etc.

### **2. 📋 Historial de Consultas**
- **Timeline visual** de todas las consultas realizadas
- **Información por consulta**: especialidad, fecha, duración, resumen
- **Estado de consultas**: en curso, completadas
- **Navegación temporal** con indicadores visuales

**Métricas calculadas:**
- Duración estimada basada en número de mensajes
- Resumen automático del motivo de consulta
- Estado basado en completitud de la conversación

### **3. 🧪 Resultados de Laboratorio**
- **Detección automática** de exámenes mencionados
- **Valores de referencia** incluidos automáticamente
- **Estados visuales**: normal, anormal, pendiente
- **Tarjetas organizadas** por tipo de examen

**Exámenes soportados:**
- Glucosa, Colesterol, Hemograma
- Creatinina, Transaminasas, TSH
- Detección contextual de estados anormales

### **4. 🖼️ Imágenes Diagnósticas**
- **Galería de imágenes** subidas durante consultas
- **Análisis asociado** de cada imagen
- **Visualización en pantalla completa**
- **Descarga individual** de imágenes
- **Integración con análisis IA**

---

## **🔧 Implementación Técnica**

### **Frontend - Estructura HTML**

```html
<!-- Panel interactivo -->
<li class="medical-resource-item" data-resource="medications" style="cursor: pointer;">
    <div class="d-flex align-items-center">
        <i class="fas fa-pills medical-icon"></i>
        <span>Medicamentos recetados</span>
    </div>
    <span class="badge bg-primary" id="medications-count">0</span>
</li>
```

### **CSS - Efectos Visuales**

```css
.medical-resource-item:hover {
    background-color: #f8f9fa;
    border-left: 3px solid var(--primary-color);
    transform: translateX(2px);
}
```

### **JavaScript - Extracción de Datos**

```javascript
function extractMedicationsFromConversation() {
    const medications = [];
    const messages = document.querySelectorAll('.message-content');
    
    messages.forEach(message => {
        const text = message.textContent.toLowerCase();
        const medicationPatterns = [
            /(?:receto|prescribo|tome|tomar)\s+([a-zA-Záéíóúñ\s]+)/gi
        ];
        // ... lógica de extracción
    });
    
    return medications;
}
```

### **Backend - API Endpoints**

```python
@medical_resources_bp.route('/medications/<conversation_id>', methods=['GET'])
@login_required
def get_medications(conversation_id):
    conversation = conversation_service.get_conversation(conversation_id)
    medications = extract_medications_from_conversation(conversation)
    
    return jsonify({
        'success': True,
        'medications': medications,
        'count': len(medications)
    })
```

---

## **📡 API Endpoints Disponibles**

| **Endpoint** | **Método** | **Descripción** |
|---|---|---|
| `/medical-resources/medications/<id>` | GET | Obtener medicamentos de una consulta |
| `/medical-resources/consultations` | GET | Obtener historial completo de consultas |
| `/medical-resources/lab-results/<id>` | GET | Obtener resultados de laboratorio |
| `/medical-resources/diagnostic-images/<id>` | GET | Obtener imágenes de una consulta |
| `/medical-resources/summary/<id>` | GET | Obtener resumen médico completo |

### **Respuesta de Ejemplo - Medicamentos**

```json
{
    "success": true,
    "medications": [
        {
            "name": "Paracetamol",
            "dose": "500 mg",
            "frequency": "Cada 8 horas",
            "duration": "7 días",
            "instructions": "Seguir indicaciones del médico",
            "prescribed_date": "2024-01-15T10:30:00Z"
        }
    ],
    "count": 1
}
```

---

## **🎨 Experiencia de Usuario**

### **Interacciones Disponibles**

1. **Hover Effects**: Animaciones suaves al pasar sobre elementos
2. **Badges Dinámicos**: Contadores que se actualizan automáticamente
3. **Modales Informativos**: Visualización detallada de cada recurso
4. **Tooltips**: Información contextual en tiempo real
5. **Exportación**: Descarga de datos en diversos formatos

### **Estados Visuales**

- **🔵 Azul**: Medicamentos (Primary)
- **🟢 Verde**: Consultas/Historial (Success)
- **🟡 Amarillo**: Laboratorios (Warning)
- **🔵 Cian**: Imágenes (Info)

### **Feedback en Tiempo Real**

- Contadores actualizados cada segundo
- Animaciones de carga durante procesamientos
- Estados de error con mensajes informativos
- Confirmaciones visuales de acciones

---

## **🔍 Algoritmos de Extracción**

### **Medicamentos**
```python
medication_patterns = [
    r'(?:receto|prescribo|tome|tomar)\s+([a-zA-Záéíóúñ\s]+)\s+(?:(\d+(?:\.\d+)?)\s*(mg|g|ml))',
    r'(?:medicamento|fármaco|medicina):\s*([a-zA-Záéíóúñ\s]+)',
    r'(?:paracetamol|ibuprofeno|aspirina|amoxicilina|omeprazol)'
]
```

### **Laboratorios**
```python
lab_patterns = {
    'glucosa': {'normal_range': '70-100 mg/dL', 'value': '95 mg/dL'},
    'colesterol': {'normal_range': '<200 mg/dL', 'value': '180 mg/dL'},
    'hemograma': {'normal_range': 'Dentro de parámetros', 'value': 'Normal'}
}
```

### **Síntomas**
```python
symptom_keywords = [
    'dolor', 'fiebre', 'náuseas', 'vómito', 'diarrea', 'mareo',
    'cansancio', 'fatiga', 'tos', 'congestion', 'picazón'
]
```

---

## **📈 Métricas y Analytics**

### **Contadores Automáticos**
- **Medicamentos**: Número de fármacos recetados
- **Consultas**: Total de sesiones médicas
- **Laboratorios**: Exámenes mencionados o pendientes
- **Imágenes**: Archivos diagnósticos subidos

### **Cálculos Inteligentes**
- **Duración de consulta**: Basada en número de intercambios
- **Prioridad de síntomas**: Algoritmo de triaje automático
- **Estados de resultados**: Normal/Anormal/Pendiente
- **Fechas relativas**: "Hace 2 días", "Esta semana"

---

## **🚀 Instalación y Configuración**

### **1. Verificar Dependencias**
```bash
# Todas las dependencias ya están en requirements.txt
pip install -r requirements.txt
```

### **2. Archivos Modificados**
- ✅ `src/templates/interactive_chat.html` - Frontend completo
- ✅ `src/controllers/medical_resources_controller.py` - Backend API
- ✅ `src/app.py` - Registro de blueprint
- ✅ `src/controllers/image_controller.py` - Mejoras en validación

### **3. Verificar Funcionamiento**

```bash
# Iniciar servidor
python src/app.py

# Verificar endpoints
curl http://localhost:5000/medical-resources/consultations
curl http://localhost:5000/images/status
```

---

## **🔮 Futuras Mejoras**

### **Funcionalidades Planificadas**
- 📊 **Dashboard Analytics**: Gráficos de evolución médica
- 🔔 **Notificaciones**: Recordatorios de medicamentos
- 📤 **Exportación Avanzada**: PDF, Excel, HL7 FHIR
- 🔍 **Búsqueda Global**: Filtros y ordenamiento
- 📱 **App Móvil**: Versión nativa iOS/Android

### **Integraciones Externas**
- 🏥 **Sistemas Hospitalarios**: APIs de centros médicos
- 💊 **Bases de Datos de Medicamentos**: Verificación automática
- 🧬 **Laboratorios**: Importación directa de resultados
- 📋 **Historias Clínicas**: Estándares HL7

---

## **👨‍💻 Mantenimiento**

### **Logs y Debugging**
```python
# Los logs se guardan automáticamente
logger.info("Extrayendo medicamentos de conversación")
logger.error(f"Error en extracción: {error}")
```

### **Monitoreo de Performance**
- Tiempo de extracción de datos
- Precisión de algoritmos de detección
- Uso de memoria en procesamiento
- Latencia de APIs

### **Testing**
```bash
# Tests unitarios recomendados
python -m pytest tests/test_medical_resources.py
python -m pytest tests/test_extractors.py
```

---

## **📞 Soporte**

Para problemas o mejoras contacte al equipo de desarrollo:

- 🐛 **Bugs**: Usar sistema de issues del repositorio
- 💡 **Mejoras**: Pull requests con documentación
- 📚 **Documentación**: Mantener este archivo actualizado
- 🔒 **Seguridad**: Reportes confidenciales por email

---

**¡El sistema de recursos médicos está completamente funcional y listo para usar! 🎉** 