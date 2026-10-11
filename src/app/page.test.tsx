import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HomePage from "@/app/page";

describe("starter home page", () => {
  it("communicates the neutral starting point and links to project guidance", () => {
    render(<HomePage />);
    expect(screen.getByRole("heading", { name: "Start with a clear product contract." })).toBeInTheDocument();
    expect(screen.getByText(/intentionally neutral/)).toBeInTheDocument();
    expect(screen.getByText(/defining the user, problem, and outcome/)).toBeInTheDocument();
  });
});
