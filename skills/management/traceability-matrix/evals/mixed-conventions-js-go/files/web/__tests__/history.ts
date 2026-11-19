import { newestFirst } from "../client/history";

describe("history", () => {
  it("R-021 lists points transactions newest first", () => {
    const sorted = newestFirst([
      { id: "a", postedAt: "2026-10-01", points: 10 },
      { id: "b", postedAt: "2026-10-03", points: 20 },
    ]);
    expect(sorted.map((t) => t.id)).toEqual(["b", "a"]);
  });
});
