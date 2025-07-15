"""
Markdown Documentation Generator

Generates comprehensive Markdown documentation compatible with GitHub and other platforms.
"""

import time
from typing import Dict, Any, List
from .base_generator import BaseFormatGenerator, GenerationContext, GenerationResult


class MarkdownDocumentationGenerator(BaseFormatGenerator):
    """Generator for comprehensive Markdown documentation."""

    @property
    def format_name(self) -> str:
        return "Documentación Markdown"

    @property
    def file_extension(self) -> str:
        return ".md"

    @property
    def mime_type(self) -> str:
        return "text/markdown"

    @property
    def is_binary(self) -> bool:
        return False

    def generate(self, context: GenerationContext) -> GenerationResult:
        """Generate comprehensive Markdown documentation."""
        start_time = time.time()

        try:
            self.validate_context(context)

            # Generate Markdown content
            md_content = self._generate_markdown_content(context)

            generation_time = time.time() - start_time

            return self.create_generation_result(
                md_content, context, generation_time,
                metadata={
                    "sections": 6,
                    "github_compatible": True,
                    "includes_toc": True
                }
            )

        except Exception as e:
            return self.handle_generation_error(e, context)

    def _generate_header(self, template_vars: Dict[str, Any]) -> str:
        """Generate the document header."""
        return f"""# 📊 Análisis SQL - {template_vars['original_filename']}

> **Reporte de Análisis Automático**
> Generado por SQL Analyzer Enterprise
> Fecha: {template_vars['analysis_timestamp'].strftime('%d de %B de %Y a las %H:%M:%S')}

---

[![SQL Analyzer](https://img.shields.io/badge/SQL-Analyzer-blue.svg)](https://github.com/sql-analyzer-enterprise)
[![Calidad](https://img.shields.io/badge/Calidad-{template_vars['summary']['quality_score']}%25-{'green' if template_vars['summary']['quality_score'] >= 80 else 'yellow' if template_vars['summary']['quality_score'] >= 60 else 'red'}.svg)](#{template_vars['summary']['quality_score']})
[![Errores](https://img.shields.io/badge/Errores-{template_vars['summary']['total_errors']}-{'red' if template_vars['summary']['total_errors'] > 10 else 'yellow' if template_vars['summary']['total_errors'] > 0 else 'green'}.svg)](#{template_vars['summary']['total_errors']})"""

- [📊 Resumen Ejecutivo](#-resumen-ejecutivo)
- [🐛 Errores Detectados](#-errores-detectados)
- [💡 Recomendaciones](#-recomendaciones)
- [🔧 Detalles Técnicos](#-detalles-técnicos)
- [📈 Métricas de Calidad](#-métricas-de-calidad)
- [🚀 Próximos Pasos](#-próximos-pasos)"""

Este documento presenta el análisis completo del archivo SQL **`{template_vars['original_filename']}`**.

### 📊 Métricas Principales

| Métrica | Valor | Estado |
|---------|-------|--------|
| **Total de Errores** | {summary['total_errors']} | {'🔴 Crítico' if summary['total_errors'] > 20 else '🟡 Atención' if summary['total_errors'] > 5 else '🟢 Bueno'} |
| **Puntuación de Calidad** | {summary['quality_score']}% | {'🟢 Excelente' if summary['quality_score'] >= 90 else '🟡 Bueno' if summary['quality_score'] >= 70 else '🔴 Necesita Mejora'} |
| **Líneas Analizadas** | {summary['lines_analyzed']:,} | 📏 |
| **Correcciones Sugeridas** | {summary['fixes_suggested']} | {'🔧 Disponibles' if summary['fixes_suggested'] > 0 else '✅ Ninguna'} |

### 🎨 Distribución de Errores

```mermaid
pie title Distribución de Errores por Severidad
    "Críticos" : {summary['critical_errors']}
    "Altos" : {summary['high_errors']}
    "Medios" : {summary['medium_errors']}
    "Bajos" : {summary['low_errors']}
```"""

El análisis del archivo **`{template_vars['original_filename']}`** ({summary['file_size']:,} bytes) ha sido completado exitosamente. Se procesaron **{summary['lines_analyzed']:,} líneas** de código SQL y se identificaron **{summary['total_errors']} errores** de diferentes niveles de severidad.

### 📈 Puntuación de Calidad: {summary['quality_score']}%

{'🟢 **Excelente calidad de código**' if summary['quality_score'] >= 90 else '🟡 **Buena calidad con margen de mejora**' if summary['quality_score'] >= 70 else '🔴 **Calidad baja - requiere atención inmediata**'}

### 🚨 Errores por Severidad

| Severidad | Cantidad | Porcentaje | Descripción |
|-----------|----------|------------|-------------|
| 🔴 **Críticos** | {summary['critical_errors']} | {(summary['critical_errors']/max(1,summary['total_errors'])*100):.1f}% | Errores que impiden la ejecución |
| 🟠 **Altos** | {summary['high_errors']} | {(summary['high_errors']/max(1,summary['total_errors'])*100):.1f}% | Errores que afectan funcionalidad |
| 🟡 **Medios** | {summary['medium_errors']} | {(summary['medium_errors']/max(1,summary['total_errors'])*100):.1f}% | Problemas de rendimiento o estilo |
| 🟢 **Bajos** | {summary['low_errors']} | {(summary['low_errors']/max(1,summary['total_errors'])*100):.1f}% | Sugerencias de mejora |

### 🎯 Hallazgos Clave

{self._generate_key_findings(summary)}"""

    def _generate_errors_section(self, template_vars: Dict[str, Any]) -> str:
        """Generate errors section."""
        errors = template_vars['errors']

        if not errors:
            return """## 🐛 Errores Detectados

### ✅ ¡Excelente! No se encontraron errores

El código SQL analizado no presenta errores detectables. Esto indica:

- ✅ Sintaxis correcta
- ✅ Buenas prácticas aplicadas
- ✅ Código bien estructurado"""

        content = ["""## 🐛 Errores Detectados

### 📋 Lista de Errores Encontrados

A continuación se detallan todos los errores identificados durante el análisis:"""]

        # Group errors by severity
        errors_by_severity = {
            'CRITICAL': [e for e in errors if e.get('severity') == 'CRITICAL'],
            'HIGH': [e for e in errors if e.get('severity') == 'HIGH'],
            'MEDIUM': [e for e in errors if e.get('severity') == 'MEDIUM'],
            'LOW': [e for e in errors if e.get('severity') == 'LOW']
        }

        severity_icons = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }

        severity_names = {
            'CRITICAL': 'Críticos',
            'HIGH': 'Altos',
            'MEDIUM': 'Medios',
            'LOW': 'Bajos'
        }

        for severity, error_list in errors_by_severity.items():
            if not error_list:
                continue

            content.append(f"""### {severity_icons[severity]} Errores {severity_names[severity]} ({len(error_list)})""")

            for i, error in enumerate(error_list[:10], 1):  # Limit to 10 per severity
                content.append(self._format_error_markdown(error, i))

            if len(error_list) > 10:
                content.append(f"\n> **Nota:** Se muestran los primeros 10 errores. Total: {len(error_list)}")

        return '\n\n'.join(content)

**📍 Ubicación:** Línea {error.get('line', 'N/A')}, Columna {error.get('column', 'N/A')}
**🏷️ Severidad:** ![{error.get('severity', 'LOW')}](https://img.shields.io/badge/Severidad-{error.get('severity', 'LOW')}-{color}.svg)
**📂 Categoría:** `{error.get('category', 'general')}`

**📝 Descripción:**
{error.get('description', 'Sin descripción disponible')}"""

        # Add fixes if available
        fixes = error.get('fixes', [])
        if fixes:
            content += "\n\n**🔧 Correcciones Sugeridas:**\n"
            for j, fix in enumerate(fixes[:3], 1):  # Limit to 3 fixes
                confidence = fix.get('confidence', 0) * 100
                content += f"\n{j}. **{fix.get('description', 'Sin descripción')}**"
                content += f"\n   - Confianza: {confidence:.1f}%"
                if fix.get('explanation'):
                    content += f"\n   - Explicación: {fix.get('explanation')}"

        return content

    def _generate_recommendations_section(self, template_vars: Dict[str, Any]) -> str:
        """Generate recommendations section."""
        summary = template_vars['summary']

        content = ["""## 💡 Recomendaciones

### 🎯 Acciones Recomendadas

Basándose en el análisis realizado, se sugieren las siguientes acciones:"""]

        recommendations = []

        if summary['critical_errors'] > 0:
            recommendations.append({
                'priority': 'URGENTE',
                'icon': '🚨',
                'title': 'Corrección de Errores Críticos',
                'description': f'Se encontraron {summary["critical_errors"]} errores críticos que deben corregirse antes de ejecutar el código en producción.',
                'action': 'Revisar y corregir cada error crítico listado en la sección anterior.'
            })

        if summary['high_errors'] > 0:
            recommendations.append({
                'priority': 'ALTA',
                'icon': '⚠️',
                'title': 'Corrección de Errores de Alta Prioridad',
                'description': f'Se identificaron {summary["high_errors"]} errores de alta prioridad que afectan la funcionalidad.',
                'action': 'Planificar la corrección de estos errores en el próximo ciclo de desarrollo.'
            })

        if summary['quality_score'] < 70:
            recommendations.append({
                'priority': 'MEDIA',
                'icon': '📈',
                'title': 'Mejora de Calidad del Código',
                'description': f'La puntuación de calidad ({summary["quality_score"]}%) está por debajo del umbral recomendado (70%).',
                'action': 'Considerar refactorización del código para mejorar la legibilidad y mantenibilidad.'
            })

        if summary['fixes_suggested'] > 0:
            recommendations.append({
                'priority': 'MEDIA',
                'icon': '🔧',
                'title': 'Aplicación de Correcciones Automáticas',
                'description': f'{summary["fixes_suggested"]} correcciones pueden aplicarse automáticamente.',
                'action': 'Revisar y aplicar las correcciones automáticas sugeridas.'
            })

        # Add general recommendations
        recommendations.extend([
            {
                'priority': 'BAJA',
                'icon': '📚',
                'title': 'Documentación y Mejores Prácticas',
                'description': 'Revisar la documentación para implementar mejores prácticas de SQL.',
                'action': 'Consultar guías de estilo SQL y estándares de la organización.'
            },
            {
                'priority': 'BAJA',
                'icon': '🔍',
                'title': 'Revisiones de Código Regulares',
                'description': 'Implementar un proceso de revisión de código sistemático.',
                'action': 'Establecer revisiones por pares antes de desplegar cambios.'
            },
            {
                'priority': 'BAJA',
                'icon': '🧪',
                'title': 'Testing y Validación',
                'description': 'Probar el código en un entorno de desarrollo antes de producción.',
                'action': 'Crear casos de prueba y validar en entorno de staging.'
            }
        ])

        for rec in recommendations:
            priority_colors = {
                'URGENTE': 'red',
                'ALTA': 'orange',
                'MEDIA': 'yellow',
                'BAJA': 'green'
            }

            color = priority_colors.get(rec['priority'], 'gray')

            content.append(f"""#### {rec['icon']} {rec['title']}

![Prioridad](https://img.shields.io/badge/Prioridad-{rec['priority']}-{color}.svg)

**Descripción:** {rec['description']}

**Acción Recomendada:** {rec['action']}""")

        return '\n\n'.join(content)

    def _generate_technical_details(self, template_vars: Dict[str, Any]) -> str:
        """Generate technical details section."""
        return f"""## 🔧 Detalles Técnicos

### 📋 Información del Análisis

| Campo | Valor |
|-------|-------|
| **Generador** | {template_vars['generator_name']} v{template_vars['generator_version']} |
| **Sesión de Análisis** | `{template_vars['session_id']}` |
| **Idioma del Reporte** | {template_vars['language']} |
| **Archivo Original** | `{template_vars['original_filename']}` |
| **Timestamp** | {template_vars['analysis_timestamp'].isoformat()} |

### 🏗️ Arquitectura del Análisis

```mermaid
graph TD
    A[Archivo SQL] --> B[Parser SQL]
    B --> C[Detector de Errores]
    C --> D[Analizador de Esquemas]
    D --> E[Generador de Reportes]
    E --> F[Reporte Markdown]
```

### 📊 Estadísticas de Procesamiento

- **Tiempo de Análisis:** Completado en tiempo óptimo
- **Memoria Utilizada:** Eficiente para archivos de este tamaño
- **Algoritmos Aplicados:** Análisis estático, detección de patrones, validación de sintaxis"""

    def _generate_footer(self, template_vars: Dict[str, Any]) -> str:
        """Generate document footer."""
        return f"""## 🚀 Próximos Pasos

### ✅ Lista de Verificación

- [ ] Revisar todos los errores críticos
- [ ] Aplicar correcciones sugeridas
- [ ] Validar cambios en entorno de desarrollo
- [ ] Ejecutar pruebas de regresión
- [ ] Documentar cambios realizados
- [ ] Desplegar a producción

### 📞 Soporte

¿Necesita ayuda adicional? Contacte al equipo de soporte:

- 📧 **Email:** support@sql-analyzer-enterprise.com
- 📚 **Documentación:** [docs.sql-analyzer-enterprise.com](https://docs.sql-analyzer-enterprise.com)
- 🐛 **Reportar Issues:** [github.com/sql-analyzer-enterprise/issues](https://github.com/sql-analyzer-enterprise/issues)

---

**Generado por SQL Analyzer Enterprise**
*Transformando el análisis de código SQL con tecnología avanzada*

![SQL Analyzer Enterprise](https://img.shields.io/badge/Powered%20by-SQL%20Analyzer%20Enterprise-blue.svg)
![Versión](https://img.shields.io/badge/Versión-{template_vars['generator_version']}-green.svg)
![Licencia](https://img.shields.io/badge/Licencia-MIT-blue.svg)

> 📅 **Fecha de generación:** {template_vars['analysis_timestamp'].strftime('%d de %B de %Y a las %H:%M:%S')}
> 🔗 **Sesión:** `{template_vars['session_id']}`"""
