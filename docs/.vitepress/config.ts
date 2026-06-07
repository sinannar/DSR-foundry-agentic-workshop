import { defineConfig } from 'vitepress'
import { labsSidebarItems } from './labs-sidebar.js'

export default defineConfig({
  title: 'Microsoft Foundry Agentic Workshop',
  description: 'Hands-on labs for building agentic solutions with Microsoft Foundry',
  base: '/foundry-agentic-workshop/',
  outDir: 'dist',
  appearance: 'auto',
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Organizer Quickstart', link: '/quickstart-organizer' },
      { text: 'Attendee Quickstart', link: '/quickstart-attendee' },
      { text: 'Instructor Quickstart', link: '/quickstart-instructor' },
      { text: 'Proctor Guide', link: '/guide-proctor' },
    ],
    sidebar: [
      {
        text: 'Getting Started',
        items: [
          { text: 'Overview', link: '/' },
          { text: 'Organizer Quickstart', link: '/quickstart-organizer' },
          { text: 'Attendee Quickstart', link: '/quickstart-attendee' },
          { text: 'Instructor Quickstart', link: '/quickstart-instructor' },
        ],
      },
      {
        text: 'Role Guides',
        items: [
          { text: 'Organizer Guide', link: '/guide-organizer' },
          { text: 'Attendee Guide', link: '/guide-attendee' },
          { text: 'Instructor Guide', link: '/guide-instructor' },
          { text: 'Proctor Guide', link: '/guide-proctor' },
          { text: 'Architecture Diagram', link: '/architecture-diagram' },
        ],
      },
      {
        text: 'Design',
        items: [
          { text: 'CI/CD Pipeline', link: '/design/cicd' },
        ],
      },
      {
        text: 'Labs',
        items: labsSidebarItems,
      },
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/PlagueHO/foundry-agentic-workshop' },
    ],
    footer: {
      message: 'Released under the MIT License.',
    },
  },
})
