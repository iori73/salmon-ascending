import { ReactNode } from "react";

/**
 * プルクオート。本文から引き上げた一節を、錆色の罫とともに見せる。
 * cite に出典（例: "Act I, The Memory of the Sea"）を渡すと斜体で添える。
 */
export default function PullQuote({
  children,
  cite,
}: {
  children: ReactNode;
  cite?: ReactNode;
}) {
  return (
    <blockquote className="pull-quote">
      <span>{children}</span>
      {cite && <cite>— {cite}</cite>}
    </blockquote>
  );
}
