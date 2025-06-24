# Config Folder Additions

When adding new folders to `src/frontend/../src` you must add then to the config files.

For `tsconfig.app.json` insert `"@folder_name/*": ["folder_name/*"],` into `compilerOptions: { paths : {} }` dictionary.

For `vite.config.ts` insert `'@folder_name': path.resolve(__dirname, 'src/folder_name'),` into `resolve: { alias : {} }` dictionary.
