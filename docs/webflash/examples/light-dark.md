---
description: "A live demonstration of how a WebFlash card follows a docs site's light/dark toggle, or stays pinned to one scheme with ?theme=."
hide:
  - toc
---
# Light and dark

Flip this site's light/dark toggle in the header. The first card follows it, live; the other two are pinned to one scheme each with a `?theme=` parameter, and stay put.

## Following the site

```markdown
![Flash Klipper to an RP2040 board](../../firmware/light-dark/light-dark.webflash.html){ type=iframe }
```

![Flash Klipper to an RP2040 board, following the site's color scheme](../../firmware/light-dark/light-dark.webflash.html){ type=iframe }

## Pinned to light

```markdown
![Flash Klipper to an RP2040 board, always light](../../firmware/light-dark/light-dark.webflash.html?theme=light){ type=iframe }
```

![Flash Klipper to an RP2040 board, always light](../../firmware/light-dark/light-dark.webflash.html?theme=light){ type=iframe }

## Pinned to dark

```markdown
![Flash Klipper to an RP2040 board, always dark](../../firmware/light-dark/light-dark.webflash.html?theme=dark){ type=iframe }
```

![Flash Klipper to an RP2040 board, always dark](../../firmware/light-dark/light-dark.webflash.html?theme=dark){ type=iframe }

These use the `default` theme, which has its own page background, so the scheme each one is in is easy to see. The other examples use `isikstech`, a transparent theme that matches this site.

[Light and dark mode](../../guides/light-dark.md) explains the order in which a page picks its scheme, and how a page on another origin is driven with a message.
