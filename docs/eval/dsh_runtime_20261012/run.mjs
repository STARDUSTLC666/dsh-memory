/** Install the actual package in a new DSH profile and exercise its real tools. */
import { closeSync, copyFileSync, existsSync, mkdirSync, mkdtempSync, openSync, readFileSync, writeFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { dirname, join, resolve } from 'node:path'
import { spawn, spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { parseArgs } from 'node:util'

const { values } = parseArgs({ options: {
  cli: { type: 'string' }, package: { type: 'string' }, python: { type: 'string' },
  workspace: { type: 'string' }, port: { type: 'string', default: '13088' },
  output: { type: 'string' }, help: { type: 'boolean', default: false },
} })
if (values.help) {
  console.log('node run.mjs --cli <dsh/lib/bin.js> --package <memory.tgz> --python <python.exe> --workspace <test-parent> --output <report.json> [--port 13088]')
  process.exit(0)
}
for (const name of ['cli', 'package', 'python', 'workspace', 'output']) {
  if (!values[name]) throw new Error('--' + name + ' is required')
}
const cli = resolve(values.cli)
const packageFile = resolve(values.package)
const python = resolve(values.python)
const workspace = resolve(values.workspace)
const output = resolve(values.output)
mkdirSync(workspace, { recursive: true })
const lab = mkdtempSync(join(workspace, 'dsh-memory-'))
const home = join(lab, 'home')
const env = { ...process.env }
for (const name of Object.keys(env)) {
  if (name.startsWith('DSH_') || name.startsWith('MDCG_') || name === 'DEEPSEEK_API_KEY') delete env[name]
}
Object.assign(env, { DSH_HOME: home, MDCG_AUX_ROOT: join(lab, 'credentials'),
  MDCG_STATE_ROOT: join(lab, 'state'), MDCG_ROOT: join(lab, 'state/cg'),
  MDCG_READ_CACHE: '1', MDCG_HOTCACHE: '0', MDCG_FRESHNESS: '0', MDCG_UNIFY_QUERY: '0',
  MDCG_EN_ATOMS: '0', MDCG_SEMANTIC: '0', MDCG_AUTO_ISSUE: '1', MDCG_AUTONOMY: 'confirm',
  DSH_DISABLE_TELEMETRY: '1', PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8',
  TEMP: join(lab, 'temp'), TMP: join(lab, 'temp') })
mkdirSync(env.TEMP, { recursive: true })

function command(args, logName) {
  const log = openSync(join(lab, logName), 'w')
  try {
    const result = spawnSync(process.execPath, [cli, ...args], { cwd: lab, env,
      stdio: ['ignore', log, log], windowsHide: true, timeout: 60000 })
    if (result.error) throw result.error
    if (result.status !== 0) throw new Error('DSH command failed; inspect ' + join(lab, logName))
  } finally { closeSync(log) }
}
command(['--profile', 'memory-lab', '--from-default-profile', 'web', '--dump-config'], 'profile.log')
command(['plugin', '--profile', 'memory-lab', 'add', packageFile, '--ignore-scripts'], 'install.log')
const profile = join(home, 'profiles/memory-lab')
const probe = join(profile, 'memory-runtime-probe.mjs')
copyFileSync(fileURLToPath(new URL('./probe.mjs', import.meta.url)), probe)
const patch = join(lab, 'runtime.patch.yml')
writeFileSync(patch, JSON.stringify([
  { id: 'furongjun1999-dsh-memory', config: {
    python, tools: ['cg', 'stg', 'mdcg_remember', 'mdcg_recall', 'mdcg_search', 'mdcg_get'],
    dbPath: join(lab, 'state/legacy.db'),
    mdcg: { enabled: true, root: env.MDCG_ROOT, actor: 'dsh-runtime-probe', tenant: 'default', clearance: 'internal' },
    memory: { userMessage: false, assistantMessage: false, toolResult: false, autoRecall: true,
      auditPath: join(lab, 'hook-audit.json'), contextWindow: { enabled: false, turns: 10 } },
    mutual: { enabled: false },
  } },
  { insert: [{ id: 'memory-runtime-probe', name: probe.replaceAll('\\', '/') }] },
], null, 2) + '\n')

const report = { date: '2026-10-12', started_at: new Date().toISOString(), ok: false,
  package_sha256: createHash('sha256').update(readFileSync(packageFile)).digest('hex'),
  node: process.version, platform: process.platform, remote_llm_used: false, phases: {} }
const delay = ms => new Promise(resolve => setTimeout(resolve, ms))
async function phase(name) {
  const resultFile = join(lab, name + '.json')
  const stdout = openSync(join(lab, name + '.stdout.log'), 'w')
  const stderr = openSync(join(lab, name + '.stderr.log'), 'w')
  const child = spawn(process.execPath, [cli, '--profile', 'memory-lab', '--patch', patch,
    '--no-open', '--port', values.port], { cwd: lab, env: { ...env,
      DSH_PROBE_PHASE: name, DSH_PROBE_REPORT: resultFile },
    stdio: ['ignore', stdout, stderr], windowsHide: true })
  closeSync(stdout)
  closeSync(stderr)
  let spawnError
  child.once('error', error => { spawnError = error })
  try {
    const deadline = Date.now() + 90000
    while (Date.now() < deadline) {
      if (spawnError) throw spawnError
      if (existsSync(resultFile)) {
        let result
        try { result = JSON.parse(readFileSync(resultFile, 'utf-8')) } catch { /* Writer has not finished this snapshot. */ }
        if (result?.ok !== undefined) {
          report.phases[name] = result
          if (!result.ok) throw new Error(name + ': ' + result.failure)
          console.log(name + ': ' + result.checks.length + ' checks, ' + result.calls.length + ' real DSH tool calls')
          return
        }
      }
      if (child.exitCode !== null) throw new Error('DSH exited before ' + name + ' finished; inspect ' + lab)
      await delay(250)
    }
    throw new Error('DSH probe timed out; inspect ' + lab)
  } finally {
    if (child.exitCode === null) {
      child.kill('SIGINT')
      await Promise.race([new Promise(resolve => child.once('exit', resolve)), delay(5000)])
      if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL')
    }
  }
}

// Public evidence preserves all test data and readings; local absolute roots are placeholders.
function publicValue(value) {
  if (Array.isArray(value)) return value.map(publicValue)
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([k,v]) => [k, publicValue(v)]))
  if (typeof value !== 'string') return value
  const harness = resolve(dirname(cli), '../../..')
  for (const [path, label] of [[lab, '${LAB}'], [harness, '${HARNESS}'], [python, '${PYTHON}']]) {
    value = value.replaceAll(path, label).replaceAll(path.replaceAll('\\', '/'), label).replaceAll(path.replaceAll('/', '\\'), label)
  }
  return value
}
try {
  await phase('functional')
  await phase('restart')
  const firstPid = report.phases.functional.calls[0].data.os.sustain.heartbeat.pid
  const secondPid = report.phases.restart.calls[0].data.os.sustain.heartbeat.pid
  if (firstPid === secondPid) throw new Error('The second phase did not start a new Python process')
  report.restart_uses_new_python_process = true
  report.total_checks = Object.values(report.phases).reduce((sum, p) => sum + p.checks.length, 0)
  report.total_tool_calls = Object.values(report.phases).reduce((sum, p) => sum + p.calls.length, 0)
  report.ok = true
} catch (error) {
  report.failure = String(error)
  process.exitCode = 1
} finally {
  report.finished_at = new Date().toISOString()
  mkdirSync(dirname(output), { recursive: true })
  writeFileSync(output, JSON.stringify(publicValue(report), null, 2) + '\n')
  console.log((report.ok ? 'PASS' : 'FAIL') + '; report=' + output + '; private logs and isolated synthetic store=' + lab)
}
