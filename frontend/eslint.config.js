import js from '@eslint/js'
import globals from 'globals'
import react from 'eslint-plugin-react'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import prettier from 'eslint-config-prettier'

export default tseslint.config(
  {
    ignores: [
      'dist/**',
      'node_modules/**',
      'public/**',
      'scripts/**',
      'tailwind.config.js',
      'postcss.config.js',
      'vite.config.ts',
    ],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ['**/*.{ts,tsx,js,jsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.es2022,
      },
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
    },
    settings: {
      react: { version: 'detect' },
    },
    plugins: {
      react,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...react.configs.recommended.rules,
      ...react.configs['jsx-runtime'].rules,
      ...reactHooks.configs.recommended.rules,
      // shadcn/ui co-exports variants with components; noise over signal here.
      'react-refresh/only-export-components': 'off',
      '@typescript-eslint/no-unused-vars': [
        'error',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_',
        },
      ],
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-empty-object-type': 'off',
      'react/prop-types': 'off',
      'react/no-unescaped-entities': 'off',
      // cmdk / radix pass data attributes that look unknown to the DOM linter.
      'react/no-unknown-property': ['error', { ignore: ['cmdk-input-wrapper'] }],
      'no-console': ['warn', { allow: ['warn', 'error', 'info', 'debug'] }],
      'react-hooks/exhaustive-deps': 'warn',
    },
  },
  prettier,
)
