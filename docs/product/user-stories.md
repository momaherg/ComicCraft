# ComicCraft AI - User Stories (Simplified MVP)

## Document Information
**Version:** 4.0 - Simplified MVP
**Last Updated:** October 22, 2025
**Status:** Ready for Development
**Story Count:** 18 core stories (down from 33)

---

## Story Writing Principles

All stories follow **INVEST** principles:
- **I**ndependent: Deliverable independently
- **N**egotiable: Focus on WHAT and WHY, not HOW
- **V**aluable: Clear user value
- **E**stimable: Clear enough to estimate effort
- **S**mall: Completable in 1-2 sprints
- **T**estable: Verifiable acceptance criteria

**Simplification Goal:** Maximum 5 acceptance criteria per story

---

## Table of Contents
1. [Phase 1: Ultra-MVP](#phase-1-ultra-mvp-6-weeks)
2. [Phase 2: Enhancement](#phase-2-enhancement-4-weeks)
3. [Phase 3: Growth Features](#phase-3-growth-features-backlog)
4. [Deferred Features](#deferred-features)

---

## PHASE 1: ULTRA-MVP (6 weeks)

**Goal:** Get users creating and exporting comics in the simplest possible way

### Epic 01: Authentication

#### US-001: User Account Creation
**As a** new user
**I want to** create an account with email and password
**So that** my projects are saved

**Priority:** Must Have | **Effort:** 3 points | **Dependencies:** None

**Acceptance Criteria:**
1. User can sign up with email and password
2. Email format and password strength validated (min 8 chars)
3. User receives 50 welcome credits upon registration
4. Email verification sent and must be completed before credits can be used
5. Failed signup shows clear error messages

---

#### US-002: User Login
**As a** returning user
**I want to** log into my account
**So that** I can access my content

**Priority:** Must Have | **Effort:** 2 points | **Dependencies:** US-001

**Acceptance Criteria:**
1. User can log in with email/password
2. "Remember me" keeps user logged in for 30 days
3. Failed login shows clear error message
4. "Forgot Password" initiates password reset via email
5. After login, user redirected to story gallery

---

### Epic 02: Asset Creation

#### US-003: Create Character
**As a** user
**I want to** create a character from a photo, comic character image, OR text description
**So that** I can feature characters in my stories

**Priority:** Must Have | **Effort:** 8 points | **Dependencies:** US-001

**Acceptance Criteria:**
1. User can choose between: photo upload, comic character image upload, or text description
2. Photo: Upload from camera/library and transform to comic style
3. Comic character image: Upload existing illustrated/comic character, or use as-is to skip generation (faster)
4. Text: Enter description (10-500 characters) with helpful examples
5. User can add optional text prompt for photo/image uploads to guide transformation
6. User provides character name (3-50 characters, required) to reference in panels
7. Select art style from 5 preset options
8. Select character height from preset options (e.g., 90 cm, 130 cm, 180 cm or ...)
9. Credit cost (5 credits) displayed before generation
10. Generation shows progress with estimated time (15-45s)
11. User can save or regenerate (costs 5 more credits)
12. Credits only charged when generation completes successfully and image is saved for viewing
13. Saved character appears in character library with name

**Notes:** Combined US-005 and US-006 into single unified flow. Supports real photos, comic images, and text descriptions. Character names must be unique within user's library. No hard limit on number of characters/locations per account.

---

#### US-004: Create Location
**As a** user
**I want to** create a location from a photo OR text description
**So that** I can set scenes for my story

**Priority:** Must Have | **Effort:** 8 points | **Dependencies:** US-001

**Acceptance Criteria:**
1. User can choose between photo upload or text description
2. Photo: Upload from camera/library with scenery guidelines
3. Text: Enter description (10-500 characters) with location-specific examples
4. User can add optional text prompt for photo uploads to guide transformation
5. User provides location name (3-50 characters, required)
6. Select art style from 5 preset options
7. Credit cost (5 credits) displayed before generation
8. Generation shows progress with estimated time (20-50s)
9. User can save or regenerate (costs 5 more credits)
10. Credits only charged when generation completes successfully and image is saved for viewing
11. Saved location appears in location library with name

**Notes:** Combined US-010 and US-011 into single unified flow. Location names must be unique within user's library.

---

#### US-005: View Asset Libraries
**As a** user
**I want to** browse my characters and locations
**So that** I can find and use them in panels

**Priority:** Must Have | **Effort:** 3 points | **Dependencies:** US-003, US-004

**Acceptance Criteria:**
1. Separate tabs for characters and locations
2. Grid view shows thumbnails with names and creation dates
3. Search by name
4. Tap asset to view full details: thumbnail, name (editable), creation date, height (characters only)
5. Asset detail actions: rename, use in panel, regenerate, delete

**Notes:** Merged US-007 and US-012, removed sorting/filtering complexity. Regeneration preserves original parameters (text prompt, style, height) but allows modifications before regenerating.

---

#### US-006: Delete Assets
**As a** user
**I want to** remove characters or locations I don't need
**So that** my library stays organized

**Priority:** Must Have | **Effort:** 1 point | **Dependencies:** US-005

**Acceptance Criteria:**
1. User can delete any character or location
2. Simple confirmation dialog shows asset thumbnail
3. Deletion is permanent, no recovery
4. Credits are not refunded
5. Library updates immediately

**Notes:** Removed "affected panels" warnings - users responsible for managing their assets

---

### Epic 03: Story Management

#### US-007: Create Story
**As a** user
**I want to** start a new story project
**So that** I can organize my comic panels

**Priority:** Must Have | **Effort:** 2 points | **Dependencies:** US-001

**Acceptance Criteria:**
1. User can create story from dashboard
2. Provide story title (3-100 characters, required)
3. Optional description (max 500 characters)
4. Story created immediately with default cover
5. New story appears in gallery

**Notes:** Removed AI cover generation - use default template instead

---

#### US-008: View Story Gallery
**As a** user
**I want to** see all my stories
**So that** I can access and manage them

**Priority:** Must Have | **Effort:** 2 points | **Dependencies:** US-007

**Acceptance Criteria:**
1. Gallery shows stories with cover, title, panel count, last modified date
2. Grid or list view toggle
3. Tap story to open editor
4. Long-press for menu: rename, delete
5. Empty state shows "Create Story" button

**Notes:** Removed search, sorting, duplicate features for simplicity

---

#### US-009: Delete Story
**As a** user
**I want to** delete stories I don't need
**So that** my workspace stays organized

**Priority:** Must Have | **Effort:** 1 point | **Dependencies:** US-008

**Acceptance Criteria:**
1. User can delete story from gallery
2. Confirmation shows title and panel count
3. Deletion is permanent (removes story and panels, keeps characters/locations)
4. Credits not refunded

---

### Epic 04: Panel Creation

#### US-010: Compose Panel
**As a** user
**I want to** create a panel by combining location, characters, and a description
**So that** I can build my comic story

**Priority:** Must Have | **Effort:** 10 points | **Dependencies:** US-003, US-004, US-007

**Acceptance Criteria:**
1. User initiates panel creation from within a story
2. Guided flow: select location (optional) → select characters 0-7 → enter text prompt describing the scene
3. Selected characters can be referenced by name in the prompt (e.g., "Sarah talking to John in the foreground, Mike looking surprised")
4. Text prompt (10-500 characters) describes the action, composition, and how characters should appear
5. System provides helpful prompt examples showing character name references
6. Credit cost (5 credits) displayed before generation
7. AI generates complete panel based on location, selected characters, and prompt
8. Generation shows progress (30-90s estimated)
9. Panel automatically saved to story when generation completes successfully
10. Credits only charged when generation completes successfully and panel is saved for viewing
11. Can regenerate with same or modified inputs (costs 5 credits) or accept
12. If no assets exist, quick links to create them

**Notes:** Panel composition (character positions, poses, interactions) is fully AI-generated based on the text prompt - no manual positioning controls. Characters are referenced by their names in prompts.

---

#### US-011: Arrange Panels
**As a** user
**I want to** reorder panels in my story
**So that** I control the narrative flow

**Priority:** Must Have | **Effort:** 3 points | **Dependencies:** US-010

**Acceptance Criteria:**
1. Story view shows panels in sequence with numbers
2. Each panel has up/down arrow buttons to reorder
3. Panel numbers update automatically
4. Changes save automatically

**Notes:** Removed drag-and-drop complexity, using simple up/down buttons instead

---

#### US-012: Delete Panel
**As a** user
**I want to** remove panels that don't work
**So that** I can refine my story

**Priority:** Must Have | **Effort:** 1 point | **Dependencies:** US-010

**Acceptance Criteria:**
1. Delete button on each panel
2. Confirmation shows thumbnail
3. Remaining panels automatically renumber
4. Credits not refunded

---

### Epic 05: Generation Core

#### US-013: View Generation Progress
**As a** user
**I want to** see progress when AI generates content
**So that** I know the system is working

**Priority:** Must Have | **Effort:** 3 points | **Dependencies:** US-003, US-004, US-010

**Acceptance Criteria:**
1. Progress indicator shows estimated time remaining
2. Progress updates every 5 seconds
3. User can navigate away and return without interrupting
4. Notification when generation completes
5. If generation fails, show clear error and refund credits

**Notes:** Removed cancel/refund window, queue system - simplified to essential feedback only

---

#### US-014: Handle Generation Failures
**As a** user
**I want to** clear explanations when generation fails
**So that** I can successfully retry

**Priority:** Must Have | **Effort:** 3 points | **Dependencies:** US-013

**Acceptance Criteria:**
1. Failed generation shows user-friendly error message
2. Credits not charged if generation fails (user only charged when image successfully saved)
3. Retry button available with original settings pre-filled
4. Common errors handled: API errors, network issues, timeouts

**Notes:** Removed "after 3 failures" support contact - keep it simple

---

### Epic 06: Export & Monetization

#### US-016: Export Comic as PNG
**As a** user
**I want to** export my story as a single image
**So that** I can save and share it

**Priority:** Must Have | **Effort:** 3 points | **Dependencies:** US-010

**Acceptance Criteria:**
1. Export button in story view
2. Generates single vertical PNG with all panels
3. Standard resolution (optimized for mobile sharing)
4. Native share sheet opens after export
5. No watermarks (all users equal in MVP)

**Notes:** Removed PDF, ZIP, multiple resolutions, preview, watermark system, storage - just simple PNG export

---

#### US-017: View Credit Balance
**As a** user
**I want to** see my credit balance
**So that** I know when to purchase more

**Priority:** Must Have | **Effort:** 2 points | **Dependencies:** US-001

**Acceptance Criteria:**
1. Credit balance always visible in app header
2. Tap balance to open credit screen
3. Credit screen shows: current balance and "Buy Credits" button
4. Credits displayed before every generation action
5. Unverified accounts cannot use credits and see "Verify Email" prompt
6. Insufficient credits prevent action with "Buy Credits" prompt

**Notes:** Removed color-coding, transaction history, notifications, filtering - minimal viable implementation

---

#### US-018: Purchase Credits
**As a** user
**I want to** buy credits
**So that** I can continue creating

**Priority:** Must Have | **Effort:** 8 points | **Dependencies:** US-017

**Acceptance Criteria:**
1. Purchase screen accessible from balance tap or when credits insufficient
2. Two package options: 100 credits ($9.99), 500 credits ($39.99)
3. Payment via credit/debit card or Apple Pay/Google Pay
4. Credits added within 5 seconds of payment
5. Email receipt sent automatically
6. Failed payments show clear error with retry option

**Notes:** Removed volume discounts, promotional codes, purchase history, PayPal - keep payment flow simple

---

## PHASE 2: ENHANCEMENT (4 weeks)

**Goal:** Add polish and commonly requested features

### US-019: Add Text to Panels
**As a** user
**I want to** add dialogue and captions to panels
**So that** I can tell my story with words

**Priority:** Should Have | **Effort:** 5 points | **Dependencies:** US-010

**Acceptance Criteria:**
1. Edit mode on any panel allows adding text boxes
2. Three text types: speech bubble, thought bubble, caption box
3. Text boxes can be repositioned and resized (drag handles)
4. Max 100 characters per text box with live count
5. Auto-save every 3 seconds

**Notes:** Removed: formatting (bold/italic), rotation, layering, pointer direction, color, font size - just basic text boxes

---

#### US-020: Duplicate Panel
**As a** user
**I want to** copy a panel and modify it
**So that** I can create similar scenes efficiently

**Priority:** Should Have | **Effort:** 2 points | **Dependencies:** US-010

**Acceptance Criteria:**
1. Duplicate button on each panel
2. Duplicate inserted immediately after original
3. Can edit and regenerate duplicated panel
4. Duplication free until regeneration

---

#### US-021: Account Settings
**As a** user
**I want to** manage my account
**So that** I can update my information

**Priority:** Should Have | **Effort:** 3 points | **Dependencies:** US-001

**Acceptance Criteria:**
1. Settings accessible from header menu
2. Can update: name, email, password
3. Email change requires verification
4. Password change requires current password
5. Account deletion option with confirmation

**Notes:** Removed theme, language, notifications, GDPR complexity - basic account management only

---

#### US-022: Help Documentation
**As a** user
**I want to** access help when I need it
**So that** I can learn features

**Priority:** Should Have | **Effort:** 2 points | **Dependencies:** None

**Acceptance Criteria:**
1. Help link in app header
2. Help page includes: getting started, FAQ, tips
3. Search functionality
4. Contact support link at bottom

**Notes:** Removed video tutorials, offline caching - simple web-based help

---

#### US-023: Contact Support
**As a** user
**I want to** contact support
**So that** I can get help with issues

**Priority:** Should Have | **Effort:** 2 points | **Dependencies:** US-001

**Acceptance Criteria:**
1. Contact support form accessible from help
2. Form includes: category, subject, description
3. Confirmation email sent with ticket number
4. Expected response time communicated (24-48 hours)

**Notes:** Removed screenshot upload, ticket history, priority flagging - minimal support form

---

## PHASE 3: GROWTH FEATURES (Backlog)

**Goal:** Features for retention and monetization after validating core product

### Authentication Enhancements
- **US-024:** OAuth Login (Google, Apple, Facebook)
- **US-025:** Social profile integration

### Premium Features
- **US-026:** Subscription Plans (monthly credits + perks)
- **US-027:** Advanced Export Options (PDF, high-res, individual panels)
- **US-028:** Premium Art Styles
- **US-029:** Batch Operations (multi-select delete, duplicate)

### User Experience
- **US-030:** Interactive Onboarding Tutorial
- **US-031:** Usage Analytics Dashboard
- **US-032:** Panel Templates Library
- **US-033:** Collaboration Features (share stories for editing)

### Advanced Features
- **US-034:** Advanced Panel Controls (manual pose selection, composition presets)
- **US-035:** Panel Layout Templates (grid layouts, dynamic sizes)

---

## Development Roadmap

### Phase 1: Ultra-MVP (6 weeks, ~50 points)
**Target:** Functional comic creation and export

**Week 1-2: Foundation**
- US-001: Account Creation (3)
- US-002: Login (2)
- US-017: Credit Balance (2)
- US-018: Purchase Credits (8)

**Week 3-4: Asset Creation**
- US-003: Create Character (8)
- US-004: Create Location (8)
- US-005: Asset Libraries (3)
- US-006: Delete Assets (1)
- US-013: Generation Progress (3)
- US-014: Handle Failures (3)

**Week 5-6: Story & Export**
- US-007: Create Story (2)
- US-008: Story Gallery (2)
- US-009: Delete Story (1)
- US-010: Compose Panel (10)
- US-011: Arrange Panels (3)
- US-012: Delete Panel (1)
- US-016: Export PNG (3)

### Phase 2: Enhancement (4 weeks, ~14 points)
**Target:** Polish and usability improvements

- US-019: Add Text (5)
- US-020: Duplicate Panel (2)
- US-021: Settings (3)
- US-022: Help Docs (2)
- US-023: Contact Support (2)

### Phase 3: Growth (Timeline TBD)
**Target:** Driven by user feedback and metrics

- Features added based on usage data
- Prioritize based on user requests
- Focus on retention and monetization

---

## Definition of Done

A user story is considered complete when:
1. All acceptance criteria are met
2. Code reviewed and approved
3. Unit tests passing
4. Manual QA tested on iOS and Android
5. No critical bugs


/docs
├── product/
│   ├── product-vision.md               # High-level vision (2-3 pages)
│   ├── user-stories.md                 # stories (this doc)
│
├── technical/
│   ├── technical-architecture.md       # System design
│   ├── api-specifications.md           # API contracts
│   ├── data-models.md                  # Database schemas
│   └── security-compliance.md          # Security requirements
│
├── design/
│   ├── design-system.md                # Colors, typography, components
│   ├── wireframes/                     # Low-fidelity wireframes
│   └── user-flows/                     # Journey maps
│
└── project-management/
    ├── sprint-planning.md              # Sprint goals and planning
    ├── release-roadmap.md              # Version releases