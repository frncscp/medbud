# NOTA:
Este proyecto es solo un prototipo de lo que podría ser el uso de la inteligencia artificial como tecnología complementaria en el sistema médico. Si bien los modelos de transcripción funcionan actualmente con bastante precisión, es importante recalcar que la funcionalidad de chat con contexto puede retornar respuestas incorrectas.

# medbud
Este asistente puede:
- Transcribir conversaciones completas entre médico y paciente.
- Generar un resumen estructurado, segmentando inteligentemente la conversación en:
    - Datos de identificación:
      (Nombre, número de historia clínica, nacionalidad, fecha de nacimiento, teléfono, ocupación y estado civil).
    - Motivo de consulta.
    - Antecedentes de enfermedad.
    - Antecedentes de interés.
    - Anamnesis y exploración física.
    - Diagnóstico.
    - Órdenes médicas.
    - Tratamiento farmacológico.
    - Plan médico y planificaicón de cuidados.
- Responder preguntas sobre la conversación que no aparezcan en el resumen.

#### El proyecto depende de APIs de terceros, por lo que un error a la hora de usarlo seguramente provenga del límite de uso de las mismas (o la continuidad de sus existencias). 

![Demo](https://github.com/frncscp/medbud/blob/master/demo.jpg)
