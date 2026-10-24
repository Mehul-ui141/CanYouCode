"""Auto-detection helper for programming languages."""

def detect_language(code: str) -> str:
    """Detect programming language from code snippets."""
    code_lower = code.lower()

    # Python indicators
    if "def " in code or "import " in code or "print(" in code or "__init__" in code or "self." in code or ":" in code and ("elif" in code or "except" in code):
        if "public class" not in code and "public static void" not in code:
            return "python"

    # Java indicators
    if "public class" in code or "private class" in code or "public static void main" in code or "System.out.println" in code or "java.util" in code:
        return "java"

    # C++ indicators
    if "#include <iostream>" in code or "std::" in code or "cout << " in code or "cin >>" in code or "vector<" in code or "namespace" in code:
        return "cpp"

    # C indicators
    if "#include <stdio.h>" in code or "#include <stdlib.h>" in code or "printf(" in code or "scanf(" in code or "malloc(" in code:
        return "c"

    # TypeScript indicators
    if ": string" in code or ": number" in code or ": boolean" in code or "interface " in code or "type " in code or "<T>" in code:
        return "typescript"

    # JavaScript indicators
    if "const " in code or "let " in code or "var " in code or "console.log" in code or "=>" in code or "require(" in code:
        return "javascript"

    # Fallback to python
    return "python"
