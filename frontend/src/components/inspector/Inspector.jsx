import { useState, useEffect, useRef } from "react";
import { ArrowRight, X, AlertTriangle, CalendarDays, Download, MapPin } from "lucide-react";
import { pretty, monthLabel } from "../../utils/format.js";
import { useRequest } from "../../hooks/useRequest.js";
import { SectorIcon } from "../common/SectorIcon.jsx";
import { ErrorBox } from "../common/ErrorBox.jsx";
import { Loading } from "../common/Loading.jsx";
import { Warnings } from "../common/Warnings.jsx";
import { ValueCard } from "./ValueCard.jsx";
import { History } from "./History.jsx";
import { Provenance } from "./Provenance.jsx";

export function Inspector({ selection, client, mode, onClose, onSelect, embedded = false }) {
  const [tab, setTab] = useState(selection.tab || "overview");
  const ref = useRef();
  const { result, loading, error } = useRequest(
    client,
    `/projects/${encodeURIComponent(selection.code)}`,
    { report_month: selection.month },
  );
  useEffect(() => {
    if (embedded) {
      const previous = document.activeElement;
      const panel = ref.current;
      panel?.focus({ preventScroll: true });
      if (window.matchMedia("(max-width: 1000px)").matches) {
        panel?.scrollIntoView({ block: "start", behavior: "instant" });
      }
      return () => { if (panel?.contains(document.activeElement) && previous?.isConnected) previous.focus({ preventScroll: true }); };
    }
    const prev = document.activeElement;
    ref.current?.focus();
    const fn = (e) => {
      if (e.key === "Escape") onClose();
      if (e.key === "Tab") {
        const nodes = [
          ...ref.current.querySelectorAll(
            'button:not(:disabled),input,select,summary,a,[tabindex="0"]',
          ),
        ].filter((x) => x.getClientRects().length);
        const first = nodes[0],
          last = nodes.at(-1);
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };
    document.addEventListener("keydown", fn);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", fn);
      document.body.style.overflow = "";
      prev?.focus();
    };
  }, [embedded]);
  const s = result?.data;
  const download = () => {
    const u = URL.createObjectURL(
      new Blob([JSON.stringify(result, null, 2)], { type: "application/json" }),
    );
    const a = document.createElement("a");
    a.href = u;
    a.download = `sentinel-${selection.code}-${selection.month}.json`;
    a.click();
    URL.revokeObjectURL(u);
  };
  return (
    <div
      className={embedded ? "detail-pane" : "drawer-backdrop"}
      onMouseDown={(e) => {
        if (!embedded && e.target === e.currentTarget) onClose();
      }}
    >
      <section
        className="drawer"
        ref={ref}
        role={embedded ? "region" : "dialog"}
        aria-modal={embedded ? undefined : true}
        aria-labelledby="inspector-title"
        tabIndex={-1}
      >
        <div className="drawer-top">
          <span className="eyebrow">PROJECT / {selection.code}</span>
          <div>
            {s && (
              <button
                className="icon-button"
                aria-label="Download snapshot JSON"
                onClick={download}
              >
                <Download size={18} />
              </button>
            )}
            <button
              className="icon-button"
              aria-label="Close inspector"
              onClick={onClose}
            >
              <X size={21} />
            </button>
          </div>
        </div>
        <h2 id="inspector-title">
          {s?.identity.project_name || `Project ${selection.code}`}
        </h2>
        <div className="drawer-subtitle">
          <MapPin size={15} />
          {s?.identity.state || "Reported identity"}
          <span>·</span>
          {monthLabel(selection.month)}
        </div>
        <div className="drawer-tabs" role="tablist" aria-label="Project detail views" onKeyDown={(e) => {
          const tabs = ["overview", "history", "provenance"];
          const index = tabs.indexOf(tab);
          const next = e.key === "ArrowRight" ? (index + 1) % 3 : e.key === "ArrowLeft" ? (index + 2) % 3 : e.key === "Home" ? 0 : e.key === "End" ? 2 : null;
          if (next !== null) { e.preventDefault(); setTab(tabs[next]); e.currentTarget.querySelectorAll('[role="tab"]')[next].focus(); }
        }}>
          {["overview", "history", "provenance"].map((t) => (
            <button
              role="tab"
              id={`detail-tab-${t}`}
              aria-controls="detail-content"
              tabIndex={tab === t ? 0 : -1}
              aria-selected={tab === t}
              key={t}
              onClick={() => setTab(t)}
            >
              {t === "provenance" ? "Source" : pretty(t)}
            </button>
          ))}
        </div>
        <div className="drawer-body" id="detail-content" role="tabpanel" aria-labelledby={`detail-tab-${tab}`}>
          {tab === "history" ? (
            <History
              client={client}
              code={selection.code}
              mode={mode}
              onMonth={(m) => {
                onSelect({ ...selection, month: m });
                setTab("overview");
              }}
            />
          ) : loading ? (
            <Loading />
          ) : error ? (
            <ErrorBox error={error} />
          ) : tab === "provenance" ? (
            <Provenance s={s} meta={result.meta} />
          ) : (
            <>
              <span className="badge green">
                <SectorIcon name={s.identity.sector} size={13} />
                {s.identity.sector}
              </span>
              <div className="value-grid">
                {[
                  "physical_progress_pct",
                  "cumulative_expenditure_rs_crore",
                  "original_cost_rs_crore",
                  "revised_cost_rs_crore",
                ].map((f) => (
                  <ValueCard field={f} value={s.values[f]} key={f} />
                ))}
              </div>
              {s.values.revised_cost_rs_crore.normalized === "0" &&
                s.report_month === "2026-08" && (
                  <div className="notice amber">
                    <AlertTriangle size={17} />
                    <p>
                      August reports a literal revised-cost zero. It is
                      preserved as published; baseline comparisons require
                      review.
                    </p>
                  </div>
                )}
              <h3 className="subheading">Dates & identifiers</h3>
              <div className="value-grid compact">
                {[
                  "approval_date",
                  "start_date",
                  "original_target_doc",
                  "revised_doc",
                  "legacy_ocms_code",
                  "pmgid",
                ].map((f) => (
                  <ValueCard field={f} value={s.values[f]} key={f} />
                ))}
              </div>
              <h3 className="subheading">Reported identity</h3>
              <div className="definition-list">
                {["agency", "ministry", "state"].map((f) => (
                  <div key={f}>
                    <span>{pretty(f)}</span>
                    <strong>{s.identity[f]}</strong>
                  </div>
                ))}
              </div>
              <Warnings
                items={[...s.quality.snapshot_flags, ...result.warnings]}
                title="Warnings retained from source"
              />
              {s.quality.source_notes?.length > 0 && (
                <details>
                  <summary>Linked source notes</summary>
                  <pre>{JSON.stringify(s.quality.source_notes, null, 2)}</pre>
                </details>
              )}
              <button className="button wide" onClick={() => setTab("history")}>
                <CalendarDays size={16} />
                Explore monthly history
                <ArrowRight size={16} />
              </button>
              <p className="hint">
                Raw and normalized values are shown together. Unknown never
                becomes zero.
              </p>
              <details>
                <summary>Exact response JSON</summary>
                <pre>{JSON.stringify(result, null, 2)}</pre>
              </details>
            </>
          )}
        </div>
      </section>
    </div>
  );
}
