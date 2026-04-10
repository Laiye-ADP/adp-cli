#!/usr/bin/env node

'use strict';

const fs = require('fs');
const path = require('path');

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
    console.log(`Skipping binary check for unsupported platform: ${platformKey}`);
    return;
  }

  const binaryPath = path.join(__dirname, '..', 'dist', platformKey, binaryName);

  if (!fs.existsSync(binaryPath)) {
    console.error(`Error: Binary not found: ${binaryPath}`);
    console.error('Installation may be incomplete. Try reinstalling.');
    process.exit(1);
  }

  console.log(`Binary verified: ${binaryName}`);
}

main();
