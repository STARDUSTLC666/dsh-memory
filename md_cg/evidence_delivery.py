"""Experimental query-time text delivery. Pure functions; no production hooks.

The budget counts the actual rendered text, including metadata and separators,
using the project's token ESTIMATOR, not a model tokenizer. All excerpts point
to source character offsets and retain their source hash. No text is invented.
"""
from __future__ import annotations

import hashlib
import json
import re

from .mdcg import expand_query_terms
from .mdcos import est_tokens, excerpt_tokens

COMPACT_FIELDS = ('id', 'created_at', 'source', 'conditions', 'verification_state',
                  'qualification', 'effective_from', 'effective_until', 'believed_at')
PRESERVING_FIELDS = COMPACT_FIELDS + ('non_applicable_conditions',
    'verification_basis', 'version', 'source_version', 'observation_time_window',
    'condition_comment')


def query_excerpt(content, query, budget):
    if est_tokens(content) <= budget:
        return content, [{'start': 0, 'end': len(content)}]
    terms = tuple(dict.fromkeys(t.lower() for t in expand_query_terms(query) if t))[:64]
    # Bounded windows keep a single huge line from consuming all the budget.
    windows = []
    for match in re.finditer(r'[^\n]+(?:\n|$)', content):
        for start in range(match.start(), match.end(), 160):
            end = min(start + 240, match.end())
            block = content[start:end].lower()
            score = sum(1 for term in terms if term in block)
            windows.append((score, start, end))
    windows.sort(key=lambda w: (-w[0], w[1]))
    chosen = []
    for score, start, end in windows:
        if not score and chosen:
            continue
        if any(start < b and end > a for a, b in chosen):
            continue
        trial = sorted(chosen + [(start, end)])
        rendered = '\n[…]\n'.join(content[a:b] for a, b in trial)
        if est_tokens(rendered) <= budget:
            chosen = trial
    if not chosen:
        clipped = excerpt_tokens(content, budget)
        end = len(clipped[:-1]) if clipped.endswith('…') else len(clipped)
        return clipped, [{'start': 0, 'end': end}]
    text = '\n[…]\n'.join(content[a:b] for a, b in chosen)
    return text, [{'start': a, 'end': b} for a, b in chosen]


def deliver(rows, query, *, budget_tokens=240, max_item_tokens=120,
            mode='query_metadata'):
    """Consume production search_rrf rows, preserving their order and gates."""
    if mode not in ('prefix', 'query', 'query_metadata', 'query_metadata_compact',
                    'query_metadata_preserving'):
        raise ValueError('unknown delivery mode')
    if budget_tokens < 0 or max_item_tokens < 1:
        raise ValueError('invalid delivery budget')
    records, blocks = [], []
    fields = PRESERVING_FIELDS if mode == 'query_metadata_preserving' else COMPACT_FIELDS
    schema = ('memory_metadata_columns=' + json.dumps(fields, separators=(',', ':')) + '\n'
              if mode in ('query_metadata_compact', 'query_metadata_preserving') else '')

    def rendered(items):
        return schema + '\n\n'.join(items) if items else ''

    for node, score, qual, paths in rows:
        fm = node.get('frontmatter') or {}
        content = node.get('content') or ''
        metadata = {'id': node['id'], 'created_at': fm.get('created_at'),
                    'source': fm.get('source'), 'conditions': fm.get('condition_space'),
                    'verification_state': fm.get('verification_state', 'unverified'),
                    'qualification': qual.get('state')}
        for field in ('effective_from', 'effective_until', 'believed_at'):
            if fm.get(field) is not None:
                metadata[field] = fm[field]
        if mode == 'query_metadata_preserving':
            metadata['non_applicable_conditions'] = fm.get('non_applicable_conditions') or []
            for field in ('verification_basis', 'version', 'source_version'):
                metadata[field] = fm.get(field)
            metadata['condition_comment'] = (fm.get('state_attributes') or {}).get('comment')
            conditions = metadata['conditions']
            if isinstance(conditions, dict) and 'time_window' in conditions:
                metadata['conditions'] = {k: v for k, v in conditions.items() if k != 'time_window'}
                metadata['observation_time_window'] = conditions['time_window']
        header = (json.dumps(metadata, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
                  + '\n') if mode == 'query_metadata' else ''
        if mode in ('query_metadata_compact', 'query_metadata_preserving'):
            header = json.dumps([metadata.get(field) for field in fields],
                                ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n'
        remaining = budget_tokens - est_tokens(rendered(blocks))
        if schema and not blocks:
            remaining -= est_tokens(schema)
        room = min(max_item_tokens, remaining - est_tokens(header) - 2)
        if room < 8:
            continue
        if mode == 'prefix':
            excerpt = excerpt_tokens(content, room)
            end = len(excerpt[:-1]) if excerpt.endswith('…') else len(excerpt)
            spans = [{'start': 0, 'end': end}]
        else:
            excerpt, spans = query_excerpt(content, query, room)
        block = header + excerpt
        if est_tokens(rendered(blocks + [block])) > budget_tokens:
            continue
        blocks.append(block)
        records.append({'id': node['id'], 'metadata': metadata, 'spans': spans,
                        'source_sha256': hashlib.sha256(content.encode('utf-8')).hexdigest(),
                        'truncated': excerpt != content})
    text = rendered(blocks)
    return {'text': text, 'records': records, 'tokens_used': est_tokens(text),
            'budget': budget_tokens, 'mode': mode, 'token_measure': 'project_estimator'}


def preserving_recall(cg, recalled, query, *, budget_tokens=1200, max_item_tokens=450):
    """Opt-in D1: re-read authorized selected sources, retain native conditions.

Uses D's existing query windows. Partial selected sources are explicitly
INCOMPLETE, never certified as sufficient. Raw memory and ranking stay intact;
arbitrary JSON is not projected or summarized. The full wire object is budgeted
with the project estimator, not a promise about provider-billed token counts.
"""
    if type(budget_tokens) is not int or budget_tokens < 0:
        raise ValueError('invalid_evidence_budget')
    if type(max_item_tokens) is not int or max_item_tokens < 1:
        raise ValueError('invalid_evidence_item_budget')
    def count(value):
        return est_tokens(json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False))
    empty = {'text': '', 'evidence_status': 'INCOMPLETE', 'reason': 'budget_or_source_unavailable'}
    if count(empty) > budget_tokens:
        raise ValueError('budget_below_control_envelope_minimum')
    def defer(reason):
        value = {**empty, 'reason': reason}
        return value if count(value) <= budget_tokens else dict(empty)
    if recalled.get('recent'):
        return defer('recent_evidence_requires_original_delivery')
    rows, selected, seen = [], [], {}
    credential_keys = {'api_key', 'apikey', 'access_token', 'refresh_token',
                       'password', 'private_key', 'secret_key', 'credentials',
                       'credential', 'authorization', 'bearer_token'}
    def unsafe(value):
        if isinstance(value, dict):
            return any(str(k).lower().replace('-', '_') in credential_keys or unsafe(v)
                       for k, v in value.items())
        return isinstance(value, (list, tuple)) and any(unsafe(v) for v in value)
    for item in recalled.get('pack', []):
        node = cg.get(item['id'])  # Authoritative visibility/decryption gate.
        if node is None:
            return defer('visibility_changed_before_delivery')
        body, fm = node.get('content'), node.get('frontmatter') or {}
        if not isinstance(body, str) or len(body) > 1_000_000 or len(rows) >= 128:
            return defer('invalid_or_oversize_source')
        if unsafe({k: fm.get(k) for k in ('source', 'condition_space',
                   'non_applicable_conditions', 'verification_basis', 'version', 'source_version')}):
            return defer('disallowed_source_metadata')
        fingerprint = json.dumps([body, fm], ensure_ascii=False, sort_keys=True, allow_nan=False)
        if node['id'] in seen:
            if seen[node['id']] != fingerprint:
                return defer('same_id_source_changed')
            continue
        seen[node['id']] = fingerprint
        selected.append(node['id'])
        rows.append((node, 0, {'state': item.get('state')}, []))
    rendered = deliver(rows, query, budget_tokens=budget_tokens,
                       max_item_tokens=max_item_tokens, mode='query_metadata_preserving')
    records = [{k: r[k] for k in ('id', 'source_sha256', 'spans', 'truncated')}
               for r in rendered['records']]
    delivered = [r['id'] for r in records]
    incomplete = [id for id in selected if id not in delivered or
                  next(r['truncated'] for r in records if r['id'] == id)]
    value = {'text': rendered['text'], 'records': records, 'delivered_ids': delivered,
             'incomplete_ids': incomplete,
             'evidence_status': ('INCOMPLETE' if incomplete else
                                 'COMPLETE_SELECTED_SOURCES' if selected else 'INSUFFICIENT')}
    if count(value) > budget_tokens:
        return defer('serialized_response_exceeds_budget')
    return value
