# Plan: Configurar Modelos de Agentes Óptimos

## TL;DR

> **Quick Summary**: Configurar todos los agentes de OpenCode con los modelos MÁS ÓPTIMOS de cada proveedor (Gemini 3.1 Pro, GPT-5 Codex, GLM-5, DeepSeek).
> 
> **Deliverables**:
> - Archivo `oh-my-opencode.json` configurado con modelos óptimos
> - Archivo `opencode.json` con todos los proveedores
> - Agentes funcionando al máximo rendimiento
>
> **Estimated Effort**: Quick
> **Parallel Execution**: NO - secuencial
> **Critical Path**: Config → Restart → Test

---

## Contexto

### Proveedores y Modelos Disponibles

| Proveedor | Modelos | Fortaleza |
|-----------|---------|-----------|
| **Vertex Gemini** | `gemini-3.1-pro`, `gemini-3.0`, `gemini-2.5-flash` | Razonamiento, multimodal |
| **Z.AI** | `glm-5` | Coding, rápido, YA FUNCIONA |
| **OpenAI** | `gpt-5.3-codex`, `gpt-5.2`, `gpt-4.1` | Código, calidad máxima |
| **DeepSeek** | `deepseek-chat`, `deepseek-reasoner` | Bajo costo |

### 🎯 Asignación ÓPTIMA (Mejor modelo para cada tarea)

| Agente | Modelo | Razón |
|--------|--------|-------|
| **sisyphus** | `google/gemini-3.1-pro` | 🏆 Orquestador principal - necesita lo MEJOR |
| **prometheus** | `google/gemini-3.1-pro` | 🏆 Planificación estratégica - necesita lo MEJOR |
| **hephaestus** | `openai/gpt-5.3-codex` | 🔧 Trabajo autónomo profundo - código avanzado |
| **explore** | `zai-coding-plan/glm-5` | ⚡ Exploración código - YA FUNCIONA |
| **librarian** | `google/gemini-3.0` | 📚 Investigación - conocimiento amplio |
| **metis** | `google/gemini-3.1-pro` | 🧠 Consulta pre-plan - razonamiento |
| **momus** | `openai/gpt-4.1` | ✅ Revisión crítica - calidad máxima |
| **atlas** | `zai-coding-plan/glm-5` | ⚡ Coordinación tareas - rápido |
| **oracle** | `deepseek/deepseek-chat` | 💰 Read-only - económico |
| **multimodal-looker** | `google/gemini-3.0` | 👁️ Visión/PDF - multimodal |

### Categorías Óptimas

| Categoría | Modelo | Razón |
|-----------|--------|-------|
| **visual-engineering** | `google/gemini-3.1-pro` | 🏆 Multimodal de máxima calidad |
| **ultrabrain** | `google/gemini-3.1-pro` | 🏆 Razonamiento máximo |
| **deep** | `openai/gpt-5.3-codex` | 🔧 Trabajo profundo de código |
| **artistry** | `google/gemini-3.0` | 🎨 Creativo, multimodal |
| **quick** | `zai-coding-plan/glm-5` | ⚡ Rápido, ya funciona |
| **unspecified-low** | `deepseek/deepseek-chat` | 💰 Económico |
| **unspecified-high** | `google/gemini-3.1-pro` | 🏆 Alta calidad |
| **writing** | `google/gemini-3.0` | ✍️ Escritura fluida |

---

## TODOs

### Archivo 1: oh-my-opencode.json

**Ruta**: `C:\Users\yago\.config\opencode\oh-my-opencode.json`

**Contenido exacto a escribir**:

```json
{
  "$schema": "https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/master/assets/oh-my-opencode.schema.json",
  "google_auth": false,
  "agents": {
    "sisyphus": {
      "model": "google/gemini-3.1-pro",
      "variant": "high"
    },
    "hephaestus": {
      "model": "openai/gpt-5.3-codex",
      "variant": "medium"
    },
    "oracle": {
      "model": "deepseek/deepseek-chat"
    },
    "librarian": {
      "model": "google/gemini-3.0"
    },
    "explore": {
      "model": "zai-coding-plan/glm-5"
    },
    "multimodal-looker": {
      "model": "google/gemini-3.0"
    },
    "prometheus": {
      "model": "google/gemini-3.1-pro",
      "variant": "high"
    },
    "metis": {
      "model": "google/gemini-3.1-pro",
      "variant": "high"
    },
    "momus": {
      "model": "openai/gpt-4.1",
      "variant": "medium"
    },
    "atlas": {
      "model": "zai-coding-plan/glm-5"
    }
  },
  "categories": {
    "visual-engineering": {
      "model": "google/gemini-3.1-pro",
      "variant": "high"
    },
    "ultrabrain": {
      "model": "google/gemini-3.1-pro",
      "variant": "high"
    },
    "deep": {
      "model": "openai/gpt-5.3-codex",
      "variant": "medium"
    },
    "artistry": {
      "model": "google/gemini-3.0",
      "variant": "high"
    },
    "quick": {
      "model": "zai-coding-plan/glm-5"
    },
    "unspecified-low": {
      "model": "deepseek/deepseek-chat"
    },
    "unspecified-high": {
      "model": "google/gemini-3.1-pro",
      "variant": "high"
    },
    "writing": {
      "model": "google/gemini-3.0"
    }
  }
}
```

---

### Archivo 2: opencode.json - Añadir proveedores

**Ruta**: `C:\Users\yago\.config\opencode\opencode.json`

**Añadir/actualizar en la sección `provider`**:

```json
  "provider": {
    "deepseek": {
      "models": {
        "deepseek-chat": {
          "name": "DeepSeek Chat",
          "limit": { "context": 64000, "output": 8000 },
          "modalities": { "input": ["text"], "output": ["text"] }
        },
        "deepseek-reasoner": {
          "name": "DeepSeek Reasoner",
          "limit": { "context": 64000, "output": 8000 },
          "modalities": { "input": ["text"], "output": ["text"] }
        }
      }
    },
    "google": {
      "models": {
        "gemini-3.1-pro": {
          "name": "Gemini 3.1 Pro",
          "limit": { "context": 1048576, "output": 65536 },
          "modalities": { "input": ["text", "image", "pdf"], "output": ["text"] }
        },
        "gemini-3.0": {
          "name": "Gemini 3.0",
          "limit": { "context": 1048576, "output": 65536 },
          "modalities": { "input": ["text", "image", "pdf"], "output": ["text"] }
        },
        "gemini-2.5-flash": {
          "name": "Gemini 2.5 Flash",
          "limit": { "context": 1048576, "output": 65536 },
          "modalities": { "input": ["text", "image", "pdf"], "output": ["text"] }
        }
      }
    },
    "openai": {
      "models": {
        "gpt-5.3-codex": {
          "name": "GPT-5.3 Codex",
          "limit": { "context": 200000, "output": 64000 },
          "modalities": { "input": ["text"], "output": ["text"] }
        },
        "gpt-5.2": {
          "name": "GPT-5.2",
          "limit": { "context": 200000, "output": 64000 },
          "modalities": { "input": ["text"], "output": ["text"] }
        },
        "gpt-4.1": {
          "name": "GPT-4.1",
          "limit": { "context": 1047576, "output": 32768 },
          "modalities": { "input": ["text", "image"], "output": ["text"] }
        }
      }
    }
  }
```

---

## Success Criteria

### Verification Commands
```bash
# 1. Verificar que el archivo existe y tiene contenido correcto
cat "C:\Users\yago\.config\opencode\oh-my-opencode.json"

# 2. Verificar estructura JSON válida
python -c "import json; json.load(open(r'C:\Users\yago\.config\opencode\oh-my-opencode.json'))"
```

### Final Checklist
- [ ] Archivo `oh-my-opencode.json` actualizado con modelos óptimos
- [ ] Archivo `opencode.json` tiene todos los proveedores configurados
- [ ] OpenCode reiniciado
- [ ] Agente `explore` funciona con glm-5
- [ ] Agente `librarian` funciona con gemini-3.0
- [ ] Agente `sisyphus` funciona con gemini-3.1-pro

---

## Ejecución

**Después de validar este plan, ejecutar:**
```
/start-work
```

Sisyphus aplicará los cambios automáticamente.
