#!/usr/bin/env node

'use strict';

const path = require('path');
const { execFileSync } = require('child_process');

// Platform to binary name mapping
const PLATFORM_MAP = {
  'win32-x64': 'adp.exe',
  'linux-x64': 'adp',
  'linux-arm64': 'adp',
  'darwin-x64': 'adp',
  'darwin-arm64': 'adp'
};

function getPlatformKey() {
  const platform = process.platform;
  const arch = process.arch;

  let key = `${platform}-${arch}`;
  if (platform === 'darwin' && arch === 'arm64') {
    key = 'darwin-arm64';
  }

  return key;
}

function main() {
  const platformKey = getPlatformKey();
  const binaryName = PLATFORM_MAP[platformKey];

  if (!binaryName) {
    console.error(`Error: Unsupported platform ${platformKey}`);
    console.error('Supported: win32-x64, linux-x64, linux-arm64, darwin-x64, darwin-arm64');
    process.exit(1);
  }

  const binaryPath = path.join(__dirname, '..', 'dist', platformKey, binaryName);

  try {
    execFileSync(binaryPath, process.argv.slice(2), {
      stdio: 'inherit',
      windowsHide: true
    });
  } catch (error) {
    if (error.code === 'ENOENT') {
      console.error(`Error: Binary not found at ${binaryPath}`);
      console.error('Installation may be incomplete. Try reinstalling.');
      process.exit(1);
    }
    process.exit(error.status || 1);
  }
}

main();
