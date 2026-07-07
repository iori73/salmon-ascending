import { ReactNode } from "react";

interface SideNoteProps {
  /** 見出し（例: 註・出典） */
  label?: string;
  children: ReactNode;
}

/**
 * 本文から分離した技術的注記・出典の受け皿（章末の「註」ブロック）。
 * 本文の流れを妨げずに典拠を担保する。
 */
export default function SideNote({ label = "註・出典", children }: SideNoteProps) {
  return (
    <aside className="footnotes">
      <p className="footnotes-label mb-3">{label}</p>
      <div className="editorial-note space-y-2">{children}</div>
    </aside>
  );
}
