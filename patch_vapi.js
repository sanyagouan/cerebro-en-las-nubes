const fs = require('fs');
const https = require('https');

const token = 'c5eefe50-cd80-41ac-9d64-fb7cccc2d5f6';

function patchEntity(path, payload) {
    return new Promise((resolve, reject) => {
        const body = JSON.stringify(payload);
        const req = https.request({
            hostname: 'api.vapi.ai',
            path: path,
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json; charset=utf-8',
                'Content-Length': Buffer.byteLength(body, 'utf8')
            }
        }, res => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(JSON.parse(data)));
        });
        req.on('error', reject);
        req.write(body);
        req.end();
    });
}

async function run() {
    try {
        console.log("Patching assistant...");
        const assRes = await patchEntity('/assistant/9a1f2df2-1c2d-4061-b11c-bdde7568c85d', {
            transcriber: { provider: 'deepgram', model: 'nova-2', language: 'es' },
            voice: { provider: '11labs', voiceId: 'cgSgspJ2msm6clMCkdW9', model: 'eleven_multilingual_v2', stability: 0.5, similarityBoost: 0.75 }
        });
        console.log("Assistant patched:", assRes.id);

        const tools = [
            { id: '7d7ddadf-759d-4414-a4d0-7f8191d183a2', msg: 'Dame un momento para buscar esa información.' },
            { id: '7cf36f29-2f03-4173-903e-dae1e1b416fa', msg: 'Un segundo, voy a comprobar nuestros horarios.' },
            { id: '836b5649-4087-40dd-83c8-7f0c640a3a3e', msg: 'Un momento por favor, estoy procesando tu reserva.' },
            { id: '6e6b8cca-99cd-4ce0-84b2-4cc9b423be9e', msg: 'Dame un segundo, voy a revisar la disponibilidad de mesas.' }
        ];

        for (const t of tools) {
            console.log("Patching tool", t.id);
            await patchEntity(`/tool/${t.id}`, {
                server: {
                    url: "https://go84sgscs4ckcs08wog84o0o.app.generaia.site/vapi/tools/" + (t.id === '7d7ddadf-759d-4414-a4d0-7f8191d183a2' ? 'get_info' : t.id === '7cf36f29-2f03-4173-903e-dae1e1b416fa' ? 'get_horarios' : t.id === '836b5649-4087-40dd-83c8-7f0c640a3a3e' ? 'create_reservation' : 'check_availability'),
                    timeoutSeconds: 20
                },
                messages: [{ type: 'request-start', content: t.msg }]
            });
        }
        console.log("All tools patched.");
    } catch (e) {
        console.error(e);
    }
}
run();
