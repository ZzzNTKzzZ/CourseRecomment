# Design System: Course AI Finder

## Overview
This document outlines the design tokens used in the "Course AI Finder" project, extracted via Stitch MCP.

## Typography
| Category | Font Family |
| :--- | :--- |
| **Main Font** | Manrope |
| **Headlines** | Manrope |
| **Body Text** | Inter |
| **Labels** | Inter |

## Color Palette

### Primary Colors
| Token | Hex | Preview |
| :--- | :--- | :--- |
| `primary` | `#3525cd` | ![#3525cd](https://via.placeholder.com/15/3525cd/000000?text=+) |
| `on_primary` | `#ffffff` | ![#ffffff](https://via.placeholder.com/15/ffffff/000000?text=+) |
| `primary_container` | `#4f46e5` | ![#4f46e5](https://via.placeholder.com/15/4f46e5/000000?text=+) |
| `on_primary_container` | `#dad7ff` | ![#dad7ff](https://via.placeholder.com/15/dad7ff/000000?text=+) |

### Secondary Colors
| Token | Hex | Preview |
| :--- | :--- | :--- |
| `secondary` | `#58579b` | ![#58579b](https://via.placeholder.com/15/58579b/000000?text=+) |
| `on_secondary` | `#ffffff` | ![#ffffff](https://via.placeholder.com/15/ffffff/000000?text=+) |
| `secondary_container` | `#b6b4ff` | ![#b6b4ff](https://via.placeholder.com/15/b6b4ff/000000?text=+) |
| `on_secondary_container` | `#454386` | ![#454386](https://via.placeholder.com/15/454386/000000?text=+) |

### Tertiary Colors
| Token | Hex | Preview |
| :--- | :--- | :--- |
| `tertiary` | `#7e3000` | ![#7e3000](https://via.placeholder.com/15/7e3000/000000?text=+) |
| `on_tertiary` | `#ffffff` | ![#ffffff](https://via.placeholder.com/15/ffffff/000000?text=+) |
| `tertiary_container` | `#a44100` | ![#a44100](https://via.placeholder.com/15/a44100/000000?text=+) |
| `on_tertiary_container` | `#ffd2be` | ![#ffd2be](https://via.placeholder.com/15/ffd2be/000000?text=+) |

### Global Colors
| Token | Hex | Preview |
| :--- | :--- | :--- |
| `background` | `#f7f9fb` | ![#f7f9fb](https://via.placeholder.com/15/f7f9fb/000000?text=+) |
| `on_background` | `#191c1e` | ![#191c1e](https://via.placeholder.com/15/191c1e/000000?text=+) |
| `surface` | `#f7f9fb` | ![#f7f9fb](https://via.placeholder.com/15/f7f9fb/000000?text=+) |
| `on_surface` | `#191c1e` | ![#191c1e](https://via.placeholder.com/15/191c1e/000000?text=+) |
| `surface_variant` | `#e0e3e5` | ![#e0e3e5](https://via.placeholder.com/15/e0e3e5/000000?text=+) |
| `on_surface_variant` | `#464555` | ![#464555](https://via.placeholder.com/15/464555/000000?text=+) |
| `outline` | `#777587` | ![#777587](https://via.placeholder.com/15/777587/000000?text=+) |
| `outline_variant` | `#c7c4d8` | ![#c7c4d8](https://via.placeholder.com/15/c7c4d8/000000?text=+) |

### Status Colors
| Token | Hex | Preview |
| :--- | :--- | :--- |
| `error` | `#ba1a1a` | ![#ba1a1a](https://via.placeholder.com/15/ba1a1a/000000?text=+) |
| `on_error` | `#ffffff` | ![#ffffff](https://via.placeholder.com/15/ffffff/000000?text=+) |
| `error_container` | `#ffdad6` | ![#ffdad6](https://via.placeholder.com/15/ffdad6/000000?text=+) |
| `on_error_container` | `#93000a` | ![#93000a](https://via.placeholder.com/15/93000a/000000?text=+) |

## Design Philosophy (The Academic Curator)
This design system moves beyond the "SaaS template" aesthetic to embrace an editorial, high-end educational experience. It utilizes intentional asymmetry, expansive negative space, and tonal layering.

### Key Rules:
- **No-Line Rule**: Avoid 1px solid borders. Use tonal shifts and white space for separation.
- **Surface Hierarchy**: Use layered surfaces (e.g., `surface-container-low` on `surface`) to create depth.
- **Glassmorphism**: Floating elements use semi-transparent backgrounds with backdrop blur.
- **Dual-Font System**: Pair Manrope (Modern-Intellectual) with Inter (Functional).
