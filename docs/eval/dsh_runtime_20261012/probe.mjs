import { readFileSync, writeFileSync } from 'node:fs'
import { createRequire } from 'node:module'
import { createHash } from 'node:crypto'
import { dirname, join } from 'node:path'
import { pathToFileURL } from 'node:url'
import assert from 'node:assert/strict'

export const name = 'memory-runtime-probe'
export const inject = ['tools', 'systemPrompt']
export function apply(ctx) {
  void (async () => {
    const started = Date.now()
    while (!ctx.tools.get('lingshu_cg')) {
      assert(Date.now() - started < 30000, 'DSH did not register lingshu_cg')
      await new Promise(resolve => setTimeout(resolve, 250))
    }
    const phase = process.env.DSH_PROBE_PHASE
    const report = { date: '2026-10-12', entrypoint: 'dsh --profile memory-lab', phase,
      actual_host_pipeline: 'ctx.tools.execute', remote_llm_used: false, calls: [], checks: [] }
    function check(name, condition) {
      assert(condition, name)
      report.checks.push({ name, passed: true })
    }
    async function call(name, args) {
      const start = performance.now()
      const result = await ctx.tools.execute({ callId: `memory-probe-${report.calls.length}`, name,
        arguments: args, signal: AbortSignal.timeout(30000) })
      const text = (result.content ?? []).filter(c => c.type === 'text').map(c => c.text).join('\n')
      let data
      try { data = JSON.parse(text) } catch { data = text }
      report.calls.push({ name, args, elapsed_ms: performance.now() - start, isError: result.isError,
        error: result.error, data })
      writeFileSync(process.env.DSH_PROBE_REPORT, JSON.stringify(report, null, 2) + '\n')
      assert.equal(result.isError, false, `${name} failed: ${text}`)
      return data
    }
    try {
      const require = createRequire(join(process.env.DSH_HOME, 'profiles', 'memory-lab', 'package.json'))
      report.runtime_packages = Object.fromEntries(['@deepseek-ai/dsh-tools', '@deepseek-ai/cordis',
        '@furongjun1999/dsh-memory'].map(name => {
        const localPlugin = name === '@furongjun1999/dsh-memory'
        const file = localPlugin
          ? join(process.env.DSH_HOME, 'profiles', 'memory-lab', 'node_modules', name, 'package.json')
          : join(dirname(dirname(require.resolve(name))), 'package.json')
        const entry = localPlugin ? join(dirname(file), 'lib/index.js') : require.resolve(name)
        return [name, { version: JSON.parse(readFileSync(file, 'utf-8')).version, manifest: file, entry }]
      }))
      const pluginFile = report.runtime_packages['@furongjun1999/dsh-memory'].entry
      const pluginRoot = new URL('../', pathToFileURL(pluginFile))
      report.python_sha256 = Object.fromEntries(['mdcg.py', 'mdcos.py', 'readcache.py'].map(name =>
        [name, createHash('sha256').update(readFileSync(new URL('md_cg/' + name, pluginRoot))).digest('hex')]))
      report.names = ctx.tools.schemas().map(t => t.name).filter(n => n.startsWith('lingshu_'))
      check('six plugin tools are registered in the actual DSH host', report.names.length === 6)
      const info = await call('lingshu_cg', { op: 'info' })
      check('DSH info reports the real isolated node count and tenant',
        typeof info.total_nodes === 'number' && info.security.tenant === 'default')
      const missing = await call('lingshu_mdcg_get', { node_id: 'dsh_probe_absent_000' })
      check('missing record has a structured not_found result', missing.ok === false && missing.error === 'not_found')

      const session = 'dsh-runtime-20261012'
      const excerptArgs = { query: 'anchorrecord', budget_tokens: 80, max_item_tokens: 80,
        causal: false, temporal: false, session }
      if (phase !== 'restart') {
        const write = await call('lingshu_mdcg_remember', { content_kind: 'text', content: 'anchorrecord '
          + 'a'.repeat(160) + ' evidenceKEEP42 ' + 'b'.repeat(400), node_id: 'dsh_runtime_excerpt',
          layer: 'knowledge', verification_basis: 'test', session, importance: 0.6 })
        check('remember commits the English record through DSH', write.ok === true && write.committed === true)
      }
      const excerpt = await call('lingshu_mdcg_recall', excerptArgs)
      const row = excerpt.pack.find(r => r.id === 'dsh_runtime_excerpt')
      check('80-token recall retains the previously cut-off evidence marker', row?.content.includes('evidenceKEEP42'))
      check('the entire excerpt including ellipsis fits the original token estimator',
        row.tokens === 80 && excerpt.tokens_used === 80 && Math.trunc(row.content.length / 4) + 1 === row.tokens)
      check('recall preserves unverified qualification rather than upgrading it',
        row.metadata.verification_state === 'unverified' && row.state === 'BLINDSPOT')
      const primitive = await call('lingshu_cg', { op: 'read', ...excerptArgs })
      check('the cg read primitive also retains the evidence marker',
        primitive.pack.some(r => r.id === row.id && r.content.includes('evidenceKEEP42')))
      const otherSession = await call('lingshu_mdcg_recall', { ...excerptArgs, session: 'another-dsh-test-session' })
      check('internal shared memory remains readable across query session declarations',
        otherSession.pack.some(r => r.id === row.id && r.frontmatter.session === session))
      const otherTimeline = await call('lingshu_stg', { op: 'timeline', limit: 10, session: 'another-dsh-test-session' })
      check('timeline session view excludes records attributed to another session', otherTimeline.items.length === 0)
      const zero = await call('lingshu_mdcg_recall', { ...excerptArgs, budget_tokens: 0 })
      check('zero budget returns no over-budget content', zero.tokens_used === 0 && zero.pack.length === 0)

      const ccg = '# 功能名：海棠计划缓存实测\n# 生效条件：查询隔离的测试计划窗口\n'
        + '# 子功能：窗口配置记录\n# 执行：返回当前窗口值，本条仅为隔离测试\n'
        + '# 验证方式：test，读取当前记录并比较窗口文本\n# 不适用条件：生产系统或真实用户数据\n'
      const oldBody = ccg + '缓存实测：海棠计划目前使用 quartzoldx77，夜间窗口十点，外部记录仅作测试。\n'
      const newBody = ccg + '缓存实测：海棠计划更新为 nebulaNEW900，夜间窗口十一点，外部记录仅作测试。\n'
      if (phase !== 'restart') {
        const rejected = await call('lingshu_cg', { op: 'write', content_kind: 'text',
          content: '缺少 CCG 六要素的隔离测试记录', node_id: 'dsh_runtime_invalid', layer: 'knowledge',
          verification_basis: 'test', session, importance: 0.5 })
        check('cg write still rejects a record lacking the project CCG requirements',
          rejected.ok === false && rejected.committed === false && rejected.moved_to === 'rejected')
        const written = await call('lingshu_cg', { op: 'write', content_kind: 'text', content: oldBody,
          node_id: 'dsh_runtime_cache', layer: 'knowledge', verification_basis: 'test', session, importance: 0.5 })
        check('the cg write primitive commits the Chinese record', written.ok === true && written.committed === true)
        const warm = []
        for (let i = 0; i < 3; i++) {
          const result = await call('lingshu_mdcg_search', { query: 'quartzoldx77', session, k: 10 })
          const item = result.results.find(r => r.node.id === 'dsh_runtime_cache')
          check(`warm query ${i + 1} returns the original text`, item?.node.content.includes('quartzoldx77'))
          warm.push({ id: item.node.id, score: item.score, state: item.state, content: item.node.content })
        }
        check('repeated warm queries preserve id, score, state and content',
          warm.every(r => JSON.stringify(r) === JSON.stringify(warm[0])))
        const updated = await call('lingshu_cg', { op: 'write', content_kind: 'text', content: newBody,
          node_id: 'dsh_runtime_cache', layer: 'knowledge', verification_basis: 'test', session, importance: 0.5 })
        check('default confirmation gate stages the update without silently committing',
          updated.ok === true && updated.committed === false && updated.moved_to === 'review_queue' && Boolean(updated.pid))
        const beforeApproval = await call('lingshu_mdcg_get', { node_id: 'dsh_runtime_cache' })
        check('before approval the old record remains intact', beforeApproval.content === oldBody)
        const accepted = await call('lingshu_cg', { op: 'review', pid: updated.pid, decision: 'accept',
          reason: 'Approve the isolated synthetic DSH runtime test update' })
        check('the existing review endpoint accepts the isolated update', accepted.ok === true)
      }
      const updatedSearch = await call('lingshu_mdcg_search', { query: 'nebulaNEW900', session, k: 10 })
      check('query after update sees the changed body',
        updatedSearch.results.some(r => r.node.id === 'dsh_runtime_cache' && r.node.content.includes('nebulaNEW900')))
      const oldSearch = await call('lingshu_mdcg_search', { query: 'quartzoldx77', session, k: 10 })
      check('old cache does not produce an obsolete exact hit',
        oldSearch.results.every(r => r.node.id !== 'dsh_runtime_cache'))
      const get = await call('lingshu_mdcg_get', { node_id: 'dsh_runtime_cache' })
      check('get returns the updated persisted body', get.content === newBody)
      const assembly = await ctx.systemPrompt.assemble({ signal: AbortSignal.timeout(30000) })
      const memory = assembly.contexts.find(c => c.name === 'lingshu:auto-recall')
      report.auto_recall_context = memory
      check('actual DSH prompt assembly includes the plugin memory block', Boolean(memory?.text))
      check('the automatically injected block marks memory as untrusted data',
        memory.text.includes('<untrusted-memory>') && memory.text.includes('</untrusted-memory>'))
      report.ok = true
      writeFileSync(process.env.DSH_PROBE_REPORT, JSON.stringify(report, null, 2) + '\n')
      console.log('DSH_MEMORY_PROBE ' + phase + ' passed ' + report.checks.length + ' checks')
    } catch (error) {
      report.ok = false
      report.failure = String(error)
      writeFileSync(process.env.DSH_PROBE_REPORT, JSON.stringify(report, null, 2) + '\n')
      console.error('DSH_MEMORY_PROBE_ERROR', error)
    }
  })().catch(err => console.error('DSH_MEMORY_PROBE_STARTUP_ERROR', err))
}
