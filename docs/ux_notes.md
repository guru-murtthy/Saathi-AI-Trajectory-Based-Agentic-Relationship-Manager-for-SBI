# Saathi AI - User Experience (UX) Notes & Usability Feedback

This document captures usability observations and accessibility intent for **Saathi AI** based on informal walkthrough sessions with non-team bank associates.

---

## 1. Usability Observations (Feedback from Walkthroughs)

We ran the Saathi AI RM Dashboard flow past 3 mock users (retail branch relationship managers and staff) and observed the following:

*   **Immediate Comprehension of FFI**: Users instantly understood the Financial Future Index (FFI) score. One user noted: *"It's like a credit score but telling me what they can afford next instead of what they owed last."*
*   **Predictive Life Events Panel**: The predicted life events timeline (e.g. Home Purchase probability at 78%) was highly appreciated. RMs felt it gave them a concrete reason to reach out to the customer.
*   **Clarity on "Requires Human Approval"**: RMs were relieved to see the explicit "Requires Human Approval" warning on product pre-approvals. They expressed that they would not trust an AI to trigger disbursals directly without their review.
*   **Initial Confusion over DNA drivers**: The "DNA Panel" drivers (e.g. `saver_bias` or `UPI ratio`) were slightly confusing at first glance. RMs suggested renaming technical feature descriptors to simpler labels (e.g., changing "UPI ratio" to "Digital payment preference").
*   **Desire for Direct Edit**: In the RM Chat, users wanted to be able to edit the generated recommendation text before copy-pasting it into the customer communication logs.
*   **Feedback loop convenience**: Users liked the direct thumbs-up/down widget. They noted that an inline comment box makes it easy to flag when a recommendation doesn't align with a customer's known circumstances.

---

## 2. Accessibility Intent & Web Compliance

To ensure Saathi AI is usable by all bank personnel, we have designed the user interface with the following accessibility goals:

*   **Color Contrast Compliance**: The application uses a sleek dark slate background (`bg-slate-900`) combined with high-contrast text colors (`text-slate-100` and `text-teal-300`). Color choices adhere to WCAG AA guidelines (contrast ratio of at least 4.5:1 for body text).
*   **Keyboard Navigation**: All interactive elements (prospect selectors, chat input box, feedback thumbs-up/down buttons, and the submit button) are focusable and navigable using standard keyboard tabs. Focus rings are clearly demarcated.
*   **Semantic HTML**: Form inputs use matching `<label>` elements, and icon buttons include `aria-label` attributes to ensure screen readers can announce their actions correctly.
