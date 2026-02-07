# Shared Packages

This directory contains shared packages that can be used by both the frontend and other applications.

## Structure

```
packages/
├── tsconfig.base.json    # Base TypeScript config
├── shared-types/         # Shared TypeScript types (future)
├── ui/                   # Shared UI components (future)
└── utils/               # Shared utilities (future)
```

## Creating a New Package

1. Create a new directory under `packages/`
2. Add a `package.json` with the package name scoped: `@botcraft/package-name`
3. Add a `tsconfig.json` extending from `tsconfig.base.json`

## Example Package Structure

```
packages/shared-types/
├── package.json
├── tsconfig.json
├── src/
│   └── index.ts
└── dist/
```
