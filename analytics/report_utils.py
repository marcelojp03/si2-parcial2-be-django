"""
Utilidades para reportes con IA
Sistema adaptado de Flask a Django
"""
import csv
import io
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple

from django.db import connection
from django.conf import settings

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_API_KEY = settings.OPENAI_API_KEY
    LLM_MODEL = settings.LLM_MODEL
    openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except (ImportError, AttributeError):
    openai_client = None
    OPENAI_API_KEY = None


# Patrones prohibidos para seguridad
FORBIDDEN = re.compile(r"\b(DROP|DELETE|TRUNCATE|UPDATE|INSERT|ALTER|EXEC|EXECUTE)\b", re.I)


def get_database_schema() -> Tuple[Dict[str, List[str]], set]:
    """
    Obtiene el esquema completo de la base de datos mediante introspección
    Retorna (schema_dict, tables_with_org_id)
    """
    schema = {}
    tables_with_org = set()
    
    with connection.cursor() as cursor:
        # Obtener todas las tablas del schema actual
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = current_schema()
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        for table_name in tables:
            # Obtener columnas y tipos de cada tabla
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = current_schema()
                AND table_name = %s
                ORDER BY ordinal_position;
            """, [table_name])
            
            columns = []
            has_org_id = False
            
            for col_name, col_type in cursor.fetchall():
                columns.append(f"{col_name}:{col_type}")
                if col_name == 'org_id':
                    has_org_id = True
            
            schema[table_name] = columns
            if has_org_id:
                tables_with_org.add(table_name)
    
    return schema, tables_with_org


def schema_str(schema: Dict[str, List[str]]) -> str:
    """Convierte el esquema a string legible"""
    lines = []
    for table, cols in schema.items():
        lines.append(f"- {table}({', '.join(cols)})")
    return "\n".join(lines)


def normalize_sql(s: str) -> str:
    """Limpia y normaliza SQL generado por LLM"""
    # Quita fences y tags
    s = re.sub(r"```(?:sql)?\s*|\s*```", "", s, flags=re.I).strip()
    # Sin punto y coma final
    s = s.rstrip("; \n\t")
    return s


def has_only_select_single_stmt(sql: str) -> bool:
    """Valida que sea solo un SELECT y no haya comandos prohibidos"""
    if FORBIDDEN.search(sql):
        return False
    # No múltiples sentencias
    if ";" in sql:
        return False
    # Solo SELECT
    return sql.strip().upper().startswith("SELECT")


def inject_limit(sql: str, limit: int) -> str:
    """Agrega LIMIT si no existe"""
    if re.search(r"\bLIMIT\s+\d+", sql, re.I):
        return sql
    return f"{sql}\nLIMIT {limit}"


def llm_generate_sql(nl_query: str, limit: int = 100) -> str:
    """
    Genera SQL desde lenguaje natural usando LLM
    """
    if not openai_client:
        raise RuntimeError("OpenAI no configurado (falta OPENAI_API_KEY)")
    
    schema, tables_with_org = get_database_schema()
    
    system = (
        "Eres un generador de SQL para PostgreSQL. Devuelves SOLO una sentencia SELECT válida y nada más. "
        "Debes respetar EXACTAMENTE los tipos de datos de cada columna. "
        "IMPORTANTE: Prioriza columnas con información legible (nombres, códigos, descripciones) sobre IDs numéricos."
    )
    
    user = f"""
Base de datos PostgreSQL (formato: columna:tipo):
{schema_str(schema)}

Reglas OBLIGATORIAS:
1) SOLO una sentencia SELECT, sin comentarios, sin backticks, sin 'sql'.
2) NUNCA uses DROP/DELETE/UPDATE/INSERT/ALTER/EXEC.
3) Incluye siempre LIMIT {limit} si el usuario no especifica otro límite.
4) Usa nombres EXACTOS de tablas/columnas (sensible a mayúsculas).
5) Respeta los TIPOS DE DATOS:
   - BOOLEAN: usa TRUE/FALSE (no 'active', 'true', 1, 0)
   - INTEGER/BIGINT: números sin comillas
   - VARCHAR/TEXT: texto entre comillas simples
   - TIMESTAMP: formato '2025-01-01 12:00:00'
6) PRIORIZA INFORMACIÓN LEGIBLE:
   - Selecciona columnas 'name', 'code', 'description' en lugar de solo 'id'
   - En JOIN, incluye nombres de tablas relacionadas, no solo foreign keys
   - Evita SELECT * a menos que sea explícitamente solicitado
7) PostgreSQL puro.

Pregunta del usuario:
\"\"\"{nl_query}\"\"\"

Devuelve únicamente el SQL (una sola línea o varias, pero una única sentencia).
"""
    
    response = openai_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.1,
    )
    
    sql = normalize_sql(response.choices[0].message.content or "")
    return sql


def llm_fix_sql(bad_sql: str, error: str, limit: int = 100) -> str:
    """
    Intenta corregir SQL con errores usando LLM
    """
    if not openai_client:
        raise RuntimeError("OpenAI no configurado")
    
    schema, _ = get_database_schema()
    
    system = (
        "Eres un corrector de SQL PostgreSQL. Devuelves SOLO una sentencia SELECT válida. "
        "Debes respetar EXACTAMENTE los tipos de datos de cada columna. "
        "Prioriza columnas con información legible (nombres, códigos) sobre IDs."
    )
    
    user = f"""
Corrige la siguiente consulta para PostgreSQL (formato columna:tipo):
{schema_str(schema)}

Reglas:
- SOLO una sentencia SELECT (sin ; final, sin backticks).
- Debe incluir LIMIT {limit} si no existe.
- Respeta los TIPOS DE DATOS exactos.
- INFORMACIÓN LEGIBLE: selecciona 'name', 'code', etc en lugar de IDs.

Consulta con error:
{bad_sql}

Error de PostgreSQL:
{error}

Devuelve únicamente el SQL corregido.
"""
    
    response = openai_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.1,
    )
    
    sql = normalize_sql(response.choices[0].message.content or "")
    return sql


def llm_interpret_results(nl_query: str, sql: str, columns: List[str], rows: List[Dict], max_rows: int = 5) -> str:
    """
    Genera una interpretación en lenguaje natural de los resultados
    """
    if not openai_client:
        return None
    
    sample_rows = rows[:max_rows]
    total_rows = len(rows)
    
    system = "Eres un asistente que interpreta resultados de consultas SQL en lenguaje natural claro y conciso."
    
    user = f"""
Pregunta del usuario:
"{nl_query}"

SQL ejecutado:
{sql}

Resultados ({total_rows} fila(s) total, mostrando primeras {len(sample_rows)}):
Columnas: {', '.join(columns)}
Datos:
{chr(10).join([str(row) for row in sample_rows])}

Genera una respuesta en lenguaje natural que:
1. Responda directamente la pregunta del usuario
2. Sea clara y concisa (máximo 3 oraciones)
3. Incluya números/datos relevantes
4. Use un tono profesional pero amigable

Respuesta:
"""
    
    try:
        response = openai_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            temperature=0.3,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except:
        return None


def execute_readonly_sql(sql: str) -> Tuple[List[Dict], List[str]]:
    """
    Ejecuta SQL de solo lectura y retorna resultados
    """
    with connection.cursor() as cursor:
        # Timeout de seguridad
        cursor.execute("SET LOCAL statement_timeout = '8s'")
        cursor.execute(sql)
        
        columns = [col[0] for col in cursor.description]
        rows = []
        
        for row in cursor.fetchall():
            row_dict = {}
            for idx, col in enumerate(columns):
                value = row[idx]
                # Convertir tipos especiales
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif hasattr(value, "as_tuple"):  # Decimal
                    value = float(value)
                row_dict[col] = value
            rows.append(row_dict)
    
    return rows, columns


def generate_csv(columns: List[str], rows: List[Dict]) -> str:
    """Genera contenido CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    
    for row in rows:
        writer.writerow([row.get(col, '') for col in columns])
    
    output.seek(0)
    return output.getvalue()


def generate_excel(columns: List[str], rows: List[Dict], title: str = "Reporte") -> bytes:
    """Genera archivo Excel"""
    if not EXCEL_AVAILABLE:
        raise ImportError("openpyxl no está instalado")
    
    output = io.BytesIO()
    wb = Workbook()
    ws = wb.active
    ws.title = "Datos"
    
    # Estilo para encabezados
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    # Escribir encabezados
    for col_idx, col_name in enumerate(columns, 1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
    
    # Escribir datos
    for row_idx, row_data in enumerate(rows, 2):
        for col_idx, col_name in enumerate(columns, 1):
            value = row_data.get(col_name, '')
            ws.cell(row=row_idx, column=col_idx, value=value)
    
    # Ajustar ancho de columnas
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    wb.save(output)
    output.seek(0)
    return output.getvalue()


def generate_pdf(columns: List[str], rows: List[Dict], title: str = "Reporte", nl_query: str = "") -> bytes:
    """Genera archivo PDF"""
    if not PDF_AVAILABLE:
        raise ImportError("reportlab no está instalado")
    
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    if nl_query:
        title_text = f"Reporte: {nl_query}"
    else:
        title_text = title
    
    title_para = Paragraph(f"<b>{title_text}</b>", styles['Title'])
    elements.append(title_para)
    elements.append(Spacer(1, 0.3*inch))
    
    # Fecha
    date_para = Paragraph(f"Generado: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", styles['Normal'])
    elements.append(date_para)
    elements.append(Spacer(1, 0.2*inch))
    
    # Tabla
    table_data = [columns]
    for row in rows:
        table_data.append([str(row.get(col, '')) for col in columns])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(table)
    doc.build(elements)
    output.seek(0)
    return output.getvalue()
