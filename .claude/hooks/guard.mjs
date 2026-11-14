#!/usr/bin/env node
// PreToolUse guard for Edit|Write|MultiEdit. No dependencies.
//  - deny: generated build output (backend/static/frontend/, backend/staticfiles/)
//  - ask:  assigning `.status` in backend/apps/**/*.py outside services.py, tests.py, migrations
//          (CLAUDE.md convention 1; ask rather than deny because the ProductUnit manual
//          add/edit views are a documented exception)
// Anything else, or any unexpected input, produces no output so the normal permission flow applies.

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => (raw += chunk));
process.stdin.on('end', () => {
  let input;
  try {
    input = JSON.parse(raw.replace(/^﻿/, '')); // tolerate a UTF-8 BOM
  } catch {
    process.exit(0); // fail open on unparseable input
  }

  const ti = (input && input.tool_input) || {};
  const filePath = typeof ti.file_path === 'string' ? ti.file_path : '';
  if (!filePath) process.exit(0);

  // Normalize Windows paths: backslashes -> slashes, lowercase for comparison.
  const p = filePath.replace(/\\/g, '/').replace(/\/{2,}/g, '/').toLowerCase();

  const respond = (decision, reason) => {
    const out = JSON.stringify({
      hookSpecificOutput: {
        hookEventName: 'PreToolUse',
        permissionDecision: decision,
        permissionDecisionReason: reason,
      },
    });
    // Exit only after stdout is flushed so the decision is never truncated.
    process.stdout.write(out, () => process.exit(0));
  };

  // 1. Generated files: hard block.
  if (p.includes('/backend/static/frontend/') || p.includes('/backend/staticfiles/')) {
    return respond(
      'deny',
      'Generated build output (backend/static/frontend/ and backend/staticfiles/) must not be edited by hand (AGENTS.md). Edit the source in frontend/src/ and rebuild with `npm run build` instead.',
    );
  }

  // 2. ProductUnit status assignment outside services.py.
  const base = p.slice(p.lastIndexOf('/') + 1);
  const inApps = p.includes('/backend/apps/') && p.endsWith('.py');
  const exempt = base === 'services.py' || base === 'tests.py' || p.includes('/migrations/');
  if (inApps && !exempt) {
    // Text being added: Write.content, Edit.new_string, MultiEdit.edits[].new_string
    const added = [];
    if (typeof ti.content === 'string') added.push(ti.content);
    if (typeof ti.new_string === 'string') added.push(ti.new_string);
    if (Array.isArray(ti.edits)) {
      for (const e of ti.edits) if (e && typeof e.new_string === 'string') added.push(e.new_string);
    }
    if (added.some((t) => /\.status\s*=(?!=)/.test(t))) {
      return respond(
        'ask',
        'This edit assigns `.status` outside services.py. CLAUDE.md convention 1: never mutate ProductUnit.status outside services.py; call a services.py function (atomic, select_for_update, StockMovement). Approve only if this is the documented exception (ProductUnitListCreateAPIView / ProductUnitDetailAPIView manual add/edit) or not a ProductUnit.',
      );
    }
  }

  process.exit(0);
});
