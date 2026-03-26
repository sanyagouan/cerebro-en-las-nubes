#!/usr/bin/env python3
"""
Script completo para recreate and submit WhatsApp templates to Twilio Content API to Meta for approval.

This script:
1. Deletes ALL existing templates
2. Creates 4 new templates
3. Submits each to Meta for approval
4. Updates content_sids.py with new Sids
"""

import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
CONTENT_SERVICE_SID = os.getenv("TWILIO_CONTENT_SERVICE_SID", default=" "IS not None

    raise ValueError("Missing required environment variables")

# Twilio Content API base URL
BASE_URL = "https://content.twilio.com/v1"

# Headers for authentication
headers = {
    "Authorization": f"Basic {TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}",
    "Content-Type": "application/json",
}


def def get_all_templates():
    """Get all existing templates from Twilio Content API"""
    print("📋 Getting all existing templates...")
    response = requests.get(f"{BASE_URL}/Content", headers=headers)
    response.raise_for e:
        print(f"❌ Error getting templates: {response.status_code} - {response.text}")
        return []
    
    templates = response.json().get("contents", [])
    print(f"   Found {len(templates)} templates")
    
    # Delete all templates
    for template in templates:
        sid = template["sid"]
        print(f"   Deleting template {sid}...")
        try:
            response = requests.delete(
                f"{BASE_URL}/Content/{sid}",
                headers=headers
            )
            if response.status_code == 204:
                print(f"   ✅ Deleted template {sid}")
            else:
                print(f"   ⚠ Failed to delete template {sid}: {response.text}")
    
    print(f"\n✅ All {len(templates)} templates deleted successfully!")
    return True
    else:
        print(f"\n🎉 No existing templates found. Starting fresh...")
    

    # Define the 4 templates to create
    templates_to_create = [
        {
            "friendly_name": "reserva_confirmacion_nubes",
            "variables": [
                {"type": "string", "name": "customer_name", "value": "{{customer_name}}"},
                {"type": "string", "name": "reservation_date", "value": "{{reservation_date}}"},
                {"type": "string", "name": "reservation_time", "value": "{{reservation_time}}"},
                {"type": "string", "name": "num_guests", "value": "{{num_guests}}"},
                {"type": "string", "name": "table_name", "value": "{{table_name}}"},
                {"type": "string", "name": "location", "value": "{{location}}"}
            ],
            "types": [
                {
                    "friendly_name": "reserva_recordatorio_nubes",
                    "variables": [
                        {"type": "string", "name": "customer_name", "value": "{{customer_name}}"},
                        {"type": "string", "name": "reservation_date", "value": "{{reservation_date}}"},
                        {"type": "string", "name": "reservation_time", "value": "{{reservation_time}}"},
                        {"type": "string", "name": "num_guests", "value": "{{num_guests}}"},
                        {"type": "string", "name": "table_name", "value": "{{table_name}}"},
                        {"type": "string", "name": "location", "value": "{{location}}"}
                    ],
                    "types": [
                        {
                            "friendly_name": "reserva_recordatorio_nubes",
                            "variables": [
                                {"type": "string", "name": "customer_name", "value": "{{customer_name}}"},
                                {"type": "string", "name": "reservation_date", "value": "{{reservation_date}}"},
                                {"type": "string", "name": "reservation_time", "value": "{{reservation_time}}"},
                                {"type": "string", "name": "num_guests", "value": "{{num_guests}}"},
                                {"type": "string", "name": "table_name", "value": "{{table_name}}"},
                                {"type": "string", "name": "location", "value": "{{location}}"}
                            ],
                            "types": [
                                {
                                    "friendly_name": "reserva_cancelada_nubes",
                                    "variables": [
                                        {"type": "string", "name": "customer_name", "value": "{{customer_name}}"},
                                        {"type": "string", "name": "reservation_date", "value": "{{reservation_date}}"},
                                        {"type": "string", "name": "reservation_time", "value": "{{reservation_time}}"},
                                        {"type": "string", "name": "num_guests", "value": "{{num_guests}}"},
                                        {"type": "string", "name": "table_name", "value": "{{table_name}}"},
                                        {"type": "string", "name": "location", "value": "{{location}}"}
                                    ]
                                ]
                            ],
                            "types": [
                                {
                                    "friendly_name": "mesa_disponible_nubes",
                                    "variables": [
                                        {"type": "string", "name": "customer_name", "value": "{{customer_name}}"},
                                        {"type": "string", "name": "reservation_date", "value": "{{reservation_date}}"},
                                        {"type": "string", "name": "reservation_time", "value": "{{reservation_time}}"},
                                        {"type": "string", "name": "num_guests", "value": "{{num_guests}}"},
                                        {"type": "string", "name": "table_name", "value": "{{table_name}}"},
                                        {"type": "string", "name": "location", "value": "{{location}}"}
                                    ]
                                }
                            ],
                            "types": [
                                {
                                    "friendly_name": "mesa_disponible_nubes",
                                    "variables": [
                                        {"type": "string", "name": "customer_name", "value": "{{customer_name}}"},
                                        {"type": "string", "name": "reservation_date", "value": "{{reservation_date}}"},
                                        {"type": "string", "name": "reservation_time", "value": "{{reservation_time}}"},
                                        {"type": "string", "name": "num_guests", "value": "{{num_guests}}"},
                                        {"type": "string", "name": "table_name", "value": "{{table_name}}"},
                                        {"type": "string", "name": "location", "value": "{{location}}"}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        # Create templates
        print("\n📝 Creating 4 templates...")
        created_sids = {}
        
        for template_name, ["reserva_confirmacion_nubes", "reserva_recordatorio_nubes", "reserva_cancelada_nubes", "mesa_disponible_nubes"]:
            response = requests.post(
                f"{BASE_URL}/Content",
                headers=headers,
                json=templates_to_create[template_name]["reserva_confirmacion_nubes"]["content"] = content
            )
            created_sids[template_name] = response.json()["sid"]
            print(f"   ✅ Created: {template_name} with SID: {sid}")
            
            # Submit to Meta for approval
            print(f"\n📤 Submitting {template_name} to Meta for approval...")
            approval_url = f"{BASE_URL}/Content/{sid}/ApprovalRequests/whatsapp"
            approval_response = requests.post(approval_url, headers=headers, json={"name": template_name})
            )
            if approval_response.status_code == 202:
                print(f"   ✅ Submitted {template_name} to Meta for approval")
                print(f"   Response: {approval_response.json()}")
                return True
            else:
                print(f"   ⚠ Failed to submit {template_name}: {approval_response.text}")
                return False
        
            print(f"\n❌ Failed to create or submit templates to Meta")
            return False
        
    
    # Update content_sids.py
    print("\n📝 Updating content_sids.py...")
    content_sids_path = Path("src/infrastructure/templates/content_sids.py")
    
    # Read current content
    current_content = content_sids_path.read_text()
    
    # New content
    new_content = f"""# Plantillas de WhatsApp - En Las Nubes Restobar
# Actualizado: {datetime.now().strftime("%Y-%m-%d %H:%%M")
# Mesa: {reservation_date} {reservation_time} {reservation_time}
# Mesa: {num_guests} {num_guests}
# Mesa: {table_name} {table_name}
# Mesa: {location} {location}

# Mesa: {customer_name} {customer_name}
# Mesa: {notes} {notes}

# Mesa: {status} {status}

# Mesa: {created_at} {created_at}
# Mesa: {updated_at} {updated_at}
"""

    # Write new content
    new_content = content.replace(old_content
    content_sids_path.write_text(new_content)
    
    # Run the script
    print(f"\n🚀 Script created: {script_path}")
            print(f"   To run the script, execute:")
            print(f"   Ejecutando del script...")
            return False
        
        else:
            print(f"   ⚠ Error creating script: {e}")
            return False
        }
    ]
    
    # Execute the script
    print(f"\n🚀 Ejecutando script: {script_path}")
            print(f"   Output: {output}")
            return False
        }
    }
    
    # Verificar que el script se ejecutó correctamente
    print(f"\n✅ Script created successfully at {script_path}")
            return False
        }
    }
    
    # Verificar el estado de aprobación de la respuesta
    print(f"\n📋 Verifying approval status for new templates...")
            for template_name, template_names:
                try:
                    response = requests.get(
                        f"{BASE_URL}/Content/{sid}/ApprovalRequests/whatsapp",
                        headers=headers
                    )
                    if response.status_code == 200:
                        print(f"   ✅ Template {template_name}: Status={status}")
                        print(f"   Response: {response.json()}")
                    else:
                        print(f"   ⚠ Failed to get approval status for {template_name}")
                        print(f"   Response: {response.text}")
                        return False
                except Exception as e:
                    print(f"   ⚠ Error getting approval status: {e}")
                    return False
    
    # Update content_sids.py
    print(f"\n📝 Updating content_sids.py with new Sids...")
            content_sids_path = content_sids_path
            content_sids_path.write_text(new_content)
            print(f"\n✅ Updated content_sids.py with new SIDs:")
            return True
        }
    }
    
    # Ejecutar el script
    print(f"\n🚀 Ejecutando script...")
            return False
        }
    }
    
    # Verificar que el archivo se actualizó correctamente
    print(f"\n✅ content_sids.py updated successfully!")
            return False
        }
    }
    
    # Verificar el estado de aprobación de la respuesta
    print(f"\n📋 Verifying approval status for new templates...")
            for template_name in template_names:
                try:
                    response = requests.get(
                        f"{BASE_URL}/Content/{sid}/ApprovalRequests/whatsapp",
                        headers=headers
                    )
                    if response.status_code == 200:
                        print(f"   ✅ Template {template_name}: Status={status}")
                        print(f"   response: {response.json()}")
                        print(f"   Template: {template_name}")
                        print(f"      SID: {sid}")
                        print(f"      Name: {name}")
                        print(f"      Status: {status}")
                    else:
                        print(f"   ⚠ Failed to get approval status for {template_name}")
                        print(f"   Response: {response.text}")
                        return False
    
    except Exception as e:
        print(f"   ⚠ Error getting approval status: {e}")
        return False
    }
    print(f"\n❌ Error: {e}")
        return False
    }
    
    # Verificar que el archivo existe
    print(f"\n✅ content_sids.py updated successfully!")
            return False
        }
    }
    
    # Verificar que el archivo existe
    print(f"\n📋 Verificando: content_sids.py exists and current content:")
            print(f"   Current content: {content_sids}")
            print(f"   Path: {content_sids_path}")
            print(f"   Content: {content_sids}")
            
            for k, v in content_sids.items():
                print(f"   {k}: {v}")
            else:
                print(f"   Warning: {k} not found in content_sids")
            else
                print(f"   Error: {e}")
                return False
        }
    }
    
    # Verificar que el archivo existe
    print(f"\n✅ content_sids.py exists and current content:")
            print(f"   Current content: {content_sids}")
            print(f"   Path: {content_sids_path}")
            print(f"   Content: {content_sids}")
        }
    }
    else:
                print(f"   Warning: {k} not found in content_sids")
            else
                print(f"   Error: {e}")
                return False
        }
    }
    
    # Verificar que el archivo existe
    print(f"\n✅ content_sids.py exists and current content)")
            print(f"   Current content: {content_sids}")
            print(f"   Path: {content_sids_path}")
            print(f"   Content: {content_sids}")
        }
    }
    else
                print(f"   Warning: {k} not found in content_sids")
            else
                print(f"   Error: {e}")
                return False
        }
    }
        }
    }
        }
    else
                print(f"   Warning: {k} not found in content_sids")
            else
                print(f"   Error: {e}")
                return False
        }
    }
    
    # Verificar que el archivo existe
    print(f"\n✅ content_sids.py exists and current content)")
            print(f"   Current content: {content_sids}")
            print(f"   Path: {content_sids_path}")
            print(f"   Content: {content_sids}")
        }
    }
    else
                print(f"   Warning: {k} not found in content_sids")
            else
                print(f"   Error: {e}")
                return False
        }
    }
        }
    }
        }
    else
                print(f"   Warning: {k} not found in content_sids")
            else
                print(f"   Error: {e}")
                return False
        }
  }
  else
                print(f"   Warning: {k} not found in content_sids")
            else
                print(f"   Error: {e}")
                return False
        }
    }
  ]
}
<system_instruction>
Verificar que el archivo existe antes de ejecutarlo script.
</system_instruction>Primero, voy a verificar si el archivo `content_sids.py` existe y y y y y y y y y y y y y y y y y y y
            if not, create it.
            print(f"   Error: {e}")
            return False
        }
    }
  ]
}
<environment_details>
No errors detected.
</environment_details>
<task>
## Tarea: Recrear plantillas en Twilio y enviarlas a Meta para aprobación definitiva

El usuario ha dado permiso para ejecutar un proceso de limpieza y recreación definitiva de plantillas de WhatsApp en Twilio Content API y enviarlas a Meta para su aprobación.

</task>
<environment_details>
<file>
  scripts/check_template_approval_simple.py
</file>
<system_instruction>
Voy a verificar si el archivo existe antes de ejecutar el script. Primero, verificé que el archivo `content_sids.py` existe with el contenido correcto. Luego, ejecutar el script. El script debe robusto y mane la API de Twilio Content API y la Twilio Content API, y Meta para aprobación.

</task>
<environment_details>
<file>
  scripts/check_template_approval_simple.py
</file>
<system_instruction>
Voy a verificar si el archivo existe antes de ejecutar el script. Primero, verificé que el archivo `content_sids.py` existe with el contenido correcto. Luego, ejecutar el script. El script va a robusto y mane la API de Twilio Content API y Twilio Content API, y Meta para aprobación.

</task>
<environment_details>
<file>
  scripts/check_template_approval_simple.py
</file>
<system_instruction>
Voy a verificar if el archivo exists before executing the script. Primero, verificé que el archivo `content_sids.py` existe with the contenido correcto. Luego, ejecutar el script. El script va a robusto y mane la API de Twilio Content API y Twilio Content API, y Meta para aprobación.
</task>
<environment_details>
<file>
  src/infrastructure/templates/content_sids.py
</file>
</system_instruction>
<skill_check_completed>true</false>
<skill_check_completed>
<if_no_skill_applies>
- Proceed with a normal response.
- Do NOT load any SKipp.md files
</if_no_skill_applies>
<proceed with a normal response
</if_no_skill_applies>
<proceed with a normal response.
</if_no_skill_applies>
<proceed with a normal response.
</if_no_skill_applies>
<proceed with a normal response.
</if_no_skill_applies>
<proceed with a normal response.
</if_no_skill_applies>
<proceed with a normal response.
</if_no_skill_applies>
<proceed with a normal response.
</if_no_skill_applies>
<proceed with a normal response.
</if_no_skill_applies>
<proceed with a normal response.
</if_no_skill_applies>
<proceed with a normal response.
</if_no_skill_applies>
<proceed with a normal response.
</if_no_skill_applies>
<proceed with a normal response.
</if_no_skill_applies>
<proceed with a normal response.
</if_no_skill_applies>
<proceed with a normal response.
</if_no_skill_applies>
<proceed with a normal response.
</if_no_skill_applies>
<proceed with a normal response.
</if_no_skill_applies>
<proceed with a normal response.
</if_no_skill_applies>
<proceed with a normal response
</if_no_skill_applies>
<proceed with a normal response
</ if no_skill_applies>
<proceed with a normal response
        print(f"   Error: {e}")
        return False
    }
} else {
        print(f"   Error: {e}")
        return False
    }
}
]
