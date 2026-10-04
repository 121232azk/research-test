# Clone Yeldra Landing Site

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 1:1 pixel-faithful clone of the yeldra.com landing page as a single index.html using Tailwind CSS CDN, matching the reference screenshot and the provided CSS style guide.

**Architecture:** Single static index.html with all Tailwind via CDN. No backend. Inline CSS where needed for the exact brand colors from the CSS variables. Served via the existing `node serve.mjs` dev server at localhost:3000.

**Tech Stack:** Tailwind CSS CDN (via `<script src="https://cdn.tailwindcss.com">`), vanilla JS for interactive elements (FAQ accordion, mobile nav, pricing toggle). Single `index.html` plus a `serve.mjs` and `screenshot.mjs` helper if not present.

**Spec:** Reference image `yeldra.com_.png` (1740×16384 full-page screenshot) and the pasted CSS style variables. The actual site content was extracted from yeldra.com.

## Global Constraints

- Single `index.html` file, all styles inline (unless user says otherwise)
- Tailwind CSS via CDN: `<script src="https://cdn.tailwindcss.com"></script>`
- Serve on localhost — start dev server before screenshots
- Match the reference screenshot color-for-color
- Match the provided CSS variables exactly:
  - `--ink: #1e2030` (dark surface background)
  - `--ink-foreground: #f4f5f9` (light text)
  - `--background: oklch(.99 .004 277)` (page background, near-white purple tint)
  - `--card: #fff` (card background)
  - `--foreground: #18181c` (body text)
  - `--primary: oklch(.64 .16 277)` (purple primary)
  - `--teal: #30a06a` (teal accent)
  - `--info: #2463ef` (info blue)
  - `--brand-hue: 277`
  - `--radius: .75rem`, `--radius-2xl: 1rem`, `--radius-3xl: 1.5rem`
- Placeholder images via `https://placehold.co/WIDTHxHEIGHT`
- Mobile-first responsive
- Never use default Tailwind palette colors (indigo-500, blue-600, etc.) as primary
- Never use `transition-all` — use explicit property transitions or `transition-[property]`
- Every clickable element needs hover, focus-visible, and active states
- Fonts: Geist Sans for body, Geist Mono for code (from CSS variables)

## Review Focus

1. **Color fidelity against reference** — the purple brand hue (277), the dark #1E2030 "ink" surfaces, the teal and info accents must match the reference pixel-for-pixel. Test: screenshot and visually compare.
2. **Typography pairing** — body text must use a clean sans (not matching the display treatment), headings must use tight tracking (-0.025em). Test: inspect font-family and letter-spacing.
3. **Responsive behavior** — layout must collapse gracefully to mobile. Test: screenshot at mobile width (375px).
4. **Interactive states** — every button/link/card needs hover, focus-visible, active. Test: tab through and check ring visibility.
5. **Image treatment** — hero graphic mockup and card images need gradient overlays and mix-blend-multiply color layers per the guardrails.

---

## Task 1: Set up project scaffolding and dev environment

**Files:**
- Create: `index.html` (placeholder)
- Create: `serve.mjs`
- Create: `screenshot.mjs`
- Ensure: `.claude/settings.json` or `.vscode/settings.json` allows localhost server

**Interfaces:**
- `serve.mjs` serves the directory at `http://localhost:3000` using native Node HTTP
- `screenshot.mjs` launches Puppeteer against a localhost URL and saves PNG

- [ ] Write the placeholder index.html
- [ ] Write serve.mjs (Node HTTP server, static file serving, 1000ms poll)
- [ ] Write screenshot.mjs (Puppeteer, viewport 1280x800, auto-increment filenames)
- [ ] Start server and verify `http://localhost:3000` returns 200

## Task 2: Build HTML skeleton with correct CSS variable system

**Files:**
- Modify: `index.html` — full document structure and `<style>` with Tailwind config

**Interfaces:**
- Uses Tailwind CDN with `tailwind.config` extending the exact color tokens from the pasted CSS
- Sets `--ink`, `--ink-foreground`, `--background`, `--card`, `--primary`, `--teal`, `--info`, `--brand-hue` as CSS custom properties
- Defines `--font-geist-sans` and `--font-geist-mono` (fallback to system fonts if CDN fails)
- Sets `body { background-color: var(--background); color: var(--foreground) }`

- [ ] Write the full HTML document structure (header, 9 content sections, footer)
- [ ] Add Tailwind CDN script with config overriding colors and fonts
- [ ] Add `<style>` block with custom CSS variables matching the spec
- [ ] Add base typography: `container { max-width: 1440px }`, line-height 1.5 for body
- [ ] Screenshot the empty scaffold and verify it serves

## Task 3: Build navigation header with sticky behavior

**Files:**
- Modify: `index.html` — `<header>` and nav styles

**Interfaces:**
- Header uses `bg-card` with `border-b border-border`
- On scroll: adds shadow `shadow-sm` (via JS class toggle)
- Logo: "Yeldra" in primary purple, bold display
- Nav links: `/#benefices` (Pourquoi Yeldra?), `/#methode` (Méthode), `/#tarif` (Tarif), `/#faq` (FAQ), `/simulateur`, `/blog`
- Mobile: hamburger menu → slides down mobile nav
- Buttons: "Se connecter" (ghost) and "Essayer gratuitement" (primary)

- [ ] Build desktop nav: logo left, links center, buttons right
- [ ] Build mobile nav: hamburger icon, panel slides down
- [ ] Add scroll-link smooth behavior for anchor links
- [ ] Add hover/focus/active states for all nav links
- [ ] Screenshot and check alignment against reference (header ~90px height)

## Task 4: Build Hero section with two-column layout

**Files:**
- Modify: `index.html` — hero section, styles

**Interfaces:**
- Hero background: a gradient from `#f5f6fb` to lighter (the reference shows a soft blue-gray)
- Left column (text): `max-w-[650px]`
  - Headline: "Paie-toi mieux, sans travailler plus." (tight tracking, display serif or bold sans)
  - Body: "Construis une activité rentable..." (line-height 1.7)
  - Badge: "Si l'outil coûtait 10x son prix, ça vaudrait le coup." (quote with attribution)
  - CTA: "Créer mon compte gratuitement" (primary button)
- Right column (graphic): a placeholder dashboard visualization at `330px` width, aspect 3/4
- Background: subtle gradient mask or radial overlay

- [ ] Build hero container: `grid lg:grid-cols-[1.05fr_1fr]` matching the reference
- [ ] Add headline with `tracking-tight` and custom font pairing
- [ ] Add hero background gradient (purple-tinted light)
- [ ] Add hero graphic placeholder with dashboard-style visualization
- [ ] Add quote testimonial with attribution
- [ ] Screenshot and compare against reference hero (y=0-1000 in the screenshot)

## Task 5: Build Core Benefits section

**Files:**
- Modify: `index.html` — benefits section

**Interfaces:**
- Section heading: "Des décisions prises sur tes chiffres."
- Subheading/lead: paragraph about data-driven pricing
- Benefits (based on reference analysis, 6 benefits detected):
  1. "Ton offre la plus vendue n'est pas celle qui te paie." / "Facture ce que ton travail coûte"
  2. "Ce calcul tourne en continu." / "Corrige en cours d'année"
  3. "La vie que tu veux devient un chiffre à atteindre." / "Tarification alignée sur objectifs"
  4. "Décide ton net, Yeldra remonte le calcul." / "Net-to-gross calculation"
  5. "Le mois où ça coince, tu le sais des mois à l'avance." / "Cash flow prediction"
- Layout: 2-column grid (text + visual) alternating, or 3-col card grid
- Background: `#F5F6FB` with subtle pattern/mask

- [ ] Write section heading and lead
- [ ] Build benefit items: each with a number/icon, short title, description
- [ ] Add "Calculer ma rentabilité" CTA button
- [ ] Match background color from reference (#F5F6FB / white alternation)
- [ ] Screenshot and verify against reference benefits section

## Task 6: Build Methodology 4-step section

**Files:**
- Modify: `index.html` — methodology section

**Interfaces:**
- Section background: `#1E2030` (dark) with `#f4f5f9` text (ink foreground)
- Heading: "Ta stratégie en quatre étapes."
- Lead: "Du seuil de rentabilité au suivi au réel..."
- Four numbered steps:
  1. "Découvre le CA minimum pour bien te payer." — "Yeldra calcule ton seuil de rentabilité..."
  2. "Construis des offres calibrées sur ta rentabilité." — "Définit tes produits et services..."
  3. "Anticipe tes dépenses, protège ta marge." — "Intègre tes charges et frais professionnels..."
  4. "Suis le réel, ajuste toute l'année." — "Enregistre tes ventes et dépenses..."
- Layout: vertical stepper on mobile, horizontal on desktop

- [ ] Build dark background section with light text
- [ ] Build 4-step horizontal layout on desktop, stacked on mobile
- [ ] Each step: numbered badge + title + description
- [ ] "Construire mon prévisionnel" CTA button
- [ ] Screenshot and verify dark section matches reference's #1E2030

## Task 7: Build Target Audience section

**Files:**
- Modify: `index.html` — audience section

**Interfaces:**
- Heading: "Pensé pour les freelances qui vendent leur expertise."
- Lead: "Tu factures ton temps et ton savoir-faire..."
- 10 audience cards (from extracted site content):
  - Graphistes & designers, Développeurs web & mobile, Marketers & growth, Rédacteurs & copywriters, Consultants SEO/SEA, UX/UI designers, Photographes & vidéastes, Coachs & formateurs, Consultants & experts, Community managers
- Background: white (#FFFFFF)

- [ ] Build audience cards as a responsive grid
- [ ] Each card has a category icon (placeholder) + label
- [ ] Cards match the reference's card style (border, radius, hover)
- [ ] Screenshot and verify against reference audience section

## Task 8: Build Testimonials section

**Files:**
- Modify: `index.html` — testimonials section

**Interfaces:**
- Heading: "Ils ont repensé leurs offres et leurs prix."
- At least 3 testimonial cards with:
  - Quote text
  - Customer name
  - Their title/company
- Background: white

- [ ] Build testimonial cards with quote styling
- [ ] Add avatar placeholder + name + title
- [ ] Match card styling: border, radius, shadow
- [ ] Screenshot and verify against reference testimonial section

## Task 9: Build Pricing section

**Files:**
- Modify: `index.html` — pricing section

**Interfaces:**
- Heading: "Commence gratuitement. Pour de bon."
- Lead: "Pas d'essai qui expire, pas de carte bancaire. Premium arrive le jour où tu veux comparer plusieurs offres."
- Two-tier pricing:
  - Free: "0€" / "Plan gratuit" / unlimited duration / features list
  - Premium: "9,99€ HT / mois" / "sans engagement" / features list
- Toggle between monthly/yearly (optional — implement if reference shows it)
- Background: white/light

- [ ] Build pricing table: two cards side by side
- [ ] Free tier card: simple border, light emphasis
- [ ] Premium tier card: primary purple emphasis, elevated
- [ ] Feature list in each card with checkmarks
- [ ] "Créer mon compte gratuitement" CTA (both tiers)
- [ ] Screenshot and verify pricing cards match reference

## Task 10: Build FAQ accordion section

**Files:**
- Modify: `index.html` — FAQ section (HTML + JS)

**Interfaces:**
- Heading: "FAQ"
- Accordion items (from extracted content):
  - "À qui s'adresse Yeldra ?"
  - "Puis-je facturer..." (pricing questions)
  - "Yeldra, c'est bien pour..." (use cases)
  - "Est-ce que Yeldra remplace un expert-comptable ?"
  - Questions about security, data, billing
- Accordion: only one open at a time, smooth height transition
- Background: dark `#1E2030` with light text (#F4F5F9)

- [ ] Build FAQ heading
- [ ] Create accordion JS: click toggles open, sibling closes
- [ ] Accordion item: summary (bold) + answer (expandable)
- [ ] Focus-visible states on accordion headers
- [ ] Match dark background and light text from reference
- [ ] Screenshot and verify against reference FAQ section

## Task 11: Build Footer

**Files:**
- Modify: `index.html` — footer section

**Interfaces:**
- Background: `#1E2030` (dark)
- Content: dark background with light text
- Columns: product, legal, social, copyright
- Final CTA banner above footer
- Links: mentions légales, CGU, politique de confidentialité, contact

- [ ] Build footer with dark background (#1E2030)
- [ ] Add column layout: links grouped by category
- [ ] Add "Se transformer" or final CTA strip above footer
- [ ] Add copyright notice
- [ ] Screenshot and verify footer color/text against reference

## Task 12: Add interactivity and final polish

**Files:**
- Modify: `index.html` — `<script>` block with JS

**Interfaces:**
- Mobile nav toggle: hamburger → menu
- FAQ accordion: open/close behavior
- Smooth scroll for anchor links
- Scroll-header shadow on scroll
- Hover/focus states already in CSS via Tailwind group and focus classes

- [ ] Add mobile menu toggle JS (class toggle on nav panel)
- [ ] Add FAQ accordion JS (accordion behavior)
- [ ] Add scroll-smooth behavior (CSS `scroll-behavior: smooth`)
- [ ] Add header shadow on scroll JS
- [ ] Verify all interactive elements have focus-visible states
- [ ] Screenshot final site, compare against all reference sections

## Task 13: Screenshot comparison rounds (2 rounds minimum)

**Interfaces:**
- Start dev server with `node serve.mjs` in background
- Run `node screenshot.mjs http://localhost:3000`
- Read the resulting PNG and compare against reference segments

- [ ] Start server, take first full-page screenshot
- [ ] Compare against reference: note all mismatches in spacing, fonts, colors
- [ ] Fix mismatches, take second screenshot
- [ ] Verify no visible differences remain in hero, nav, sections
- [ ] Screenshot mobile view (375px) for responsive verification
