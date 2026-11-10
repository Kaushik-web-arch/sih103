# Option B project workspace

Implemented 10 November 2026 in sih103, continuing the existing React frontend.

## Interaction

- Projects is the entry page. Search names or filter by project code, then select a result.
- Desktop shows results alongside Overview, History and Source tabs. Narrow screens stack the details below results and scroll to the selected project.
- Navigation uses Projects, Portfolio, Report changes and Sources & gaps. Existing API endpoints and page behavior remain intact.
- Keyboard users can skip to content, navigate detail tabs with arrows/Home/End, and close details with focus restored to the opener.
- White/cobalt styling includes a dark theme, responsive tables and reduced-motion support.

Reference examples remain explicitly labelled. Source values, literal zeros, unknown values, warnings and dataset revision pinning are preserved. No forecasts or prediction accuracy are introduced by this UI change.

## Verification

Passed in the remote Linux workspace:

- 11 frontend contract tests, no skips.
- Vite production build.
- Existing risk browser smoke: connection, source evidence, filters and history drilldown.
- New workspace browser smoke: selection, desktop split layout, History/Source tabs, search reset, theme switching, mobile overflow and navigation across all four pages.
- Visual review of browser screenshots, including desktop project details and mobile portfolio.

Run from the repository root after installing frontend dependencies:

```sh
npm --prefix frontend test
npm --prefix frontend run build
node frontend/tests/risk-browser-smoke.mjs
node frontend/tests/workspace-browser-smoke.mjs
```

Both browser checks are included in the existing integration workflow. These local UI checks use reference fixtures and do not establish live database or Windows-browser verification. The integration workflow separately checks PostgreSQL-backed backend behavior.
