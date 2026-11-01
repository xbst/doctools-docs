---
description: "A live demonstration of how a 3DStep page follows a docs site's light/dark toggle, or stays pinned to one scheme with ?theme=."
hide:
  - toc
---
# Light and dark

Flip this site's light/dark toggle in the header. The first page follows it, live; the other two are pinned to one scheme each with a `?theme=` parameter, and stay put.

## Following the site

```markdown
![Put the PiCAN 2 in its shell](../../3d/pican2/pican2-default.3dstep.html){ type=iframe }
```

![Put the PiCAN 2 in its shell, following the site's color scheme](../../3d/pican2/pican2-default.3dstep.html){ type=iframe }

## Pinned to light

```markdown
![Put the PiCAN 2 in its shell, always light](../../3d/pican2/pican2-default.3dstep.html?theme=light){ type=iframe }
```

![Put the PiCAN 2 in its shell, always light](../../3d/pican2/pican2-default.3dstep.html?theme=light){ type=iframe }

## Pinned to dark

```markdown
![Put the PiCAN 2 in its shell, always dark](../../3d/pican2/pican2-default.3dstep.html?theme=dark){ type=iframe }
```

![Put the PiCAN 2 in its shell, always dark](../../3d/pican2/pican2-default.3dstep.html?theme=dark){ type=iframe }

These use the `default` theme, which has its own background, so the scheme each one is in is easy to see. The [PiCAN 2 example](assembly.md) uses a transparent theme instead, and sits on the site's background.

[Light and dark mode](../../guides/light-dark.md) explains the order in which a page picks its scheme, and how a page on another origin is driven with a message.
