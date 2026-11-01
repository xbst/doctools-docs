---
description: "A live demonstration of how a PinConnect pinout follows a docs site's light/dark toggle, or stays pinned to one scheme with ?theme=."
hide:
  - toc
---
# Light and dark

Flip this site's light/dark toggle in the header. The first pinout follows it, live; the other two are pinned to one scheme each with a `?theme=` parameter, and stay put.

## Following the site

```markdown
![Jumper settings pinout](../../pinouts/jumpers/jumpers.pinout.html){ type=iframe }
```

![Jumper settings pinout, following the site's color scheme](../../pinouts/jumpers/jumpers.pinout.html){ type=iframe style="min-height:50vh;width:100%" }

## Pinned to light

```markdown
![Jumper settings pinout, always light](../../pinouts/jumpers/jumpers.pinout.html?theme=light){ type=iframe }
```

![Jumper settings pinout, always light](../../pinouts/jumpers/jumpers.pinout.html?theme=light){ type=iframe style="min-height:50vh;width:100%" }

## Pinned to dark

```markdown
![Jumper settings pinout, always dark](../../pinouts/jumpers/jumpers.pinout.html?theme=dark){ type=iframe }
```

![Jumper settings pinout, always dark](../../pinouts/jumpers/jumpers.pinout.html?theme=dark){ type=iframe style="min-height:50vh;width:100%" }

These use the `default` theme, which has its own page background, so the scheme each one is in is easy to see. The [OwlFC-Mini example](board.md) uses a transparent theme instead.

[Light and dark mode](../../guides/light-dark.md) explains the order in which a page picks its scheme, and how a page on another origin is driven with a message.
