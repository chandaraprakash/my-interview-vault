# My Interview Vault

My Interview Vault is a docs-as-code resource hub for interview preparation.
The site is built with Docusaurus, and the content lives as Markdown/MDX files
under `docs/`.

## Local development

Install dependencies:

```bash
npm install
```

Start the local site:

```bash
npm run start
```

Build the static site:

```bash
npm run build
```

Run TypeScript checks:

```bash
npm run typecheck
```

## Contribution model

Contributors fork the repository, edit Markdown files, and open pull requests.
Changes are not published until a maintainer reviews and merges the pull
request.

## Project layout

- `docs/`: interview prep content.
- `src/pages/`: custom Docusaurus pages.
- `src/components/`: React components used by custom pages.
- `docusaurus.config.ts`: site metadata, navigation, analytics, and deployment config.
- `sidebars.ts`: docs sidebar configuration.

## Next setup steps

1. Initialize this folder as a Git repository.
2. Create a GitHub repository named `my-interview-vault`.
3. Replace `your-github-username` in `docusaurus.config.ts`.
4. Choose GitHub Pages, Vercel, or Netlify for hosting.
5. Add Plausible or Google Analytics if analytics are needed.
