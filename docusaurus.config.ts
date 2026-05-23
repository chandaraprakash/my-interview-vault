import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'My Interview Vault',
  tagline: 'A community-maintained interview preparation hub.',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://your-github-username.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'your-github-username',
  projectName: 'my-interview-vault',

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl:
            'https://github.com/your-github-username/my-interview-vault/tree/main/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/logo.svg',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'My Interview Vault',
      logo: {
        alt: 'My Interview Vault Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'vaultSidebar',
          position: 'left',
          label: 'Vault',
        },
        {
          href: 'https://github.com/your-github-username/my-interview-vault',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Start here',
              to: '/docs/intro',
            },
            {
              label: 'Coding practice',
              to: '/docs/category/coding-practice',
            },
            {
              label: 'System design',
              to: '/docs/category/system-design',
            },
          ],
        },
        {
          title: 'Contribute',
          items: [
            {
              label: 'Edit on GitHub',
              href: 'https://github.com/your-github-username/my-interview-vault',
            },
            {
              label: 'Contribution guide',
              href: 'https://github.com/your-github-username/my-interview-vault/blob/main/CONTRIBUTING.md',
            },
          ],
        },
        {
          title: 'Project',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/your-github-username/my-interview-vault',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} My Interview Vault contributors. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
