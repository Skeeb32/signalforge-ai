import { afterEach, describe, expect, it, vi } from "vitest";
import { api, percent } from "./lib";
describe("API contract", () => {
  afterEach(() => vi.unstubAllGlobals());
  it("formats measured probabilities", () => {
    expect(percent(0.1234)).toBe("12.3%");
  });
  it("surfaces server errors instead of showing invented data", async () => {
    vi.stubGlobal("sessionStorage", { getItem: () => null });
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        text: async () => "Model missing",
      }),
    );
    await expect(api("/model/info")).rejects.toThrow("503");
  });
  it("submits prediction JSON with optional session authentication", async () => {
    vi.stubGlobal("sessionStorage", { getItem: () => "test-key" });
    const fetch = vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => ({ prediction: 0.4 }) });
    vi.stubGlobal("fetch", fetch);
    expect(await api("/predict", { customer_id: "C1" })).toEqual({
      prediction: 0.4,
    });
    expect(fetch.mock.calls[0][1].headers["X-API-Key"]).toBe("test-key");
  });
});
