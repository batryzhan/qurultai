# Design and implementation decisions

The master specification is the authority. This is a local research prototype with no account requirement. The historical biys are cultural metaphors, never historical impersonations.

## Visual direction

Colors: council navy `#0C1016`, ink surface `#151B24`, raised slate `#1C2530`, parchment text `#F4F0E8`, gold `#C9A66B`, teal `#54B89A`. These follow the supplied brief rather than an unrelated landing-page theme.

Typography: Cyrillic-capable Manrope for product controls, restrained Georgia serif for council headings with system fallback. External fonts must not prevent operation offline.

Layout: left-aligned research workbench with persistent navigation and a broad question composer. Three differentiated agent cards make the council legible; session records take priority over decoration. Mobile navigation becomes compact and content stacks vertically. Gold marks user actions; teal, gold and copper distinguish the agent roles without substituting for text labels.

Review against the brief: retain the specified dark council palette, avoid neon and stock imagery, preserve labeled empty states and scientific limitations. Real measurements alone populate benchmark displays. Simulated data is visibly labeled.

## Integration boundaries

Provider capability is an integration hypothesis until tested against Alem with credentials. Manual model configuration avoids guessing supported model IDs. Connection tests are actual server-side requests; no secret is returned to the browser. Curated retrieval only searches the local corpus, and passage matching does not constitute factual verification.

API keys live in the backend environment. This local prototype is intended for loopback use; exposing it publicly would require authentication, authorization, and deployment hardening.
