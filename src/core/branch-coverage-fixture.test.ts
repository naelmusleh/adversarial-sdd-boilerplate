import { describe, expect, it } from "vitest";
import { branchCoverageFixture } from "./branch-coverage-fixture";

describe("branch coverage failure fixture", () => {
  it("covers both outcomes in the first nine branches and one in the last", () => {
    expect(branchCoverageFixture(Array(10).fill(true))).toEqual(Array(10).fill("a"));
    expect(branchCoverageFixture([...Array(9).fill(false), true])).toEqual([
      ...Array(9).fill("b"),
      "a",
    ]);
  });
});
