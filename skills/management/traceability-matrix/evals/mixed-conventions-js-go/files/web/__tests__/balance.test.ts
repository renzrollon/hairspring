import { fetchBalance } from "../client/balance";

describe("balance", () => {
  it("R-020 returns posted and pending points separately", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      json: async () => ({ posted_points: 800, pending_points: 120 }),
    }) as unknown as typeof fetch;
    await expect(fetchBalance("M1")).resolves.toEqual({ posted: 800, pending: 120 });
  });
});
