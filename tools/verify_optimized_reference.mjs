// Independent upstream decoder, read-only. No package installation required.
// node --experimental-vm-modules tools/verify_optimized_reference.mjs <watchface-js>
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';

const root = path.resolve(process.argv[2]);
const cache = new Map();
async function moduleAt(filename) {
  if (!path.extname(filename)) filename += '.js';
  if (cache.has(filename)) return cache.get(filename);
  const source = fs.readFileSync(filename, 'utf8');
  const m = filename.endsWith('.json')
    ? new vm.SyntheticModule(['default'], function () { this.setExport('default', JSON.parse(source)); }, {identifier: filename})
    : new vm.SourceTextModule(source, {identifier: filename});
  cache.set(filename, m);
  await m.link(specifier => moduleAt(path.resolve(path.dirname(filename), specifier)));
  return m;
}
const parser = await moduleAt(path.join(root, 'src/watchFaceBinTools/watchFaceBinParser.js'));
await parser.evaluate();
const model = parser.namespace.getAvailableModels().find(m => m.id === 'amazfittrexpro');
function parse(file) {
  const raw = fs.readFileSync(file);
  return parser.namespace.parseWatchFaceBin(raw.buffer.slice(raw.byteOffset, raw.byteOffset + raw.byteLength), model.fileType);
}
const before = parse('out/fastabiqulkhairat.bin');
const after = parse('out/fastabiqulkhairat-optimized.bin');
assert.deepEqual(after.parameters, before.parameters);
assert.equal(after.images.length, before.images.length);
for (let i = 0; i < before.images.length; i++) {
  assert.equal(after.images[i].width, before.images[i].width);
  assert.equal(after.images[i].height, before.images[i].height);
  assert.deepEqual(Buffer.from(after.images[i].pixels), Buffer.from(before.images[i].pixels));
}
const report = {
  decoder: 'Nadeflore/watchface-js',
  revision: execFileSync('git', ['-C', root, 'rev-parse', 'HEAD'], {encoding:'utf8'}).trim(),
  parameter_identity: true, images_verified: after.images.length, max_pixel_delta: 0,
  device_compatibility_verified: false,
};
fs.writeFileSync('out/optimization-reference-check.json', JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
