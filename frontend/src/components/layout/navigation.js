import { Search, GitCompareArrows, AlertTriangle, FileText } from "lucide-react";

// Main pages, in sidebar order: [key, label, icon].
export const PAGES = [
  ["explore", "Projects", Search],
  ["portfolio", "Portfolio", GitCompareArrows],
  ["risk", "Report changes", AlertTriangle],
  ["evidence", "Sources & gaps", FileText],
];

export const pageLabel = (key) => PAGES.find(([k]) => k === key)?.[1];
