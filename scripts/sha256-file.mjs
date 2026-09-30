import { createReadStream } from 'node:fs';
import { createHash } from 'node:crypto';

/** Hash arbitrarily large archives without allocating a whole-file Buffer. */
export async function sha256File(filename) {
  const hash = createHash('sha256');
  for await (const chunk of createReadStream(filename)) hash.update(chunk);
  return hash.digest('hex');
}
