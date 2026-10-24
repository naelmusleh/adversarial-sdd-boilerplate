import { describe, expect, it } from "vitest";

type BoundaryRule = (value: number, limit: number) => boolean;

const boundaryRule: BoundaryRule = (value, limit) => {
  if (value < limit) return true;
  if (value === limit) return true;
  return false;
};

const boundaryMutant: BoundaryRule = (value, limit) => {
  if (value < limit) return true;
  if (value === limit) return false;
  return false;
};

function observedOutcome(rule: BoundaryRule, asserting: boolean): "pass" | "fail" {
  try {
    const outcomes = [rule(9, 10), rule(10, 10), rule(11, 10)];
    if (asserting && outcomes.join(",") !== "true,true,false") {
      throw new Error(`unexpected boundary outcomes: ${outcomes.join(",")}`);
    }
  } catch {
    return "fail";
  }
  return "pass";
}

describe("FW-028 controlled anti-gaming matrix: TypeScript/Vitest", () => {
  it("call-only execution does not distinguish the boundary mutant, assertions do", () => {
    expect(observedOutcome(boundaryRule, false)).toBe("pass");
    expect(observedOutcome(boundaryMutant, false)).toBe("pass");
    expect(observedOutcome(boundaryRule, true)).toBe("pass");
    expect(observedOutcome(boundaryMutant, true)).toBe("fail");
  });
});
