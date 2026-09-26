/**
 * Jev System One TypeScript Client ⚡
 * Ultra-low latency typed decision engine for Node.js, Next.js, and Vercel Edge.
 * Author: Javohirbek Asqarov (Jasper) & Open Source Community
 */

export type JevQuestionType = "choice" | "noul" | "score";

export interface JevQuestion {
  name: string;
  type: JevQuestionType;
  options?: string[];
  min?: number;
  max?: number;
}

export interface JevQuestionResult {
  name: string;
  type: JevQuestionType;
  value: any;
  confidence: number;
  probabilities?: Record<string, number>;
}

export interface JevEvaluatePayload {
  state: Record<string, any>;
  questions: JevQuestion[];
  model?: string;
}

export interface JevDecisionResponse {
  id: string;
  model: string;
  results: Record<string, JevQuestionResult>;
  latencyMs: number;
}

export interface JevClientOptions {
  apiKey?: string;
  baseUrl?: string;
  backend?: "typesafe" | "openrouter" | "auto";
  timeoutMs?: number;
}

export class JevDecisionEngine {
  private apiKey: string;
  private baseUrl: string;
  private backend: "typesafe" | "openrouter";
  private timeoutMs: number;

  constructor(options: JevClientOptions = {}) {
    const tsKey = options.apiKey || (typeof process !== "undefined" ? process.env.TYPESAFE_API_KEY : undefined);
    const orKey = options.apiKey || (typeof process !== "undefined" ? process.env.OPENROUTER_API_KEY : undefined);

    if (options.backend === "openrouter" || (!tsKey && orKey)) {
      this.backend = "openrouter";
      this.apiKey = orKey || "";
      this.baseUrl = options.baseUrl || "https://openrouter.ai/api/v1";
    } else {
      this.backend = "typesafe";
      this.apiKey = tsKey || "";
      this.baseUrl = options.baseUrl || "https://api.typesafe.ai/v1";
    }

    this.timeoutMs = options.timeoutMs || 5000;
  }

  async evaluate(payload: JevEvaluatePayload): Promise<Record<string, JevQuestionResult>> {
    const startTime = performance.now();
    const model = payload.model || "jev-1.13";

    if (!this.apiKey) {
      return this.mockEvaluation(payload, startTime);
    }

    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), this.timeoutMs);

      if (this.backend === "typesafe") {
        const response = await fetch(`${this.baseUrl}/systemone`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${this.apiKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            model,
            state: payload.state,
            questions: payload.questions,
          }),
          signal: controller.signal,
        });

        clearTimeout(timer);
        if (!response.ok) {
          throw new Error(`TypeSafe API responded with status ${response.status}`);
        }

        const data = await response.json();
        return data.results;
      } else {
        // OpenRouter fallback
        const prompt = `State:\n${JSON.stringify(payload.state, null, 2)}\n\nQuestions:\n${JSON.stringify(
          payload.questions,
          null,
          2
        )}`;

        const response = await fetch(`${this.baseUrl}/chat/completions`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${this.apiKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            model: `typesafe/${model}`,
            messages: [{ role: "user", content: prompt }],
            response_format: { type: "json_object" },
          }),
          signal: controller.signal,
        });

        clearTimeout(timer);
        const data = await response.json();
        const content = data.choices[0].message.content;
        const parsed = typeof content === "string" ? JSON.parse(content) : content;

        const results: Record<string, JevQuestionResult> = {};
        for (const q of payload.questions) {
          const val = parsed[q.name];
          results[q.name] = {
            name: q.name,
            type: q.type,
            value: typeof val === "object" && val !== null ? val.value || val.choice : val,
            confidence: typeof val === "object" && val !== null ? val.confidence || 0.95 : 0.95,
          };
        }
        return results;
      }
    } catch (err) {
      console.warn("Jev evaluation error, fallback to deterministic mock:", err);
      return this.mockEvaluation(payload, startTime);
    }
  }

  private mockEvaluation(
    payload: JevEvaluatePayload,
    startTime: number
  ): Record<string, JevQuestionResult> {
    const results: Record<string, JevQuestionResult> = {};
    for (const q of payload.questions) {
      if (q.type === "choice") {
        results[q.name] = {
          name: q.name,
          type: "choice",
          value: q.options?.[0] || "DEFAULT",
          confidence: 0.98,
        };
      } else if (q.type === "noul") {
        results[q.name] = {
          name: q.name,
          type: "noul",
          value: true,
          confidence: 0.99,
        };
      } else {
        results[q.name] = {
          name: q.name,
          type: "score",
          value: ((q.min || 0) + (q.max || 10)) / 2,
          confidence: 0.94,
        };
      }
    }
    return results;
  }
}
