"""
AI Flowchart Architect - Configuration & Prompts
"""

# ── LLM Defaults ──────────────────────────────────────────────
OPENAI_MODEL = "gpt-4o"
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096
TEMPERATURE = 0.3

# ── System Prompt ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are a Mermaid.js flowchart expert. Your ONLY job is to convert
natural language process descriptions into valid Mermaid flowchart code.

STRICT RULES:
1. Return ONLY the raw Mermaid code. No markdown backticks, no explanations, no extra text.
2. Always use `graph TD` (top-down) direction unless the user explicitly asks otherwise.
3. Use meaningful node IDs (e.g., A, B, C or start, check, end).
4. Decision nodes MUST use curly braces for diamond shape: {Is condition?}
5. Terminal/start nodes use round edges: ([Start]) or ([End])
6. Process nodes use square brackets: [Process step]
7. Keep labels concise but clear.
8. Support both Hebrew and English input - output labels in the SAME language as input.
9. Add style classes at the bottom for:
   - Decision nodes: fill:#FF8C00,stroke:#FF6600,color:#fff
   - Start nodes: fill:#2ECC71,stroke:#27AE60,color:#fff
   - End/terminal nodes: fill:#E74C3C,stroke:#C0392B,color:#fff
   - Process nodes: fill:#3498DB,stroke:#2980B9,color:#fff

Example output format:
graph TD
    A([Start]) --> B[Step 1]
    B --> C{Decision?}
    C -->|Yes| D[Action A]
    C -->|No| E[Action B]
    D --> F([End])
    E --> F
    style A fill:#2ECC71,stroke:#27AE60,color:#fff
    style F fill:#E74C3C,stroke:#C0392B,color:#fff
    style C fill:#FF8C00,stroke:#FF6600,color:#fff
    style B fill:#3498DB,stroke:#2980B9,color:#fff
    style D fill:#3498DB,stroke:#2980B9,color:#fff
    style E fill:#3498DB,stroke:#2980B9,color:#fff
"""

REFINEMENT_PROMPT = """You are a Mermaid.js flowchart expert. The user wants to modify an existing diagram.

Current Mermaid code:
```
{current_code}
```

User instruction: {instruction}

STRICT RULES:
1. Return ONLY the updated raw Mermaid code. No markdown backticks, no explanations.
2. Preserve the existing structure and only apply the requested changes.
3. Keep all existing style classes and update/add as needed.
4. Support Hebrew and English instructions.
"""

VALIDATION_PROMPT = """You are a flowchart logic auditor. Analyze the following Mermaid flowchart code for logical integrity.

Mermaid code:
```
{code}
```

Check for these issues:
1. **Orphan nodes**: Nodes that are not connected to any other node (no incoming or outgoing edges).
2. **Infinite loops**: Cycles with no exit condition or break path.
3. **Missing exit paths**: Decision nodes (diamonds) that don't have all required branches (e.g., a Yes/No decision missing one path).
4. **Dead ends**: Non-terminal nodes that have no outgoing edges (the flow stops unexpectedly).

STRICT RULES:
1. Return ONLY valid JSON. No markdown, no explanations, no extra text.
2. Use this exact format:
{{"status": "green", "issues": []}}
or:
{{"status": "yellow", "issues": [{{"type": "orphan_node", "node": "X", "detail": "Node X is not connected to any other node"}}, {{"type": "missing_exit", "node": "C", "detail": "Decision node C is missing a No branch"}}]}}

Status values:
- "green": No issues found, logic is sound.
- "yellow": Issues found, include details in the issues array.
"""

PROFESSIONAL_TONE_PROMPT = """You are a business writing expert. Rewrite ALL node labels in the following Mermaid flowchart
to use formal, professional business terminology. Keep the exact same structure, connections, and node IDs.
Only change the text inside brackets/parentheses/braces.

Current Mermaid code:
```
{code}
```

STRICT RULES:
1. Return ONLY the updated raw Mermaid code. No markdown backticks, no explanations.
2. Keep all node IDs, arrows, and style definitions unchanged.
3. Only rewrite the human-readable labels to sound more corporate/professional.
4. CRITICAL: Keep the SAME LANGUAGE as the original labels. If labels are in Hebrew, rewrite in professional Hebrew. If in English, rewrite in professional English. NEVER translate between languages.
5. Examples (English): "Check email" -> "Email Verification Process", "Show error" -> "Display Error Notification"
6. Examples (Hebrew): "בדוק אימייל" -> "תהליך אימות דואר אלקטרוני", "הצג שגיאה" -> "הצגת התראת שגיאה"
"""

# ── UI Text (i18n) ────────────────────────────────────────────
UI_TEXT = {
    "en": {
        "title": "AI Flowchart Architect",
        "subtitle": "Transform process descriptions into beautiful flowcharts",
        "input_label": "Describe your process",
        "input_placeholder": "e.g., A user signs up, if email is verified they get a welcome mail, else they are redirected to support...",
        "generate_btn": "Generate Flowchart",
        "refine_label": "Refine the diagram",
        "refine_placeholder": "e.g., Change the rejection node to red, add a retry step...",
        "refine_btn": "Update",
        "copy_btn": "Copy Code",
        "download_png": "Download PNG",
        "download_svg": "Download SVG",
        "download_pptx": "Download PPTX",
        "provider_label": "LLM Provider",
        "api_key_label": "API Key",
        "language_label": "Language / שפה",
        "sidebar_title": "Settings",
        "error_invalid": "Could not generate a valid flowchart. Please try rephrasing.",
        "error_api": "API error: {}",
        "error_no_key": "API key not found. Add your key to the .env file (OPENAI_API_KEY or ANTHROPIC_API_KEY).",
        "success_copy": "Code copied to clipboard!",
        "no_diagram": "Generate a flowchart to see it here",
        "validation_title": "🩺 Logic Health Check",
        "validation_green": "✅ Logic is sound — all paths lead to proper exit nodes.",
        "validation_yellow": "⚠️ Potential issues detected:",
        "validation_running": "🔍 Analyzing flowchart logic...",
        "professional_tone": "💼 Professional Tone",
        "professional_tone_help": "Rewrite node labels using formal business terminology",
        "rewriting_tone": "✍️ Rewriting labels in professional tone...",
        "tips_box": "💡 <b>Tips:</b><br>• Be specific in your descriptions<br>• Use the refinement chat to iterate<br>• Export as PNG/SVG/PPTX for presentations",
        "model_label": "LLM Model",
        "spinner_generating": "🏗️ Architecting your flowchart...",
        "spinner_refining": "🔧 Refining your diagram...",
        "toast_ready": "Diagram Ready!",
        "toast_updated": "Diagram Updated!",
    },
    "he": {
        "title": "AI Flowchart Architect",
        "subtitle": "הפוך תיאורי תהליכים לדיאגרמות מקצועיות",
        "input_label": "תאר את התהליך שלך",
        "input_placeholder": 'לדוגמה: משתמש נרשם, אם האימייל מאומת הוא מקבל מייל ברוכים הבאים, אחרת הוא מופנה לתמיכה...',
        "generate_btn": "צור דיאגרמה",
        "refine_label": "שפר את הדיאגרמה",
        "refine_placeholder": "לדוגמה: שנה את צבע הצומת לאדום, הוסף שלב נוסף...",
        "refine_btn": "עדכן",
        "copy_btn": "העתק קוד",
        "download_png": "הורד PNG",
        "download_svg": "הורד SVG",
        "download_pptx": "הורד PPTX",
        "provider_label": "ספק LLM",
        "api_key_label": "מפתח API",
        "language_label": "Language / שפה",
        "sidebar_title": "הגדרות",
        "error_invalid": "לא ניתן ליצור דיאגרמה תקינה. נסה לנסח מחדש.",
        "error_api": "שגיאת API: {}",
        "error_no_key": "מפתח API לא נמצא. הוסף את המפתח לקובץ .env (OPENAI_API_KEY או ANTHROPIC_API_KEY).",
        "success_copy": "הקוד הועתק!",
        "no_diagram": "צור דיאגרמה כדי לראות אותה כאן",
        "validation_title": "🩺 בדיקת תקינות לוגית",
        "validation_green": "✅ הלוגיקה תקינה — כל הנתיבים מגיעים לצמתי סיום.",
        "validation_yellow": "⚠️ זוהו בעיות פוטנציאליות:",
        "validation_running": "🔍 מנתח לוגיקת דיאגרמה...",
        "professional_tone": "💼 סגנון מקצועי",
        "professional_tone_help": "כתוב מחדש תוויות צמתים בשפה עסקית פורמלית",
        "rewriting_tone": "✍️ משכתב תוויות בסגנון מקצועי...",
        "tips_box": "💡 <b>טיפים:</b><br>• היה ספציפי בתיאורים שלך<br>• השתמש בצ'אט השיפור כדי לשפר<br>• ייצא כ-PNG/SVG/PPTX למצגות",
        "model_label": "מודל LLM",
        "spinner_generating": "🏗️ מתכנן את הדיאגרמה שלך...",
        "spinner_refining": "🔧 משפר את הדיאגרמה...",
        "toast_ready": "הדיאגרמה מוכנה!",
        "toast_updated": "הדיאגרמה עודכנה!",
    },
}

# ── Mermaid.ink API ───────────────────────────────────────────
MERMAID_INK_BASE = "https://mermaid.ink"
