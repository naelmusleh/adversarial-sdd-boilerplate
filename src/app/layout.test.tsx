import { describe, expect, it } from "vitest";
import RootLayout, { metadata } from "@/app/layout";

describe("root layout", () => {
  it("provides the document language and body wrapper", () => {
    const layout = RootLayout({ children: <p>Route content</p> });
    expect(layout.props.lang).toBe("en");
    expect(layout.props.children.type).toBe("body");
    expect(layout.props.children.props.children.props.children).toBe("Route content");
  });

  it("defines neutral starter metadata", () => {
    expect(metadata).toMatchObject({
      title: "New application",
      description: "A new application built with the Adversarial SDD template.",
    });
  });
});
