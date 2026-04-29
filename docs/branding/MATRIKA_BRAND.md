# Matrika — Brand Identity Guide

> **Version:** 1.0 | **Date:** April 2026 | **Product:** Matrika Academic Management Platform

---

## 1. Brand Foundation

### Name

**Matrika** derives from the Portuguese *matrícula* (enrollment/registration) — the defining act of an institution welcoming a student. The truncation into a proper noun gives the product a distinct, memorable identity that signals its purpose without sounding bureaucratic.

- Easy to pronounce in Portuguese, English, and Bantu languages
- No existing trademark conflicts in the Angolan software space
- Works as domain, app store handle, and wordmark
- Feels modern, not a legacy acronym

### Vision

Dignify academic administration in Africa — make the work that institutions do invisible to the people who matter most: students and educators.

### Mission

Give any school, technical institute, or professional training centre the digital infrastructure it needs to run confidently, regardless of internet reliability or technical staff size.

### Values

| Value | Expression |
|---|---|
| **Simplicity** | Every screen has one primary action. No feature without a clear user need. |
| **Reliability** | Works on slow connections. Survives outages. Never loses data silently. |
| **Dignity** | Language, icons, and flows treat admins and students as professionals. |
| **Honesty** | Errors are explained in plain language. No false loading spinners. |
| **Locality** | Defaults to Portuguese. Understands the Angolan context (Multicaixa, CINFOTEC, Kwanza). |

### Brand Personality

Matrika speaks like a capable, calm colleague — never condescending, never chatty. Think of a well-run secretary's office that moves fast and never loses a file.

- **Not**: startup-cool, gamified, overly friendly
- **Is**: trustworthy, efficient, quietly confident

---

## 2. Visual Identity

### Color Palette

#### Primary — Institutional Amber

The warm amber-gold signals education, documentation, and institutional trust without the coldness of tech-blue or the aggression of red. It references ink on official documents.

| Name | Hex | RGB | Usage |
|---|---|---|---|
| **Amber 600** | `#D97706` | rgb(217, 119, 6) | Primary CTAs, active nav states, key highlights |
| **Amber 500** | `#F59E0B` | rgb(245, 158, 11) | Hover states, secondary emphasis |
| **Amber 100** | `#FEF3C7` | rgb(254, 243, 199) | Backgrounds for highlighted rows, badges |

#### Base — Warm Neutral

| Name | Hex | RGB | Usage |
|---|---|---|---|
| **Slate 900** | `#0F172A` | rgb(15, 23, 42) | Main background (dark mode) |
| **Warm 900** | `#1C1917` | rgb(28, 25, 23) | Sidebar, deep backgrounds |
| **Warm 700** | `#44403C` | rgb(68, 64, 60) | Cards, elevated containers |
| **Warm 400** | `#A8A29E` | rgb(168, 162, 158) | Secondary text, placeholders |
| **Warm 200** | `#E7E5E4` | rgb(231, 229, 228) | Borders, dividers |

#### Semantic

| Name | Hex | Usage |
|---|---|---|
| **Success** | `#10B981` | Confirmations, active status badges |
| **Danger** | `#EF4444` | Errors, deactivation actions |
| **Warning** | `#F59E0B` | Connectivity issues, pending states |
| **Info** | `#3B82F6` | Info toasts, neutral notices |

#### Light Mode (future)

White base with warm-neutral 700 text; amber accents unchanged.

---

### Typography

#### Primary — Inter

```css
font-family: 'Inter', system-ui, -apple-system, sans-serif;
```

Used for all UI text: labels, body, navigation, tables. Inter at weight 400/600/700 covers all hierarchy needs without a secondary sans-serif.

#### Monospace — JetBrains Mono

```css
font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
```

Used only for: registration codes, student/class codes, API keys, error traces. Signals "this is a unique identifier."

#### Scale

| Token | Size | Weight | Line Height | Usage |
|---|---|---|---|---|
| `--text-xs` | 11px | 400 | 1.4 | Micro-labels, timestamps |
| `--text-sm` | 13px | 400 | 1.5 | Table cells, captions |
| `--text-base` | 15px | 400 | 1.6 | Body, form labels |
| `--text-md` | 17px | 600 | 1.4 | Section subheadings |
| `--text-lg` | 20px | 700 | 1.3 | Page headings |
| `--text-xl` | 28px | 700 | 1.2 | Dashboard stats, hero figures |
| `--text-2xl` | 36px | 700 | 1.1 | Auth page headlines |

---

### Logo

#### Concept

The Matrika wordmark is set in Inter Bold with a square amber bracket pair framing the first letter: **[M]atrika**. The bracket references a matrix cell, a form field, and a register entry simultaneously.

#### Variations

**Full wordmark (preferred):**
```
[M] Matrika
```
Inter Bold, amber bracket, white "atrika"

**Compact (sidebar collapsed, favicon):**
```
[M]
```
Amber square, white M, rounded corners

**Monochrome:**
Full white on dark, or full dark on light — no amber. For watermarks, print.

#### Clear Space

Minimum clear space = height of the capital M on all four sides.

#### Minimum Size

- Digital: 20px height for compact mark, 80px width for full wordmark
- Print: 8mm height

#### Don'ts

- Do not rotate or skew
- Do not apply drop shadows
- Do not place amber logo on amber background
- Do not use a different font in the wordmark
- Do not add "by PyNerd" adjacent to the logo in product UI (footer only)

---

### Iconography

**Library:** Lucide Icons (stroke, 1.5px weight, rounded caps)

**Size system:**

| Context | Size |
|---|---|
| Inline body text | 16px |
| Action buttons | 18px |
| Navigation items | 20px |
| Empty state illustrations | 48–64px |

**Color rules:**

- Navigation icons: `Warm 400` when inactive, `Amber 500` when active
- Action icons (edit, delete): inherit button text color
- Status icons: use semantic color directly

---

### Spacing & Layout

```
4px  — XS: icon padding, tight badge spacing
8px  — SM: between related inline elements
12px — MD-: form element internal padding
16px — MD: section padding, card internal spacing
24px — LG: between card rows, section margins
32px — XL: section separators, page top padding
48px — 2XL: major section breaks
64px — 3XL: auth card max padding
```

**Border radius:**
- Inputs, buttons: `6px`
- Cards, modals: `10px`
- Badges, pills: `9999px` (fully round)

**Grid:** 12-column, 24px gutter, max content width 1200px.

---

## 3. Voice & Tone

### Principles

**Be direct.** Say "Student deactivated." Not "The operation to deactivate the student record has been successfully completed."

**Use active voice.** "Matrika saved your changes." Not "Changes have been saved."

**Name the person, not the record.** "Ana Luísa cannot be found." Not "No records matching query."

**Errors earn an explanation and a path forward.** Every error message answers: what happened, and what should the user do next.

### Example Copy

| Situation | ✅ Matrika voice | ❌ Avoid |
|---|---|---|
| Save success | "Saved." | "Operation completed successfully!" |
| Delete confirm | "Remove João Melo? This cannot be undone." | "Are you sure you want to delete this record?" |
| Network error | "No connection. Changes will sync when you're back online." | "Error 503: Service unavailable" |
| Empty state | "No students enrolled yet. Add the first one →" | "No data to display." |
| Form validation | "Phone number must start with +244 or 09" | "Invalid format" |

### Terminology (PT default)

| Product term | Portuguese | English |
|---|---|---|
| Institution | Instituição | Institution |
| Course | Curso | Course |
| Class | Turma | Class |
| Trainer/Teacher | Formador | Trainer |
| Student | Aluno | Student |
| Registration code | Código de acesso | Access code |
| Enrollment | Matrícula | Enrollment |
| Dashboard | Painel | Dashboard |

---

## 4. Product Positioning

### Category

**Academic Management SaaS** — not an LMS, not a CRM. Matrika handles the administrative layer: enrollment, attendance, grading, reporting.

### Target Persona

**Primary: Administrative Director or Secretary**
- Responsible for enrollment, records, reports
- May not be technical; may be the only person with a computer
- Currently uses Excel, WhatsApp, and paper
- Cares about: not losing data, printing lists, knowing who is enrolled

**Secondary: Institution Owner / Director**
- Wants visibility into enrollment numbers, revenue, activity
- Needs monthly reports for stakeholders
- Cares about: dashboards, exports, not paying for something that breaks

**Tertiary: Trainers/Teachers**
- Needs to see their class list, take attendance, submit grades
- Low motivation to learn new tools
- Cares about: mobile access, speed, not having to ask the secretary

### Differentiation

| Dimension | Matrika | Generic international tools |
|---|---|---|
| Language | Portuguese (default) | English (primary) |
| Connectivity | Works offline, syncs later | Assumes stable broadband |
| Pricing | Kwanza, bank transfer / Multicaixa | USD, international card |
| Setup | 15 min, no IT required | Days to weeks |
| Support | WhatsApp, same timezone | Ticket system, UTC-5 |
| Localization | Angolan document formats, ID types | Generic Western |

### Positioning Statement

> For Angolan educational institutions tired of managing students in spreadsheets, Matrika is the academic management platform that works reliably on any internet connection, speaks Portuguese by default, and is ready in 15 minutes — without an IT team.

---

## 5. Brand Application

### Product UI

- Dark sidebar with warm-900 background
- Amber accent on active nav items and primary CTAs
- Clean white (or warm-50) content area
- Tables with subtle warm-200 row separators
- No decorative illustrations in operational screens — only in empty states and onboarding

### Marketing Materials

- Documents: white background, amber header band, Inter throughout
- Presentations: dark warm-900 slides with amber highlights for key numbers
- Proposals: formal, numbered sections, no emoji in body text

### Email Templates (future)

- Plain-text first, HTML fallback
- Footer: "Matrika · by PyNerd · Luanda, Angola"

### PyNerd Relationship

PyNerd is the parent startup brand. In the Matrika product:
- PyNerd appears **only** in the footer: "Powered by PyNerd"
- PyNerd brand colors (green/cyan) are **never** used in Matrika UI
- Matrika has complete visual independence

---

## 6. Brand Checklist (per release)

- [ ] All new strings exist in PT and EN in i18n.js
- [ ] No hardcoded English in user-facing HTML/JS
- [ ] Error messages follow the voice guide (direct, path-forward)
- [ ] New icons use Lucide at correct size
- [ ] New CTAs use amber-600 as primary color
- [ ] Page `<title>` follows pattern: `Page — Matrika`
- [ ] No `window.alert()` or `window.confirm()` in new code
- [ ] Empty states have a call to action

---

*Matrika Brand Guide v1.0 — April 2026*
*Maintained by: Anderson Cafurica / PyNerd*
