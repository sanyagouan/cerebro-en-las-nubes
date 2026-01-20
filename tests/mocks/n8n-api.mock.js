/**
 * Mock de n8n API para testing
 * Simula las respuestas de la API de n8n
 */

/**
 * Mock de workflow de n8n
 */
export const mockN8nWorkflow = (overrides = {}) => {
  const defaults = {
    id: `${Math.floor(Math.random() * 1000)}`,
    name: 'Test Workflow',
    active: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    nodes: [
      {
        id: 'trigger',
        name: 'Webhook',
        type: 'n8n-nodes-base.webhook',
        typeVersion: 1,
        position: [250, 300],
        parameters: {
          path: 'test-webhook',
          httpMethod: 'POST',
        },
      },
    ],
    connections: {},
    settings: {
      executionOrder: 'v1',
    },
    staticData: null,
    tags: [],
  };

  return { ...defaults, ...overrides };
};

/**
 * Mock de ejecución de workflow
 */
export const mockN8nExecution = (overrides = {}) => {
  const defaults = {
    id: `${Math.floor(Math.random() * 10000)}`,
    finished: true,
    mode: 'webhook',
    retryOf: null,
    retrySuccessId: null,
    startedAt: new Date(Date.now() - 5000).toISOString(),
    stoppedAt: new Date().toISOString(),
    workflowId: '1',
    workflowData: mockN8nWorkflow(),
    data: {
      resultData: {
        runData: {
          Webhook: [
            {
              startTime: Date.now() - 5000,
              executionTime: 5000,
              data: {
                main: [
                  [
                    {
                      json: {
                        status: 'success',
                        message: 'Workflow executed successfully',
                      },
                    },
                  ],
                ],
              },
            },
          ],
        },
        lastNodeExecuted: 'Webhook',
      },
    },
  };

  return { ...defaults, ...overrides };
};

/**
 * Mock de credencial de n8n
 */
export const mockN8nCredential = (overrides = {}) => {
  const defaults = {
    id: `${Math.floor(Math.random() * 100)}`,
    name: 'Test Credential',
    type: 'httpBasicAuth',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  return { ...defaults, ...overrides };
};

/**
 * Mock de listado de workflows
 */
export const mockN8nWorkflowsList = (count = 3) => {
  return {
    data: Array.from({ length: count }, (_, i) =>
      mockN8nWorkflow({
        id: `${i + 1}`,
        name: `Workflow ${i + 1}`,
      })
    ),
  };
};

/**
 * Mock de listado de ejecuciones
 */
export const mockN8nExecutionsList = (count = 5) => {
  return {
    data: Array.from({ length: count }, (_, i) =>
      mockN8nExecution({
        id: `${i + 1}`,
      })
    ),
  };
};

/**
 * Mock de error de n8n API
 */
export const mockN8nError = (statusCode = 400, message = 'Bad Request') => {
  return {
    code: statusCode,
    message,
    hint: 'Check your request parameters',
  };
};

/**
 * Mock del cliente de n8n API completo
 */
export class MockN8nClient {
  constructor() {
    this.workflows = new Map();
    this.executions = new Map();
    this.credentials = new Map();
  }

  // Workflows
  async getWorkflows() {
    return {
      data: Array.from(this.workflows.values()),
    };
  }

  async getWorkflow(id) {
    const workflow = this.workflows.get(id);
    if (!workflow) throw new Error('Workflow not found');
    return workflow;
  }

  async createWorkflow(data) {
    const workflow = mockN8nWorkflow(data);
    this.workflows.set(workflow.id, workflow);
    return workflow;
  }

  async updateWorkflow(id, data) {
    const existing = this.workflows.get(id);
    if (!existing) throw new Error('Workflow not found');

    const updated = {
      ...existing,
      ...data,
      updatedAt: new Date().toISOString(),
    };
    this.workflows.set(id, updated);
    return updated;
  }

  async deleteWorkflow(id) {
    const existing = this.workflows.get(id);
    if (!existing) throw new Error('Workflow not found');

    this.workflows.delete(id);
    return { success: true };
  }

  async activateWorkflow(id) {
    return this.updateWorkflow(id, { active: true });
  }

  async deactivateWorkflow(id) {
    return this.updateWorkflow(id, { active: false });
  }

  // Executions
  async getExecutions(workflowId) {
    const executions = Array.from(this.executions.values())
      .filter(e => !workflowId || e.workflowId === workflowId);

    return {
      data: executions,
    };
  }

  async getExecution(id) {
    const execution = this.executions.get(id);
    if (!execution) throw new Error('Execution not found');
    return execution;
  }

  async deleteExecution(id) {
    const existing = this.executions.get(id);
    if (!existing) throw new Error('Execution not found');

    this.executions.delete(id);
    return { success: true };
  }

  // Credentials
  async getCredentials() {
    return {
      data: Array.from(this.credentials.values()),
    };
  }

  async getCredential(id) {
    const credential = this.credentials.get(id);
    if (!credential) throw new Error('Credential not found');
    return credential;
  }

  async createCredential(data) {
    const credential = mockN8nCredential(data);
    this.credentials.set(credential.id, credential);
    return credential;
  }

  async deleteCredential(id) {
    const existing = this.credentials.get(id);
    if (!existing) throw new Error('Credential not found');

    this.credentials.delete(id);
    return { success: true };
  }

  // Helpers
  reset() {
    this.workflows.clear();
    this.executions.clear();
    this.credentials.clear();
  }

  // Simular ejecución de workflow
  async executeWorkflow(workflowId, data = {}) {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) throw new Error('Workflow not found');

    const execution = mockN8nExecution({
      workflowId,
      workflowData: workflow,
      data: {
        resultData: {
          runData: {
            Webhook: [
              {
                startTime: Date.now(),
                executionTime: 100,
                data: {
                  main: [
                    [
                      {
                        json: data,
                      },
                    ],
                  ],
                },
              },
            ],
          },
        },
      },
    });

    this.executions.set(execution.id, execution);
    return execution;
  }
}

export default {
  mockN8nWorkflow,
  mockN8nExecution,
  mockN8nCredential,
  mockN8nWorkflowsList,
  mockN8nExecutionsList,
  mockN8nError,
  MockN8nClient,
};
