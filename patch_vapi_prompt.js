const axios = require('axios');

const VAPI_KEY = 'c5eefe50-cd80-41ac-9d64-fb7cccc2d5f6';
const ASSISTANT_ID = '9a1f2df2-1c2d-4061-b11c-bdde7568c85d';

async function updatePrompt() {
    try {
        // 1. Get current assistant 
        const res = await axios.get(`https://api.vapi.ai/assistant/${ASSISTANT_ID}`, {
            headers: { Authorization: `Bearer ${VAPI_KEY}` }
        });

        let assistant = res.data;
        let currentMessage = "";

        if (assistant.model && assistant.model.messages && assistant.model.messages.length > 0) {
            currentMessage = assistant.model.messages[0].content;
        }

        if (!currentMessage) {
            console.log("No current message found.");
            return;
        }

        // 2. Add current date logic if not present
        if (!currentMessage.includes("{{now}}")) {
            const dateString = "\n\nINFORMACIÓN DE SISTEMA: La hora y fecha actual exacta es: {{now}}. Utiliza siempre esta fecha como referencia para 'hoy', 'mañana', o buscar turnos disponibles sin equivocarte de año.\n\n";
            currentMessage = dateString + currentMessage;

            console.log("Patching assistant to include {{now}}...");
            const patchRes = await axios.patch(`https://api.vapi.ai/assistant/${ASSISTANT_ID}`, {
                model: {
                    ...assistant.model,
                    messages: [
                        { role: "system", content: currentMessage }
                    ]
                }
            }, {
                headers: { Authorization: `Bearer ${VAPI_KEY}` }
            });
            console.log("Assistant patched successfully!", patchRes.data.id);
        } else {
            console.log("System prompt already contains {{now}}.");
        }

    } catch (error) {
        console.error("Error:", error.response ? error.response.data : error.message);
    }
}

updatePrompt();
