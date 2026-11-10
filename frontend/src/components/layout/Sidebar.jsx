import { Shield } from "lucide-react";
import { PAGES } from "./navigation.js";
export function Sidebar({ page, onNavigate }) {
  return <header className="workspace-nav">
    <a className="workspace-brand" href="#" onClick={e => { e.preventDefault(); onNavigate("explore"); }}><Shield size={25} /><span>SENTINEL</span></a>
    <nav aria-label="Main navigation">{PAGES.map(([key, label]) => <button key={key} className={`workspace-link ${page === key ? "selected" : ""}`} aria-current={page === key ? "page" : undefined} onClick={() => onNavigate(key)}>{label}</button>)}</nav>
    <span className="workspace-purpose">Infrastructure monitoring</span>
  </header>;
}
