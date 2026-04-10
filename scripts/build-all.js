#!/usr/bin/env node

'use strict';

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const PLATFORMS = [
  { platform: 'win32', arch: 'x64', dir: 'win32-x64', script: 'build.bat' },
  { platform: 'linux', arch: 'x64', dir: 'linux-x64', script: 'build.sh' },
  { platform: 'linux', arch: 'arm64', dir: 'linux-arm64', script: 'build.sh' },
  { platform: 'darwin', arch: 'x64', dir: 'darwin-x64', script: 'build.sh' },
  { platform: 'darwin', arch: 'arm64', dir: 'darwin-arm64', script: 'build.sh' }
];

const PROJECT_ROOT = path.join(__dirname, '..');

console.log('ADP CLI Multi-Platform Build');
console.log('============================\n');

PLATFORMS.forEach(({ platform, arch, dir, script }) => {
  console.log(`[${platform}-${arch}] Building...`);

  const scriptPath = path.join(PROJECT_ROOT, 'scripts', script);

  try {
    if (platform === 'win32') {
      execSync(`cmd /c "${scriptPath}"`, { cwd: PROJECT_ROOT, stdio: 'inherit' });
    } else {
      execSync(`bash "${scriptPath}"`, { cwd: PROJECT_ROOT, stdio: 'inherit' });
    }

    const distPath = path.join(PROJECT_ROOT, 'dist', dir);
    if (fs.existsSync(distPath)) {
      const files = fs.readdirSync(distPath);
      console.log(`[${platform}-${arch}] Success: ${files.join(', ')}\n`);
    }
  } catch (error) {
    console.error(`[${platform}-${arch}] Failed\n`);
  }
});

console.log('\nAll builds complete. Check dist/ directory.');
