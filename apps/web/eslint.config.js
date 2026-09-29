import js from '@eslint/js';
import tseslint from 'typescript-eslint';
export default tseslint.config({ignores:['dist']},js.configs.recommended,...tseslint.configs.recommended,{
 files:['src/**/*.{ts,tsx}'],languageOptions:{globals:{fetch:'readonly',sessionStorage:'readonly',FormData:'readonly',URL:'readonly',document:'readonly',setTimeout:'readonly',clearTimeout:'readonly',prompt:'readonly'}},rules:{'@typescript-eslint/no-unused-vars':['error',{argsIgnorePattern:'^_'}]}
});
